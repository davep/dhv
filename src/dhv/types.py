"""Provides helper types used in the application."""

##############################################################################
# Python imports.
from typing import NamedTuple


##############################################################################
class Location(NamedTuple):
    """A location within a body of code."""

    start_line: int | None
    """The line the location starts on."""
    start_column: int | None = None
    """The column the location starts on."""
    end_line: int | None = None
    """The line the location ends on."""
    end_column: int | None = None
    """The column the location ends on."""

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


### types.py ends here
