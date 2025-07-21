"""Track enforcement history and patterns."""

import json
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .enforcement_levels import EnforcementLevel


@dataclass
class EnforcementEvent:
    """Record of an enforcement action."""

    id: str
    timestamp: float
    rule_id: str
    level: EnforcementLevel
    context: Any  # EnforcementContext
    result: Any  # EnforcementResult
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "id": self.id,
            "timestamp": self.timestamp,
            "rule_id": self.rule_id,
            "level": self.level.name,
            "message": self.message,
            "metadata": self.metadata or {},
        }

        # Handle context serialization
        if hasattr(self.context, "__dict__"):
            data["context"] = {k: v for k, v in self.context.__dict__.items() if not k.startswith("_")}
        else:
            data["context"] = str(self.context)

        # Handle result serialization
        if hasattr(self.result, "__dict__"):
            result_dict = {k: v for k, v in self.result.__dict__.items() if not k.startswith("_")}
            # Convert EnforcementLevel to string
            if "level" in result_dict and hasattr(result_dict["level"], "name"):
                result_dict["level"] = result_dict["level"].name
            data["result"] = result_dict
        else:
            data["result"] = str(self.result)

        return data


class EnforcementHistory:
    """Track and analyze enforcement history."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path(".quaestor/.enforcement_history.json")
        self.events: list[EnforcementEvent] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load history from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    json.load(f)
                    # Note: This is simplified - in production would deserialize properly
                    self.events = []
            except Exception:
                self.events = []
        else:
            self.events = []

    def _save_history(self) -> None:
        """Save history to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Keep only last 1000 events
            recent_events = self.events[-1000:]

            data = [event.to_dict() for event in recent_events]

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Fail silently for now

    def add_event(self, event: EnforcementEvent) -> None:
        """Add an enforcement event to history."""
        self.events.append(event)
        self._save_history()

    def get_rule_violations(self, rule_id: str, hours: float = 24) -> list[EnforcementEvent]:
        """Get recent violations for a specific rule."""
        cutoff_time = time.time() - (hours * 3600)
        return [
            event
            for event in self.events
            if event.rule_id == rule_id and event.timestamp > cutoff_time and event.level > EnforcementLevel.INFORM
        ]

    def get_violation_count(self, rule_id: str, context_key: str = None) -> int:
        """Get violation count for a rule, optionally filtered by context."""
        violations = 0
        for event in self.events:
            if event.rule_id == rule_id and event.level > EnforcementLevel.WARN:
                if context_key and hasattr(event.context, context_key):
                    # Filter by context attribute if specified
                    violations += 1
                elif not context_key:
                    violations += 1
        return violations

    def get_override_patterns(self, rule_id: str) -> dict[str, int]:
        """Analyze override patterns for a rule."""
        patterns = defaultdict(int)

        for event in self.events:
            if event.rule_id == rule_id and event.metadata and event.metadata.get("override"):
                # Extract pattern from context
                if hasattr(event.context, "user_intent"):
                    pattern_key = f"{event.context.user_intent}:{event.context.workflow_phase}"
                    patterns[pattern_key] += 1

        return dict(patterns)

    def get_enforcement_stats(self, hours: float = 24) -> dict[str, Any]:
        """Get enforcement statistics for the specified time period."""
        cutoff_time = time.time() - (hours * 3600)
        recent_events = [e for e in self.events if e.timestamp > cutoff_time]

        stats = {
            "total_events": len(recent_events),
            "by_level": defaultdict(int),
            "by_rule": defaultdict(int),
            "overrides": 0,
            "unique_rules": set(),
        }

        for event in recent_events:
            stats["by_level"][event.level.name] += 1
            stats["by_rule"][event.rule_id] += 1
            stats["unique_rules"].add(event.rule_id)

            if event.metadata and event.metadata.get("override"):
                stats["overrides"] += 1

        stats["by_level"] = dict(stats["by_level"])
        stats["by_rule"] = dict(stats["by_rule"])
        stats["unique_rules"] = len(stats["unique_rules"])

        return stats
