# LDPlayer Bot

An automation bot that uses ADB to interact with LDPlayer using a state machine architecture with multi-screen template matching.

## Features

- **State Machine Architecture**: Loop-based state detection and action execution
- **Multi-Screen Support**: States can detect multiple visual patterns or text
- **Template Matching**: OpenCV-based image template matching
- **Text Detection**: **EasyOCR** for robust text-based state detection
- **Auto-Registration**: States self-register on import
- **Efficient Startup**: EasyOCR model is preloaded to prevent runtime lag
- **Smart Cleanup**: Auto-clears `screenshots/` and `unknown_states/` on startup

## Project Structure

```
ldplayer-bot/
├── bot_main.py              # Main entry point (Preloads EasyOCR)
├── state_machine.py         # State machine core
├── utils.py                 # ADB, CV, and EasyOCR utilities
├── states/                  # State definitions (auto-registered)
├── jupyter_tests/           # Verification tools
│   ├── test_text.ipynb      # EasyOCR text detection tester
│   └── test_template.ipynb  # Template matching tester
├── screenshots/             # Screenshots (gitignored)
├── unknown_states/          # Unmatched states (gitignored)
└── debug_temp/              # Temporary debug files (gitignored)
```

## Quick Start

1. Ensure `adb` is available on PATH and LDPlayer is running
2. Install dependencies:
   ```bash
   pip install easyocr opencv-python numpy
   # (And other dependencies as needed)
   ```
3. Run the bot:
   ```bash
   python bot_main.py
   ```
   *Note: The first run may take a moment to download the EasyOCR model.*

## Adding New States

Each state is a self-contained module:

1. Create a new folder in `states/` (e.g., `states/my_state/`)
2. Add your state Python file and templates
3. Import the state in `states/__init__.py`

Example state using standard template matching:

```python
from state_machine import Action, auto_register_state, get_state_logger
import os

STATE_NAME = "my_state"
TEMPLATE = os.path.join(os.path.dirname(__file__), "template.png")

# Define actions
def my_action_func(context):
    logger = get_state_logger(STATE_NAME)
    logger.info("Executing action...")
    return True # Return True if action was successful

auto_register_state(
    STATE_NAME, 
    actions=[Action(my_action_func)], 
    patterns=[TEMPLATE]
)
```

## Testing

Use the notebooks in `jupyter_tests/` to verify detection:
- `test_text.ipynb`: Check if EasyOCR can read text from your screenshots.
- `test_template.ipynb`: Check if your templates match your screenshots.
