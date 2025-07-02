"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dis import Bytecode, Instruction, opname
from typing import Final, Self

##############################################################################
# Python enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Textual imports.
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
LINE_NUMBER_WIDTH: Final[int] = 6
"""Width for line numbers."""
OPNAME_WIDTH: Final[int] = max(len(operation) for operation in opname)
"""Get the maximum length of an operation name."""

##############################################################################
class Operation(Option):
    """The view of an operation."""

    def __init__(self, operation: Instruction, show_opcode: bool=False) -> None:
        """Initialise the object.

        Args:
            operation: The operation.
            show_opcode: Show the opcode in the display?
        """
        self.operation = operation
        """The operation being displayed."""
        # TODO: Label?
        line_number = str(operation.line_number) if operation.starts_line else ""
        opcode = f" [i dim]({operation.opcode})[/]" if show_opcode else ""
        super().__init__(f"{line_number:{LINE_NUMBER_WIDTH}} {operation.opname:{OPNAME_WIDTH}}{opcode} {operation.argrepr}")

##############################################################################
class Disassembly(EnhancedOptionList):
    """Widget that displays Python code disassembly."""

    code: var[str | None] = var(None)
    """The code to disassemble."""

    show_opcodes: var[bool] = var(False)
    """Should we show the opcodes in the disassembly?"""

    def _add_operations(self) -> Self:
        self.clear_options()
        if self.code:
            self.add_options(Operation(operation, self.show_opcodes) for operation in Bytecode(self.code))
        return self

    def _watch_code(self) -> None:
        """React to the code being changed."""
        with self.preserved_highlight:
            self._add_operations()

    def _watch_show_opcodes(self) -> None:
        """React to the show opcodes flag being toggled."""
        with self.preserved_highlight:
            self._add_operations()

### disassembly.py ends here
