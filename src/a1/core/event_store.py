"""Simple event storage for Quaestor A1 event system."""

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from .events import Event


class EventStore:
    """Simple persistent storage for events."""

    def __init__(self, db_path: Path | None = None):
        """Initialize event store.

        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        self.db_path = str(db_path) if db_path else ":memory:"
        self._lock = asyncio.Lock()
        self._initialized = False
        self._is_memory_db = db_path is None
        self._shared_conn = None  # For in-memory databases

    async def initialize(self) -> None:
        """Initialize the database schema."""
        async with self._lock:
            if self._initialized:
                return

            await asyncio.get_event_loop().run_in_executor(None, self._init_db)
            self._initialized = True

    def _init_db(self) -> None:
        """Initialize database schema."""
        if self._is_memory_db and self._shared_conn is None:
            # For in-memory databases, keep a shared connection
            self._shared_conn = sqlite3.connect(self.db_path)
            conn = self._shared_conn
        else:
            conn = sqlite3.connect(self.db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")

        conn.commit()

        # Only close if not using shared connection
        if not self._is_memory_db:
            conn.close()

    async def store_event(self, event: Event) -> None:
        """Store an event in the database."""
        await self.initialize()

        event_dict = event.to_dict()

        async with self._lock:
            await asyncio.get_event_loop().run_in_executor(None, self._store_event_sync, event_dict)

    def _store_event_sync(self, event_dict: dict[str, Any]) -> None:
        """Store event synchronously."""
        conn = self._shared_conn if self._is_memory_db and self._shared_conn else sqlite3.connect(self.db_path)

        try:
            conn.execute(
                """
                INSERT INTO events (id, event_type, timestamp, source, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_dict["id"],
                    event_dict["type"],
                    event_dict["timestamp"],
                    event_dict["source"],
                    json.dumps(event_dict["data"]),
                    time.time(),
                ),
            )
            conn.commit()
        finally:
            # Only close if not using shared connection
            if not self._is_memory_db:
                conn.close()

    async def get_events(self, event_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get events from the database.

        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        await self.initialize()

        async with self._lock:
            return await asyncio.get_event_loop().run_in_executor(None, self._get_events_sync, event_type, limit)

    def _get_events_sync(self, event_type: str | None, limit: int) -> list[dict[str, Any]]:
        """Get events synchronously."""
        conn = self._shared_conn if self._is_memory_db and self._shared_conn else sqlite3.connect(self.db_path)

        try:
            if event_type:
                cursor = conn.execute(
                    """
                    SELECT id, event_type, timestamp, source, data, created_at
                    FROM events
                    WHERE event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (event_type, limit),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT id, event_type, timestamp, source, data, created_at
                    FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,),
                )

            events = []
            for row in cursor:
                events.append(
                    {
                        "id": row[0],
                        "type": row[1],
                        "timestamp": row[2],
                        "source": row[3],
                        "data": json.loads(row[4]),
                        "created_at": row[5],
                    }
                )

            return events
        finally:
            # Only close if not using shared connection
            if not self._is_memory_db:
                conn.close()

    async def close(self) -> None:
        """Close the event store."""
        async with self._lock:
            if self._shared_conn:
                await asyncio.get_event_loop().run_in_executor(None, self._close_shared_conn)

    def _close_shared_conn(self) -> None:
        """Close shared connection synchronously."""
        if self._shared_conn:
            self._shared_conn.close()
            self._shared_conn = None
