"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace

##############################################################################
# Textual enhanced imports.
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__

##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"DHV v{__version__}"

    def __init__(self, arguments: Namespace) -> None:
        """Initialise the main screen.

        Args:
            arguments: The arguments passed to the application on the command line.
        """
        self._arguments = arguments
        """The arguments passed on the command line."""
        super().__init__()

### main.py ends here
