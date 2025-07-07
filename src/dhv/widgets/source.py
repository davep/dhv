"""Widget for showing some Python source code."""

##############################################################################
# Python imports.
from dis import Instruction

##############################################################################
# Textual imports.
from textual.widgets import TextArea
from textual.widgets.text_area import Selection


##############################################################################
class Source(TextArea):
    """Widget that displays Python source code."""

    def __init__(self) -> None:
        """Initialise the widget."""
        super().__init__(
            "",
            language="python",
            soft_wrap=False,
            show_line_numbers=True,
        )

    def highlight(self, instruction: Instruction) -> None:
        """Highlight the given instruction.

        Args:
            instruction: The instruction to highlight.
        """
        if (
            (position := instruction.positions) is not None
            and position.lineno is not None
            and position.col_offset is not None
            and position.end_lineno is not None
            and position.end_col_offset is not None
        ):
            self.selection = Selection(
                start=(position.lineno - 1, position.col_offset),
                end=(position.end_lineno - 1, position.end_col_offset),
            )
        elif instruction.line_number:
            self.select_line(instruction.line_number - 1)


### source.py ends here
