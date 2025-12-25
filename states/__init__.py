"""
Bot states module
Importing this package triggers registration of all states located in submodules.
"""

# Import state modules to trigger self-registration
from . import launcher
from . import game_main
from . import game_loading

__all__ = ['launcher', 'game_main', 'game_loading']

