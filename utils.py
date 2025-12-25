"""
Bot Utilities
Core functions for ADB operations, screenshots, and template matching.
"""

import os
import subprocess
from pathlib import Path
import cv2
import pytesseract
import time

# Set tesseract path (standard install location on Windows)
# If it's in PATH, this might not be needed, but safe to have reference.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Configuration constants


# Configuration constants
TEST_OUTPUT_DIR = "test-output"
ADB_PATH = "adb"
SCREENSHOT_FILE = os.path.join(TEST_OUTPUT_DIR, "screen.png")
TEMPLATE_DIR = "templates"
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
        data = proc.stdout if isinstance(proc.stdout, (bytes, bytearray)) else proc.stdout.encode("utf-8")
        with open(filename, "wb") as f:
            f.write(data)
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


def tap_point(x, y):
    """Tap a specific point on the screen."""
    run_adb(["shell", "input", "tap", str(x), str(y)])
    print(f"Tapped at ({x}, {y})")


def get_template_center(screenshot_file, template_file, threshold=0.8):
    """Return center (x, y) if template is found, else None."""
    res = match_template(screenshot_file, template_file)
    if not res:
        return None
    max_val, (x, y), (w, h) = res[0], res[1], res[2]
    if max_val >= threshold:
        return int(x + w // 2), int(y + h // 2)
    return None


def find_icon_and_tap(screenshot_file, template_file, threshold=0.8):
    """Find the template in screenshot and tap its center via ADB."""
    center = get_template_center(screenshot_file, template_file, threshold)
    if center:
        tap_point(center[0], center[1])
        return True
    print("Game icon not found.")
    return False


def template_present(screenshot_file, template_file, threshold=0.8):
    """Return True if the template is found in the given screenshot."""
    res = match_template(screenshot_file, template_file)
    if not res:
        return False
    max_val = res[0]
    return max_val >= threshold


def is_ldplayer_running():
    """Check if LDPlayer is running by looking for dnplayer.exe process.
    
    Returns:
        bool: True if LDPlayer is running, False otherwise
    """
    try:
        # Use tasklist command on Windows to check for dnplayer.exe
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq dnplayer.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # If dnplayer.exe is found, it will appear in the output
        if result.returncode == 0 and "dnplayer.exe" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"Error checking if LDPlayer is running: {e}")
        return False


def close_game():
    """Close the game by force-stopping the app package if set, otherwise send HOME."""
    if APP_PACKAGE:
        run_adb(["shell", "am", "force-stop", APP_PACKAGE])
        print(f"Force-stopped {APP_PACKAGE}.")
        return
    run_adb(["shell", "input", "keyevent", "3"])
    print("Closed the game (sent HOME).")


def extract_text(image_path):
    """Extract text from an image using Tesseract OCR."""
    if not Path(image_path).exists():
        return ""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return ""
        
        # Preprocessing for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Simple thresholding to make text stand out
        # adjust 127/255 as needed or use adaptive thresholding
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        text = pytesseract.image_to_string(thresh)
        
        # Debug: Print extracted text
        clean_text = text.strip().replace('\n', ' ') 
        # print(f"[OCR] Extracted: '{clean_text[:50]}...' (Len: {len(text)})")
            
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
