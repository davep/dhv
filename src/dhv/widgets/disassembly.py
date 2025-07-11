"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dis import Bytecode, Instruction, opname
from types import CodeType
from typing import Final, Self
from webbrowser import open_new

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
from ..types import Location

##############################################################################
LINE_NUMBER_WIDTH: Final[int] = 6
"""Width for line numbers."""
OFFSET_WIDTH: Final[int] = 4
"""The width of the display of the offset."""
OPNAME_WIDTH: Final[int] = max(len(operation) for operation in opname)
"""Get the maximum length of an operation name."""


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
        display.add_column(width=OPNAME_WIDTH)
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
            else escape(operation.argrepr),
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
            "o",
            "opcode_documentation",
            "About opcode",
            tooltip="Show the opcode's documentation in the Python documentation",
        )
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

    def _add_operations(self, code: str | CodeType, fresh: bool = False) -> Self:
        """Add the operations from the given code.

        Args:
            code: The code to add the operations from.
            fresh: Is this a fresh add; should we clear the display?

        Returns:
            Self.
        """

        # Build the code up first.
        try:
            operations = Bytecode(code)
        except SyntaxError:
            # There was an error so nope out, but keep the display as is so
            # the user can see what was and also doesn't keep getting code
            # disappear and then appear again.
            self.error = True
            return self
        self.error = False

        # If this is a fresh add we start out by clearing everything down.
        if fresh:
            self.clear_options()
            self._line_map = {}

        # If we've been given a code object, rather than some source, add a
        # marker for that.
        if isinstance(code, CodeType):
            self.add_option(Code(code))

        # Add each operation...
        for operation in operations:
            self.add_option(
                Operation(
                    operation,
                    show_offset=self.show_offset,
                    show_opcode=self.show_opcodes,
                    code=operations.codeobj,
                )
            )
            if operation.line_number is not None and operation.starts_line:
                self._line_map[operation.line_number] = self.option_count - 1

        # Now look for any operations that have code as their arguments, and
        # add that code too.
        for operation in operations:
            if isinstance(operation.argval, CodeType):
                self._add_operations(operation.argval)

        return self

    def _watch_error(self) -> None:
        """React to the error state being toggled."""
        self.set_class(self.error, "--error")

    def _repopulate(self) -> None:
        """Fully repopulate the display."""
        with self.preserved_highlight:
            self._add_operations(self.code or "", True)

    def _watch_code(self) -> None:
        """React to the code being changed."""
        self._repopulate()

    def _watch_show_offset(self) -> None:
        """React to the show offset flag being toggled."""
        self._repopulate()

    def _watch_show_opcodes(self) -> None:
        """React to the show opcodes flag being toggled."""
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
                LocationChanged(self, Location(message.option.operation.line_number))
                if message.option.operation.positions is None
                else LocationChanged(
                    self,
                    Location(
                        start_line=message.option.operation.positions.lineno,
                        start_column=message.option.operation.positions.col_offset,
                        end_line=message.option.operation.positions.end_lineno,
                        end_column=message.option.operation.positions.end_col_offset,
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
        """Go to the first instruction for a given line number."""
        if line in self._line_map:
            self.highlighted = self._line_map[line]

    def action_opcode_documentation(self) -> None:
        """Handle a request to view the opcode's documentation."""
        if self.highlighted is not None and isinstance(
            option := self.get_option_at_index(self.highlighted), Operation
        ):
            open_new(
                f"https://docs.python.org/3/library/dis.html#opcode-{option.operation.opname}"
            )


### disassembly.py ends here
