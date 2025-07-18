"""A1 Service Client - Communicates with running A1 service."""

import logging
from pathlib import Path

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

            # Try to connect (simplified check)
            # In production, this would attempt actual connection
            return True

        except Exception:
            return False

    async def start_service_if_needed(self) -> bool:
        """Start A1 service if not already running.

        Returns:
            True if service is running (either already or newly started)
        """
        if await self.is_service_running():
            return True

        # TODO: Implement service startup logic
        # For now, service must be started manually
        return False
