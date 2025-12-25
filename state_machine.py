"""
State Machine for LDPlayer Bot
Loop-based state machine that continuously takes screenshots, matches templates,
and executes actions when states are detected.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, List
import time
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

@dataclass
class StateDefinition:
    state: str
    patterns: List[str]  # Renamed from pattern to patterns to be generic
    threshold: float
    actions: List['Action']
    matcher_type: str = "template"  # "template" or "text"

# Registry for auto-discovered states
REGISTERED_STATES: List[StateDefinition] = []

def auto_register_state(state: str, pattern: Optional[str] = None, actions: List['Action'] = None, threshold: float = 0.8, matcher_type: str = "template", patterns: Optional[List[str]] = None):
    """
    Auto-register a state definition.
    
    Args:
        state: State name
        pattern: Single pattern string (legacy support)
        actions: List of actions to execute
        threshold: Match threshold
        matcher_type: "template" or "text"
        patterns: List of pattern strings (preferred)
    """
    if actions is None:
        actions = []
        
    # Normalize to list
    final_patterns = []
    if patterns:
        final_patterns.extend(patterns)
    if pattern:
        final_patterns.append(pattern)
        
    if not final_patterns:
        print(f"WARNING: State {state} registered with no patterns!")
        
    REGISTERED_STATES.append(StateDefinition(state, final_patterns, threshold, actions, matcher_type))


class Action(ABC):
    """Abstract base class for actions that can be performed on a state."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the action. Returns True if successful, False otherwise."""
        pass


