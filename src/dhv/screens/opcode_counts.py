"""Dialog that shows a table of opcode counts."""

##############################################################################
# Python imports.
from collections import Counter
from dis import Bytecode
from operator import itemgetter
from types import CodeType

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable

##############################################################################
# Textual enhanced imports.
from textual_enhanced.tools import add_key

##############################################################################
# Local imports.
from ..python_docs import visit_operation


##############################################################################
class OpcodeCountsView(ModalScreen[None]):
    """Dialog that displays a table of opcode counts."""

    CSS = """
    OpcodeCountsView {
        align: center middle;

        & > Vertical {
            width: auto;
            height: auto;
            background: $panel;
            border: panel $border;
            max-height: 80%;

            #table-sizer {
                height: auto;
                max-height: 70vh;
                width: auto;
            }

            DataTable {
                margin: 1 2;
                width: auto;
                background: $panel;
                &:focus {
                    background-tint: $foreground 0%;
                }
            }

            Center {
                width: 100%;
            }
        }
    }
    """

    BINDINGS = [("escape", "close")]

    def __init__(self, code: str) -> None:
        """Initialise the dialog.

        Args:
            code: The code to show the counts for.
        """
        super().__init__()
        self._code = code
        """The code to show the counts for."""

    def compose(self) -> ComposeResult:
        """Compose the dialog.

        Returns:
            The content of the dialog.
        """
        with Vertical() as dialog:
            dialog.border_title = "Opcode counts"
            with Vertical(id="table-sizer"):
                yield DataTable()
            with Center():
                yield Button(add_key("Close", "Esc"))

    @classmethod
    def _operation_count(cls, operations: Bytecode) -> Counter[str]:
        """Get the operation counts for the given code.

        Args:
            operations: The operations to take a count from.

        Returns:
            The count of operations within the code.
        """
        return sum(
            [
                cls._operation_count(Bytecode(instruction.argval))
                for instruction in operations
                if isinstance(instruction.argval, CodeType)
            ],
            Counter(instruction.opname for instruction in operations),
        )

    def on_mount(self) -> None:
        """Populate the dialog once the DOM is loaded."""
        count_width = 10
        operations: Bytecode | None = None
        try:
            operations = Bytecode(self._code)
        except SyntaxError:
            pass
        if operations is not None:
            table = self.query_one(DataTable)
            table.cursor_type = "row"
            table.add_columns("Opcode", "Count".rjust(count_width))
            for opcode, count in sorted(
                self._operation_count(operations).items(),
                key=itemgetter(1),
                reverse=True,
            ):
                table.add_row(opcode, f"{count:>{count_width}}", key=opcode)

    @on(Button.Pressed)
    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()

    @on(DataTable.RowSelected)
    def _about_opcode(self, message: DataTable.RowSelected) -> None:
        """Show information about the selected opcode.

        Args:
            message: The message to react to.
        """
        if (opname := message.row_key.value) is not None:
            visit_operation(opname)


### opcode_counts.py ends here
