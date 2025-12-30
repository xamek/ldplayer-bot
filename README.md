# LDPlayer Bot

An automation bot that uses ADB to interact with LDPlayer using a state machine architecture with multi-screen template matching.

## Features

- **State Machine Architecture**: Loop-based state detection and action execution
- **Multi-Screen Support**: States can detect multiple visual patterns or text
- **Template Matching**: OpenCV-based image template matching
- **Text Detection**: Tesseract OCR for text-based state detection
- **Auto-Registration**: States self-register on import

## Project Structure

```
ldplayer-bot/
├── bot_main.py              # Main entry point
├── state_machine.py         # State machine core
├── utils.py                 # ADB and CV utilities
├── states/                  # State definitions
│   ├── launcher/            # Launcher state
│   │   ├── launcher.py
│   │   └── launcher.png
│   ├── splash_screen/       # Splash screen state
│   │   ├── splash_screen.py
│   │   └── splash_screen.png
│   └── game_loading/        # Loading state
│       ├── game_loading.py
│       └── templates/       # Multiple loading screens
├── screenshots/             # Screenshots (gitignored)
└── unknown_states/          # Unmatched states (gitignored)
```

## Quick Start

1. Ensure `adb` is available on PATH and LDPlayer is running
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot_main.py
   ```

## Adding New States

Each state is a self-contained module with its templates:

1. Create a new folder in `states/` (e.g., `states/my_state/`)
2. Add your state Python file and templates
3. Import the state in `states/__init__.py`

Example state structure:
```python
from state_machine import Action, auto_register_state
import os

STATE_NAME = "my_state"
TEMPLATE = os.path.join(os.path.dirname(__file__), "template.png")

class MyAction(Action):
    def execute(self) -> bool:
        # Your action logic
        return True

auto_register_state(STATE_NAME, actions=[MyAction()], patterns=[TEMPLATE])
```

## Notes

- Screenshots are saved to `screenshots/` for debugging
- Unknown states are logged to `unknown_states/` for analysis
- States support multiple patterns for robust detection

