"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dis import Bytecode, Instruction, opname
from statistics import median_high
from types import CodeType
from typing import Final, Iterator

##############################################################################
# Rich imports.
from rich.console import Group
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ..messages import LocationChanged
from ..python_docs import visit_operation
from ..types import Location

##############################################################################
LINE_NUMBER_WIDTH: Final[int] = 6
"""Width for line numbers."""
OFFSET_WIDTH: Final[int] = 4
"""The width of the display of the offset."""
OPNAME_WIDTH: Final[int] = median_high(len(operation) for operation in opname) + 10
"""The default width to use for opcode names."""


##############################################################################
class Code(Option):
    """Option that marks a new disassembly."""

    def __init__(self, code: CodeType) -> None:
        """Initialise the object.

        Args:
            code: The code that will follow.
        """
        super().__init__(
            Group("", Rule(f"[dim bold]@{hex(id(code))}[/]", style="dim bold")),
            id=f"{hex(id(code))}",
        )


##############################################################################
class Operation(Option):
    """The view of an operation."""

    def __init__(
        self,
        operation: Instruction,
        *,
        opname_width: int = OPNAME_WIDTH,
        show_offset: bool = False,
        show_opcode: bool = False,
        code: CodeType | None = None,
    ) -> None:
        """Initialise the object.

        Args:
            operation: The operation.
            show_offset: Show the offset in the display?
            show_opcode: Show the opcode in the display?
            code: The code that the operation came from.
        """
        self._operation = operation
        """The operation being displayed."""
        self._code = code
        """The code the operation came from."""

        display = Table.grid(expand=True, padding=1)
        display.add_column(width=LINE_NUMBER_WIDTH)
        display.add_column(width=OFFSET_WIDTH if show_offset else 0)
        display.add_column(width=opname_width)
        display.add_column(ratio=1)
        display.add_row(
            str(operation.line_number)
            if operation.line_number is not None and operation.starts_line
            else "",
            f"[dim]{operation.offset}[/]",
            f"{operation.opname} [dim]({operation.opcode})[/]"
            if show_opcode
            else operation.opname,
            f"[dim]code@[/]{hex(id(operation.argval))}"
            if isinstance(operation.argval, CodeType)
            # With Python 3.14, LOAD_SMALL_INT at least has no populated
            # argrepr value despite having a value, so here we use argrepr
            # if it has a value, and if not we repr any non-None argval.
            # This could result in a false negative I guess, but I'd hope
            # that mostly argrepr does the right thing.
            else escape(
                operation.argrepr
                or (repr(operation.argval) if operation.argval is not None else "")
            ),
        )
        super().__init__(
            Group(
                Rule(
                    f"[italic dim]-- L{operation.label}[/]",
                    align="left",
                    style="dim",
                    characters="-",
                ),
                display,
            )
            if operation.is_jump_target
            else display,
            id=self.make_id(operation.offset, code),
        )

    @property
    def operation(self) -> Instruction:
        """The operation being displayed."""
        return self._operation

    @property
    def code(self) -> CodeType | None:
        """The code that the operation belongs to."""
        return self._code

    @staticmethod
    def make_id(offset: int, code: CodeType | None = None) -> str | None:
        """Make an ID for the given operation.

        Args:
           offset: The offset of the instruction.
           code: The code the instruction came from.

        Returns:
            The ID for the operation, or [`None`] if one isn't needed.
        """
        if code:
            return f"operation-{hex(id(code))}-{offset}"
        return f"operation-{offset}"


