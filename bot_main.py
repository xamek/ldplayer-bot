"""
LDPlayer Bot - Main Bot Implementation
Combines bot utilities with state machine to automate game tasks.
"""

from state_machine import ScreenStateManager
from utils import screenshot, template_present, extract_text, SCREENSHOT_FILE, is_ldplayer_running

# Import states package to trigger registration
import states



def setup_bot() -> ScreenStateManager:
    """
    Setup and configure the bot's state machine.
    Registers all states, templates, and actions.
    """
    
    print("=" * 50)
    print("Setting up LDPlayer Bot")
    print("=" * 50)
    
    # Create state machine with screenshot callback
    sm = ScreenStateManager(
        screenshot_callback=lambda: screenshot(SCREENSHOT_FILE) or SCREENSHOT_FILE,
        poll_interval=2.0  # Check every 2 seconds
    )
    
    # Set the matching functions
    sm.set_template_matcher(template_present)
    sm.set_text_extractor(extract_text)
    
    # Register all auto-discovered states
    sm.load_registered_states()
    
    print("\n[SETUP] Setup complete!\n")
    return sm



def run_bot(max_iterations=None):
    """
    Run the bot's main loop.
    
    Args:
        max_iterations: Number of iterations to run (None = infinite, Ctrl+C to stop)
    """
    
    # Check if LDPlayer is running
    print("Checking if LDPlayer is running...")
    if not is_ldplayer_running():
        print("=" * 50)
        print("ERROR: LDPlayer is not running!")
        print("Please start LDPlayer before running the bot.")
        print("=" * 50)
        return
    print("✓ LDPlayer is running\n")
    
    # Setup
    sm = setup_bot()
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
    # Set max_iterations=10 for testing (will run for 10 screenshot iterations)
    run_bot(max_iterations=200)
