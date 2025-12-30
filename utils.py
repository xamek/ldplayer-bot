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
SCREENSHOTS_DIR = "screenshots"
ADB_PATH = "adb"
APP_PACKAGE = "com.klab.captain283.global"


def get_screenshot_path(iteration: int = None) -> str:
    """Generate a screenshot path, optionally including iteration number."""
    if iteration is not None:
        return os.path.join(SCREENSHOTS_DIR, f"screen_{iteration}.png")
    return os.path.join(SCREENSHOTS_DIR, "screen.png")


def clear_screenshots():
    """Clear all files in the screenshots directory."""
    try:
        if os.path.exists(SCREENSHOTS_DIR):
            for file in os.listdir(SCREENSHOTS_DIR):
                if file == ".gitkeep":
                    continue
                file_path = os.path.join(SCREENSHOTS_DIR, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            print(f"[STARTUP] Cleared {SCREENSHOTS_DIR} folder")
    except Exception as e:
        print(f"ERROR: Failed to clear screenshots folder: {e}")


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
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = run_adb(["exec-out", "screencap", "-p"], capture=True)
    if proc and proc.stdout:
        data = proc.stdout if isinstance(proc.stdout, (bytes, bytearray)) else proc.stdout.encode("utf-8")
        with open(filename, "wb") as f:
            f.write(data)
    else:
        print("Failed to capture screenshot")


def match_template(screenshot_file, template_file, retries=3):
    """Return (max_val, top_left, (w,h)) if match succeeded, else None."""
    if not Path(screenshot_file).exists() or not Path(template_file).exists():
        return None
        
    img = None
    template = cv2.imread(str(template_file))
    
    # Retry reading screenshot to avoid conflict with ADB write
    for i in range(retries):
        img = cv2.imread(str(screenshot_file))
        if img is not None:
            break
        time.sleep(0.1 * (i + 1))
        
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


def send_tab():
    """Send a tab keyevent to the emulator."""
    run_adb(["shell", "input", "keyevent", "61"])
    print("Sent TAB key")


def tap_center():
    """Tap the center of the screen."""
    res = run_adb(["shell", "wm", "size"], capture=True, text=True)
    if res and res.stdout:
        # Expected format: "Physical size: 1280x720"
        try:
            size_str = res.stdout.split(":")[-1].strip()
            width, height = map(int, size_str.split("x"))
            tap_point(width // 2, height // 2)
            return True
        except (ValueError, IndexError):
            print(f"Failed to parse screen size: {res.stdout}")
    
    print("Could not determine screen size for center tap")
    return False


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


def is_game_running():
    """Check if the game app is running on the device."""
    if not APP_PACKAGE:
        return False
    # Use pidof to check if the process exists
    res = run_adb(["shell", "pidof", APP_PACKAGE], capture=True, text=True)
    return res and res.stdout.strip() != ""


def extract_text(image_path, config="", region=None, threshold_val=127, invert=False, adaptive=False):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_path: Path to the image file
        config: Optional tesseract config string (e.g., "--psm 11")
        region: Optional region tuple (y1, y2, x1, x2) as percentages (0.0 to 1.0)
        threshold_val: Value for binary thresholding (default 127, use 0 for Otsu)
        invert: Whether to invert the image (bitwise_not) before OCR
        adaptive: Whether to use adaptive thresholding (overrides threshold_val)
    """
    if not Path(image_path).exists():
        return ""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return ""
        
        # Apply ROI if specified
        if region:
            h, w = img.shape[:2]
            y1, y2, x1, x2 = region
            img = img[int(y1*h):int(y2*h), int(x1*w):int(x2*w)]
        
        # Preprocessing for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Thresholding
        if adaptive:
            # Adaptive thresholding (useful for varied lighting/contrast)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
        elif threshold_val == 0:
            # Otsu's thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Simple thresholding
            _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
            
        # Invert if requested
        if invert:
            thresh = cv2.bitwise_not(thresh)
        
        text = pytesseract.image_to_string(thresh, config=config)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""


def is_solid_color(image_path, color_name, tolerance=30, std_dev_threshold=20):
    """
    Check if the image is a solid color (black or white).
    
    Args:
        image_path: Path to the image file
        color_name: "white" or "black"
        tolerance: How close the mean must be to 0 or 255
        std_dev_threshold: Maximum standard deviation allowed (lower means more uniform)
    """
    if not Path(image_path).exists():
        return False
    
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            return False
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean and standard deviation
        mean, std_dev = cv2.meanStdDev(gray)
        mean_val = mean[0][0]
        std_val = std_dev[0][0]
        
        # Check if the image is uniform enough
        if std_val > std_dev_threshold:
            return False
            
        if color_name.lower() == "white":
            # White is 255
            return mean_val >= (255 - tolerance)
        elif color_name.lower() == "black":
            # Black is 0
            return mean_val <= tolerance
            
        return False
    except Exception as e:
        print(f"Error in is_solid_color: {e}")
        return False
