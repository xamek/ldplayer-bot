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
    """Action to navigate to Main Story from Story Menu."""
    
    def __init__(self):
        super().__init__("click_main_story")
    
    def execute(self, context) -> bool:
        print("[GAME] In Story Menu. Looking for Main Story...")
        
        main_story_template = os.path.join(STORY_MENU_BUTTONS_DIR, "main_story.png")
        threshold = context.get("threshold", 0.7)
        
        if os.path.exists(main_story_template):
            from utils import find_icon_and_tap
            screenshot_path = context.get("last_screenshot")
            if find_icon_and_tap(screenshot_path, main_story_template, threshold=threshold):
                return True
            print(f"  > Main Story icon not found at {threshold} threshold. Trying fallback...")
        
        # Fallback coordinate for 1600x900
        from utils import tap_point
        print("  > [FALLBACK] Tapping Main Story at (185, 332)...")
        tap_point(185, 332)
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
