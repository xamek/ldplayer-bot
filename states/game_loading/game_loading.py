"""
Game Loading State
Detects when the game is in a loading state using multiple loading screen templates
and text-based detection.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
import os

LOADING_STATE = "game_loading"
LOADING_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
LOADING_TEXT = "Loading"  # Text to match

# Auto-register this state with all loading screen templates
loading_patterns = get_templates_from_dir(LOADING_TEMPLATES_DIR)
if loading_patterns:
    auto_register_state(
        LOADING_STATE, 
        actions=[],  # No actions needed, state detection is enough
        matcher_type="template",
        patterns=loading_patterns,
        threshold=0.8
    )
else:
    print(f"WARNING: No loading templates found in {LOADING_TEMPLATES_DIR}")

# Also register text-based detection for "Loading" text
auto_register_state(
    LOADING_STATE,
    actions=[],
    matcher_type="text",
    patterns=[LOADING_TEXT]
)

# Register solid color detection for white and black screens
auto_register_state(
    LOADING_STATE,
    actions=[],
    matcher_type="solid_color",
    patterns=["white", "black"],
    threshold=30  # Tolerance for mean color
)




