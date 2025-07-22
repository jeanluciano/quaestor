"""Symbol table for tracking code symbols and their relationships.

This module provides a comprehensive symbol table that tracks all symbols
(functions, classes, variables) in a codebase and their relationships.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from a1.core.event_bus import EventBus
from a1.core.events import SystemEvent


class SymbolType(Enum):
    """Types of symbols we track."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    PARAMETER = "parameter"
    IMPORT = "import"


@dataclass
class SymbolLocation:
    """Location of a symbol in the codebase."""

    file_path: Path
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0


@dataclass
class Symbol:
    """A code symbol with its metadata."""

    name: str
    qualified_name: str  # Full dotted path
    symbol_type: SymbolType
    location: SymbolLocation
    parent: str | None = None  # Qualified name of parent symbol
    children: list[str] = field(default_factory=list)  # Child symbol names
    references: list[SymbolLocation] = field(default_factory=list)
    docstring: str | None = None
    signature: str | None = None  # For functions/methods
    value: str | None = None  # For constants/variables
    metadata: dict[str, any] = field(default_factory=dict)


@dataclass
class SymbolRelation:
    """Relationship between two symbols."""

    source: str  # Qualified name
    target: str  # Qualified name
    relation_type: str  # 'calls', 'inherits', 'imports', 'uses', etc.
    location: SymbolLocation  # Where the relation occurs


