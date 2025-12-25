"""
Game Main Screen State
Detects the main game screen when it's fully loaded.
"""

from state_machine import ScreenState, Action
from utils import screenshot, SCREENSHOT_FILE, close_game, TEMPLATE_DIR
import os


GAME_MAIN_STATE = ScreenState.GAME_MAIN
GAME_MAIN_TEMPLATE = os.path.join(TEMPLATE_DIR, "game_main.png")


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


def get_game_main_actions():
    """Get all actions for the game main state."""
    return [
        TakeScreenshotAction(),
        PrintGameReadyAction(),
        CloseGameAction(),
    ]
