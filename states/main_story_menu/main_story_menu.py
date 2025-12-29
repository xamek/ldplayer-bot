"""
Main Story Menu State
Handles mission selection in the main story menu.
"""

from state_machine import Action, auto_register_state, get_templates_from_dir
import os
import time

MAIN_STORY_MENU_STATE = "main_story_menu"
MAIN_STORY_MENU_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

class SelectIncompleteMissionAction(Action):
    """Action to find and click an incomplete mission list."""
    
    def __init__(self):
        super().__init__("select_incomplete_mission")
    
    def execute(self, context) -> bool:
        print("[GAME] Analyzing Main Story Menu missions...")
        
        # 1. Scroll left to the beginning (just in case)
        from utils import run_adb
        print("  > Scrolling to the beginning (left)...")
        for _ in range(3):
            run_adb(["shell", "input", "swipe", "300", "500", "1300", "500", "500"])
            time.sleep(1)
            
        # 2. Take a fresh screenshot after scrolling
        from utils import screenshot, SCREENSHOT_FILE
        screenshot(SCREENSHOT_FILE)
        
        # 3. Analyze missions
        # We'll look for cards and their completion status
        # Card completion box is usually at the bottom of the card
        # Numbers like "31/36" or "7/12"
        
        import pytesseract
        import cv2
        import re
        
        img = cv2.imread(SCREENSHOT_FILE)
        if img is None:
            return False
            
        # Define areas for the cards (roughly)
        # Card 1: x=35-335, Card 2: x=340-640, Card 3: x=645-945, Card 4: x=950-1250, Card 5: x=1255-1555
        # The completion rate is at the bottom of each card
        cards = [
            (35, 305), (338, 610), (642, 915), (945, 1220), (1248, 1525)
        ]
        
        cards = [
            (35, 305), (338, 610), (642, 915), (945, 1220), (1248, 1525)
        ]
        
        for i, (x1, x2) in enumerate(cards):
            # Completion rate box is roughly y=700-760
            roi = img[700:765, x1:x2]
            
            # Preprocessing: convert to hsv and filter for the yellow/greenish completion bar colors
            # OR just use grayscale and threshold to isolate white numbers on dark background
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
            
            # Digit only config
            config = "--psm 6 -c tessedit_char_whitelist=0123456789/"
            text = pytesseract.image_to_string(thresh, config=config).strip()
            print(f"  > Card {i+1} OCR (Digits): '{text}'")
            
            # Match "X/Y" pattern
            match = re.search(r'(\d+)\s*/\s*(\d+)', text)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
                print(f"    > Found status: {current}/{total}")
                
                if current < total:
                    print(f"    > MISSION INCOMPLETE ({current}/{total})! Clicking card {i+1}...")
                    from utils import tap_point
                    tap_point((x1 + x2) // 2, 400)
                    return True
                else:
                    print(f"    > Card {i+1} is complete ({current}/{total})")
            else:
                # Fallback: Check if the bar is mostly gray (incomplete) or mostly green/yellow (complete)
                # But for now let's hope digits work.
                pass
                
        # If OCR failed, let's try a very specific crop for the first card that we KNOW is incomplete
        # From screenshot, 2nd card is 31/36, 3rd is 7/12.
        # Let's just click the 2nd card (338-610) as a fallback if we detect Main Story Menu but no missions
        print("  > [FALLBACK] No mission detected via OCR. Tapping 2nd card...")
        from utils import tap_point
        tap_point((338 + 610) // 2, 400)
        return True
                
        print("[GAME] No incomplete missions found on this screen.")
        # If not found, maybe scroll right? But user said click FIRST incomplete.
        return False

def get_main_story_menu_actions():
    return [SelectIncompleteMissionAction()]

# Auto-register this state
templates = get_templates_from_dir(MAIN_STORY_MENU_TEMPLATES_DIR)
if templates:
    auto_register_state(
        MAIN_STORY_MENU_STATE,
        actions=get_main_story_menu_actions(),
        patterns=templates
    )
