"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from dis import Bytecode, Instruction, opname
from typing import Final, Self

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
LINE_NUMBER_WIDTH: Final[int] = 6
"""Width for line numbers."""
OPNAME_WIDTH: Final[int] = max(len(operation) for operation in opname)
"""Get the maximum length of an operation name."""


##############################################################################
class Operation(Option):
    """The view of an operation."""

    def __init__(self, operation: Instruction, show_opcode: bool = False) -> None:
        """Initialise the object.

        Args:
            operation: The operation.
            show_opcode: Show the opcode in the display?
        """
        self.operation = operation
        """The operation being displayed."""
        label = (
            f"[bold italic i $accent]L{operation.label}:[/]\n"
            if operation.label
            else ""
        )
        line_number = (
            str(operation.line_number)
            if operation.starts_line and operation.line_number is not None
            else ""
        )
        opcode = f" [i dim]({operation.opcode})[/]" if show_opcode else ""
        super().__init__(
            f"{label}{line_number:{LINE_NUMBER_WIDTH}} {operation.opname:{OPNAME_WIDTH}}{opcode} {operation.argrepr}"
        )


##############################################################################
class Disassembly(EnhancedOptionList):
    """Widget that displays Python code disassembly."""

    DEFAULT_CSS = """
    Disassembly.--error {
        color: $text-error;
        background: $error;
    }
    """

    code: var[str | None] = var(None)
    """The code to disassemble."""

    show_opcodes: var[bool] = var(False)
    """Should we show the opcodes in the disassembly?"""

    adaptive: var[bool] = var(False)
    """Show adaptive output?"""

    error: var[bool] = var(False)
    """Is there an error with the code we've been given?"""

    def _add_operations(self) -> Self:
        if self.code:
            try:
                operations = Bytecode(self.code, adaptive=self.adaptive)
            except SyntaxError:
                self.error = True
                return self
            self.clear_options()
            self.add_options(
                Operation(operation, self.show_opcodes) for operation in operations
            )
        else:
            self.clear_options()
        self.error = False
        return self

    def _watch_error(self) -> None:
        """React to the error state being toggled."""
        self.set_class(self.error, "--error")

    def _watch_code(self) -> None:
        """React to the code being changed."""
        with self.preserved_highlight:
            self._add_operations()

    def _watch_show_opcodes(self) -> None:
        """React to the show opcodes flag being toggled."""
        with self.preserved_highlight:
            self._add_operations()

    def _watch_adaptive(self) -> None:
        """React to the adaptive flag being toggled."""
        with self.preserved_highlight:
            self._add_operations()

    @dataclass
    class InstructionHighlighted(Message):
        """Message posted when an instruction is highlighted."""

        instruction: Instruction
        """The highlighted instruction."""

    @on(EnhancedOptionList.OptionHighlighted)
    def _instruction_highlighted(
        self, message: EnhancedOptionList.OptionHighlighted
    ) -> None:
        """Handle an instruction being highlighted.

        Args:
            message: The message to handle.
        """
        message.stop()
        assert isinstance(message.option, Operation)
        self.post_message(self.InstructionHighlighted(message.option.operation))


### disassembly.py ends here
