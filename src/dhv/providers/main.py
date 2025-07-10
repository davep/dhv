"""Provides the main application commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import (
    ChangeTheme,
    CommandHits,
    CommandsProvider,
    Help,
    Quit,
)

##############################################################################
# Local imports.
from ..commands import (
    LoadFile,
    NewCode,
    ShowASTOnly,
    ShowDisassemblyAndAST,
    ShowDisassemblyOnly,
    SwitchLayout,
    ToggleOffsets,
    ToggleOpcodes,
)


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield ChangeTheme()
        yield Help()
        yield Quit()
        yield LoadFile()
        yield NewCode()
        yield SwitchLayout()
        yield ToggleOffsets()
        yield ToggleOpcodes()
        yield ShowASTOnly()
        yield ShowDisassemblyAndAST()
        yield ShowDisassemblyOnly()


### main.py ends here
