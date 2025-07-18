"""Tests for A1 event queue system."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from a1.core.events import ClaudeEvent
from a1.core.queue import EventQueue, IPCEventTransport


class TestEventQueue:
    """Test EventQueue class."""

    @pytest.mark.asyncio
    async def test_queue_creation(self):
        """Test creating an event queue."""
        queue = EventQueue(max_size=100)

        assert queue.max_size == 100
        assert queue.overflow_policy == "drop_oldest"
        metrics = queue.get_metrics()
        assert metrics["events_received"] == 0
        assert metrics["events_processed"] == 0

    @pytest.mark.asyncio
    async def test_queue_put_get(self):
        """Test putting and getting events."""
        queue = EventQueue()
        event = ClaudeEvent(type="test", data={"foo": "bar"})

        # Put event
        result = await queue.put(event)
        assert result is True

        # Get event
        retrieved = await queue.get(timeout=1.0)
        assert retrieved == event

        # Check metrics
        metrics = queue.get_metrics()
        assert metrics["events_received"] == 1
        assert metrics["events_processed"] == 1

    @pytest.mark.asyncio
    async def test_queue_priority(self):
        """Test event prioritization."""
        queue = EventQueue()

        # Add events with different priorities
        event1 = ClaudeEvent(type="test1")
        event2 = ClaudeEvent(type="test2")
        event3 = ClaudeEvent(type="test3")

        await queue.put(event1, priority=5)  # Normal
        await queue.put(event2, priority=1)  # High
        await queue.put(event3, priority=9)  # Low

        # Should get high priority first
        retrieved = await queue.get()
        assert retrieved == event2

    @pytest.mark.asyncio
    async def test_queue_overflow_drop_oldest(self):
        """Test drop_oldest overflow policy."""
        queue = EventQueue(max_size=2, overflow_policy="drop_oldest")

        event1 = ClaudeEvent(type="event1")
        event2 = ClaudeEvent(type="event2")
        event3 = ClaudeEvent(type="event3")

        await queue.put(event1)
        await queue.put(event2)
        await queue.put(event3)  # Should drop event1

        # Should get event2 first (oldest remaining)
        retrieved1 = await queue.get()
        retrieved2 = await queue.get()

        assert retrieved1 == event2
        assert retrieved2 == event3

        metrics = queue.get_metrics()
        assert metrics["queue_overflows"] == 1

    @pytest.mark.asyncio
    async def test_queue_overflow_drop_newest(self):
        """Test drop_newest overflow policy."""
        queue = EventQueue(max_size=2, overflow_policy="drop_newest")

        event1 = ClaudeEvent(type="event1")
        event2 = ClaudeEvent(type="event2")
        event3 = ClaudeEvent(type="event3")

        await queue.put(event1)
        await queue.put(event2)
        result = await queue.put(event3)  # Should be dropped

        assert result is False

        # Should only have first two events
        retrieved1 = await queue.get()
        retrieved2 = await queue.get()

        assert retrieved1 == event1
        assert retrieved2 == event2

        metrics = queue.get_metrics()
        assert metrics["events_dropped"] == 1

    @pytest.mark.asyncio
    async def test_queue_timeout(self):
        """Test queue get timeout."""
        queue = EventQueue()

        # Should timeout when empty
        result = await queue.get(timeout=0.1)
        assert result is None


class TestIPCEventTransport:
    """Test IPCEventTransport class."""

    @pytest.mark.asyncio
    async def test_ipc_creation(self):
        """Test creating IPC transport."""
        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "test.sock"
            transport = IPCEventTransport(socket_path)

            assert transport.socket_path == socket_path
            assert transport.server is None

    @pytest.mark.asyncio
    async def test_ipc_server_client(self):
        """Test IPC server and client communication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "test.sock"

            # Create server transport
            server_transport = IPCEventTransport(socket_path)
            received_events = []

            async def handler(event):
                received_events.append(event)

            # Start server
            await server_transport.start_server(handler)

            # Create client transport
            client_transport = IPCEventTransport(socket_path)

            # Send event
            test_event = ClaudeEvent(type="test_event", data={"message": "hello"})

            result = await client_transport.send_event(test_event)
            assert result is True

            # Give server time to process
            await asyncio.sleep(0.1)

            # Check received
            assert len(received_events) == 1
            received = received_events[0]
            assert isinstance(received, ClaudeEvent)
            assert received.type == "test_event"
            assert received.data["message"] == "hello"

            # Stop server
            await server_transport.stop_server()

    @pytest.mark.asyncio
    async def test_ipc_serialization(self):
        """Test event serialization/deserialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "test.sock"
            transport = IPCEventTransport(socket_path)

            # Test ClaudeEvent
            claude_event = ClaudeEvent(type="post_tool_use", data={"tool": "Read", "path": "/test.py"})

            serialized = transport._serialize_event(claude_event)
            assert serialized["__type__"] == "ClaudeEvent"
            assert serialized["type"] == "post_tool_use"
            assert serialized["data"]["tool"] == "Read"

            deserialized = transport._deserialize_event(serialized)
            assert isinstance(deserialized, ClaudeEvent)
            assert deserialized.type == claude_event.type
            assert deserialized.data == claude_event.data

    @pytest.mark.asyncio
    async def test_ipc_error_handling(self):
        """Test IPC error handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            socket_path = Path(tmpdir) / "nonexistent.sock"
            transport = IPCEventTransport(socket_path)

            # Should fail when server not running
            event = ClaudeEvent(type="test")
            result = await transport.send_event(event)
            assert result is False
