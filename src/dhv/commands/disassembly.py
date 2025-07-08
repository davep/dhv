"""Provides commands that are aimed at the disassembly display."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class ToggleOffsets(Command):
    """Toggle the display of the offsets"""

    BINDING_KEY = "f3"


##############################################################################
class ToggleOpcodes(Command):
    """Toggle the display of the numeric opcodes"""

    BINDING_KEY = "f4"


### disassembly.py ends here
