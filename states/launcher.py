"""
Launcher Screen State
Detects the app launcher and launches the game.
"""

from state_machine import ScreenState, Action
from utils import find_icon_and_tap, SCREENSHOT_FILE, TEMPLATE_DIR
import time
import os


LAUNCHER_STATE = ScreenState.LAUNCHER
LAUNCHER_TEMPLATE = os.path.join(TEMPLATE_DIR, "launcher.png")


class TapGameIconAction(Action):
    """Tap the game icon to launch the game."""
    
    def __init__(self):
        super().__init__("tap_game_icon")
    
    def execute(self) -> bool:
        return find_icon_and_tap(SCREENSHOT_FILE, LAUNCHER_TEMPLATE, threshold=0.8)


class WaitAfterLaunchAction(Action):
    """Wait for game to start loading after tapping icon."""
    
    def __init__(self, duration: float = 3):
        super().__init__(f"wait_after_launch")
        self.duration = duration
    
    def execute(self) -> bool:
        print(f"Waiting {self.duration}s for game to load...")
        time.sleep(self.duration)
        return True


def get_launcher_actions():
    """Get all actions for the launcher state."""
    return [
        TapGameIconAction(),
        WaitAfterLaunchAction(3),
    ]


from state_machine import auto_register_state

# Auto-register this state
auto_register_state(LAUNCHER_STATE, LAUNCHER_TEMPLATE, get_launcher_actions(), threshold=0.8)

