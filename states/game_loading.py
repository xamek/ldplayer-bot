"""
Game Loading State
Detects when the game is in a loading state (e.g., "Loading..." text on screen).
"""

import time
from state_machine import Action, auto_register_state

LOADING_STATE = "game_loading"
LOADING_TEXT = "Loading" # Text to match

class LogLoadingAction(Action):
    """Log that the game is loading."""
    
    def __init__(self):
        super().__init__("log_loading")
    
    def execute(self) -> bool:
        print("Game is loading... Waiting.")
        return True

def get_loading_actions():
    """Get all actions for the loading state."""
    return [
        LogLoadingAction(),
    ]

# Auto-register this state
# Auto-register this state
auto_register_state(LOADING_STATE, LOADING_TEXT, get_loading_actions(), matcher_type="text")
