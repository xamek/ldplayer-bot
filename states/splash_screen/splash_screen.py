"""
Splash Screen State
Detects the splash screen when it's fully loaded.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
from utils import tap_center
import os


SPLASH_SCREEN_STATE = "splash_screen"
SPLASH_SCREEN_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")





class TapCenterAction(Action):
    """Tap the center of the screen."""
    
    def __init__(self):
        super().__init__("tap_center")
    
    def execute(self, context) -> bool:
        print("[GAME] Tapping center of screen...")
        return tap_center()


def get_splash_screen_actions():
    """Get all actions for the splash screen state."""
    return [
        TapCenterAction(),
    ]

# Auto-register this state with all templates in the folder
splash_patterns = get_templates_from_dir(SPLASH_SCREEN_TEMPLATES_DIR)
if splash_patterns:
    auto_register_state(
        SPLASH_SCREEN_STATE, 
        actions=get_splash_screen_actions(), 
        patterns=splash_patterns,
        threshold=0.7
    )


