"""Exception tracking system for rule enforcement events."""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class ExceptionEvent:
    """Represents an exception or override event."""

    id: str
    timestamp: float
    rule_id: str
    event_type: str  # override, violation, adaptation, exception
    context: dict[str, Any]
    outcome: str  # allowed, blocked, overridden
    enforcement_level: str
    justification: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "rule_id": self.rule_id,
            "event_type": self.event_type,
            "context": self.context,
            "outcome": self.outcome,
            "enforcement_level": self.enforcement_level,
            "justification": self.justification,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExceptionEvent":
        """Create from dictionary."""
        return cls(**data)

    @property
    def datetime(self) -> datetime:
        """Get event datetime."""
        return datetime.fromtimestamp(self.timestamp)


class ExceptionTracker:
    """Track and store exception events for analysis."""

    def __init__(self, storage_path: Path | None = None, max_events: int = 10000):
        self.storage_path = storage_path or Path(".quaestor/.a1/exception_events.json")
        self.max_events = max_events
        self.events: list[ExceptionEvent] = []
        self.event_index: dict[str, list[int]] = {}  # rule_id -> event indices
        self._load_events()

    def _load_events(self) -> None:
        """Load events from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)

                for event_data in data.get("events", []):
                    event = ExceptionEvent.from_dict(event_data)
                    self.events.append(event)

                self._rebuild_index()

            except Exception as e:
                print(f"Error loading events: {e}")
                self.events = []
                self.event_index = {}

    def _rebuild_index(self) -> None:
        """Rebuild the event index."""
        self.event_index = {}
        for i, event in enumerate(self.events):
            if event.rule_id not in self.event_index:
                self.event_index[event.rule_id] = []
            self.event_index[event.rule_id].append(i)

    def _save_events(self) -> None:
        """Save events to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Keep only recent events if over limit
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events :]
                self._rebuild_index()

            data = {
                "events": [e.to_dict() for e in self.events],
                "last_updated": time.time(),
                "total_events": len(self.events),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving events: {e}")

    def track_event(
        self,
        rule_id: str,
        event_type: str,
        context: dict[str, Any],
        outcome: str,
        enforcement_level: str,
        justification: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExceptionEvent:
        """Track a new exception event."""
        event = ExceptionEvent(
            id=str(uuid4()),
            timestamp=time.time(),
            rule_id=rule_id,
            event_type=event_type,
            context=context,
            outcome=outcome,
            enforcement_level=enforcement_level,
            justification=justification,
            metadata=metadata or {},
        )

        self.events.append(event)

        # Update index
        if rule_id not in self.event_index:
            self.event_index[rule_id] = []
        self.event_index[rule_id].append(len(self.events) - 1)

        self._save_events()
        return event

    def get_events_for_rule(
        self, rule_id: str, hours: float | None = None, event_types: list[str] | None = None
    ) -> list[ExceptionEvent]:
        """Get events for a specific rule."""
        if rule_id not in self.event_index:
            return []

        events = [self.events[i] for i in self.event_index[rule_id]]

        # Filter by time if specified
        if hours is not None:
            cutoff_time = time.time() - (hours * 3600)
            events = [e for e in events if e.timestamp > cutoff_time]

        # Filter by event type if specified
        if event_types:
            events = [e for e in events if e.event_type in event_types]

        return events

    def get_recent_events(self, hours: float = 24, limit: int | None = None) -> list[ExceptionEvent]:
        """Get recent events across all rules."""
        cutoff_time = time.time() - (hours * 3600)
        recent = [e for e in self.events if e.timestamp > cutoff_time]

        # Sort by timestamp descending
        recent.sort(key=lambda e: e.timestamp, reverse=True)

        if limit:
            recent = recent[:limit]

        return recent

    def get_event_summary(self, hours: float = 24) -> dict[str, Any]:
        """Get summary statistics for recent events."""
        recent_events = self.get_recent_events(hours)

        summary = {
            "total_events": len(recent_events),
            "by_type": {},
            "by_rule": {},
            "by_outcome": {},
            "by_level": {},
            "override_rate": 0.0,
        }

        for event in recent_events:
            # Count by type
            event_type = event.event_type
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1

            # Count by rule
            rule_id = event.rule_id
            summary["by_rule"][rule_id] = summary["by_rule"].get(rule_id, 0) + 1

            # Count by outcome
            outcome = event.outcome
            summary["by_outcome"][outcome] = summary["by_outcome"].get(outcome, 0) + 1

            # Count by level
            level = event.enforcement_level
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1

        # Calculate override rate
        if recent_events:
            overrides = sum(1 for e in recent_events if e.outcome == "overridden")
            summary["override_rate"] = overrides / len(recent_events)

        return summary

    def find_patterns(self, rule_id: str, min_frequency: int = 3) -> list[dict[str, Any]]:
        """Find common patterns in exception events."""
        events = self.get_events_for_rule(rule_id)

        if len(events) < min_frequency:
            return []

        # Group by common attributes
        patterns = []

        # Pattern 1: File path patterns
        file_patterns = {}
        for event in events:
            file_path = event.context.get("file_path", "")
            if file_path:
                # Extract directory or file type
                if "/" in file_path:
                    directory = file_path.rsplit("/", 1)[0]
                    file_patterns[directory] = file_patterns.get(directory, 0) + 1

        for path, count in file_patterns.items():
            if count >= min_frequency:
                patterns.append(
                    {"type": "file_path", "pattern": path, "frequency": count, "percentage": count / len(events)}
                )

        # Pattern 2: Intent patterns
        intent_patterns = {}
        for event in events:
            intent = event.context.get("user_intent", "")
            if intent and intent != "unknown":
                intent_patterns[intent] = intent_patterns.get(intent, 0) + 1

        for intent, count in intent_patterns.items():
            if count >= min_frequency:
                patterns.append(
                    {"type": "user_intent", "pattern": intent, "frequency": count, "percentage": count / len(events)}
                )

        # Pattern 3: Time patterns (hour of day)
        hour_patterns = {}
        for event in events:
            hour = datetime.fromtimestamp(event.timestamp).hour
            hour_patterns[hour] = hour_patterns.get(hour, 0) + 1

        for hour, count in hour_patterns.items():
            if count >= min_frequency:
                patterns.append(
                    {
                        "type": "time_of_day",
                        "pattern": f"{hour:02d}:00-{hour + 1:02d}:00",
                        "frequency": count,
                        "percentage": count / len(events),
                    }
                )

        # Sort by frequency
        patterns.sort(key=lambda p: p["frequency"], reverse=True)

        return patterns

    def get_summary(self, hours: float = 24) -> dict[str, Any]:
        """Get summary of exception events."""
        summary = self.get_event_summary(hours)

        # Add by_rule breakdown with override rates
        for rule_id in summary["by_rule"]:
            rule_events = self.get_events_for_rule(rule_id, hours)
            overrides = sum(1 for e in rule_events if e.outcome == "overridden")
            total = len(rule_events)
            if total > 0:
                if isinstance(summary["by_rule"][rule_id], int):
                    summary["by_rule"][rule_id] = {"total": total, "override_rate": overrides / total}

        return summary

    def detect_patterns(self, rule_id: str, min_frequency: int = 3) -> list[dict[str, Any]]:
        """Detect patterns in rule exceptions (alias for find_patterns)."""
        patterns = self.find_patterns(rule_id, min_frequency)

        # Transform to expected format
        result = []
        for pattern in patterns:
            # Group similar patterns
            common_context = {}
            if pattern["type"] == "user_intent":
                common_context["user_intent"] = pattern["pattern"]
            elif pattern["type"] == "file_path":
                common_context["file_path"] = pattern["pattern"]

            result.append(
                {
                    "count": pattern["frequency"],
                    "common_context": common_context,
                    "pattern_type": pattern["type"],
                    "percentage": pattern["percentage"],
                }
            )

        return result
