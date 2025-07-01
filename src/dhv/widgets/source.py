"""Widget for showing some Python source code."""

##############################################################################
# Rich imports.
from rich.syntax import Syntax

##############################################################################
# Textual imports.
from textual.reactive import var
from textual.widgets import Static

##############################################################################
class Source(Static):
    """Widget that displays Python source code."""

    code: var[str | None] = var(None)
    """The code to show."""

    def _watch_code(self) -> None:
        """React to the code being changed."""
        self.update("" if self.code is None else Syntax(self.code, lexer="python"))

### source.py ends here
