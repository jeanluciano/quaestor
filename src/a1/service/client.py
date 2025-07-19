"""A1 Service Client - Communicates with running A1 service."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from a1.core.events import Event
from a1.core.queue import IPCEventTransport

logger = logging.getLogger(__name__)


class A1ServiceClient:
    """Client for communicating with A1 service."""

    def __init__(self, socket_path: Path | None = None):
        """Initialize client with optional socket path."""
        if socket_path is None:
            # Default socket location
            socket_path = Path.home() / ".quaestor" / "a1" / "service.sock"
        self.socket_path = socket_path
        self.transport = IPCEventTransport(socket_path)

    async def send_event(self, event: Event) -> bool:
        """Send event to A1 service.

        Args:
            event: Event to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Send event via IPC transport
            return await self.transport.send_event(event)

        except Exception as e:
            # Don't let communication failures break anything
            logger.debug(f"Failed to send event: {e}")
            return False

    async def is_service_running(self) -> bool:
        """Check if A1 service is running.

        Returns:
            True if service is accessible, False otherwise
        """
        try:
            # Check if socket file exists
            if not self.socket_path.exists():
                return False

            # Try to connect briefly
            # This is a simple check - could be enhanced
            return True

        except Exception:
            return False

    def close(self) -> None:
        """Close client connection."""
        # Cleanup if needed
        pass


class A1Client(A1ServiceClient):
    """Extended client for TUI dashboard with additional methods.

    This class extends the basic A1ServiceClient with methods needed
    by the TUI dashboard for fetching metrics, events, and status.
    """

    def __init__(self, socket_path: Path | None = None):
        """Initialize the extended client."""
        super().__init__(socket_path)
        self.connected = False
        self._mock_data = True  # Use mock data until full IPC implementation

    async def connect(self) -> bool:
        """Connect to the A1 service.

        Returns:
            True if connected successfully
        """
        try:
            self.connected = await self.is_service_running()
            return self.connected
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the A1 service."""
        self.connected = False
        self.close()

    async def get_recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent events from the A1 service.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        if self._mock_data or not self.connected:
            # Return mock events for testing
            return [
                {
                    "type": "tool_use",
                    "timestamp": datetime.now().isoformat(),
                    "source": "claude",
                    "data": {"tool": "Read", "parameters": {"file_path": "/src/example.py"}},
                },
                {
                    "type": "intent_change",
                    "timestamp": datetime.now().isoformat(),
                    "source": "a1",
                    "data": {"old_intent": "IDLE", "new_intent": "EXPLORING", "confidence": 0.85},
                },
            ]

        # TODO: Implement actual event fetching via IPC
        return []

    async def get_current_intent(self) -> dict[str, Any]:
        """Get the current detected intent from A1.

        Returns:
            Dictionary with intent information
        """
        if self._mock_data or not self.connected:
            # Return mock intent data
            return {
                "intent": "EXPLORING",
                "confidence": 0.75,
                "evidence": [
                    "Multiple file reads detected",
                    "Search pattern indicates exploration",
                    "No write operations",
                ],
            }

        # TODO: Implement actual intent fetching
        return {"intent": "IDLE", "confidence": 0.0, "evidence": []}

    async def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics.

        Returns:
            Dictionary of metric values
        """
        if self._mock_data or not self.connected:
            # Return mock metrics
            return {
                "cpu_usage": 12.5,
                "memory_usage": 45.8,
                "event_rate": 25.3,
                "avg_response_time": 15.2,
                "active_operations": 3,
                "errors": 0,
            }

        # TODO: Implement actual metrics fetching
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "event_rate": 0.0,
            "avg_response_time": 0.0,
            "active_operations": 0,
            "errors": 0,
        }
