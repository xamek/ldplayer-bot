"""
Bot states module
Importing this package triggers registration of all states located in submodules.
"""

# Import state modules to trigger self-registration
from . import launcher
from . import splash_screen
from . import game_loading
from . import main_menu

__all__ = ['launcher', 'splash_screen', 'game_loading', 'main_menu']


