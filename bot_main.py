"""
LDPlayer Bot - Main Bot Implementation
Combines bot utilities with state machine to automate game tasks.
"""

import time
from state_machine import ScreenStateManager
from utils import screenshot, template_present, extract_text, is_solid_color, is_ldplayer_running

# Import states package to trigger registration
import states



def setup_bot(target_activity: str = "story", threshold: float = 0.8) -> ScreenStateManager:
    """
    Setup and configure the bot's state machine.
    Registers all states, templates, and actions.
    """
    
    print("=" * 50)
    print("Setting up LDPlayer Bot")
    print(f"Target Activity: {target_activity}")
    print(f"Default Threshold: {threshold}")
    print("=" * 50)
    
    # Preload EasyOCR model
    from utils import get_ocr_reader
    print("[SETUP] Preloading EasyOCR model...")
    get_ocr_reader()
    
    # Create state machine with screenshot callback
    from utils import get_screenshot_path
    sm = ScreenStateManager(
        screenshot_callback=lambda iter_idx: screenshot(get_screenshot_path(iter_idx)) or get_screenshot_path(iter_idx),
        poll_interval=2.0,  # Check every 2 seconds
        default_threshold=threshold
    )
    
    # Set the matching functions
    sm.set_template_matcher(template_present)
    sm.set_text_extractor(extract_text)
    sm.set_solid_color_matcher(is_solid_color)
    
    # Set the target activity and threshold in context
    sm.context["target_activity"] = target_activity
    sm.context["threshold"] = threshold
    
    # Register all auto-discovered states
    sm.load_registered_states()
    
    print("\n[SETUP] Setup complete!\n")
    return sm



def run_bot(max_iterations=None, target_activity="story", threshold=0.8):
    """
    Run the bot's main loop.
    
    Args:
        max_iterations: Number of iterations to run (None = infinite, Ctrl+C to stop)
        target_activity: The activity to branch into (story, pvp, next_dream)
        threshold: Centralized template matching threshold
    """
    
    # Check if LDPlayer is running
    print("Checking if LDPlayer is running...")
    if not is_ldplayer_running():
        print("=" * 50)
        print("ERROR: LDPlayer is not running!")
        print("Please start LDPlayer before running the bot.")
        print("=" * 50)
        return
    print("[OK] LDPlayer is running\n")
    
    # Check if the game is already running and close it
    from utils import is_game_running, close_game
    if is_game_running():
        print("[STARTUP] Game is already running. Closing it for a clean start...")
        close_game()
        time.sleep(2)  # Give it a moment to close
    
    # Setup
    sm = setup_bot(target_activity=target_activity, threshold=threshold)
    sm.print_state_info()
    
    # Run the state machine loop
    print("=" * 50)
    print("Starting Bot Loop")
    print("=" * 50 + "\n")
    
    try:
        sm.run(max_iterations=max_iterations)
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    except Exception as e:
        print(f"\n\nBot error: {e}")
        raise
    
    # Summary
    print("\n" + "=" * 50)
    print("Bot Finished")
    print(f"Final State: {sm.get_current_state()}")
    print("=" * 50)


if __name__ == "__main__":
    # Run the bot
    # Set max_iterations=None to run infinitely (Ctrl+C to stop)
    # target_activity can be "story", "pvp", or "next_dream"
    # threshold can be tuned (e.g., 0.7 for more relaxed matching)
    run_bot(max_iterations=200, target_activity="story", threshold=0.7)
