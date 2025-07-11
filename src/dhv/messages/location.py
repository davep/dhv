"""Provides a message to signify a location change."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message
from textual.widget import Widget

##############################################################################
# Local imports.
from ..types import Location


##############################################################################
@dataclass
class LocationChanged(Message):
    """Message that can be sent to signify a location change."""

    changer: Widget
    """The widget responsible for changing the location."""
    location: Location
    """The new location."""

    @property
    def control(self) -> Widget:
        """An alias for `changer`."""
        return self.changer


### location.py ends here
