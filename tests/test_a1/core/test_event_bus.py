"""Tests for simplified event bus system."""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio

from a1.core import EventBus, EventStore, SystemEvent, ToolUseEvent


class TestEventBus:
    """Test cases for the simplified event bus."""

    @pytest_asyncio.fixture
    async def event_bus(self):
        """Create an event bus for testing."""
        bus = EventBus()
        await bus.start()
        yield bus
        await bus.stop()

    @pytest_asyncio.fixture
    async def event_bus_with_store(self):
        """Create an event bus with storage for testing."""
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            store = EventStore(db_path)
            bus = EventBus(store)
            await bus.start()
            yield bus
            await bus.stop()

    @pytest.mark.asyncio
    async def test_basic_event_publishing(self, event_bus):
        """Test basic event publishing and handling."""
        events_received = []

        def handler(event):
            events_received.append(event)

        event_bus.subscribe(handler)

        # Publish an event
        test_event = SystemEvent(event_name="test", component="test")
        await event_bus.publish(test_event)

        # Give time for processing
        await asyncio.sleep(0.1)

        assert len(events_received) == 1
        assert events_received[0].event_name == "test"

    @pytest.mark.asyncio
    async def test_event_type_filtering(self, event_bus):
        """Test event type filtering."""
        system_events = []
        tool_events = []

        def system_handler(event):
            system_events.append(event)

        def tool_handler(event):
            tool_events.append(event)

        event_bus.subscribe(system_handler, "system")
        event_bus.subscribe(tool_handler, "tool_use")

        # Publish different event types
        await event_bus.publish(SystemEvent(event_name="system_test"))
        await event_bus.publish(ToolUseEvent(tool_name="test_tool"))

        # Give time for processing
        await asyncio.sleep(0.1)

        assert len(system_events) == 1
        assert len(tool_events) == 1
        assert system_events[0].event_name == "system_test"
        assert tool_events[0].tool_name == "test_tool"

    @pytest.mark.asyncio
    async def test_async_handler(self, event_bus):
        """Test async event handlers."""
        events_received = []

        async def async_handler(event):
            await asyncio.sleep(0.01)  # Simulate async work
            events_received.append(event)

        event_bus.subscribe(async_handler)

        await event_bus.publish(SystemEvent(event_name="async_test"))

        # Give time for processing
        await asyncio.sleep(0.1)

        assert len(events_received) == 1
        assert events_received[0].event_name == "async_test"

    @pytest.mark.asyncio
    async def test_unsubscribe(self, event_bus):
        """Test event handler unsubscription."""
        events_received = []

        def handler(event):
            events_received.append(event)

        event_bus.subscribe(handler)
        await event_bus.publish(SystemEvent(event_name="before_unsubscribe"))

        # Give time for processing
        await asyncio.sleep(0.1)

        event_bus.unsubscribe(handler)
        await event_bus.publish(SystemEvent(event_name="after_unsubscribe"))

        # Give time for processing
        await asyncio.sleep(0.1)

        assert len(events_received) == 1
        assert events_received[0].event_name == "before_unsubscribe"

    @pytest.mark.asyncio
    async def test_event_persistence(self, event_bus_with_store):
        """Test event persistence to storage."""
        test_event = SystemEvent(event_name="persistent_test", component="test")
        await event_bus_with_store.publish(test_event)

        # Give time for processing
        await asyncio.sleep(0.1)

        # Check that event was stored
        stored_events = await event_bus_with_store.event_store.get_events()
        assert len(stored_events) == 1
        assert stored_events[0]["type"] == "system"
        assert stored_events[0]["data"]["event_name"] == "persistent_test"

    @pytest.mark.asyncio
    async def test_stats(self, event_bus):
        """Test event bus statistics."""

        def handler(event):
            pass

        event_bus.subscribe(handler)
        stats = event_bus.get_stats()

        assert "queue_size" in stats
        assert "handler_count" in stats
        assert stats["handler_count"] >= 1

    @pytest.mark.asyncio
    async def test_error_handling(self, event_bus):
        """Test error handling in event handlers."""
        events_received = []

        def good_handler(event):
            events_received.append(event)

        def bad_handler(event):
            raise ValueError("Test error")

        event_bus.subscribe(good_handler)
        event_bus.subscribe(bad_handler)

        await event_bus.publish(SystemEvent(event_name="error_test"))

        # Give time for processing
        await asyncio.sleep(0.1)

        # Good handler should still receive the event
        assert len(events_received) == 1
        assert events_received[0].event_name == "error_test"
