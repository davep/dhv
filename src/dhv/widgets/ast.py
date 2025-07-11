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
from textual import on
from textual.reactive import var
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

##############################################################################
# Local imports.
from ..messages import LocationChanged
from ..types import Location

##############################################################################
ASTNode = TreeNode[Any]
"""The type of a node in the widget."""


##############################################################################
class AbstractSyntaxTree(Tree[Any]):
    """Widget that displays Python code AST."""

    ICON_NODE = "…"
    ICON_NODE_EXPANDED = " "

    DEFAULT_CSS = """
    AbstractSyntaxTree.--error {
        color: $text-error;
        background: $error 25%;
    }
    """

    HELP = """
    ## Abstract Syntax Tree

    This panel is the abstract syntax tree of the Python source code.
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
        self.show_guides = False
        self.guide_depth = 1
        self._line_to_node_map: dict[int, ASTNode] = {}
        """A map to help translate a line number to a node in the tree."""

    def clear(self) -> Self:
        """Clear down the AST tree."""
        self._line_to_node_map = {}
        return super().clear()

    @classmethod
    def maybe_add(cls, value: Any) -> bool:
        """Does the value look like it should be added to the display?

        Args:
            value: The value to consider.

        Returns:
            `True` if the value should be added, `False` if not.
        """
        return bool(value) if isinstance(value, (list, tuple)) else True

    @classmethod
    def _location_of(cls, node: ASTNode) -> Location | None:
        """Get the location of a node in the AST.

        Args:
            node: The node in the tree to get the location of.

        Returns:
            The location, or `None` if nothing could be worked out.
        """
        if all(
            hasattr(node.data, location_property)
            for location_property in (
                "lineno",
                "col_offset",
                "end_lineno",
                "end_col_offset",
            )
        ):
            return Location(
                getattr(node.data, "lineno", None),
                getattr(node.data, "col_offset", None),
                getattr(node.data, "end_lineno", None),
                getattr(node.data, "end_col_offset", None),
            )
        elif node.parent is not None:
            return cls._location_of(node.parent)
        return None

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
            label = f"{label} [dim italic]{escape(item.name)}[/]"
        node = to_node.add(label, data=item)
        if (
            location := self._location_of(to_node)
        ) is not None and location.line_number not in self._line_to_node_map:
            self._line_to_node_map[location.line_number] = node
        return node

    @_base_node.register
    def _(self, item: str, to_node: ASTNode) -> ASTNode:
        """Attach a base node.

        Args:
            item: The item to associate with the node.
            to_node: The node to attach to.

        Returns:
            The new node.
        """
        return to_node.add(escape(item), data=item)

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
        self.move_cursor(self.root)

    @on(Tree.NodeHighlighted)
    def _ast_node_highlighted(self, message: Tree.NodeHighlighted[ASTNode]) -> None:
        """Handle a node being highlighted in the AST.

        Args:
            message: The message to handle.
        """
        if location := self._location_of(message.node):
            message.stop()
            self.post_message(LocationChanged(self, location))

    def goto_first_node_on_line(self, line: int) -> None:
        """Go to the first node that's related to the given line.

        Args:
            line: The line to find a node for.
        """
        if (node := self._line_to_node_map.get(line)) is not None:
            with self.prevent(Tree.NodeHighlighted):
                self.move_cursor(node)


### ast.py ends here
