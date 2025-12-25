"""
State Machine for LDPlayer Bot
Loop-based state machine that continuously takes screenshots, matches templates,
and executes actions when states are detected.
"""

from enum import Enum
from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, List
import time
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

@dataclass
class StateDefinition:
    state: 'ScreenState'
    template_path: str
    threshold: float
    actions: List['Action']

# Registry for auto-discovered states
REGISTERED_STATES: List[StateDefinition] = []

def auto_register_state(state: 'ScreenState', template_path: str, actions: List['Action'], threshold: float = 0.8):
    """Auto-register a state definition."""
    REGISTERED_STATES.append(StateDefinition(state, template_path, threshold, actions))



class ScreenState(Enum):
    """Enum for all possible screen states in the bot."""
    LAUNCHER = "launcher"
    GAME_MAIN = "game_main"
    # Add more states as needed


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
        self.current_state: Optional[ScreenState] = None
        self.previous_state: Optional[ScreenState] = None
        
        # Maps state -> (template_path, threshold)
        self.state_templates: Dict[ScreenState, tuple] = {}
        
        # Maps state -> list of actions to execute when state is detected
        self.state_actions: Dict[ScreenState, List[Action]] = {}
        
        # Template matching function
        self.template_matcher: Optional[Callable[[str, str, float], bool]] = None
        
        # Running state
        self.is_running = False
        
        # Unknown state handling
        self.unknown_states_dir = "unknown_states"
        self.log_file = Path(self.unknown_states_dir) / "unknown_states.log"
        Path(self.unknown_states_dir).mkdir(parents=True, exist_ok=True)
        self.unmatched_count = 0
    
    def set_template_matcher(self, matcher_func: Callable[[str, str, float], bool]) -> None:
        """
        Set the template matching function.
        
        Args:
            matcher_func: Function(screenshot_path, template_path, threshold) -> bool
        """
        self.template_matcher = matcher_func
    
    def register_state(self, state: ScreenState, template_path: str, threshold: float = 0.8) -> None:
        """
        Register a state with its template.
        
        Args:
            state: The screen state
            template_path: Path to the template image
            threshold: Match threshold (0.0 to 1.0)
        """
        self.state_templates[state] = (template_path, threshold)
        print(f"Registered state {state.name} with template: {template_path} (threshold: {threshold})")
    
    def register_action(self, state: ScreenState, action: Action) -> None:
        """Register an action to execute when a state is detected."""
        if state not in self.state_actions:
            self.state_actions[state] = []
        self.state_actions[state].append(action)
        print(f"Registered action '{action.name}' for state {state.name}")
    
    def _take_screenshot(self) -> str:
        """Take a screenshot using the callback function."""
        return self.screenshot_callback()
    
    def _match_template(self, screenshot_path: str, state: ScreenState) -> bool:
        """Check if a screenshot matches a state's template."""
        if not self.template_matcher:
            print("ERROR: No template matcher set!")
            return False
        
        if state not in self.state_templates:
            return False
        
        template_path, threshold = self.state_templates[state]
        try:
            return self.template_matcher(screenshot_path, template_path, threshold)
        except Exception as e:
            print(f"Error matching template for {state.name}: {e}")
            return False
    
    def _detect_state(self, screenshot_path: str) -> Optional[ScreenState]:
        """Detect which state the current screenshot matches."""
        for state in self.state_templates.keys():
            if self._match_template(screenshot_path, state):
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
    
    
    def _execute_state_actions(self, state: ScreenState, iteration: int = 0) -> None:
        """Execute all actions registered for a state."""
        if state not in self.state_actions:
            return
        
        iter_str = f" [ITER {iteration}]" if iteration > 0 else ""
        print(f"\n=== STATE: {state.name}{iter_str} ===")
        print(f"Executing {len(self.state_actions[state])} action(s)...")
        
        for action in self.state_actions[state]:
            try:
                print(f"  > {action.name}...", end=" ")
                result = action.execute()
                print("✓" if result else "✗")
                if not result:
                    print(f"    Warning: Action '{action.name}' returned False")
            except Exception as e:
                print(f"✗ ERROR: {e}")
        
        print()
    
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
        
        if not self.state_templates:
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
                
                # Detect state
                detected_state = self._detect_state(screenshot_path)
                
                if detected_state:
                    # State detected
                    if detected_state != self.current_state:
                        # State changed
                        print(f"[ITER {iteration}] Template matched: {detected_state.name}")
                        self.previous_state = self.current_state
                        self.current_state = detected_state
                        state_hold_frames = 1
                        
                        # Execute actions for new state
                        self._execute_state_actions(self.current_state, iteration)
                    else:
                        # Same state
                        state_hold_frames += 1
                else:
                    # No state detected
                    if self.current_state is not None:
                        print(f"[ITER {iteration}] No template matched (was in {self.current_state.name})")
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
    
    def get_current_state(self) -> Optional[ScreenState]:
        """Get the current detected state."""
        return self.current_state
    
    def print_state_info(self) -> None:
        """Print current state information."""
        print(f"\n--- State Info ---")
        print(f"Current: {self.current_state.name if self.current_state else 'None'}")
        print(f"Previous: {self.previous_state.name if self.previous_state else 'None'}")
        print(f"Registered States: {[s.name for s in self.state_templates.keys()]}")
        print(f"-------------------\n")
