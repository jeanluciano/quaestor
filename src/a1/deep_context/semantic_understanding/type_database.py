"""Type database for storing and querying inferred type information.

This module provides persistent storage for type information using SQLite,
enabling fast lookups and cross-module type resolution.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

from a1.core.event_bus import EventBus

from ..events import SystemEvent
from .type_inference import TypeInfo


class TypeDatabase:
    """Database for storing and querying type information."""

    def __init__(self, db_path: Path | None = None, event_bus: EventBus | None = None):
        """Initialize the type database.

        Args:
            db_path: Path to SQLite database file (in-memory if None)
            event_bus: Optional event bus for database events
        """
        self.db_path = db_path
        self.event_bus = event_bus
        self.conn = self._initialize_database()

    def _initialize_database(self) -> sqlite3.Connection:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(str(self.db_path)) if self.db_path else sqlite3.connect(":memory:")

        cursor = conn.cursor()

        # Create types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS types (
                symbol_id TEXT PRIMARY KEY,
                module TEXT NOT NULL,
                symbol_name TEXT NOT NULL,
                type_name TEXT NOT NULL,
                type_module TEXT,
                is_generic BOOLEAN DEFAULT 0,
                type_params TEXT,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT 'inference',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create type relationships table (for inheritance, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS type_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                target_type TEXT NOT NULL,
                relation TEXT NOT NULL,
                FOREIGN KEY (source_type) REFERENCES types(symbol_id),
                FOREIGN KEY (target_type) REFERENCES types(symbol_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_types_module ON types(module)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_types_name ON types(symbol_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_types_type ON types(type_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relations_source ON type_relations(source_type)")

        conn.commit()
        return conn

    def store_type(self, symbol_id: str, module: str, symbol_name: str, type_info: TypeInfo) -> None:
        """Store type information for a symbol.

        Args:
            symbol_id: Unique identifier for the symbol
            module: Module containing the symbol
            symbol_name: Name of the symbol
            type_info: Type information to store
        """
        cursor = self.conn.cursor()

        type_params_json = json.dumps(type_info.type_params) if type_info.type_params else None

        cursor.execute(
            """
            INSERT OR REPLACE INTO types
            (symbol_id, module, symbol_name, type_name, type_module,
             is_generic, type_params, confidence, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                symbol_id,
                module,
                symbol_name,
                type_info.type_name,
                type_info.module,
                type_info.is_generic,
                type_params_json,
                type_info.confidence,
                type_info.source,
            ),
        )

        self.conn.commit()

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="type_stored",
                    data={"symbol_id": symbol_id, "type": type_info.type_name, "confidence": type_info.confidence},
                )
            )

    def get_type(self, symbol_id: str) -> TypeInfo | None:
        """Get type information for a symbol.

        Args:
            symbol_id: Symbol identifier

        Returns:
            Type information or None if not found
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT type_name, type_module, is_generic, type_params,
                   confidence, source
            FROM types
            WHERE symbol_id = ?
        """,
            (symbol_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        type_name, type_module, is_generic, type_params_json, confidence, source = row

        type_params = json.loads(type_params_json) if type_params_json else []

        return TypeInfo(
            type_name=type_name,
            module=type_module,
            is_generic=bool(is_generic),
            type_params=type_params,
            confidence=confidence,
            source=source,
        )

    def find_symbols_by_type(self, type_name: str, module: str | None = None) -> list[tuple[str, str, str]]:
        """Find all symbols with a given type.

        Args:
            type_name: Type to search for
            module: Optional module to limit search to

        Returns:
            List of (symbol_id, module, symbol_name) tuples
        """
        cursor = self.conn.cursor()

        if module:
            cursor.execute(
                """
                SELECT symbol_id, module, symbol_name
                FROM types
                WHERE type_name = ? AND module = ?
            """,
                (type_name, module),
            )
        else:
            cursor.execute(
                """
                SELECT symbol_id, module, symbol_name
                FROM types
                WHERE type_name = ?
            """,
                (type_name,),
            )

        return cursor.fetchall()

    def get_module_types(self, module: str) -> dict[str, TypeInfo]:
        """Get all type information for a module.

        Args:
            module: Module name

        Returns:
            Dictionary mapping symbol names to type information
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT symbol_name, type_name, type_module, is_generic,
                   type_params, confidence, source
            FROM types
            WHERE module = ?
        """,
            (module,),
        )

        types = {}
        for row in cursor.fetchall():
            symbol_name, type_name, type_module, is_generic, type_params_json, confidence, source = row

            type_params = json.loads(type_params_json) if type_params_json else []

            types[symbol_name] = TypeInfo(
                type_name=type_name,
                module=type_module,
                is_generic=bool(is_generic),
                type_params=type_params,
                confidence=confidence,
                source=source,
            )

        return types

    def add_type_relation(self, source_type: str, target_type: str, relation: str) -> None:
        """Add a relationship between types.

        Args:
            source_type: Source type symbol ID
            target_type: Target type symbol ID
            relation: Relationship type (e.g., "inherits", "implements")
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO type_relations (source_type, target_type, relation)
            VALUES (?, ?, ?)
        """,
            (source_type, target_type, relation),
        )

        self.conn.commit()

    def get_type_hierarchy(self, type_name: str) -> dict[str, list[str]]:
        """Get the inheritance hierarchy for a type.

        Args:
            type_name: Type to get hierarchy for

        Returns:
            Dictionary mapping types to their subtypes
        """
        cursor = self.conn.cursor()

        # Find all symbols with this type
        cursor.execute(
            """
            SELECT symbol_id FROM types WHERE type_name = ?
        """,
            (type_name,),
        )

        type_ids = [row[0] for row in cursor.fetchall()]

        hierarchy = {}

        for type_id in type_ids:
            # Find all types that inherit from this one
            cursor.execute(
                """
                SELECT t.type_name
                FROM type_relations r
                JOIN types t ON r.source_type = t.symbol_id
                WHERE r.target_type = ? AND r.relation = 'inherits'
            """,
                (type_id,),
            )

            subtypes = [row[0] for row in cursor.fetchall()]
            if subtypes:
                hierarchy[type_id] = subtypes

        return hierarchy

    def update_confidence(self, symbol_id: str, new_confidence: float) -> None:
        """Update the confidence score for a type inference.

        Args:
            symbol_id: Symbol identifier
            new_confidence: New confidence score (0.0 to 1.0)
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE types
            SET confidence = ?, updated_at = CURRENT_TIMESTAMP
            WHERE symbol_id = ?
        """,
            (new_confidence, symbol_id),
        )

        self.conn.commit()

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the type database.

        Returns:
            Dictionary of statistics
        """
        cursor = self.conn.cursor()

        stats = {}

        # Total types
        cursor.execute("SELECT COUNT(*) FROM types")
        stats["total_types"] = cursor.fetchone()[0]

        # Types by source
        cursor.execute("""
            SELECT source, COUNT(*)
            FROM types
            GROUP BY source
        """)
        stats["by_source"] = dict(cursor.fetchall())

        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM types")
        stats["avg_confidence"] = cursor.fetchone()[0] or 0.0

        # Generic types
        cursor.execute("SELECT COUNT(*) FROM types WHERE is_generic = 1")
        stats["generic_types"] = cursor.fetchone()[0]

        # Type relations
        cursor.execute("SELECT COUNT(*) FROM type_relations")
        stats["total_relations"] = cursor.fetchone()[0]

        return stats

    def clear(self) -> None:
        """Clear all type information from the database."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM types")
        cursor.execute("DELETE FROM type_relations")
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
