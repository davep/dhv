"""Provides a message to request a change of code editor theme."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
@dataclass
class SetCodeTheme(Message):
    """Message sent to request a change of code editor theme."""

    theme: str
    """The name of the theme to set."""


### code_theme.py ends here
