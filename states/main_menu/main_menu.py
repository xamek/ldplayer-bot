"""
Main Menu State
Detects when the game is on the main menu and provides an action to close the game.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
from utils import close_game
import os

MAIN_MENU_STATE = "main_menu"
MAIN_MENU_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

class CloseGameAction(Action):
    """Action to close the game when the main menu is detected."""
    
    def __init__(self):
        super().__init__("close_game")
    
    def execute(self) -> bool:
        print("[GAME] Main menu detected. Closing game...")
        close_game()
        return True

def get_main_menu_actions():
    """Get all actions for the main menu state."""
    return [
        CloseGameAction(),
    ]

# Auto-register this state with all templates in the folder
main_menu_patterns = get_templates_from_dir(MAIN_MENU_TEMPLATES_DIR)
if main_menu_patterns:
    auto_register_state(
        MAIN_MENU_STATE, 
        actions=get_main_menu_actions(), 
        threshold=0.8, 
        patterns=main_menu_patterns
    )
