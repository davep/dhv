"""Code theme commands for the command palette."""

##############################################################################
from textual.widgets import TextArea

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import CommandHit, CommandHits, CommandsProvider

##############################################################################
# Local imports.
from ..messages import SetCodeTheme


##############################################################################
class CodeThemeCommands(CommandsProvider):
    """A command provider for code themes."""

    def commands(self) -> CommandHits:
        """Provide code editor theme commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        for theme in sorted(TextArea().available_themes):
            yield CommandHit(
                theme,
                f"Change the theme of the code editor to {theme}",
                SetCodeTheme(theme),
            )


### code_themes.py ends here
