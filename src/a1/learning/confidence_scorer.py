"""Confidence scoring for learned patterns and rule adaptations."""

import math
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ConfidenceFactors:
    """Factors that influence confidence scoring."""

    frequency_weight: float = 0.3
    recency_weight: float = 0.2
    consistency_weight: float = 0.25
    context_match_weight: float = 0.25

    def validate(self) -> None:
        """Ensure weights sum to 1.0."""
        total = self.frequency_weight + self.recency_weight + self.consistency_weight + self.context_match_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Confidence weights must sum to 1.0, got {total}")


class ConfidenceScorer:
    """Score confidence in patterns and adaptations."""

    def __init__(self, factors: ConfidenceFactors | None = None):
        self.factors = factors or ConfidenceFactors()
        self.factors.validate()

    def score_pattern(self, pattern_data: dict[str, Any], context: dict[str, Any]) -> float:
        """Calculate confidence score for a pattern in given context."""
        # Base scores
        frequency_score = self._score_frequency(pattern_data.get("frequency", 0))
        recency_score = self._score_recency(pattern_data.get("last_seen", 0))
        consistency_score = self._score_consistency(pattern_data.get("applications", []))
        context_score = self._score_context_match(pattern_data, context)

        # Weighted combination
        confidence = (
            frequency_score * self.factors.frequency_weight
            + recency_score * self.factors.recency_weight
            + consistency_score * self.factors.consistency_weight
            + context_score * self.factors.context_match_weight
        )

        # Apply modifiers
        confidence = self._apply_modifiers(confidence, pattern_data, context)

        return max(0.0, min(1.0, confidence))

    def _score_frequency(self, frequency: int) -> float:
        """Score based on pattern frequency."""
        # Logarithmic scale with diminishing returns
        if frequency <= 0:
            return 0.0

        # Score increases with frequency but plateaus
        return min(1.0, math.log(frequency + 1) / math.log(50))

    def _score_recency(self, last_seen: float) -> float:
        """Score based on how recently pattern was seen."""
        if last_seen <= 0:
            return 0.0

        current_time = time.time()
        hours_ago = (current_time - last_seen) / 3600

        if hours_ago < 1:
            return 1.0
        elif hours_ago < 24:
            return 0.9
        elif hours_ago < 24 * 7:  # 1 week
            return 0.7
        elif hours_ago < 24 * 30:  # 1 month
            return 0.5
        else:
            # Exponential decay after 1 month
            months = hours_ago / (24 * 30)
            return max(0.1, 0.5 * math.exp(-0.5 * (months - 1)))

    def _score_consistency(self, applications: list[dict[str, Any]]) -> float:
        """Score based on consistency of pattern applications."""
        if not applications:
            return 0.5  # Neutral score for no data

        # Check success rate
        successful = sum(1 for app in applications if app.get("successful", True))
        success_rate = successful / len(applications)

        # Check time consistency (are applications spread out or clustered?)
        if len(applications) > 1:
            timestamps = sorted([app.get("timestamp", 0) for app in applications])
            intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]

            if intervals:
                # Calculate coefficient of variation
                mean_interval = sum(intervals) / len(intervals)
                if mean_interval > 0:
                    std_dev = math.sqrt(sum((x - mean_interval) ** 2 for x in intervals) / len(intervals))
                    cv = std_dev / mean_interval

                    # Lower CV means more consistent timing
                    timing_score = max(0, 1 - cv)
                else:
                    timing_score = 0.5
            else:
                timing_score = 0.5
        else:
            timing_score = 0.5

        # Combine success rate and timing consistency
        return 0.7 * success_rate + 0.3 * timing_score

    def _score_context_match(self, pattern_data: dict[str, Any], context: dict[str, Any]) -> float:
        """Score how well pattern matches current context."""
        if not pattern_data.get("pattern_criteria"):
            return 0.5

        criteria = pattern_data["pattern_criteria"]
        match_scores = []

        for key, expected_value in criteria.items():
            if key not in context:
                match_scores.append(0.0)
                continue

            actual_value = context[key]

            # Different scoring for different types
            if isinstance(expected_value, bool):
                score = 1.0 if actual_value == expected_value else 0.0
            elif isinstance(expected_value, str):
                # Fuzzy string matching
                score = self._string_similarity(str(actual_value), expected_value)
            elif isinstance(expected_value, int | float):
                # Numeric proximity
                diff = abs(actual_value - expected_value)
                score = max(0, 1 - diff / max(abs(expected_value), 1))
            elif isinstance(expected_value, list):
                # Set membership
                score = 1.0 if actual_value in expected_value else 0.0
            else:
                score = 0.5  # Unknown type

            match_scores.append(score)

        return sum(match_scores) / len(match_scores) if match_scores else 0.5

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity score."""
        # Simple approach: check for substring and common words
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0

        if s2_lower in s1_lower or s1_lower in s2_lower:
            return 0.8

        # Check common words
        words1 = set(s1_lower.split())
        words2 = set(s2_lower.split())

        if not words1 or not words2:
            return 0.0

        common = len(words1 & words2)
        total = len(words1 | words2)

        return common / total if total > 0 else 0.0

    def _apply_modifiers(self, base_confidence: float, pattern_data: dict[str, Any], context: dict[str, Any]) -> float:
        """Apply confidence modifiers based on special conditions."""
        modified = base_confidence

        # Boost for high-frequency patterns
        if pattern_data.get("frequency", 0) > 20:
            modified *= 1.1

        # Boost for patterns with manual confirmation
        if pattern_data.get("manually_confirmed", False):
            modified *= 1.2

        # Penalty for patterns with recent failures
        recent_failures = pattern_data.get("recent_failures", 0)
        if recent_failures > 0:
            modified *= 0.9**recent_failures

        # Context-specific modifiers
        if context.get("is_critical_operation", False):
            modified *= 0.8  # Be more conservative for critical operations

        if context.get("developer_experience", 0) > 0.8:
            modified *= 1.05  # Trust experienced developers more

        return modified

    def calculate_adaptation_confidence(
        self,
        rule_id: str,
        base_level: str,
        adapted_level: str,
        context: dict[str, Any],
        historical_data: dict[str, Any] | None = None,
    ) -> float:
        """Calculate confidence in a rule adaptation decision."""
        # Base confidence from level change magnitude
        level_map = {"INFORM": 1, "WARN": 2, "JUSTIFY": 3, "BLOCK": 4}
        base_val = level_map.get(base_level, 2)
        adapted_val = level_map.get(adapted_level, 2)

        change_magnitude = abs(adapted_val - base_val)

        # Lower confidence for larger changes
        magnitude_confidence = 1.0 - (change_magnitude * 0.2)

        # Factor in context clarity
        context_confidence = 0.5  # Default

        if context.get("user_intent") and context["user_intent"] != "unknown":
            context_confidence += 0.2

        if context.get("workflow_phase") in ["research", "planning", "implementing"]:
            context_confidence += 0.1

        if context.get("file_path"):
            context_confidence += 0.1

        # Historical success rate
        historical_confidence = 0.5  # Default

        if historical_data:
            success_rate = historical_data.get("adaptation_success_rate", 0.5)
            historical_confidence = success_rate

        # Combine factors
        total_confidence = magnitude_confidence * 0.4 + context_confidence * 0.3 + historical_confidence * 0.3

        return max(0.1, min(0.95, total_confidence))

    def get_confidence_explanation(self, confidence: float) -> str:
        """Get human-readable explanation of confidence level."""
        if confidence >= 0.9:
            return "Very high confidence - pattern well-established"
        elif confidence >= 0.75:
            return "High confidence - pattern consistently observed"
        elif confidence >= 0.6:
            return "Moderate confidence - pattern emerging"
        elif confidence >= 0.4:
            return "Low confidence - pattern tentative"
        else:
            return "Very low confidence - insufficient data"
