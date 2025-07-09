"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.reactive import var
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
from ..commands import LoadFile, NewCode, SwitchLayout, ToggleOffsets, ToggleOpcodes
from ..data import load_configuration, update_configuration
from ..providers import MainCommands
from ..widgets import Disassembly, Source


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"DHV v{__version__}"

    DEFAULT_CSS = """
    Main.--horizontal {
        layout: horizontal;
    }

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

    HELP = """
    ## Main application keys and commands

    The following key bindings and commands are available:
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
        SwitchLayout,
        ToggleOffsets,
        ToggleOpcodes,
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    horizontal_layout: var[bool] = var(True)
    """Should the panes lay out horizontally?"""

    def __init__(self, arguments: Namespace) -> None:
        """Initialise the main screen.

        Args:
            arguments: The arguments passed to the application on the command line.
        """
        self._arguments = arguments
        """The arguments passed on the command line."""
        super().__init__()
        self.horizontal_layout = load_configuration().horizontal_layout

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        yield Header()
        yield Source()
        yield Disassembly()
        yield Footer()

    def _show_source(self, source: Path) -> None:
        """Load up the content of a Python source file.

        Args:
            source: The path to the source file to load.
        """
        try:
            self.query_one(Source).load_text(source.read_text())
        except IOError as error:
            self.notify(str(error), title=f"Unable to load {source}", severity="error")
            return
        with update_configuration() as config:
            config.last_load_location = str(source.absolute().parent)

    def on_mount(self) -> None:
        """Configure the display once the DOM is mounted."""
        self.query_one(Disassembly).show_offset = load_configuration().show_offsets
        self.query_one(Disassembly).show_opcodes = load_configuration().show_opcodes
        if isinstance(to_open := self._arguments.source, Path):
            self._show_source(to_open)

    def _watch_horizontal_layout(self) -> None:
        """React to the horizontal layout setting being changed."""
        self.set_class(self.horizontal_layout, "--horizontal")

    @on(Disassembly.InstructionHighlighted)
    def _highlight_code(self, message: Disassembly.InstructionHighlighted) -> None:
        """Handle a request to highlight some code."""
        if self.focused == self.query_one(Disassembly):
            self.query_one(Source).highlight(message.instruction)

    @on(Source.SelectionChanged)
    def _highlight_disassembly(self, message: Source.SelectionChanged) -> None:
        """Handle the selection changing in the code."""
        if self.focused == self.query_one(Source):
            self.query_one(Disassembly).goto_first_instruction_on_line(
                message.selection.end[0] + 1
            )

    @on(Source.Changed)
    def _code_changed(self) -> None:
        """Handle the fact that the code has changed."""
        self.query_one(Disassembly).code = self.query_one(Source).document.text

    def action_new_code_command(self) -> None:
        """Handle the new code command."""
        self.query_one(Source).load_text("")

    @work
    async def action_load_file_command(self) -> None:
        """Browse for and open a Python source file."""
        if not (
            start_location := Path(load_configuration().last_load_location or ".")
        ).is_dir():
            start_location = Path(".")
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
            self._show_source(python_file)

    def action_switch_layout_command(self) -> None:
        """Switch the layout of the window."""
        self.horizontal_layout = not self.horizontal_layout
        with update_configuration() as config:
            config.horizontal_layout = self.horizontal_layout

    def action_toggle_offsets_command(self) -> None:
        """Toggle the display of the offsets."""
        show = not self.query_one(Disassembly).show_offset
        self.query_one(Disassembly).show_offset = show
        with update_configuration() as config:
            config.show_offsets = show

    def action_toggle_opcodes_command(self) -> None:
        """Toggle the display of the numeric opcodes."""
        show = not self.query_one(Disassembly).show_opcodes
        self.query_one(Disassembly).show_opcodes = show
        with update_configuration() as config:
            config.show_opcodes = show


### main.py ends here
