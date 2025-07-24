"""Simple event wrapper for deep context module."""

from typing import Any


class SystemEvent:
    """Simple event wrapper that works with mock event bus."""

    def __init__(self, type: str, data: dict[str, Any]):
        """Initialize event with type and data."""
        self.type = type
        self.data = data
        self.event_type = type
