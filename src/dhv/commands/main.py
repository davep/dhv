"""Provides the main commands for the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class NewCode(Command):
    """Empty the editor ready to enter some new code."""

    BINDING_KEY = "ctrl+n"
    SHOW_IN_FOOTER = True
    FOOTER_TEXT = "New"


### main.py ends here
