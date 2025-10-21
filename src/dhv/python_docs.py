"""Tools for visiting locations within the Python documentation."""

##############################################################################
# Python imports
from ast import AST
from dis import Instruction
from typing import Final
from webbrowser import open_new

##############################################################################
DOCS: Final[str] = "https://docs.python.org/3/library/"
"""Root for the Python docs."""


##############################################################################
def visit_operation(operation: str | Instruction) -> None:
    """Visit the documentation for the given operation.

    Args:
        operation: An opname or an [`Instruction`][dis.Instruction].
    """
    if isinstance(operation, Instruction):
        operation = operation.opname
    open_new(f"{DOCS}dis.html#opcode-{operation}")


##############################################################################
def visit_ast(ast: AST) -> None:
    """Visit the documentation for the given AST entry.

    Args:
        operation: An [`AST`][ast.AST] entry.
    """
    open_new(f"{DOCS}ast.html#ast.{ast.__class__.__name__}")


### python_docs.py ends here
