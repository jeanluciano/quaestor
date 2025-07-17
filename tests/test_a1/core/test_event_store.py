"""Tests for simplified event store."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio

from a1.core import EventStore, SystemEvent, ToolUseEvent


class TestEventStore:
    """Test cases for the simplified event store."""

    @pytest_asyncio.fixture
    async def memory_store(self):
        """Create an in-memory event store for testing."""
        store = EventStore()
        await store.initialize()
        return store

    @pytest_asyncio.fixture
    async def file_store(self):
        """Create a file-based event store for testing."""
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            store = EventStore(db_path)
            await store.initialize()
            yield store

    @pytest.mark.asyncio
    async def test_store_and_retrieve_events(self, memory_store):
        """Test storing and retrieving events."""
        # Store some events
        event1 = SystemEvent(event_name="test1", component="core")
        event2 = ToolUseEvent(tool_name="test_tool", success=True)

        await memory_store.store_event(event1)
        await memory_store.store_event(event2)

        # Retrieve all events
        events = await memory_store.get_events()
        assert len(events) == 2

        # Events should be returned in reverse chronological order
        assert events[0]["type"] == "tool_use"
        assert events[1]["type"] == "system"

    @pytest.mark.asyncio
    async def test_event_type_filtering(self, memory_store):
        """Test filtering events by type."""
        # Store different event types
        await memory_store.store_event(SystemEvent(event_name="system1"))
        await memory_store.store_event(ToolUseEvent(tool_name="tool1"))
        await memory_store.store_event(SystemEvent(event_name="system2"))

        # Get only system events
        system_events = await memory_store.get_events(event_type="system")
        assert len(system_events) == 2
        assert all(event["type"] == "system" for event in system_events)

        # Get only tool events
        tool_events = await memory_store.get_events(event_type="tool_use")
        assert len(tool_events) == 1
        assert tool_events[0]["type"] == "tool_use"

    @pytest.mark.asyncio
    async def test_event_limit(self, memory_store):
        """Test limiting number of returned events."""
        # Store multiple events
        for i in range(10):
            await memory_store.store_event(SystemEvent(event_name=f"test{i}"))

        # Get limited number of events
        events = await memory_store.get_events(limit=5)
        assert len(events) == 5

        # Should get most recent events first
        event_names = [event["data"]["event_name"] for event in events]
        assert event_names == ["test9", "test8", "test7", "test6", "test5"]

    @pytest.mark.asyncio
    async def test_file_persistence(self, file_store):
        """Test persistence to file."""
        # Store an event
        event = SystemEvent(event_name="persistent", component="test")
        await file_store.store_event(event)

        # Create a new store instance with the same file
        new_store = EventStore(file_store.db_path)
        events = await new_store.get_events()

        assert len(events) == 1
        assert events[0]["data"]["event_name"] == "persistent"

    @pytest.mark.asyncio
    async def test_event_serialization(self, memory_store):
        """Test event data serialization."""
        # Store a complex event
        event = ToolUseEvent(tool_name="complex_tool", success=False, duration_ms=123.45)
        await memory_store.store_event(event)

        # Retrieve and verify
        events = await memory_store.get_events()
        assert len(events) == 1

        stored_event = events[0]
        assert stored_event["type"] == "tool_use"
        assert stored_event["data"]["tool_name"] == "complex_tool"
        assert stored_event["data"]["success"] is False
        assert stored_event["data"]["duration_ms"] == 123.45

    @pytest.mark.asyncio
    async def test_empty_store(self, memory_store):
        """Test querying empty store."""
        events = await memory_store.get_events()
        assert len(events) == 0

        # Test with filtering
        system_events = await memory_store.get_events(event_type="system")
        assert len(system_events) == 0

    @pytest.mark.asyncio
    async def test_store_close(self, memory_store):
        """Test store closing."""
        # Should not raise any errors
        await memory_store.close()

    @pytest.mark.asyncio
    async def test_database_schema(self, file_store):
        """Test that database schema is created correctly."""
        # Initialize the store
        await file_store.initialize()

        # Store an event to test schema
        event = SystemEvent(event_name="schema_test")
        await file_store.store_event(event)

        # Verify we can retrieve it
        events = await file_store.get_events()
        assert len(events) == 1
        assert events[0]["data"]["event_name"] == "schema_test"
