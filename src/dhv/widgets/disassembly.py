"""Widget for showing the disassembly of some Python code."""

##############################################################################
# Python imports.
from dis import Bytecode

##############################################################################
# Python enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Textual imports.
from textual.reactive import var

##############################################################################
class Disassembly(EnhancedOptionList):
    """Widget that displays Python code disassembly."""

    code: var[str | None] = var(None)
    """The code to disassemble."""

    def _watch_code(self) -> None:
        """React to the code being changed."""
        self.clear_options()
        if self.code:
            for operation in Bytecode(self.code):
                self.add_option(str(operation)[:-1])

### disassembly.py ends here
