"""Function signature indexing and search.

This module provides fast lookup and matching of function signatures,
enabling features like finding compatible functions and overload resolution.
"""

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from a1.core.event_bus import EventBus

from ..events import SystemEvent
from .signature_extractor import FunctionSignature, ParameterInfo, SignatureExtractor


class SignatureIndex:
    """Index for fast function signature lookups."""

    def __init__(self, index_path: Path | None = None, event_bus: EventBus | None = None):
        """Initialize the signature index.

        Args:
            index_path: Path to SQLite index file (in-memory if None)
            event_bus: Optional event bus for index events
        """
        self.index_path = index_path
        self.event_bus = event_bus
        self.extractor = SignatureExtractor(event_bus)
        self.conn = self._initialize_database()

    def _initialize_database(self) -> sqlite3.Connection:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(str(self.index_path)) if self.index_path else sqlite3.connect(":memory:")

        cursor = conn.cursor()

        # Create signatures table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signatures (
                qualified_name TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                module TEXT NOT NULL,
                param_count INTEGER NOT NULL,
                param_names TEXT,
                param_types TEXT,
                return_type TEXT,
                is_async BOOLEAN DEFAULT 0,
                is_method BOOLEAN DEFAULT 0,
                decorators TEXT,
                normalized TEXT,
                signature_json TEXT NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create parameters table for detailed queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signature_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                name TEXT NOT NULL,
                type_annotation TEXT,
                has_default BOOLEAN DEFAULT 0,
                is_variadic BOOLEAN DEFAULT 0,
                is_keyword_variadic BOOLEAN DEFAULT 0,
                FOREIGN KEY (signature_id) REFERENCES signatures(qualified_name)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signatures_name ON signatures(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signatures_module ON signatures(module)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signatures_return ON signatures(return_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parameters_sig ON parameters(signature_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parameters_type ON parameters(type_annotation)")

        conn.commit()
        return conn

    def index_signature(self, signature: FunctionSignature) -> None:
        """Index a function signature.

        Args:
            signature: Function signature to index
        """
        cursor = self.conn.cursor()

        # Extract module from qualified name
        parts = signature.qualified_name.split("::")
        module = parts[0] if parts else ""

        # Prepare data
        param_names = [p.name for p in signature.parameters]
        param_types = [p.type_annotation or "Any" for p in signature.parameters]
        decorators = json.dumps(signature.decorators)
        normalized = self.extractor.normalize_signature(signature)
        signature_json = json.dumps(asdict(signature))

        # Insert signature
        cursor.execute(
            """
            INSERT OR REPLACE INTO signatures
            (qualified_name, name, module, param_count, param_names,
             param_types, return_type, is_async, is_method, decorators,
             normalized, signature_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                signature.qualified_name,
                signature.name,
                module,
                len(signature.parameters),
                json.dumps(param_names),
                json.dumps(param_types),
                signature.return_type,
                signature.is_async,
                signature.is_method,
                decorators,
                normalized,
                signature_json,
            ),
        )

        # Insert parameters
        cursor.execute("DELETE FROM parameters WHERE signature_id = ?", (signature.qualified_name,))

        for param in signature.parameters:
            cursor.execute(
                """
                INSERT INTO parameters
                (signature_id, position, name, type_annotation, has_default,
                 is_variadic, is_keyword_variadic)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    signature.qualified_name,
                    param.position,
                    param.name,
                    param.type_annotation,
                    param.default_value is not None,
                    param.is_variadic,
                    param.is_keyword_variadic,
                ),
            )

        self.conn.commit()

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="signature_indexed",
                    data={
                        "name": signature.qualified_name,
                        "params": len(signature.parameters),
                    },
                )
            )

    def find_by_name(self, name: str, limit: int = 10) -> list[FunctionSignature]:
        """Find signatures by function name.

        Args:
            name: Function name to search for
            limit: Maximum results to return

        Returns:
            List of matching signatures
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT signature_json
            FROM signatures
            WHERE name = ? OR name LIKE ?
            ORDER BY CASE WHEN name = ? THEN 0 ELSE 1 END
            LIMIT ?
        """,
            (name, f"%{name}%", name, limit),
        )

        results = []
        for (signature_json,) in cursor.fetchall():
            sig_dict = json.loads(signature_json)
            results.append(self._dict_to_signature(sig_dict))

        return results

    def find_by_parameters(
        self, param_types: list[str] | None = None, param_count: int | None = None, return_type: str | None = None
    ) -> list[FunctionSignature]:
        """Find signatures by parameter types and return type.

        Args:
            param_types: List of parameter types to match
            param_count: Number of parameters
            return_type: Return type to match

        Returns:
            List of matching signatures
        """
        cursor = self.conn.cursor()

        conditions = []
        params = []

        if param_count is not None:
            conditions.append("param_count = ?")
            params.append(param_count)

        if return_type:
            conditions.append("(return_type = ? OR return_type LIKE ?)")
            params.extend([return_type, f"%{return_type}%"])

        if param_types:
            # Match signatures that have these parameter types
            conditions.append("param_types LIKE ?")
            params.append(f"%{json.dumps(param_types)}%")

        query = "SELECT signature_json FROM signatures"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)

        results = []
        for (signature_json,) in cursor.fetchall():
            sig_dict = json.loads(signature_json)
            signature = self._dict_to_signature(sig_dict)

            # Additional filtering for param types if needed
            if param_types and not self._match_param_types(signature, param_types):
                continue

            results.append(signature)

        return results

    def find_compatible(
        self, target_signature: FunctionSignature, min_score: float = 0.7
    ) -> list[tuple[FunctionSignature, float]]:
        """Find signatures compatible with a target signature.

        Args:
            target_signature: Signature to match against
            min_score: Minimum compatibility score

        Returns:
            List of (signature, score) tuples sorted by score
        """
        cursor = self.conn.cursor()

        # Get all signatures from same module first, then others
        cursor.execute(
            """
            SELECT signature_json
            FROM signatures
            WHERE qualified_name != ?
            ORDER BY CASE WHEN module = ? THEN 0 ELSE 1 END
        """,
            (target_signature.qualified_name, target_signature.qualified_name.split("::")[0]),
        )

        compatible = []

        for (signature_json,) in cursor.fetchall():
            sig_dict = json.loads(signature_json)
            signature = self._dict_to_signature(sig_dict)

            score = self.extractor.signature_compatibility(target_signature, signature)

            if score >= min_score:
                compatible.append((signature, score))

        # Sort by score descending
        compatible.sort(key=lambda x: x[1], reverse=True)

        return compatible

    def find_overloads(self, function_name: str, module: str | None = None) -> list[FunctionSignature]:
        """Find all overloads of a function.

        Args:
            function_name: Name of the function
            module: Optional module to limit search

        Returns:
            List of function signatures that could be overloads
        """
        cursor = self.conn.cursor()

        if module:
            cursor.execute(
                """
                SELECT signature_json
                FROM signatures
                WHERE name = ? AND module = ?
            """,
                (function_name, module),
            )
        else:
            cursor.execute(
                """
                SELECT signature_json
                FROM signatures
                WHERE name = ?
            """,
                (function_name,),
            )

        overloads = []
        for (signature_json,) in cursor.fetchall():
            sig_dict = json.loads(signature_json)
            overloads.append(self._dict_to_signature(sig_dict))

        return overloads

    def search(self, query: str, limit: int = 20) -> list[FunctionSignature]:
        """Search signatures using natural language query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching signatures
        """
        # Simple keyword-based search
        keywords = query.lower().split()

        cursor = self.conn.cursor()

        # Build search conditions
        conditions = []
        params = []

        for keyword in keywords:
            conditions.append("""
                (LOWER(name) LIKE ? OR
                 LOWER(param_names) LIKE ? OR
                 LOWER(return_type) LIKE ? OR
                 LOWER(decorators) LIKE ?)
            """)
            pattern = f"%{keyword}%"
            params.extend([pattern] * 4)

        query_sql = f"""
            SELECT signature_json
            FROM signatures
            WHERE {" AND ".join(conditions)}
            LIMIT ?
        """
        params.append(limit)

        cursor.execute(query_sql, params)

        results = []
        for (signature_json,) in cursor.fetchall():
            sig_dict = json.loads(signature_json)
            results.append(self._dict_to_signature(sig_dict))

        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get index statistics.

        Returns:
            Dictionary of statistics
        """
        cursor = self.conn.cursor()

        stats = {}

        # Total signatures
        cursor.execute("SELECT COUNT(*) FROM signatures")
        stats["total_signatures"] = cursor.fetchone()[0]

        # Signatures by module
        cursor.execute("""
            SELECT module, COUNT(*)
            FROM signatures
            GROUP BY module
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        stats["top_modules"] = dict(cursor.fetchall())

        # Parameter statistics
        cursor.execute("SELECT AVG(param_count) FROM signatures")
        stats["avg_param_count"] = cursor.fetchone()[0] or 0

        # Async functions
        cursor.execute("SELECT COUNT(*) FROM signatures WHERE is_async = 1")
        stats["async_functions"] = cursor.fetchone()[0]

        # Methods vs functions
        cursor.execute("SELECT COUNT(*) FROM signatures WHERE is_method = 1")
        stats["methods"] = cursor.fetchone()[0]

        # Most common return types
        cursor.execute("""
            SELECT return_type, COUNT(*)
            FROM signatures
            WHERE return_type IS NOT NULL
            GROUP BY return_type
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        stats["common_return_types"] = dict(cursor.fetchall())

        return stats

    def _dict_to_signature(self, sig_dict: dict) -> FunctionSignature:
        """Convert dictionary to FunctionSignature object."""
        # Convert parameter dicts to ParameterInfo objects
        parameters = []
        for param_dict in sig_dict.get("parameters", []):
            parameters.append(ParameterInfo(**param_dict))

        sig_dict["parameters"] = parameters
        return FunctionSignature(**sig_dict)

    def _match_param_types(self, signature: FunctionSignature, param_types: list[str]) -> bool:
        """Check if signature matches parameter types."""
        sig_types = [p.type_annotation or "Any" for p in signature.parameters]

        if len(sig_types) != len(param_types):
            return False

        for sig_type, target_type in zip(sig_types, param_types, strict=False):
            if sig_type != target_type and sig_type != "Any" and target_type != "Any":
                # Could add more sophisticated type matching here
                return False

        return True

    def clear(self) -> None:
        """Clear all indexed signatures."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM signatures")
        cursor.execute("DELETE FROM parameters")
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
