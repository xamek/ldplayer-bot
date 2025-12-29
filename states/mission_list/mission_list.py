"""
Mission List State
Handles scrolling and selecting incomplete missions.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
import os
import time

MISSION_LIST_STATE = "mission_list"
MISSION_LIST_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
MISSION_LIST_BUTTONS_DIR = os.path.join(os.path.dirname(__file__), "buttons")

class FindIncompleteMissionAction(Action):
    """Action to scroll and find an incomplete mission."""
    
    def __init__(self):
        super().__init__("find_incomplete_mission")
    
    def execute(self, context) -> bool:
        print("[GAME] Analyzing Mission List...")
        
        # 1. Take a fresh screenshot
        from utils import screenshot, SCREENSHOT_FILE
        screenshot(SCREENSHOT_FILE)
        
        import cv2
        import numpy as np
        
        img = cv2.imread(SCREENSHOT_FILE)
        if img is None:
            return False
            
        # The mission list is on the right side (roughly x=315 to 1585 in 1600x900)
        # Rows are roughly 210 pixels high
        rows = [
            (110, 310), (320, 520), (530, 730), (740, 940), (950, 1150)
        ]
        
        # We look for "Incomplete" indicators:
        # - Absence of green checkmark (usually at the right end of the row)
        # - Absence of stars on the "Extreme" / "Very Hard" button
        
        # Red "Complete!" ribbon area for each row (top left of the row)
        ribbon_template = os.path.join(MISSION_LIST_TEMPLATES_DIR, "complete_ribbon.png")
        ribbon_x = (345, 485)
        
        for i, (y1, y2) in enumerate(rows):
            if y2 > img.shape[0]: continue
            
            # Use template matching on the specific row area
            row_roi_file = f"debug_row_{i}.png"
            cv2.imwrite(row_roi_file, img[y1:y1+100, ribbon_x[0]:ribbon_x[1]])
            
            from utils import template_present
            is_complete = template_present(row_roi_file, ribbon_template, threshold=0.7)
            
            if not is_complete:
                print(f"    > MISSION INCOMPLETE FOUND (No Complete ribbon)! Clicking row {i+1} at y={(y1+y2)//2}...")
                from utils import tap_point
                tap_point(1000, (y1 + y2) // 2)
                # Small wait to allow the sub-menu to load
                time.sleep(2)
                return True
            else:
                print(f"    > Row {i+1} is complete (ribbon detected).")
                
        # If no incomplete mission found on current screen, scroll down
        print("  > No incomplete mission on screen. Scrolling down...")
        from utils import run_adb
        # Swipe from bottom towards top to scroll down
        run_adb(["shell", "input", "swipe", "1000", "800", "1000", "400", "500"])
        time.sleep(2)
        return False

def get_mission_list_actions():
    return [FindIncompleteMissionAction()]

# Auto-register this state
templates = get_templates_from_dir(MISSION_LIST_TEMPLATES_DIR)
if templates:
    auto_register_state(
        MISSION_LIST_STATE,
        actions=get_mission_list_actions(),
        patterns=templates
    )
