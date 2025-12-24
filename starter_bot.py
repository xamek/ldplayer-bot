import os
import subprocess
import time
import cv2
import numpy as np

TEST_OUTPUT_DIR = "test-output"
ADB_PATH = "adb"
SCREENSHOT_FILE = os.path.join(TEST_OUTPUT_DIR, "screen.png")
TEMPLATE_DIR = "templates"
GAME_ICON_TEMPLATE = os.path.join(TEMPLATE_DIR, "game_icon.png")  # a cropped image of the Captain Tsubasa icon
GAME_OPEN_TEMPLATE = os.path.join(TEMPLATE_DIR, "game_open.png")  # optional template to detect game main screen

def adb_command(cmd):
    """Run an adb shell command."""
    full_cmd = [ADB_PATH] + cmd
    subprocess.run(full_cmd, capture_output=True)

def screenshot(filename):
    """Capture a screenshot from LDPlayer and ensure output dir exists."""
    out_dir = os.path.dirname(filename) or TEST_OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    with open(filename, "wb") as f:
        subprocess.run([ADB_PATH, "exec-out", "screencap", "-p"], stdout=f)
    print(f"Screenshot saved to {filename}")

def find_icon_and_tap(screenshot_file, template_file):
    """Find the game icon in screenshot and tap it."""
    img = cv2.imread(screenshot_file)
    template = cv2.imread(template_file)
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = 0.8  # adjust if needed
    if max_val >= threshold:
        x, y = max_loc
        h, w = template.shape[:2]
        center_x = x + w // 2
        center_y = y + h // 2
        adb_command(["shell", "input", "tap", str(center_x), str(center_y)])
        print(f"Tapped game icon at ({center_x}, {center_y})")
        return True
    else:
        print("Game icon not found.")
        return False

def template_present(screenshot_file, template_file, threshold=0.8):
    """Return True if the template is found in the given screenshot."""
    if not os.path.exists(screenshot_file) or not os.path.exists(template_file):
        return False
    img = cv2.imread(screenshot_file)
    template = cv2.imread(template_file)
    if img is None or template is None:
        return False
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= threshold

def close_game():
    """Close the game by pressing home button."""
    adb_command(["shell", "input", "keyevent", "3"])  # KEYCODE_HOME
    print("Closed the game (sent HOME).")

if __name__ == "__main__":
    print("Detecting game icon...")
    screenshot(SCREENSHOT_FILE)
    if find_icon_and_tap(SCREENSHOT_FILE, GAME_ICON_TEMPLATE):
        print("Waiting for game to open...")
        # Poll for the game opening. If `templates/game_open.png` exists, use it;
        # otherwise detect a screen change compared to the pre-launch screenshot.
        timeout = 60  # seconds
        poll_interval = 2  # seconds
        start = time.time()
        launched = False
        while time.time() - start < timeout:
            screenshot(SCREENSHOT_FILE)
            # If an explicit game-open template exists, check for it
            if os.path.exists(GAME_OPEN_TEMPLATE) and template_present(SCREENSHOT_FILE, GAME_OPEN_TEMPLATE):
                launched = True
                break
            # Fallback: detect significant screen change from the original launcher screenshot
            try:
                prev = cv2.imread(os.path.join(TEST_OUTPUT_DIR, "screen.png"))
                curr = cv2.imread(SCREENSHOT_FILE)
                if prev is not None and curr is not None and prev.shape == curr.shape:
                    diff = cv2.absdiff(prev, curr)
                    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
                    non_zero = cv2.countNonZero(thresh)
                    total = thresh.shape[0] * thresh.shape[1]
                    ratio = non_zero / float(total)
                    if ratio > 0.02:  # >2% of pixels changed — likely the app opened
                        launched = True
                        break
            except Exception:
                pass
            time.sleep(poll_interval)
        if launched:
            dest = os.path.join(TEST_OUTPUT_DIR, "game_open.png")
            # ensure a final capture of the opened game
            screenshot(dest)
            print("Captured screenshot of the game.")
        close_game()
    print("Done.")