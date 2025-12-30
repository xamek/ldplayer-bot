"""
Bot states module
Importing this package triggers registration of all states located in submodules.
"""

# Import state modules to trigger self-registration
from . import launcher
from . import splash_screen
from . import main_menu
from . import story_menu
from . import main_story_menu
from . import mission_list
from . import game_loading

__all__ = ['launcher', 'splash_screen', 'game_loading', 'main_menu', 'story_menu', 'main_story_menu', 'mission_list']


