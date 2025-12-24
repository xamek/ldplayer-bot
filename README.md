ldplayer-bot

This repository contains a small automation bot that uses ADB to interact with LDPlayer.

Project layout
- `starter_bot.py`: main script that captures screenshots and taps the game icon.
- `templates/`: image templates used for matching (e.g. `game_icon.png`).
- `test-output/`: captured screenshots and other test artifacts. The directory is tracked but its contents are ignored.

Quick start
1. Ensure `adb` is available on your PATH and LDPlayer is running.
2. (Optional) Create a Python virtual environment and install dependencies from `requirements.txt`.
3. Run the bot:

```bash
python starter_bot.py
```

Notes
- `starter_bot.py` saves screenshots to `test-output/`. A `.gitkeep` file is present so the empty folder is tracked; actual screenshots are ignored by Git.
- Templates are loaded from `templates/` — add any new `.png` templates there.
