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
        patterns=loading_patterns
    )
else:
    print(f"WARNING: No loading templates found in {LOADING_TEMPLATES_DIR}")

# Register text-based detection for "Loading"
# Optimized for fixed location in bottom right corner (y: 80-100%, x: 70-100%)
# Using PSM 6 (uniform block) and Otsu thresholding for best results in this ROI
auto_register_state(
    LOADING_STATE,
    actions=[],
    matcher_type="text",
    patterns=["Loading", "Now Loading"],
    matcher_kwargs={
        "config": "--psm 6",
        "region": (0.80, 1.0, 0.70, 1.0),
        "threshold_val": 0, # Otsu
        "adaptive": False
    }
)

# 4. Register solid color detection for white and black screens
# Using higher tolerance (50) to catch near-black/white flickers
auto_register_state(
    LOADING_STATE,
    actions=[],
    matcher_type="solid_color",
    patterns=["white", "black"],
    threshold=50
)




