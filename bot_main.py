"""
LDPlayer Bot - Main Bot Implementation
Combines bot utilities with state machine to automate game tasks.
"""

from state_machine import ScreenStateManager
from utils import screenshot, template_present, SCREENSHOT_FILE

# Import states and their actions
from states.launcher import LAUNCHER_STATE, LAUNCHER_TEMPLATE, get_launcher_actions
from states.game_main import GAME_MAIN_STATE, GAME_MAIN_TEMPLATE, get_game_main_actions


def template_matcher(screenshot_path: str, template_path: str, threshold: float) -> bool:
    """Match a template in a screenshot."""
    if not template_path:
        return False
    return template_present(screenshot_path, template_path, threshold)


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
    
    # Set the template matching function
    sm.set_template_matcher(template_matcher)
    
    # Register LAUNCHER state
    print("\n[SETUP] Registering LAUNCHER state...")
    sm.register_state(LAUNCHER_STATE, LAUNCHER_TEMPLATE, threshold=0.8)
    for action in get_launcher_actions():
        sm.register_action(LAUNCHER_STATE, action)
    
    # Register GAME_MAIN state (if template exists)
    print("[SETUP] Registering GAME_MAIN state...")
    if GAME_MAIN_TEMPLATE:
        sm.register_state(GAME_MAIN_STATE, GAME_MAIN_TEMPLATE, threshold=0.8)
    for action in get_game_main_actions():
        sm.register_action(GAME_MAIN_STATE, action)
    
    print("\n[SETUP] Setup complete!\n")
    return sm


def run_bot(max_iterations=None):
    """
    Run the bot's main loop.
    
    Args:
        max_iterations: Number of iterations to run (None = infinite, Ctrl+C to stop)
    """
    
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
