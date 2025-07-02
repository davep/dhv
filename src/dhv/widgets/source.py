"""Widget for showing some Python source code."""

##############################################################################
# Python imports.
from dis import Instruction

##############################################################################
# Textual imports.
from textual.widgets import TextArea


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
        if instruction.line_number:
            self.select_line(instruction.line_number - 1)


### source.py ends here
