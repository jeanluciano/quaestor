"""Pattern data models for the predictive engine.

This module defines the core pattern types used for behavior recognition
and prediction in the A1 system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PatternType(Enum):
    """Types of patterns the system can recognize."""

    COMMAND_SEQUENCE = "command_sequence"
    WORKFLOW = "workflow"
    FILE_ACCESS = "file_access"
    ERROR_RECOVERY = "error_recovery"
    TIME_BASED = "time_based"
    CONTEXT_SWITCH = "context_switch"


@dataclass
class BasePattern:
    """Base class for all pattern types."""

    id: str
    pattern_type: PatternType = field(init=False)
    confidence: float = 0.5
    frequency: int = 1
    first_seen: float = 0.0
    last_seen: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_confidence(self, success: bool) -> None:
        """Update pattern confidence based on observation."""
        if success:
            # Increase confidence, max 0.95
            self.confidence = min(0.95, self.confidence + 0.1)
        else:
            # Decrease confidence, min 0.1
            self.confidence = max(0.1, self.confidence - 0.2)

    def decay_confidence(self, time_since_last: float) -> None:
        """Decay confidence based on time since last observation."""
        # Decay by 0.01 per day of inactivity
        days_inactive = time_since_last / 86400
        decay_amount = days_inactive * 0.01
        self.confidence = max(0.1, self.confidence - decay_amount)


@dataclass
class CommandPattern(BasePattern):
    """Pattern representing a sequence of commands/tools."""

    command_sequence: list[str] = field(default_factory=list)
    context_requirements: dict[str, Any] = field(default_factory=dict)
    success_rate: float = 1.0
    average_duration: float = 0.0
    common_parameters: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize pattern type."""
        self.pattern_type = PatternType.COMMAND_SEQUENCE

    def matches_context(self, current_context: dict[str, Any]) -> bool:
        """Check if current context matches pattern requirements."""
        for key, required_value in self.context_requirements.items():
            if key not in current_context:
                return False
            if isinstance(required_value, list):
                if current_context[key] not in required_value:
                    return False
            elif current_context[key] != required_value:
                return False
        return True


@dataclass
class WorkflowPattern(BasePattern):
    """Pattern representing a complete workflow."""

    workflow_name: str = ""
    workflow_steps: list[dict[str, Any]] = field(default_factory=list)
    completion_rate: float = 1.0
    average_duration: float = 0.0
    common_variations: list[dict[str, Any]] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize pattern type."""
        self.pattern_type = PatternType.WORKFLOW

    def get_next_step(self, completed_steps: list[str]) -> dict[str, Any] | None:
        """Get the next expected step in the workflow."""
        completed_set = set(completed_steps)
        for step in self.workflow_steps:
            if step.get("id") not in completed_set:
                return step
        return None


@dataclass
class FilePattern(BasePattern):
    """Pattern representing file access behavior."""

    file_sequence: list[str] = field(default_factory=list)
    file_groups: list[list[str]] = field(default_factory=list)
    access_type: str = "read"  # read, write, edit
    common_operations: list[str] = field(default_factory=list)
    related_files: dict[str, float] = field(default_factory=dict)  # file -> correlation

    def __post_init__(self):
        """Initialize pattern type."""
        self.pattern_type = PatternType.FILE_ACCESS

    def suggest_next_files(self, current_file: str, limit: int = 5) -> list[tuple[str, float]]:
        """Suggest likely next files based on pattern."""
        suggestions = []
        seen = set()

        # First, check related files directly
        if current_file in self.related_files:
            # If current file is a key, its values are the related files
            for file, score in self.related_files.items():
                if file != current_file and file not in seen:
                    suggestions.append((file, score))
                    seen.add(file)

        # Also check if current file is in the sequence
        if current_file in self.file_sequence:
            idx = self.file_sequence.index(current_file)
            # Suggest next file in sequence
            if idx + 1 < len(self.file_sequence):
                next_file = self.file_sequence[idx + 1]
                if next_file not in seen and next_file in self.related_files:
                    suggestions.append((next_file, self.related_files[next_file]))
                    seen.add(next_file)

        # Check if current file is in any file group
        for group in self.file_groups:
            if current_file in group:
                for file in group:
                    if file != current_file and file not in seen:
                        # Use related_files score if available, otherwise default
                        score = self.related_files.get(file, 0.5)
                        suggestions.append((file, score))
                        seen.add(file)

        # Sort by correlation score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:limit]


@dataclass
class ErrorRecoveryPattern(BasePattern):
    """Pattern representing error recovery sequences."""

    error_type: str = ""
    error_context: dict[str, Any] = field(default_factory=dict)
    recovery_actions: list[dict[str, Any]] = field(default_factory=list)
    success_rate: float = 1.0
    common_fixes: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize pattern type."""
        self.pattern_type = PatternType.ERROR_RECOVERY

    def get_recovery_suggestion(self, error_details: dict[str, Any]) -> list[dict[str, Any]]:
        """Get suggested recovery actions for an error."""
        # Check if error matches this pattern
        if error_details.get("type") != self.error_type:
            return []

        # Return recovery actions sorted by likelihood
        return sorted(self.recovery_actions, key=lambda x: x.get("success_rate", 0), reverse=True)


@dataclass
class TimeBasedPattern(BasePattern):
    """Pattern based on time of day/week usage."""

    time_slots: list[dict[str, Any]] = field(default_factory=list)  # hour ranges
    day_of_week: list[int] = field(default_factory=list)  # 0-6
    common_activities: list[str] = field(default_factory=list)
    peak_hours: list[int] = field(default_factory=list)

    def __post_init__(self):
        """Initialize pattern type."""
        self.pattern_type = PatternType.TIME_BASED

    def is_active_time(self, hour: int, day: int) -> bool:
        """Check if current time matches pattern."""
        if self.day_of_week and day not in self.day_of_week:
            return False

        for slot in self.time_slots:
            start = slot.get("start", 0)
            end = slot.get("end", 24)
            if start <= hour < end:
                return True

        return False


# Type alias for any pattern type
Pattern = BasePattern | CommandPattern | WorkflowPattern | FilePattern | ErrorRecoveryPattern | TimeBasedPattern
