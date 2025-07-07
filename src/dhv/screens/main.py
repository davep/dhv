"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Textual fspicker imports.
from textual_fspicker import FileOpen, Filters

##############################################################################
# Local imports.
from .. import __version__
from ..commands import LoadFile, NewCode
from ..data import load_configuration, update_configuration
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
        Quit,
        NewCode,
        LoadFile,
        # Everything else.
        ChangeTheme,
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

    @on(Disassembly.InstructionHighlighted)
    def _highlight_code(self, message: Disassembly.InstructionHighlighted) -> None:
        """Handle a request to highlight some code."""
        if self.focused == self.query_one(Disassembly):
            self.query_one(Source).highlight(message.instruction)

    @on(Source.Changed)
    def _code_changed(self) -> None:
        """Handle the fact that the code has changed."""
        self.query_one(Disassembly).code = self.query_one(Source).document.text

    def action_new_code_command(self) -> None:
        """Handle the new code command."""
        self.query_one(Source).load_text("")

    @work
    async def action_load_file_command(self) -> None:
        """Load the content of a file."""
        if not (
            start_location := Path(load_configuration().last_load_location or ".")
        ).is_dir():
            start_location = "."
        if python_file := await self.app.push_screen_wait(
            FileOpen(
                location=str(start_location),
                title="Load Python code",
                open_button="Load",
                must_exist=True,
                filters=Filters(
                    (
                        "Python",
                        lambda p: p.suffix.lower() in (".py", ".pyi", ".pyw", ".py3"),
                    ),
                    ("All", lambda _: True),
                ),
            )
        ):
            try:
                self.query_one(Source).load_text(python_file.read_text())
            except IOError as error:
                self.notify(str(error), title="Unable to load that file")
                return
            with update_configuration() as config:
                config.last_load_location = str(python_file.absolute().parent)


### main.py ends here
