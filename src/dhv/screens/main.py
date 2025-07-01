"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace

##############################################################################
# Textual enhanced imports.
from textual.containers import Horizontal
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.widgets import Footer, Header

##############################################################################
# Local imports.
from .. import __version__
from ..widgets import Disassembly, Source

##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"DHV v{__version__}"

    DEFAULT_CSS = """
    Main > Horizontal > * {
        width: 1fr;
        height: 1fr;
    }
    """

    def __init__(self, arguments: Namespace) -> None:
        """Initialise the main screen.

        Args:
            arguments: The arguments passed to the application on the command line.
        """
        self._arguments = arguments
        """The arguments passed on the command line."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        with Horizontal():
            yield Source()
            yield Disassembly()
        yield Footer()

    def on_mount(self) -> None:
        from pathlib import Path
        self.query_one(Source).code = Path(__file__).read_text()
        self.query_one(Disassembly).code = Path(__file__).read_text()

### main.py ends here
