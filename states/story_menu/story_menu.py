"""
Story Menu State
Detects when the game is in the story selection menu.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
import os

STORY_MENU_STATE = "story_menu"
STORY_MENU_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
STORY_MENU_BUTTONS_DIR = os.path.join(os.path.dirname(__file__), "buttons")

class StoryAction(Action):
    """Placeholder action for Story Menu."""
    
    def __init__(self, name="story_idle"):
        super().__init__(name)
    
    def execute(self, context) -> bool:
        target = context.get("target_activity")
        print(f"[GAME] In Story Menu. Target is {target}.")
        return True

def get_story_menu_actions():
    """Get all actions for the story menu state."""
    return [
        StoryAction(),
    ]

# Auto-register this state with all templates in the folder
story_menu_patterns = get_templates_from_dir(STORY_MENU_TEMPLATES_DIR)
if story_menu_patterns:
    auto_register_state(
        STORY_MENU_STATE, 
        actions=get_story_menu_actions(), 
        patterns=story_menu_patterns
    )
else:
    # Register as text state if no templates available yet
    auto_register_state(
        STORY_MENU_STATE,
        actions=get_story_menu_actions(),
        matcher_type="text",
        patterns=["Story"]
    )
