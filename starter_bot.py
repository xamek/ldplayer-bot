import os
import subprocess
import time
from pathlib import Path
import cv2
import numpy as np

TEST_OUTPUT_DIR = "test-output"
ADB_PATH = "adb"
SCREENSHOT_FILE = os.path.join(TEST_OUTPUT_DIR, "screen.png")
TEMPLATE_DIR = "templates"
GAME_ICON_TEMPLATE = os.path.join(TEMPLATE_DIR, "game_icon.png")  # a cropped image of the Captain Tsubasa icon
GAME_OPEN_TEMPLATE = os.path.join(TEMPLATE_DIR, "game_open.png")  # optional template to detect game main screen
APP_PACKAGE = "com.klab.captain283.global"


def run_adb(cmd_args, capture=False, text=False):
    """Run adb command and optionally capture output.

    `cmd_args` is the list of arguments after `adb`.
    Returns the CompletedProcess when `capture=True`, otherwise returns None.
    """
    full_cmd = [ADB_PATH] + list(cmd_args)
    if capture:
        return subprocess.run(full_cmd, capture_output=True, text=text)
    subprocess.run(full_cmd)

def screenshot(filename):
    """Capture a screenshot from LDPlayer and ensure output dir exists."""
    out_dir = Path(filename).parent
    if str(out_dir) == ".":
        out_dir = Path(TEST_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = run_adb(["exec-out", "screencap", "-p"], capture=True)
    if proc and proc.stdout:
        # proc.stdout may be bytes when text=False; ensure we write bytes
        data = proc.stdout if isinstance(proc.stdout, (bytes, bytearray)) else proc.stdout.encode("utf-8")
        with open(filename, "wb") as f:
            f.write(data)
        print(f"Screenshot saved to {filename}")
    else:
        print("Failed to capture screenshot")

def match_template(screenshot_file, template_file):
    """Return (max_val, top_left, (w,h)) if match succeeded, else None."""
    if not Path(screenshot_file).exists() or not Path(template_file).exists():
        return None
    img = cv2.imread(str(screenshot_file))
    template = cv2.imread(str(template_file))
    if img is None or template is None:
        return None
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    h, w = template.shape[:2]
    return max_val, max_loc, (w, h)


def find_icon_and_tap(screenshot_file, template_file, threshold=0.8):
    """Find the template in screenshot and tap its center via ADB."""
    res = match_template(screenshot_file, template_file)
    if not res:
        print("Game icon not found (no template or screenshot).")
        return False
    max_val, (x, y), (w, h) = res[0], res[1], res[2]
    if max_val >= threshold:
        center_x = int(x + w // 2)
        center_y = int(y + h // 2)
        run_adb(["shell", "input", "tap", str(center_x), str(center_y)])
        print(f"Tapped game icon at ({center_x}, {center_y})")
        return True
    print("Game icon not found (below threshold).")
    return False

def template_present(screenshot_file, template_file, threshold=0.8):
    """Return True if the template is found in the given screenshot."""
    res = match_template(screenshot_file, template_file)
    if not res:
        return False
    max_val = res[0]
    return max_val >= threshold


def wait_for_game_open(timeout=60, poll_interval=2):
    """Poll until the game main screen appears or timeout.

    Returns True if the game is detected open, False on timeout.
    """
    start = time.time()
    while time.time() - start < timeout:
        screenshot(SCREENSHOT_FILE)
        # If an explicit game-open template exists, check for it
        if Path(GAME_OPEN_TEMPLATE).exists() and template_present(SCREENSHOT_FILE, GAME_OPEN_TEMPLATE):
            return True
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
                    return True
        except Exception:
            pass
        time.sleep(poll_interval)
    return False

def close_game():
    """Close the game by force-stopping the app package if set, otherwise send HOME."""
    if APP_PACKAGE:
        run_adb(["shell", "am", "force-stop", APP_PACKAGE])
        print(f"Force-stopped {APP_PACKAGE}.")
        return
    run_adb(["shell", "input", "keyevent", "3"])  # KEYCODE_HOME
    print("Closed the game (sent HOME).")


def main():
    print("Detecting game icon...")
    screenshot(SCREENSHOT_FILE)
    if find_icon_and_tap(SCREENSHOT_FILE, GAME_ICON_TEMPLATE):
        print("Waiting for game to open...")
        # Wait for the game to open (use dedicated helper)
        launched = wait_for_game_open(timeout=60, poll_interval=2)
        if launched:
            dest = os.path.join(TEST_OUTPUT_DIR, "game_open.png")
            # ensure a final capture of the opened game
            screenshot(dest)
            print("Captured screenshot of the game.")
        close_game()
    print("Done.")

if __name__ == "__main__":
    main()