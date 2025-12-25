"""
Bot states module
Each state file contains its template path and associated actions.
"""

from .launcher import LAUNCHER_STATE, LAUNCHER_TEMPLATE
from .game_main import GAME_MAIN_STATE, GAME_MAIN_TEMPLATE

__all__ = [
    'LAUNCHER_STATE', 'LAUNCHER_TEMPLATE',
    'GAME_MAIN_STATE', 'GAME_MAIN_TEMPLATE',
]
