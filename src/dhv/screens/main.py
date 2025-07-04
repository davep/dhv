"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__
from ..providers import MainCommands
from ..widgets import Disassembly, Source


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"DHV v{__version__}"

    DEFAULT_CSS = """
    Source, Disassembly {
        width: 1fr;
        height: 1fr;
        border: none;
        border-left: solid $panel;
        &:focus {
            border: none;
            border-left: solid $border;
            background: $panel 80%;
        }
    }
    """

    COMMAND_MESSAGES = (
        # Keep these together as they're bound to function keys and destined
        # for the footer.
        Help,
        # Everything else.
        ChangeTheme,
        Quit,
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

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

        self.query_one(Source).load_text(Path(__file__).read_text())

    @on(Disassembly.InstructionHighlighted)
    def _highlight_code(self, message: Disassembly.InstructionHighlighted) -> None:
        if self.focused != self.query_one(Source):
            self.query_one(Source).highlight(message.instruction)

    @on(Source.Changed)
    def _code_changed(self) -> None:
        self.query_one(Disassembly).code = self.query_one(Source).document.text


### main.py ends here
