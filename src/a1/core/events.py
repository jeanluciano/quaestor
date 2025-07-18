"""Simplified event types for Quaestor A1 event system."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Event(ABC):
    """Base event class for all Quaestor A1 events."""

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = "quaestor.a1"

    @abstractmethod
    def get_event_type(self) -> str:
        """Return the event type identifier."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.get_event_type(),
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self._get_data(),
        }

    @abstractmethod
    def _get_data(self) -> dict[str, Any]:
        """Get event-specific data for serialization."""
        pass


@dataclass
class ToolUseEvent(Event):
    """Event fired when a tool is used."""

    tool_name: str = ""
    success: bool = True
    duration_ms: float | None = None

    def get_event_type(self) -> str:
        return "tool_use"

    def _get_data(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "duration_ms": self.duration_ms,
        }


@dataclass
class FileChangeEvent(Event):
    """Event fired when a file is modified."""

    file_path: str = ""
    change_type: str = "modified"  # "created", "modified", "deleted"

    def get_event_type(self) -> str:
        return "file_change"

    def _get_data(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
        }


@dataclass
class UserActionEvent(Event):
    """Event fired when user performs an action."""

    action_type: str = "command"
    action_details: dict[str, Any] = field(default_factory=dict)

    def get_event_type(self) -> str:
        return "user_action"

    def _get_data(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "action_details": self.action_details,
        }


@dataclass
class SystemEvent(Event):
    """Event fired for system-level events."""

    event_name: str = ""
    severity: str = "info"  # "info", "warning", "error"
    component: str = ""

    def get_event_type(self) -> str:
        return "system"

    def _get_data(self) -> dict[str, Any]:
        return {
            "event_name": self.event_name,
            "severity": self.severity,
            "component": self.component,
        }


@dataclass
class LearningEvent(Event):
    """Event fired when the system learns something new."""

    learning_type: str = "pattern_detected"
    confidence: float = 0.0  # 0.0 to 1.0

    def get_event_type(self) -> str:
        return "learning"

    def _get_data(self) -> dict[str, Any]:
        return {
            "learning_type": self.learning_type,
            "confidence": self.confidence,
        }


@dataclass
class ClaudeEvent(Event):
    """Event received directly from Claude Code hooks."""

    type: str = ""  # Hook type: pre_tool_use, post_tool_use, etc.
    data: dict[str, Any] = field(default_factory=dict)  # Raw hook data
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "claude_code"

    def get_event_type(self) -> str:
        return f"claude_{self.type}"

    def _get_data(self) -> dict[str, Any]:
        return {
            "hook_type": self.type,
            "hook_data": self.data,
            "timestamp_iso": self.timestamp.isoformat(),
        }


@dataclass
class QuaestorEvent(Event):
    """Event originating from Quaestor system (not Claude)."""

    type: str = ""  # Event type: milestone_updated, config_changed, etc.
    data: dict[str, Any] = field(default_factory=dict)
    component: str = ""  # Which Quaestor component sent this
    source: str = "quaestor"

    def get_event_type(self) -> str:
        return f"quaestor_{self.type}"

    def _get_data(self) -> dict[str, Any]:
        return {
            "quaestor_type": self.type,
            "component": self.component,
            "event_data": self.data,
        }
