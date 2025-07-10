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


##############################################################################
class LoadFile(Command):
    """Load the content of a Python source file."""

    BINDING_KEY = "ctrl+l"
    SHOW_IN_FOOTER = True
    FOOTER_TEXT = "Load"


##############################################################################
class SwitchLayout(Command):
    """Switch the screen layout between horizontal and vertical."""

    BINDING_KEY = "f2"


##############################################################################
class ShowDisassemblyOnly(Command):
    """Only show the disassembly of the source code."""

    BINDING_KEY = "ctrl+b"


##############################################################################
class ShowASTOnly(Command):
    """Only show the AST of the source code."""

    BINDING_KEY = "ctrl+t"


##############################################################################
class ShowDisassemblyAndAST(Command):
    """Show both the disassembly and the AST of the source code."""

    BINDING_KEY = "ctrl+o"


### main.py ends here
