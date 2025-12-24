import subprocess
import time
import cv2
import numpy as np

ADB_PATH = "adb"
SCREENSHOT_FILE = "screen.png"
GAME_ICON_TEMPLATE = "game_icon.png"  # a cropped image of the Captain Tsubasa icon

def adb_command(cmd):
    """Run an adb shell command."""
    full_cmd = [ADB_PATH] + cmd
    subprocess.run(full_cmd, capture_output=True)

def screenshot(filename):
    """Capture a screenshot from LDPlayer."""
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

def close_game():
    """Close the game by pressing home button."""
    adb_command(["shell", "input", "keyevent", "3"])  # KEYCODE_HOME
    print("Closed the game (sent HOME).")

if __name__ == "__main__":
    print("Detecting game icon...")
    screenshot(SCREENSHOT_FILE)
    if find_icon_and_tap(SCREENSHOT_FILE, GAME_ICON_TEMPLATE):
        print("Waiting for game to open...")
        time.sleep(10)  # wait for game to load
        screenshot("game_open.png")
        print("Captured screenshot of the game.")
        close_game()
    print("Done.")