class SymbolTable:
    """Global symbol table for a codebase."""

    def __init__(self, event_bus: EventBus | None = None):
        """Initialize the symbol table.

        Args:
            event_bus: Optional event bus for symbol events
        """
        self.event_bus = event_bus
        self._symbols: dict[str, Symbol] = {}  # qualified_name -> Symbol
        self._relations: list[SymbolRelation] = []
        self._file_symbols: dict[Path, set[str]] = {}  # file -> symbol names
        self._name_index: dict[str, set[str]] = {}  # simple name -> qualified names

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the table.

        Args:
            symbol: The symbol to add
        """
        self._symbols[symbol.qualified_name] = symbol

        # Update file index
        file_path = symbol.location.file_path
        if file_path not in self._file_symbols:
            self._file_symbols[file_path] = set()
        self._file_symbols[file_path].add(symbol.qualified_name)

        # Update name index
        simple_name = symbol.name.split(".")[-1]
        if simple_name not in self._name_index:
            self._name_index[simple_name] = set()
        self._name_index[simple_name].add(symbol.qualified_name)

        # Update parent's children if applicable
        if symbol.parent and symbol.parent in self._symbols:
            parent = self._symbols[symbol.parent]
            if symbol.qualified_name not in parent.children:
                parent.children.append(symbol.qualified_name)

        # Emit event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="symbol_added",
                    data={
                        "name": symbol.qualified_name,
                        "type": symbol.symbol_type.value,
                        "file": str(symbol.location.file_path),
                    },
                )
            )

    def add_relation(self, relation: SymbolRelation) -> None:
        """Add a relationship between symbols.

        Args:
            relation: The relationship to add
        """
        self._relations.append(relation)

        # Emit event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="relation_added",
                    data={"source": relation.source, "target": relation.target, "type": relation.relation_type},
                )
            )

    def get_symbol(self, qualified_name: str) -> Symbol | None:
        """Get a symbol by its qualified name.

        Args:
            qualified_name: The full dotted path to the symbol

        Returns:
            The symbol if found, None otherwise
        """
        return self._symbols.get(qualified_name)

    def find_symbols_by_name(self, name: str) -> list[Symbol]:
        """Find all symbols with a given simple name.

        Args:
            name: The simple (unqualified) name

        Returns:
            List of matching symbols
        """
        qualified_names = self._name_index.get(name, set())
        return [self._symbols[qn] for qn in qualified_names if qn in self._symbols]

    def get_symbols_in_file(self, file_path: Path) -> list[Symbol]:
        """Get all symbols defined in a file.

        Args:
            file_path: Path to the file

        Returns:
            List of symbols in the file
        """
        symbol_names = self._file_symbols.get(file_path, set())
        return [self._symbols[name] for name in symbol_names if name in self._symbols]

    def get_children(self, qualified_name: str) -> list[Symbol]:
        """Get all child symbols of a parent.

        Args:
            qualified_name: The parent's qualified name

        Returns:
            List of child symbols
        """
        parent = self.get_symbol(qualified_name)
        if not parent:
            return []

        return [self._symbols[child_name] for child_name in parent.children if child_name in self._symbols]

    def get_relations(self, symbol_name: str, relation_type: str | None = None) -> list[SymbolRelation]:
        """Get all relations involving a symbol.

        Args:
            symbol_name: The symbol's qualified name
            relation_type: Optional filter by relation type

        Returns:
            List of relations
        """
        relations = []

        for relation in self._relations:
            if relation.source == symbol_name or relation.target == symbol_name:
                if relation_type is None or relation.relation_type == relation_type:
                    relations.append(relation)

        return relations

    def find_references(self, qualified_name: str) -> list[SymbolLocation]:
        """Find all references to a symbol.

        Args:
            qualified_name: The symbol's qualified name

        Returns:
            List of locations where the symbol is referenced
        """
        symbol = self.get_symbol(qualified_name)
        if not symbol:
            return []

        # Get direct references
        references = list(symbol.references)

        # Add relation-based references
        for relation in self._relations:
            if relation.target == qualified_name:
                references.append(relation.location)

        return references

    def find_definitions(self, name: str, context_file: Path | None = None) -> list[Symbol]:
        """Find possible definitions of a name, considering context.

        Args:
            name: The name to find definitions for
            context_file: Optional file to prioritize local definitions

        Returns:
            List of possible symbol definitions, sorted by relevance
        """
        candidates = self.find_symbols_by_name(name)

        if not context_file:
            return candidates

        # Sort by relevance - same file first, then by distance
        def relevance_score(symbol: Symbol) -> tuple[int, int]:
            if symbol.location.file_path == context_file:
                return (0, 0)  # Same file, highest priority
            else:
                # Could implement more sophisticated scoring based on imports
                return (1, 0)

        return sorted(candidates, key=relevance_score)

    def get_call_graph(self, root_symbol: str, max_depth: int = 5) -> dict[str, set[str]]:
        """Build a call graph starting from a symbol.

        Args:
            root_symbol: Starting symbol's qualified name
            max_depth: Maximum depth to traverse

        Returns:
            Dictionary mapping symbols to their callees
        """
        call_graph = {}
        visited = set()

        def _traverse(symbol_name: str, depth: int) -> None:
            if depth > max_depth or symbol_name in visited:
                return

            visited.add(symbol_name)
            callees = set()

            for relation in self._relations:
                if relation.source == symbol_name and relation.relation_type == "calls":
                    callees.add(relation.target)

            call_graph[symbol_name] = callees

            for callee in callees:
                _traverse(callee, depth + 1)

        _traverse(root_symbol, 0)
        return call_graph

    def get_inheritance_tree(self, class_name: str) -> dict[str, list[str]]:
        """Build an inheritance tree for a class.

        Args:
            class_name: The class's qualified name

        Returns:
            Dictionary mapping classes to their direct subclasses
        """
        tree = {}

        # Find all inheritance relations
        for relation in self._relations:
            if relation.relation_type == "inherits":
                parent = relation.target
                child = relation.source

                if parent not in tree:
                    tree[parent] = []
                tree[parent].append(child)

        return tree

    def export_to_dict(self) -> dict[str, any]:
        """Export the symbol table to a dictionary.

        Returns:
            Dictionary representation of the symbol table
        """
        return {
            "symbols": {
                name: {
                    "name": sym.name,
                    "type": sym.symbol_type.value,
                    "location": {
                        "file": str(sym.location.file_path),
                        "line_start": sym.location.line_start,
                        "line_end": sym.location.line_end,
                    },
                    "parent": sym.parent,
                    "children": sym.children,
                    "docstring": sym.docstring,
                    "signature": sym.signature,
                }
                for name, sym in self._symbols.items()
            },
            "relations": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "type": rel.relation_type,
                    "location": {"file": str(rel.location.file_path), "line": rel.location.line_start},
                }
                for rel in self._relations
            ],
        }

    def clear(self) -> None:
        """Clear all symbols and relations."""
        self._symbols.clear()
        self._relations.clear()
        self._file_symbols.clear()
        self._name_index.clear()

    def get_statistics(self) -> dict[str, int]:
        """Get statistics about the symbol table.

        Returns:
            Dictionary of statistics
        """
        type_counts = {}
        for symbol in self._symbols.values():
            symbol_type = symbol.symbol_type.value
            type_counts[symbol_type] = type_counts.get(symbol_type, 0) + 1

        return {
            "total_symbols": len(self._symbols),
            "total_relations": len(self._relations),
            "total_files": len(self._file_symbols),
            **type_counts,
        }