class ScreenStateManager:
    """
    Manages the state machine loop.
    Takes screenshots, matches templates to detect states, and executes actions.
    """
    
    def __init__(self, screenshot_callback: Callable, poll_interval: float = 1.0):
        """
        Initialize the state machine.
        
        Args:
            screenshot_callback: Function that takes a screenshot and returns filepath
            poll_interval: Time between screenshot attempts in seconds
        """
        self.screenshot_callback = screenshot_callback
        self.poll_interval = poll_interval
        self.current_state: Optional[str] = None
        self.previous_state: Optional[str] = None
        
        # Maps state -> List of (pattern, threshold, matcher_type)
        self.state_criteria: Dict[str, List[tuple]] = {}
        
        # Maps state -> list of actions to execute when state is detected
        self.state_actions: Dict[str, List[Action]] = {}
        
        # Helper functions
        self.template_matcher: Optional[Callable[[str, str, float], bool]] = None
        self.text_extractor: Optional[Callable[[str], str]] = None
        
        # Running state
        self.is_running = False
        
        # Unknown state handling
        self.unknown_states_dir = "unknown_states"
        self.log_file = Path(self.unknown_states_dir) / "unknown_states.log"
        Path(self.unknown_states_dir).mkdir(parents=True, exist_ok=True)
        self.unmatched_count = 0
    
    def set_template_matcher(self, matcher_func: Callable[[str, str, float], bool]) -> None:
        """Set the template matching function."""
        self.template_matcher = matcher_func

    def set_text_extractor(self, extractor_func: Callable[[str], str]) -> None:
        """Set the text extraction function."""
        self.text_extractor = extractor_func
    
    def register_state(self, state: str, pattern: str, threshold: float = 0.8, matcher_type: str = "template") -> None:
        """
        Register a state with its matching criteria.
        Can be called multiple times for the same state to add alternative patterns.
        
        Args:
            state: The screen state name
            pattern: Template path or text to match
            threshold: Match threshold (0.0 to 1.0) for templates
            matcher_type: "template" or "text"
        """
        if state not in self.state_criteria:
            self.state_criteria[state] = []
            
        self.state_criteria[state].append((pattern, threshold, matcher_type))
        print(f"Registered state {state} [{matcher_type}] with pattern: {pattern}")
    
    def register_action(self, state: str, action: Action) -> None:
        """Register an action to execute when a state is detected."""
        if state not in self.state_actions:
            self.state_actions[state] = []
        self.state_actions[state].append(action)
        print(f"Registered action '{action.name}' for state {state}")

    def load_registered_states(self) -> None:
        """Register all auto-discovery states from the global registry."""
        print(f"\n[SETUP] Found {len(REGISTERED_STATES)} registered states.")
        for state_def in REGISTERED_STATES:
            # Register each pattern for the state
            for pattern in state_def.patterns:
                self.register_state(state_def.state, pattern, threshold=state_def.threshold, matcher_type=state_def.matcher_type)
            
            # Register actions
            for action in state_def.actions:
                self.register_action(state_def.state, action)
    
    def _take_screenshot(self) -> str:
        """Take a screenshot using the callback function."""
        return self.screenshot_callback()
    
    def _match_state_criterion(self, screenshot_path: str, state: str) -> bool:
        """Check if a screenshot matches any of the state's criteria."""
        if state not in self.state_criteria:
            return False
        
        criteria_list = self.state_criteria[state]
        
        for pattern, threshold, matcher_type in criteria_list:
            matched = False
            if matcher_type == "template":
                if not self.template_matcher:
                    print("ERROR: No template matcher set!")
                    continue
                try:
                    matched = self.template_matcher(screenshot_path, pattern, threshold)
                except Exception as e:
                    print(f"Error matching template for {state}: {e}")
                    continue
                    
            elif matcher_type == "text":
                if not self.text_extractor:
                    print("ERROR: No text extractor set!")
                    continue
                try:
                    extracted_text = self.text_extractor(screenshot_path)
                    matched = pattern.lower() in extracted_text.lower()
                except Exception as e:
                    print(f"Error extracting text for {state}: {e}")
                    continue
            
            if matched:
                return True
        
        return False
    
    def _detect_state(self, screenshot_path: str) -> Optional[str]:
        """Detect which state the current screenshot matches."""
        for state in self.state_criteria.keys():
            if self._match_state_criterion(screenshot_path, state):
                return state
        return None
    
    def _save_unknown_state(self, screenshot_path: str) -> None:
        """Save and log unmatched screenshot."""
        self.unmatched_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"unknown_{timestamp}.png"
        dest_path = Path(self.unknown_states_dir) / filename
        
        # Copy the screenshot
        try:
            shutil.copy(screenshot_path, str(dest_path))
        except Exception as e:
            print(f"ERROR: Failed to save unknown state screenshot: {e}")
            return
        
        # Log the info
        log_entry = f"[{timestamp}] Unknown state detected. Screenshot: {filename}\n"
        try:
            with open(str(self.log_file), "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"ERROR: Failed to write to log: {e}")
        
        print(f"⚠️  Unknown state #{self.unmatched_count} saved to: {dest_path}")
    
    def _clear_unknown_states(self) -> None:
        """Clear all files in the unknown_states folder except .gitkeep."""
        try:
            unknown_dir = Path(self.unknown_states_dir)
            if unknown_dir.exists():
                for file in unknown_dir.iterdir():
                    if file.is_file() and file.name != ".gitkeep":
                        file.unlink()
                print(f"[STARTUP] Cleared unknown_states folder")
        except Exception as e:
            print(f"ERROR: Failed to clear unknown_states folder: {e}")
    
    
    
    def _execute_state_actions(self, state: str, iteration: int = 0) -> None:
        """Execute all actions registered for a state."""
        if state not in self.state_actions:
            return
        
        iter_str = f" [ITER {iteration}]" if iteration > 0 else ""
        print(f"=== STATE: {state}{iter_str} ===")
        
        for action in self.state_actions[state]:
            try:
                result = action.execute()
                status = "✓" if result else "✗"
                print(f"  > {action.name} {status}")
                if not result:
                    print(f"    Warning: Action '{action.name}' returned False")
            except Exception as e:
                print(f"  > {action.name} ✗ ERROR: {e}")
    
    def run(self, max_iterations: Optional[int] = None) -> None:
        """
        Start the main loop.
        
        Takes screenshots, matches templates, detects state changes, and executes actions.
        
        Args:
            max_iterations: Maximum number of loop iterations (None = infinite)
        """
        if not self.template_matcher:
            print("ERROR: Template matcher not set. Use set_template_matcher() first.")
            return
        
        if not self.state_criteria:
            print("ERROR: No states registered. Use register_state() first.")
            return
        
        # Clear unknown states folder at startup
        self._clear_unknown_states()
        
        self.is_running = True
        iteration = 0
        state_hold_frames = 0  # Track how many frames the same state has been held
        
        print(f"Starting state machine loop (poll interval: {self.poll_interval}s)")
        print(f"Max iterations: {max_iterations if max_iterations else 'infinite'}\n")
        
        try:
            while self.is_running:
                if max_iterations and iteration >= max_iterations:
                    print(f"\nReached max iterations ({max_iterations})")
                    break
                
                iteration += 1
                
                # Take screenshot
                screenshot_path = self._take_screenshot()
                print(f"[ITER {iteration}] Screenshot taken")
                
                # Detect state
                detected_state = self._detect_state(screenshot_path)
                
                if detected_state:
                    # State detected
                    if detected_state != self.current_state:
                        # State changed
                        print(f"State matched: {detected_state}")
                        self.previous_state = self.current_state
                        self.current_state = detected_state
                        state_hold_frames = 1
                        
                        # Execute actions for new state
                        self._execute_state_actions(self.current_state, iteration)
                    else:
                        # Same state
                        state_hold_frames += 1
                        print(f"State unchanged: {detected_state}")
                else:
                    # No state detected
                    if self.current_state is not None:
                        print(f"[ITER {iteration}] No template matched (was in {self.current_state})")
                        self._save_unknown_state(screenshot_path)
                        self.previous_state = self.current_state
                        self.current_state = None
                    else:
                        print(f"[ITER {iteration}] No template matched")
                        self._save_unknown_state(screenshot_path)
                
                # Wait before next iteration
                time.sleep(self.poll_interval)
        
        except KeyboardInterrupt:
            print("\n\nState machine stopped by user")
        except Exception as e:
            print(f"\n\nState machine error: {e}")
            raise
        finally:
            self.is_running = False
    
    def stop(self) -> None:
        """Stop the running state machine loop."""
        self.is_running = False
        print("Stopping state machine...")
    
    def get_current_state(self) -> Optional[str]:
        """Get the current detected state."""
        return self.current_state
    
    def print_state_info(self) -> None:
        """Print current state information."""
        print(f"\n--- State Info ---")
        print(f"Current: {self.current_state if self.current_state else 'None'}")
        print(f"Previous: {self.previous_state if self.previous_state else 'None'}")
        print(f"Registered States: {[s for s in self.state_criteria.keys()]}")
        print(f"-------------------\n")
