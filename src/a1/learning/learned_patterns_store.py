"""Storage and management of learned exception patterns."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class LearnedPattern:
    """A pattern learned from repeated exceptions."""

    id: str
    rule_id: str
    pattern_type: str
    pattern_criteria: dict[str, Any]
    confidence: float
    frequency: int
    first_seen: float
    last_seen: float
    last_applied: float | None = None
    application_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def matches(self, context: dict[str, Any]) -> bool:
        """Check if context matches this pattern."""
        for key, expected_value in self.pattern_criteria.items():
            actual_value = context.get(key)

            if actual_value is None:
                return False

            # Handle different comparison types
            if isinstance(expected_value, dict) and "operator" in expected_value:
                if not self._evaluate_operator(actual_value, expected_value):
                    return False
            elif isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True

    def _evaluate_operator(self, value: Any, condition: dict[str, Any]) -> bool:
        """Evaluate operator-based conditions."""
        op = condition["operator"]
        threshold = condition["value"]

        if op == "gt":
            return value > threshold
        elif op == "gte":
            return value >= threshold
        elif op == "lt":
            return value < threshold
        elif op == "lte":
            return value <= threshold
        elif op == "contains":
            return threshold in str(value)
        elif op == "regex":
            import re

            return bool(re.search(threshold, str(value)))

        return False

    def apply(self) -> None:
        """Record that this pattern was applied."""
        self.last_applied = time.time()
        self.application_count += 1

    def decay_confidence(self, decay_rate: float = 0.95) -> None:
        """Decay confidence over time if not used."""
        if self.last_applied:
            time_since_applied = time.time() - self.last_applied
            days_inactive = time_since_applied / 86400

            if days_inactive > 7:
                self.confidence *= decay_rate ** (days_inactive / 7)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "pattern_type": self.pattern_type,
            "pattern_criteria": self.pattern_criteria,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "last_applied": self.last_applied,
            "application_count": self.application_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnedPattern":
        """Create from dictionary."""
        return cls(**data)


class LearnedPatternsStore:
    """Store and manage learned exception patterns."""

    def __init__(self, storage_path: Path | None = None, max_patterns_per_rule: int = 20, min_confidence: float = 0.5):
        self.storage_path = storage_path or Path(".quaestor/.a1/learned_patterns.json")
        self.max_patterns_per_rule = max_patterns_per_rule
        self.min_confidence = min_confidence
        self.patterns: dict[str, LearnedPattern] = {}
        self.pattern_index: dict[str, set[str]] = {}  # rule_id -> pattern_ids
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load patterns from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)

                for pattern_data in data.get("patterns", []):
                    pattern = LearnedPattern.from_dict(pattern_data)
                    self.patterns[pattern.id] = pattern

                    # Update index
                    if pattern.rule_id not in self.pattern_index:
                        self.pattern_index[pattern.rule_id] = set()
                    self.pattern_index[pattern.rule_id].add(pattern.id)

                # Apply confidence decay
                self._apply_confidence_decay()

            except Exception as e:
                print(f"Error loading patterns: {e}")
                self.patterns = {}
                self.pattern_index = {}

    def _save_patterns(self) -> None:
        """Save patterns to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Filter out low confidence patterns
            valid_patterns = [p.to_dict() for p in self.patterns.values() if p.confidence >= self.min_confidence]

            data = {
                "patterns": valid_patterns,
                "last_updated": time.time(),
                "stats": {
                    "total_patterns": len(valid_patterns),
                    "by_rule": {rule_id: len(patterns) for rule_id, patterns in self.pattern_index.items()},
                },
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving patterns: {e}")

    def add_pattern(
        self,
        rule_id: str,
        pattern_type: str,
        pattern_criteria: dict[str, Any],
        initial_confidence: float = 0.6,
        metadata: dict[str, Any] | None = None,
    ) -> LearnedPattern:
        """Add a new learned pattern."""
        pattern_id = str(uuid4())

        pattern = LearnedPattern(
            id=pattern_id,
            rule_id=rule_id,
            pattern_type=pattern_type,
            pattern_criteria=pattern_criteria,
            confidence=initial_confidence,
            frequency=1,
            first_seen=time.time(),
            last_seen=time.time(),
            metadata=metadata or {},
        )

        self.patterns[pattern_id] = pattern

        # Update index
        if rule_id not in self.pattern_index:
            self.pattern_index[rule_id] = set()
        self.pattern_index[rule_id].add(pattern_id)

        # Enforce max patterns per rule
        self._enforce_pattern_limit(rule_id)

        self._save_patterns()
        return pattern

    def update_pattern(self, pattern_id: str, increase_confidence: bool = True) -> None:
        """Update an existing pattern."""
        if pattern_id not in self.patterns:
            return

        pattern = self.patterns[pattern_id]
        pattern.frequency += 1
        pattern.last_seen = time.time()

        if increase_confidence:
            # Increase confidence with diminishing returns
            pattern.confidence = min(0.95, pattern.confidence + (0.1 * (1 - pattern.confidence)))

        self._save_patterns()

    def get_matching_patterns(self, rule_id: str, context: dict[str, Any]) -> list[LearnedPattern]:
        """Get patterns that match the given context."""
        if rule_id not in self.pattern_index:
            return []

        matching = []
        for pattern_id in self.pattern_index[rule_id]:
            pattern = self.patterns.get(pattern_id)
            if pattern and pattern.matches(context):
                matching.append(pattern)

        # Sort by confidence and frequency
        matching.sort(key=lambda p: (p.confidence, p.frequency), reverse=True)

        return matching

    def apply_pattern(self, pattern_id: str) -> None:
        """Record that a pattern was applied."""
        if pattern_id in self.patterns:
            self.patterns[pattern_id].apply()
            self._save_patterns()

    def _enforce_pattern_limit(self, rule_id: str) -> None:
        """Enforce maximum patterns per rule."""
        if rule_id not in self.pattern_index:
            return

        pattern_ids = list(self.pattern_index[rule_id])
        if len(pattern_ids) <= self.max_patterns_per_rule:
            return

        # Sort by confidence and keep top patterns
        patterns = [self.patterns[pid] for pid in pattern_ids]
        patterns.sort(key=lambda p: (p.confidence, p.frequency), reverse=True)

        # Remove lowest confidence patterns
        to_remove = patterns[self.max_patterns_per_rule :]
        for pattern in to_remove:
            del self.patterns[pattern.id]
            self.pattern_index[rule_id].remove(pattern.id)

    def _apply_confidence_decay(self) -> None:
        """Apply confidence decay to inactive patterns."""
        for pattern in self.patterns.values():
            pattern.decay_confidence()

            # Remove if confidence too low
            if pattern.confidence < self.min_confidence:
                del self.patterns[pattern.id]
                if pattern.rule_id in self.pattern_index:
                    self.pattern_index[pattern.rule_id].discard(pattern.id)

    def get_pattern_stats(self) -> dict[str, Any]:
        """Get statistics about learned patterns."""
        total_patterns = len(self.patterns)
        active_patterns = sum(
            1 for p in self.patterns.values() if p.last_applied and (time.time() - p.last_applied) < 86400 * 7
        )

        high_confidence = sum(1 for p in self.patterns.values() if p.confidence > 0.8)

        most_applied = sorted(self.patterns.values(), key=lambda p: p.application_count, reverse=True)[:5]

        return {
            "total_patterns": total_patterns,
            "active_patterns": active_patterns,
            "high_confidence_patterns": high_confidence,
            "patterns_by_rule": {rule_id: len(patterns) for rule_id, patterns in self.pattern_index.items()},
            "most_applied": [
                {
                    "rule_id": p.rule_id,
                    "pattern_type": p.pattern_type,
                    "applications": p.application_count,
                    "confidence": p.confidence,
                }
                for p in most_applied
            ],
        }

    def suggest_permanent_exceptions(
        self, confidence_threshold: float = 0.9, application_threshold: int = 10
    ) -> list[dict[str, Any]]:
        """Suggest patterns that should become permanent exceptions."""
        suggestions = []

        for pattern in self.patterns.values():
            if pattern.confidence >= confidence_threshold and pattern.application_count >= application_threshold:
                suggestions.append(
                    {
                        "pattern_id": pattern.id,
                        "rule_id": pattern.rule_id,
                        "pattern_type": pattern.pattern_type,
                        "criteria": pattern.pattern_criteria,
                        "confidence": pattern.confidence,
                        "applications": pattern.application_count,
                        "reason": f"High confidence ({pattern.confidence:.2f}) "
                        f"with {pattern.application_count} applications",
                    }
                )

        return suggestions
