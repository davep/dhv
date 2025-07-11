"""The main screen."""

##############################################################################
# Python imports.
from argparse import Namespace
from pathlib import Path

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
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
from ..commands import (
    LoadFile,
    NewCode,
    ShowASTOnly,
    ShowDisassemblyAndAST,
    ShowDisassemblyOnly,
    SwitchLayout,
    ToggleOffsets,
    ToggleOpcodes,
)
from ..data import load_configuration, update_configuration
from ..messages import LocationChanged
from ..providers import MainCommands
from ..widgets import AbstractSyntaxTree, Disassembly, Source


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"DHV v{__version__}"

    DEFAULT_CSS = """
    Main {
        &.--horizontal {
            layout: horizontal;
        }
    }

    Disassembly, AbstractSyntaxTree {
        &.--hidden {
            display: none;
        }
    }

    Source, Disassembly, AbstractSyntaxTree {
        width: 1fr;
        height: 1fr;
        border: none;
        border-top: solid $panel;
        border-left: solid $panel;
        border-title-color: $border 75%;
        padding-right: 0;
        &:focus {
            border: none;
            border-top: solid $border;
            border-left: solid $border;
            border-title-color: $border;
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
        ShowASTOnly,
        ShowDisassemblyAndAST,
        ShowDisassemblyOnly,
    )

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    code: var[str | None] = var(None)
    """The code we're viewing."""

    horizontal_layout: var[bool] = var(True)
    """Should the panes lay out horizontally?"""

    show_disassembly: var[bool] = var(True)
    """Should we show the disassembly panel?"""

    show_ast: var[bool] = var(False)
    """Should we show the AST panel?"""

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
        yield Source()
        with Vertical():
            yield Disassembly().data_bind(Main.code)
            yield AbstractSyntaxTree().data_bind(Main.code)
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
        config = load_configuration()
        self.horizontal_layout = config.horizontal_layout
        self.show_ast = config.show_ast
        self.show_disassembly = config.show_disassembly
        self.query_one(Disassembly).show_offset = config.show_offsets
        self.query_one(Disassembly).show_opcodes = config.show_opcodes
        if isinstance(to_open := self._arguments.source, Path):
            self._show_source(to_open)

    def _watch_horizontal_layout(self) -> None:
        """React to the horizontal layout setting being changed."""
        self.set_class(self.horizontal_layout, "--horizontal")

    def _watch_show_disassembly(self) -> None:
        """React to the disassembly visibility state change."""
        self.query_one(Disassembly).set_class(not self.show_disassembly, "--hidden")

    def _watch_show_ast(self) -> None:
        """React to the AST visibility state change."""
        self.query_one(AbstractSyntaxTree).set_class(not self.show_ast, "--hidden")

    @on(LocationChanged)
    def _location_changed(self, message: LocationChanged) -> None:
        """React to a change of highlighted instruction in the code.

        Args:
            message: The message to handle.
        """
        # If we're not in the source, or we're not getting an update from
        # the source, update the source.
        if not isinstance(message.changer, Source) and not isinstance(
            self.focused, Source
        ):
            self.query_one(Source).highlight_location(message.location)

        # If we're not in the disassembly, or we're not getting an update
        # from the disassembly, update the disassembly.
        if (
            not isinstance(message.changer, Disassembly)
            and not isinstance(self.focused, Disassembly)
            and message.location.start_line is not None
        ):
            self.query_one(Disassembly).goto_first_instruction_on_line(
                message.location.start_line
            )

        # If we're not in the AST, or we're not getting an update from the
        # AST, update the AST.
        if (
            not isinstance(message.changer, AbstractSyntaxTree)
            and not isinstance(self.focused, AbstractSyntaxTree)
            and message.location.start_line is not None
        ):
            self.query_one(AbstractSyntaxTree).goto_first_node_on_line(
                message.location.start_line
            )

    @on(Source.Changed)
    def _code_changed(self) -> None:
        """Handle the fact that the code has changed."""
        self.code = self.query_one(Source).document.text

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

    def _save_panels(self) -> None:
        """Remember which panels are visible."""
        with update_configuration() as config:
            config.show_ast = self.show_ast
            config.show_disassembly = self.show_disassembly

    def action_show_disassembly_only_command(self) -> None:
        """Show only the disassembly."""
        self.show_disassembly = True
        self.show_ast = False
        self._save_panels()

    def action_show_ast_only_command(self) -> None:
        """Show only the AST."""
        self.show_disassembly = False
        self.show_ast = True
        self._save_panels()

    def action_show_disassembly_and_ast_command(self) -> None:
        """Show both the disassembly and the AST."""
        self.show_disassembly = True
        self.show_ast = True
        self._save_panels()


### main.py ends here
