"""
Bot states module
Importing this package triggers registration of all states located in submodules.
"""

# Import state modules to trigger self-registration
from . import launcher
from . import splash_screen
from . import game_loading

__all__ = ['launcher', 'splash_screen', 'game_loading']


