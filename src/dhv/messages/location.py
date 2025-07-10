"""Provides a message to signify a location change."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message
from textual.widget import Widget


##############################################################################
@dataclass
class LocationChanged(Message):
    """Message that can be sent to signify a location change."""

    changer: Widget
    """The widget responsible for changing the location."""
    start_line: int | None
    """The starting line."""
    start_column: int | None = None
    """The starting column offset within the starting line."""
    end_line: int | None = None
    """The ending line."""
    end_column: int | None = None
    """The ending column within the line."""

    @property
    def control(self) -> Widget:
        """An alias for `changer`."""
        return self.changer

    @property
    def line_number(self) -> int:
        """Alias for `start_line`."""
        return self.start_line or 0

    @property
    def line_number_only(self) -> bool:
        """Do we only have a line number?"""
        return self.start_line is not None and all(
            location is None
            for location in (
                self.start_column,
                self.end_line,
                self.end_column,
            )
        )


### location.py ends here