##############################################################################
class Disassembly(EnhancedOptionList):
    """Widget that displays Python code disassembly."""

    DEFAULT_CSS = """
    Disassembly.--error {
        color: $text-error;
        background: $error 25%;
    }
    """

    BINDINGS = [
        HelpfulBinding(
            "a",
            "about",
            "About opcode",
            tooltip="Show the opcode's documentation in the Python documentation",
        ),
        HelpfulBinding(
            "o",
            "opname(1)",
            "Opname width+",
            show=False,
            tooltip="Increase the width of the opname column",
        ),
        HelpfulBinding(
            "O",
            "opname(-1)",
            "Opname width-",
            show=False,
            tooltip="Decrease the width of the opname column",
        ),
    ]

    HELP = """
    ## Disassembly

    This panel is the disassembly of the Python source code.

    The following keys can be used as shortcuts in this panel:
    """

    code: var[str | None] = var(None)
    """The code to disassemble."""

    show_offset: var[bool] = var(False, init=False)
    """Show the offset of each instruction?"""

    show_opcodes: var[bool] = var(False, init=False)
    """Should we show the opcodes in the disassembly?"""

    opname_width: var[int] = var(OPNAME_WIDTH)
    """The width of opnames in the display."""

    error: var[bool] = var(False)
    """Is there an error with the code we've been given?"""

    def __init__(
        self, id: str | None = None, classes: str | None = None, disabled: bool = False
    ):
        """Initialise the object.

        Args:
            name: The name of the disassembly.
            id: The ID of the disassembly in the DOM.
            classes: The CSS classes of the disassembly.
            disabled: Whether the disassembly is disabled or not.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self._line_map: dict[int, int] = {}
        """A map of line numbers to locations within the disassembly display."""
        self.border_title = "Disassembly"

    def _make_options(self, code: Bytecode) -> Iterator[Code | Operation]:
        """Make the options for the list from the given code.

        Args:
            code: The code to make the options from.

        Yields:
            Either a `Code` or an `Operation` option.
        """
        for operation in code:
            yield Operation(
                operation,
                opname_width=self.opname_width,
                show_offset=self.show_offset,
                show_opcode=self.show_opcodes,
                code=code.codeobj,
            )
        for operation in code:
            if isinstance(operation.argval, CodeType):
                yield Code(operation.argval)
                yield from self._make_options(Bytecode(operation.argval))

    def _watch_error(self) -> None:
        """React to the error state being toggled."""
        self.set_class(self.error, "--error")

    def _repopulate(self) -> None:
        """Fully repopulate the display."""
        # Build the code up first.
        try:
            operations = Bytecode(self.code or "")
        except SyntaxError:
            # There was an error so nope out, but keep the display as is so
            # the user can see what was and also doesn't keep getting code
            # disappear and then appear again.
            self.error = True
            return
        self.error = False

        # Get the options and add them to the option list.
        with self.preserved_highlight:
            self.clear_options().add_options(
                options := list(self._make_options(operations))
            )

        # Build the line map.
        line = 0
        self._line_map = (line_map := {})
        for option in options:
            if (
                isinstance(option, Operation)
                and (operation := option.operation).starts_line
                and operation.line_number is not None
            ):
                line_map[operation.line_number] = line
            line += 1

    def _watch_code(self) -> None:
        """React to the code being changed."""
        self._repopulate()

    def _watch_show_offset(self) -> None:
        """React to the show offset flag being toggled."""
        self._repopulate()

    def _watch_show_opcodes(self) -> None:
        """React to the show opcodes flag being toggled."""
        self._repopulate()

    def _watch_opname_width(self) -> None:
        """React to the opname column width being changed."""
        self._repopulate()

    @on(EnhancedOptionList.OptionHighlighted)
    def _instruction_highlighted(
        self, message: EnhancedOptionList.OptionHighlighted
    ) -> None:
        """Handle an instruction being highlighted.

        Args:
            message: The message to handle.
        """
        message.stop()
        if isinstance(message.option, Operation):
            self.post_message(
                LocationChanged(
                    self,
                    Location(message.option.operation.line_number)
                    if (position := message.option.operation.positions) is None
                    else Location(
                        position.lineno,
                        position.col_offset,
                        position.end_lineno,
                        position.end_col_offset,
                    ),
                )
            )

    @on(EnhancedOptionList.OptionSelected)
    def _maybe_jump_to_code(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Maybe jump to a selected bit of code.

        Args:
            message: The message to handle.
        """
        message.stop()
        if isinstance(message.option, Operation):
            if isinstance(message.option.operation.argval, CodeType):
                self.highlighted = self.get_option_index(
                    hex(id(message.option.operation.argval))
                )
            elif message.option.operation.jump_target is not None:
                if jump_id := Operation.make_id(
                    message.option.operation.jump_target, message.option.code
                ):
                    try:
                        self.highlighted = self.get_option_index(jump_id)
                    except OptionDoesNotExist:
                        self.notify(
                            "Unable to find that jump location",
                            title="Error",
                            severity="error",
                        )

    def goto_first_instruction_on_line(self, line: int) -> None:
        """Go to the first instruction for a given line number.

        Args:
            line: The line number to find the first instruction for.
        """
        if line in self._line_map:
            with self.prevent(EnhancedOptionList.OptionHighlighted):
                self.highlighted = self._line_map[line]

    def action_about(self) -> None:
        """Handle a request to view the opcode's documentation."""
        if self.highlighted is not None and isinstance(
            option := self.get_option_at_index(self.highlighted), Operation
        ):
            visit_operation(option.operation)

    def action_opname(self, change: int) -> None:
        """Change the width of the opname column.

        Args:
            change: The amount of change to apply.
        """
        self.opname_width += change


### disassembly.py ends here
