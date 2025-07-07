"""Provides commands that are aimed at the disassembly display."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class ToggleOpcodes(Command):
    """Toggle the display of the numeric opcodes."""

    BINDING_KEY = "f3"


### disassembly.py ends here
