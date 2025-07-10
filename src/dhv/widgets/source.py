"""Widget for showing some Python source code."""

##############################################################################
# Textual imports.
from textual.widgets import TextArea
from textual.widgets.text_area import Selection

##############################################################################
# Local imports.
from ..messages import LocationChanged


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
        self.border_title = "Source"

    def highlight_location(self, location: LocationChanged) -> None:
        """Highlight the given location.

        Args:
            location: The location message to get the data from.
        """
        if location.line_number_only:
            self.select_line(location.line_number - 1)
        elif (
            location.start_line is not None
            and location.start_column is not None
            and location.end_line is not None
            and location.end_column is not None
        ):
            self.selection = Selection(
                start=(location.start_line - 1, location.start_column),
                end=(location.end_line - 1, location.end_column),
            )
        else:
            self.selection = Selection.cursor(self.selection.end)
        self.scroll_cursor_visible(True)


### source.py ends here
