"""
Game Loading Screen State
Waits for the game to load. Does not detect - just a waiting state.
Remove this state from bot_main.py registration since it doesn't match templates.
"""

from state_machine import Action
import time


class WaitForGameLoadAction(Action):
    """Wait for the game to load."""
    
    def __init__(self, duration: float = 2):
        super().__init__("wait_game_load")
        self.duration = duration
    
    def execute(self) -> bool:
        print(f"Game is loading... waiting {self.duration}s")
        time.sleep(self.duration)
        return True
