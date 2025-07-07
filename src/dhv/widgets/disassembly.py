"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from dis import Bytecode, Instruction, opname
from types import CodeType
from typing import Final, Self

##############################################################################
# Rich imports.
from rich.markup import escape
from rich.rule import Rule

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
LINE_NUMBER_WIDTH: Final[int] = 6
"""Width for line numbers."""
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
            Rule(f"@{hex(id(code))}", style="dim bold"), id=f"{hex(id(code))}"
        )


##############################################################################
class Operation(Option):
    """The view of an operation."""

    def __init__(
        self,
        operation: Instruction,
        *,
        show_opcode: bool = False,
        code: CodeType | None = None,
    ) -> None:
        """Initialise the object.

        Args:
            operation: The operation.
            show_opcode: Show the opcode in the display?
            code: The code that the operation came from.
        """
        self._operation = operation
        """The operation being displayed."""
        self._code = code
        """The code the operation came from."""
        label = (
            f"[bold italic i $accent]L{operation.label}:[/]\n"
            if operation.is_jump_target
            else ""
        )
        line_number = (
            str(operation.line_number)
            if operation.starts_line and operation.line_number is not None
            else ""
        )
        opcode = f" [i dim]({operation.opcode})[/]" if show_opcode else ""
        arg = (
            f"[dim]code@[/]{hex(id(operation.argval))}"
            if isinstance(operation.argval, CodeType)
            else escape(operation.argrepr)
        )
        super().__init__(
            f"{label}[dim]{line_number:{LINE_NUMBER_WIDTH}}[/] {operation.opname:{OPNAME_WIDTH}}{opcode} {arg}",
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

    code: var[str | None] = var(None)
    """The code to disassemble."""

    show_opcodes: var[bool] = var(False)
    """Should we show the opcodes in the disassembly?"""

    adaptive: var[bool] = var(False)
    """Show adaptive output?"""

    error: var[bool] = var(False)
    """Is there an error with the code we've been given?"""

    def _add_operations(self, code: str | CodeType, fresh: bool = False) -> Self:
        """Add the operations from the given code.

        Args:
            code: The code to add the operations from.
            fresh: Is this a fresh add; should we clear the display?

        Returns:
            Self.
        """
        try:
            operations = Bytecode(code, adaptive=self.adaptive)
        except SyntaxError:
            self.error = True
            return self
        self.error = False
        if fresh:
            self.clear_options()
        if isinstance(code, CodeType):
            self.add_option(Code(code))
        for operation in operations:
            self.add_option(
                Operation(
                    operation, show_opcode=self.show_opcodes, code=operations.codeobj
                )
            )
        for operation in operations:
            if isinstance(operation.argval, CodeType):
                self._add_operations(operation.argval)
        return self

    def _watch_error(self) -> None:
        """React to the error state being toggled."""
        self.set_class(self.error, "--error")

    def _watch_code(self) -> None:
        """React to the code being changed."""
        with self.preserved_highlight:
            self._add_operations(self.code or "", True)

    def _watch_show_opcodes(self) -> None:
        """React to the show opcodes flag being toggled."""
        with self.preserved_highlight:
            self._add_operations(self.code or "", True)

    def _watch_adaptive(self) -> None:
        """React to the adaptive flag being toggled."""
        with self.preserved_highlight:
            self._add_operations(self.code or "", True)

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
        if isinstance(message.option, Operation):
            self.post_message(self.InstructionHighlighted(message.option.operation))

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


### disassembly.py ends here
