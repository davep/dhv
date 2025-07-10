"""Widget for showing the AST of some Python code."""

##############################################################################
# Python imports.
from ast import AST, AsyncFunctionDef, ClassDef, FunctionDef, parse
from functools import singledispatchmethod
from typing import Any, Self

##############################################################################
# Rich imports.
from rich.markup import escape

##############################################################################
# Textual imports.
from textual.reactive import var
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

##############################################################################
ASTNode = TreeNode[Any]
"""The type of a node in the widget."""


##############################################################################
class AbstractSyntaxTree(Tree[Any]):
    """Widget that displays Python code AST."""

    DEFAULT_CSS = """
    AbstractSyntaxTree.--error {
        color: $text-error;
        background: $error 25%;
    }
    """

    code: var[str | None] = var(None)
    """The code to show the AST of."""

    error: var[bool] = var(False)
    """Is there an error with the code we've been given?"""

    def __init__(
        self, id: str | None = None, classes: str | None = None, disabled: bool = False
    ) -> None:
        """Initialise the object.

        Args:
            id: The ID of the AST widget in the DOM.
            classes: The CSS classes of the AST widget.
            disabled: Whether the AST widget is disabled or not.
        """
        super().__init__("", id=id, classes=classes, disabled=disabled)
        self.show_root = False
        self.border_title = "AST"

    @classmethod
    def maybe_add(cls, value: Any) -> bool:
        """Does the value look like it should be added to the display?

        Args:
            value: The value to consider.

        Returns:
            `True` if the value should be added, `False` if not.
        """
        return bool(value) if isinstance(value, (list, tuple)) else True

    @singledispatchmethod
    def _base_node(self, item: Any, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        return to_node.add(escape(item.__class__.__name__), data=item)

    @_base_node.register
    def _(self, item: AST, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        label = f"{escape(item.__class__.__name__)}"
        if isinstance(item, (ClassDef, FunctionDef, AsyncFunctionDef)):
            label = f"{label} [dim italic]{item.name}[/]"
        return to_node.add(label, data=item)

    @_base_node.register
    def _(self, item: str, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        return to_node.add(item, data=item)

    @singledispatchmethod
    def _add(self, item: Any, to_node: ASTNode) -> Self:
        """Add an AST item to the tree.

        Args:
            item: The AST item to add.
            to_node: The node to add it to.
        """
        if isinstance(item, (list, tuple)):
            for child_item in item:
                self._add(child_item, to_node)
        else:
            to_node.add_leaf(escape(repr(item)), data=item)
        return self

    @_add.register
    def _(self, item: AST, to_node: ASTNode) -> Self:
        """Add an AST item to the tree.

        Args:
            item: The ast entry to add.
            to_node: The node to add to.
        """
        node = self._base_node(item, to_node)
        if item._fields:
            for field in item._fields:
                if self.maybe_add(value := getattr(item, field)):
                    self._add(value, self._base_node(field, node))
        else:
            node.allow_expand = False
        return self

    def _watch_error(self) -> None:
        """React to the error state being toggled."""
        self.set_class(self.error, "--error")

    def _watch_code(self) -> None:
        """React to the code being changed."""
        if not self.code:
            self.clear()
            return
        try:
            ast = parse(self.code)
        except SyntaxError:
            self.error = True
            return
        self.error = False
        self.clear()._add(ast, self.root).root.expand_all()
        self.select_node(self.root)


### ast.py ends here
