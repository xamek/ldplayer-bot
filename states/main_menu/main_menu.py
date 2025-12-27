"""
Main Menu State
Detects when the game is on the main menu and provides an action to close the game.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
from utils import close_game
import os

MAIN_MENU_STATE = "main_menu"
MAIN_MENU_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
MAIN_MENU_BUTTONS_DIR = os.path.join(os.path.dirname(__file__), "buttons")

class BranchActivityAction(Action):
    """Action to navigate to a specific activity from the main menu."""
    
    def __init__(self):
        super().__init__("branch_activity")
    
    def execute(self, context) -> bool:
        target = context.get("target_activity")
        if not target:
            print("[GAME] No target activity set in context. Staying in Main Menu.")
            return True
        
        print(f"[GAME] Main menu detected. Branching to: {target}")
        
        # Look for a template named after the target activity in the buttons folder
        button_template = os.path.join(MAIN_MENU_BUTTONS_DIR, f"{target}.png")
        threshold = context.get("threshold", 0.8)
        
        if os.path.exists(button_template):
            print(f"  > Looking for button template: {target}.png (threshold: {threshold})")
            from utils import find_icon_and_tap, SCREENSHOT_FILE
            return find_icon_and_tap(SCREENSHOT_FILE, button_template, threshold=threshold)
        else:
            print(f"  > Button template not found: {button_template}")
            print(f"  > Fallback: Fixed positions (Please add {target}.png to buttons folder)")
            
            # Mapping activities to button coordination (fallback)
            activities = {
                "story": {"name": "Story Mode", "pos": (200, 300)},
                "pvp": {"name": "PvP Mode", "pos": (400, 300)},
                "next_dream": {"name": "Next Dream", "pos": (600, 300)}
            }
            
            if target in activities:
                activity = activities[target]
                print(f"  > [FALLBACK] Tapping {activity['name']} at {activity['pos']}...")
                from utils import tap
                return tap(activity['pos'][0], activity['pos'][1])
            
            return False

def get_main_menu_actions():
    """Get all actions for the main menu state."""
    return [
        BranchActivityAction(),
    ]

# Auto-register this state with all templates in the folder
main_menu_patterns = get_templates_from_dir(MAIN_MENU_TEMPLATES_DIR)
if main_menu_patterns:
    auto_register_state(
        MAIN_MENU_STATE, 
        actions=get_main_menu_actions(), 
        patterns=main_menu_patterns
    )
