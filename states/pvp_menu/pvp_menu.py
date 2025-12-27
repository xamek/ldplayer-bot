"""
PvP Menu State
Detects when the game is in the PvP selection menu.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
import os

PVP_MENU_STATE = "pvp_menu"
PVP_MENU_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
PVP_MENU_BUTTONS_DIR = os.path.join(os.path.dirname(__file__), "buttons")

class PvPAction(Action):
    """Placeholder action for PvP Menu."""
    
    def __init__(self, name="pvp_idle"):
        super().__init__(name)
    
    def execute(self, context) -> bool:
        target = context.get("target_activity")
        print(f"[GAME] In PvP Menu. Target is {target}.")
        return True

def get_pvp_menu_actions():
    """Get all actions for the pvp menu state."""
    return [
        PvPAction(),
    ]

# Auto-register this state with all templates in the folder
pvp_menu_patterns = get_templates_from_dir(PVP_MENU_TEMPLATES_DIR)
if pvp_menu_patterns:
    auto_register_state(
        PVP_MENU_STATE, 
        actions=get_pvp_menu_actions(), 
        patterns=pvp_menu_patterns
    )
else:
    # Register as text state if no templates available yet
    auto_register_state(
        PVP_MENU_STATE,
        actions=get_pvp_menu_actions(),
        matcher_type="text",
        patterns=["PvP"]
    )
