"""Code navigation index for fast lookups and go-to-definition functionality.

This module provides a fast, memory-efficient index for code navigation,
supporting features like go-to-definition, find-references, and symbol search.
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from a1.core.event_bus import EventBus
from a1.core.events import SystemEvent

from .ast_parser import ModuleInfo
from .module_analyzer import ModuleAnalyzer
from .symbol_builder import SymbolBuilder
from .symbol_table import Symbol, SymbolLocation, SymbolTable, SymbolType


@dataclass
class NavigationResult:
    """Result of a navigation query."""

    symbol: Symbol
    location: SymbolLocation
    context: str  # Surrounding code snippet
    score: float  # Relevance score


class CodeNavigationIndex:
    """Fast index for code navigation operations."""

    def __init__(self, index_path: Path | None = None, event_bus: EventBus | None = None):
        """Initialize the navigation index.

        Args:
            index_path: Optional path to store the index database
            event_bus: Optional event bus for index events
        """
        self.event_bus = event_bus
        self.symbol_table = SymbolTable(event_bus)
        self.analyzer = ModuleAnalyzer(event_bus)
        self.builder = SymbolBuilder(self.symbol_table, event_bus)

        # In-memory caches for fast lookups
        self._definition_cache: dict[str, list[Symbol]] = {}
        self._reference_cache: dict[str, list[SymbolLocation]] = {}
        self._file_cache: dict[Path, str] = {}

        # SQLite for persistent storage if path provided
        self.index_path = index_path
        self.db_conn: sqlite3.Connection | None = None
        if index_path:
            self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the SQLite database for persistent storage."""
        if not self.index_path:
            return

        self.db_conn = sqlite3.connect(str(self.index_path))
        cursor = self.db_conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                qualified_name TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL,
                parent TEXT,
                docstring TEXT,
                signature TEXT,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbol_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line INTEGER NOT NULL,
                column INTEGER NOT NULL,
                FOREIGN KEY (symbol_name) REFERENCES symbols(qualified_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_module TEXT NOT NULL,
                target_module TEXT NOT NULL,
                imported_names TEXT,
                line INTEGER NOT NULL
            )
        """)

        # Create indexes for fast lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_references_symbol ON symbol_references(symbol_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_references_file ON symbol_references(file_path)")

        self.db_conn.commit()

    def index_directory(self, directory: Path, base_module: str = "") -> None:
        """Index all Python files in a directory.

        Args:
            directory: Root directory to index
            base_module: Base module name for the directory
        """
        start_time = None
        if self.event_bus:
            import time

            start_time = time.time()
            self.event_bus.emit(
                SystemEvent(type="indexing_started", data={"directory": str(directory), "base_module": base_module})
            )

        # Build symbol table
        self.builder.process_directory(directory, base_module)

        # Build caches
        self._build_caches()

        # Persist to database if available
        if self.db_conn:
            self._persist_to_database()

        if self.event_bus and start_time:
            elapsed = time.time() - start_time
            stats = self.symbol_table.get_statistics()
            self.event_bus.emit(
                SystemEvent(
                    type="indexing_completed",
                    data={"directory": str(directory), "elapsed_seconds": elapsed, "statistics": stats},
                )
            )

    def go_to_definition(self, name: str, context_file: Path, line: int) -> list[NavigationResult]:
        """Find the definition of a symbol.

        Args:
            name: Name to find definition for
            context_file: File where the name is used
            line: Line number where the name is used

        Returns:
            List of possible definitions, sorted by relevance
        """
        # Check cache first
        cache_key = f"{name}:{context_file}:{line}"
        if cache_key in self._definition_cache:
            symbols = self._definition_cache[cache_key]
        else:
            # Find possible definitions
            symbols = self.symbol_table.find_definitions(name, context_file)
            self._definition_cache[cache_key] = symbols

        # Convert to navigation results with context
        results = []
        for symbol in symbols:
            context = self._get_code_context(symbol.location)
            score = self._calculate_relevance_score(symbol, context_file, line)

            results.append(NavigationResult(symbol=symbol, location=symbol.location, context=context, score=score))

        # Sort by relevance score
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def find_references(self, qualified_name: str) -> list[NavigationResult]:
        """Find all references to a symbol.

        Args:
            qualified_name: The symbol's qualified name

        Returns:
            List of locations where the symbol is referenced
        """
        # Check cache
        if qualified_name in self._reference_cache:
            locations = self._reference_cache[qualified_name]
        else:
            locations = self.symbol_table.find_references(qualified_name)
            self._reference_cache[qualified_name] = locations

        # Convert to navigation results
        results = []
        symbol = self.symbol_table.get_symbol(qualified_name)

        for location in locations:
            context = self._get_code_context(location)
            results.append(NavigationResult(symbol=symbol, location=location, context=context, score=1.0))

        return results

    def search_symbols(self, query: str, symbol_type: SymbolType | None = None) -> list[Symbol]:
        """Search for symbols matching a query.

        Args:
            query: Search query (supports wildcards)
            symbol_type: Optional filter by symbol type

        Returns:
            List of matching symbols
        """
        results = []

        # Simple substring matching for now
        query_lower = query.lower()

        for _qualified_name, symbol in self.symbol_table._symbols.items():
            if symbol_type and symbol.symbol_type != symbol_type:
                continue

            if query_lower in symbol.name.lower():
                results.append(symbol)

        return results

    def get_file_symbols(self, file_path: Path) -> list[Symbol]:
        """Get all symbols defined in a file.

        Args:
            file_path: Path to the file

        Returns:
            List of symbols in the file
        """
        return self.symbol_table.get_symbols_in_file(file_path)

    def get_hover_info(self, qualified_name: str) -> dict[str, any]:
        """Get hover information for a symbol.

        Args:
            qualified_name: The symbol's qualified name

        Returns:
            Dictionary with hover information
        """
        symbol = self.symbol_table.get_symbol(qualified_name)
        if not symbol:
            return {}

        info = {
            "name": symbol.name,
            "type": symbol.symbol_type.value,
            "signature": symbol.signature,
            "docstring": symbol.docstring,
            "location": {"file": str(symbol.location.file_path), "line": symbol.location.line_start},
        }

        # Add type-specific information
        if symbol.symbol_type == SymbolType.CLASS:
            # Get inheritance info
            relations = self.symbol_table.get_relations(qualified_name, "inherits")
            if relations:
                info["inherits"] = [rel.target for rel in relations]

        elif symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD]:
            # Get complexity if available
            if "complexity" in symbol.metadata:
                info["complexity"] = symbol.metadata["complexity"]

        return info

    def get_call_hierarchy(self, qualified_name: str, direction: str = "outgoing") -> dict[str, list[str]]:
        """Get call hierarchy for a function/method.

        Args:
            qualified_name: The function's qualified name
            direction: "outgoing" for calls from, "incoming" for calls to

        Returns:
            Dictionary mapping functions to their calls
        """
        if direction == "outgoing":
            return self.symbol_table.get_call_graph(qualified_name)
        else:
            # Build reverse call graph
            reverse_graph = {}

            for caller_name, callees in self.symbol_table.get_call_graph("").items():
                for callee in callees:
                    if callee not in reverse_graph:
                        reverse_graph[callee] = []
                    reverse_graph[callee].append(caller_name)

            return {qualified_name: reverse_graph.get(qualified_name, [])}

    def _build_caches(self) -> None:
        """Build internal caches for fast lookups."""
        # Clear existing caches
        self._definition_cache.clear()
        self._reference_cache.clear()

        # Pre-populate some common lookups
        # This is where we could add more sophisticated caching strategies

    def _persist_to_database(self) -> None:
        """Persist the index to SQLite database."""
        if not self.db_conn:
            return

        cursor = self.db_conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM symbols")
        cursor.execute("DELETE FROM symbol_references")
        cursor.execute("DELETE FROM imports")

        # Insert symbols
        for qualified_name, symbol in self.symbol_table._symbols.items():
            cursor.execute(
                """
                INSERT INTO symbols (qualified_name, name, type, file_path,
                                   line_start, line_end, parent, docstring,
                                   signature, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    qualified_name,
                    symbol.name,
                    symbol.symbol_type.value,
                    str(symbol.location.file_path),
                    symbol.location.line_start,
                    symbol.location.line_end,
                    symbol.parent,
                    symbol.docstring,
                    symbol.signature,
                    json.dumps(symbol.metadata),
                ),
            )

        # Insert references
        for symbol_name, locations in self._reference_cache.items():
            for location in locations:
                cursor.execute(
                    """
                    INSERT INTO symbol_references (symbol_name, file_path, line, column)
                    VALUES (?, ?, ?, ?)
                """,
                    (symbol_name, str(location.file_path), location.line_start, location.column_start),
                )

        self.db_conn.commit()

    def _get_code_context(self, location: SymbolLocation, context_lines: int = 2) -> str:
        """Get code context around a location.

        Args:
            location: The location to get context for
            context_lines: Number of lines before/after to include

        Returns:
            Code snippet with context
        """
        # Check file cache
        if location.file_path not in self._file_cache:
            try:
                with open(location.file_path) as f:
                    self._file_cache[location.file_path] = f.read()
            except:
                return ""

        content = self._file_cache[location.file_path]
        lines = content.splitlines()

        start = max(0, location.line_start - context_lines - 1)
        end = min(len(lines), location.line_end + context_lines)

        return "\n".join(lines[start:end])

    def _calculate_relevance_score(self, symbol: Symbol, context_file: Path, line: int) -> float:
        """Calculate relevance score for a symbol definition.

        Args:
            symbol: The symbol definition
            context_file: File where the symbol is referenced
            line: Line number of reference

        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.5  # Base score

        # Same file bonus
        if symbol.location.file_path == context_file:
            score += 0.3

            # Close proximity bonus
            distance = abs(symbol.location.line_start - line)
            if distance < 50:
                score += 0.2 * (1 - distance / 50)

        # Check if imported in the file
        imports = self.analyzer._module_cache.get(context_file, ModuleInfo(context_file)).imports
        for import_info in imports:
            if symbol.qualified_name.startswith(import_info.module):
                score += 0.2
                break

        return min(score, 1.0)

    def close(self) -> None:
        """Close the index and clean up resources."""
        if self.db_conn:
            self.db_conn.close()

        self._definition_cache.clear()
        self._reference_cache.clear()
        self._file_cache.clear()
