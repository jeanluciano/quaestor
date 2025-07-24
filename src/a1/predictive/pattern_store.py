"""Pattern storage system for the predictive engine.

This module handles persistence and retrieval of discovered patterns,
integrating with the existing A1 storage infrastructure.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

from .patterns import (
    BasePattern,
    CommandPattern,
    ErrorRecoveryPattern,
    FilePattern,
    Pattern,
    PatternType,
    TimeBasedPattern,
    WorkflowPattern,
)

logger = logging.getLogger(__name__)


class PatternStore:
    """Manages storage and retrieval of patterns."""

    def __init__(self, storage_path: Path | None = None):
        """Initialize pattern store.

        Args:
            storage_path: Path to store patterns (defaults to .quaestor/.a1/)
        """
        if storage_path is None:
            storage_path = Path(".quaestor/.a1")

        self.storage_path = storage_path
        self.patterns_file = storage_path / "predictive_patterns.json"
        self.index_file = storage_path / "pattern_index.json"

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load existing patterns
        self.patterns: dict[str, Pattern] = {}
        self.pattern_index: dict[str, list[str]] = {
            "by_type": {},
            "by_confidence": {},
            "by_frequency": {},
            "recent": [],
        }

        self._load_patterns()

    def save_pattern(self, pattern: Pattern) -> None:
        """Save a pattern to storage."""
        pattern.last_seen = time.time()
        self.patterns[pattern.id] = pattern

        # Update indexes
        self._update_indexes(pattern)

        # Persist to disk
        self._save_patterns()

        logger.debug(f"Saved pattern {pattern.id} of type {pattern.pattern_type.value}")

    def get_pattern(self, pattern_id: str) -> Pattern | None:
        """Retrieve a pattern by ID."""
        return self.patterns.get(pattern_id)

    def get_patterns_by_type(self, pattern_type: PatternType) -> list[Pattern]:
        """Get all patterns of a specific type."""
        pattern_ids = self.pattern_index["by_type"].get(pattern_type.value, [])
        return [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]

    def get_high_confidence_patterns(self, min_confidence: float = 0.7) -> list[Pattern]:
        """Get patterns with high confidence scores."""
        return [p for p in self.patterns.values() if p.confidence >= min_confidence]

    def get_frequent_patterns(self, min_frequency: int = 5) -> list[Pattern]:
        """Get frequently occurring patterns."""
        return [p for p in self.patterns.values() if p.frequency >= min_frequency]

    def get_recent_patterns(self, limit: int = 20) -> list[Pattern]:
        """Get recently observed patterns."""
        sorted_patterns = sorted(self.patterns.values(), key=lambda p: p.last_seen, reverse=True)
        return sorted_patterns[:limit]

    def update_pattern_observation(self, pattern_id: str, success: bool = True) -> None:
        """Update a pattern after observation."""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.frequency += 1
            pattern.last_seen = time.time()
            pattern.update_confidence(success)

            # Update pattern-specific metrics
            if isinstance(pattern, CommandPattern) and hasattr(pattern, "success_rate"):
                total = pattern.frequency
                current_success = pattern.success_rate * (total - 1)
                pattern.success_rate = (current_success + (1 if success else 0)) / total

            self._save_patterns()

    def merge_patterns(self, new_patterns: list[Pattern]) -> None:
        """Merge new patterns with existing ones."""
        for new_pattern in new_patterns:
            existing = self._find_similar_pattern(new_pattern)

            if existing:
                # Merge with existing pattern
                self._merge_pattern_data(existing, new_pattern)
            else:
                # Add as new pattern
                self.save_pattern(new_pattern)

    def prune_old_patterns(self, days_inactive: int = 30) -> int:
        """Remove patterns that haven't been seen recently."""
        current_time = time.time()
        cutoff_time = current_time - (days_inactive * 86400)
        pruned_count = 0

        patterns_to_remove = []
        for pattern_id, pattern in self.patterns.items():
            if pattern.last_seen < cutoff_time and pattern.frequency < 5:
                patterns_to_remove.append(pattern_id)

        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
            pruned_count += 1

        if pruned_count > 0:
            self._rebuild_indexes()
            self._save_patterns()
            logger.info(f"Pruned {pruned_count} old patterns")

        return pruned_count

    def export_patterns(self, output_path: Path) -> None:
        """Export patterns to a file."""
        export_data = {
            "export_time": time.time(),
            "pattern_count": len(self.patterns),
            "patterns": [self._pattern_to_dict(p) for p in self.patterns.values()],
            "statistics": self._calculate_statistics(),
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

    def _load_patterns(self) -> None:
        """Load patterns from storage."""
        if not self.patterns_file.exists():
            return

        try:
            with open(self.patterns_file) as f:
                data = json.load(f)

            for pattern_data in data.get("patterns", []):
                pattern = self._dict_to_pattern(pattern_data)
                if pattern:
                    self.patterns[pattern.id] = pattern

            # Load or rebuild indexes
            if self.index_file.exists():
                with open(self.index_file) as f:
                    self.pattern_index = json.load(f)
            else:
                self._rebuild_indexes()

            logger.info(f"Loaded {len(self.patterns)} patterns from storage")

        except Exception as e:
            logger.error(f"Error loading patterns: {e}")

    def _save_patterns(self) -> None:
        """Save patterns to storage."""
        data = {
            "version": "1.0",
            "last_updated": time.time(),
            "patterns": [self._pattern_to_dict(p) for p in self.patterns.values()],
        }

        try:
            with open(self.patterns_file, "w") as f:
                json.dump(data, f, indent=2)

            with open(self.index_file, "w") as f:
                json.dump(self.pattern_index, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving patterns: {e}")

    def _pattern_to_dict(self, pattern: Pattern) -> dict[str, Any]:
        """Convert pattern to dictionary for storage."""
        base_dict = {
            "id": pattern.id,
            "pattern_type": pattern.pattern_type.value,
            "confidence": pattern.confidence,
            "frequency": pattern.frequency,
            "first_seen": pattern.first_seen,
            "last_seen": pattern.last_seen,
            "metadata": pattern.metadata,
        }

        # Add type-specific fields
        if isinstance(pattern, CommandPattern):
            base_dict.update(
                {
                    "command_sequence": pattern.command_sequence,
                    "context_requirements": pattern.context_requirements,
                    "success_rate": pattern.success_rate,
                    "average_duration": pattern.average_duration,
                    "common_parameters": pattern.common_parameters,
                }
            )
        elif isinstance(pattern, WorkflowPattern):
            base_dict.update(
                {
                    "workflow_name": pattern.workflow_name,
                    "workflow_steps": pattern.workflow_steps,
                    "completion_rate": pattern.completion_rate,
                    "average_duration": pattern.average_duration,
                    "common_variations": pattern.common_variations,
                    "triggers": pattern.triggers,
                }
            )
        elif isinstance(pattern, FilePattern):
            base_dict.update(
                {
                    "file_sequence": pattern.file_sequence,
                    "file_groups": pattern.file_groups,
                    "access_type": pattern.access_type,
                    "common_operations": pattern.common_operations,
                    "related_files": pattern.related_files,
                }
            )
        elif isinstance(pattern, ErrorRecoveryPattern):
            base_dict.update(
                {
                    "error_type": pattern.error_type,
                    "error_context": pattern.error_context,
                    "recovery_actions": pattern.recovery_actions,
                    "success_rate": pattern.success_rate,
                    "common_fixes": pattern.common_fixes,
                }
            )
        elif isinstance(pattern, TimeBasedPattern):
            base_dict.update(
                {
                    "time_slots": pattern.time_slots,
                    "day_of_week": pattern.day_of_week,
                    "common_activities": pattern.common_activities,
                    "peak_hours": pattern.peak_hours,
                }
            )

        return base_dict

    def _dict_to_pattern(self, data: dict[str, Any]) -> Pattern | None:
        """Convert dictionary to pattern object."""
        pattern_type = PatternType(data["pattern_type"])

        # Remove pattern_type from data since it's set in __post_init__
        pattern_data = {k: v for k, v in data.items() if k != "pattern_type"}

        # Create appropriate pattern type
        if pattern_type == PatternType.COMMAND_SEQUENCE:
            return CommandPattern(**pattern_data)
        elif pattern_type == PatternType.WORKFLOW:
            return WorkflowPattern(**pattern_data)
        elif pattern_type == PatternType.FILE_ACCESS:
            return FilePattern(**pattern_data)
        elif pattern_type == PatternType.ERROR_RECOVERY:
            return ErrorRecoveryPattern(**pattern_data)
        elif pattern_type == PatternType.TIME_BASED:
            return TimeBasedPattern(**pattern_data)
        else:
            # For base pattern, we need to set pattern_type manually
            pattern = BasePattern(**pattern_data)
            pattern.pattern_type = pattern_type
            return pattern

    def _update_indexes(self, pattern: Pattern) -> None:
        """Update pattern indexes."""
        # By type
        type_key = pattern.pattern_type.value
        if type_key not in self.pattern_index["by_type"]:
            self.pattern_index["by_type"][type_key] = []
        if pattern.id not in self.pattern_index["by_type"][type_key]:
            self.pattern_index["by_type"][type_key].append(pattern.id)

        # Recent patterns
        if pattern.id in self.pattern_index["recent"]:
            self.pattern_index["recent"].remove(pattern.id)
        self.pattern_index["recent"].insert(0, pattern.id)
        self.pattern_index["recent"] = self.pattern_index["recent"][:100]

    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes from patterns."""
        self.pattern_index = {
            "by_type": {},
            "by_confidence": {},
            "by_frequency": {},
            "recent": [],
        }

        for pattern in self.patterns.values():
            self._update_indexes(pattern)

    def _find_similar_pattern(self, new_pattern: Pattern) -> Pattern | None:
        """Find existing pattern similar to new one."""
        candidates = self.get_patterns_by_type(new_pattern.pattern_type)

        for candidate in candidates:
            if self._patterns_similar(candidate, new_pattern):
                return candidate

        return None

    def _patterns_similar(self, pattern1: Pattern, pattern2: Pattern) -> bool:
        """Check if two patterns are similar enough to merge."""
        if pattern1.pattern_type != pattern2.pattern_type:
            return False

        # Type-specific similarity checks
        if isinstance(pattern1, CommandPattern) and isinstance(pattern2, CommandPattern):
            return pattern1.command_sequence == pattern2.command_sequence

        elif isinstance(pattern1, WorkflowPattern) and isinstance(pattern2, WorkflowPattern):
            # Similar if same trigger and similar steps
            if set(pattern1.triggers) & set(pattern2.triggers):
                step_ids1 = {s["id"] for s in pattern1.workflow_steps}
                step_ids2 = {s["id"] for s in pattern2.workflow_steps}
                overlap = len(step_ids1 & step_ids2)
                return overlap / max(len(step_ids1), len(step_ids2)) > 0.7

        elif isinstance(pattern1, FilePattern) and isinstance(pattern2, FilePattern):
            # Similar if significant file overlap
            files1 = set(pattern1.file_sequence)
            files2 = set(pattern2.file_sequence)
            if files1 and files2:
                overlap = len(files1 & files2)
                return overlap / min(len(files1), len(files2)) > 0.7

        return False

    def _merge_pattern_data(self, existing: Pattern, new: Pattern) -> None:
        """Merge data from new pattern into existing one."""
        # Update frequency and confidence
        existing.frequency += new.frequency
        existing.last_seen = max(existing.last_seen, new.last_seen)

        # Weighted confidence update
        total_freq = existing.frequency + new.frequency
        existing.confidence = (existing.confidence * existing.frequency + new.confidence * new.frequency) / total_freq

        # Type-specific merging
        if isinstance(existing, CommandPattern) and isinstance(new, CommandPattern):
            # Merge common parameters
            for param, values in new.common_parameters.items():
                if param not in existing.common_parameters:
                    existing.common_parameters[param] = values
                else:
                    # Merge value lists
                    all_values = existing.common_parameters[param] + values
                    existing.common_parameters[param] = list(set(all_values))[:5]

        elif isinstance(existing, WorkflowPattern) and isinstance(new, WorkflowPattern):
            # Merge triggers
            existing.triggers = list(set(existing.triggers + new.triggers))

            # Update completion rate
            total = existing.frequency + new.frequency
            existing.completion_rate = (
                existing.completion_rate * existing.frequency + new.completion_rate * new.frequency
            ) / total

    def _calculate_statistics(self) -> dict[str, Any]:
        """Calculate pattern statistics."""
        return {
            "total_patterns": len(self.patterns),
            "by_type": {ptype.value: len(self.get_patterns_by_type(ptype)) for ptype in PatternType},
            "high_confidence": len(self.get_high_confidence_patterns()),
            "frequent": len(self.get_frequent_patterns()),
            "average_confidence": (
                sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0
            ),
            "average_frequency": (
                sum(p.frequency for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0
            ),
        }
