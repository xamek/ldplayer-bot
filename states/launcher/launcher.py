"""
Launcher Screen State
Detects the app launcher and launches the game.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
from utils import find_icon_and_tap, SCREENSHOT_FILE
import time
import os


LAUNCHER_STATE = "launcher"
LAUNCHER_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class TapGameIconAction(Action):
    """Tap the game icon to launch the game."""
    
    def __init__(self):
        super().__init__("tap_game_icon")
    
    def execute(self) -> bool:
        # Use the first available template for the tap action (main icon)
        templates = get_templates_from_dir(LAUNCHER_TEMPLATES_DIR)
        if not templates:
            return False
        return find_icon_and_tap(SCREENSHOT_FILE, templates[0], threshold=0.8)


def get_launcher_actions():
    """Get all actions for the launcher state."""
    return [
        TapGameIconAction(),
    ]


# Auto-register this state with all templates in the folder
launcher_patterns = get_templates_from_dir(LAUNCHER_TEMPLATES_DIR)
if launcher_patterns:
    auto_register_state(
        LAUNCHER_STATE, 
        actions=get_launcher_actions(), 
        threshold=0.8, 
        patterns=launcher_patterns
    )

