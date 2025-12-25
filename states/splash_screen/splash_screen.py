"""
Splash Screen State
Detects the splash screen when it's fully loaded.
"""

from state_machine import Action
from utils import screenshot, SCREENSHOT_FILE, close_game, TEMPLATE_DIR
import os


SPLASH_SCREEN_STATE = "splash_screen"
SPLASH_SCREEN_TEMPLATE = os.path.join(os.path.dirname(__file__), "splash_screen.png")


class TakeScreenshotAction(Action):
    """Take a screenshot of the current game state."""
    
    def __init__(self):
        super().__init__("screenshot")
    
    def execute(self) -> bool:
        screenshot(SCREENSHOT_FILE)
        print(f"Screenshot saved: {SCREENSHOT_FILE}")
        return True


class PrintGameReadyAction(Action):
    """Print that game is ready for action."""
    
    def __init__(self):
        super().__init__("print_ready")
    
    def execute(self) -> bool:
        print("[GAME] Main screen ready! Game is fully loaded.")
        return True


class CloseGameAction(Action):
    """Close the game."""
    
    def __init__(self):
        super().__init__("close_game")
    
    def execute(self) -> bool:
        print("[GAME] Closing game...")
        close_game()
        return True


def get_splash_screen_actions():
    """Get all actions for the splash screen state."""
    return [
        CloseGameAction(),
    ]

from state_machine import auto_register_state
# Auto-register this state
if SPLASH_SCREEN_TEMPLATE:
    auto_register_state(SPLASH_SCREEN_STATE, actions=get_splash_screen_actions(), threshold=0.8, patterns=[SPLASH_SCREEN_TEMPLATE])


