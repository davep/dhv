"""Provides the main commands for the application."""

##############################################################################
# Local imports.
from .disassembly import ToggleOffsets, ToggleOpcodes
from .main import (
    ChangeCodeTheme,
    LoadFile,
    NewCode,
    ShowASTOnly,
    ShowDisassemblyAndAST,
    ShowDisassemblyOnly,
    SwitchLayout,
)

##############################################################################
# Exports.
__all__ = [
    "ChangeCodeTheme",
    "LoadFile",
    "NewCode",
    "ShowASTOnly",
    "ShowDisassemblyAndAST",
    "ShowDisassemblyOnly",
    "SwitchLayout",
    "ToggleOffsets",
    "ToggleOpcodes",
]


### __init__.py ends here
