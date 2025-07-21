"""Rule adaptation system for context-aware enforcement."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .enforcement_levels import EnforcementLevel
from .rule_enforcer import EnforcementContext


class AdaptationStrategy(Enum):
    """Adaptation strategies based on intent."""

    RESEARCH = "research"
    TESTING = "testing"
    IMPLEMENTATION = "implementation"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    HOTFIX = "hotfix"
    EXPERIMENTATION = "experimentation"


@dataclass
class AdaptationFactors:
    """Factors that influence rule adaptation."""

    intent_weight: float = 0.3
    experience_weight: float = 0.3
    pressure_weight: float = 0.2
    phase_weight: float = 0.2

    def validate(self) -> None:
        """Ensure weights sum to 1.0."""
        total = self.intent_weight + self.experience_weight + self.pressure_weight + self.phase_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Adaptation weights must sum to 1.0, got {total}")


class RuleAdapter:
    """Adapts rule enforcement based on context."""

    def __init__(self, factors: AdaptationFactors | None = None):
        self.factors = factors or AdaptationFactors()
        self.factors.validate()

        # Define adaptation strategies
        self.strategies = self._init_strategies()

    def _init_strategies(self) -> dict[AdaptationStrategy, dict[str, Any]]:
        """Initialize adaptation strategies for different intents."""
        return {
            AdaptationStrategy.RESEARCH: {
                "level_adjustment": -1,  # More lenient
                "suggestions": [
                    "Take time to explore the codebase",
                    "Use grep and read tools extensively",
                    "Document your findings",
                ],
                "allow_shortcuts": True,
            },
            AdaptationStrategy.TESTING: {
                "level_adjustment": -1,  # More lenient for test files
                "suggestions": ["Focus on test coverage", "Consider edge cases", "Use test-driven development"],
                "allow_shortcuts": True,
            },
            AdaptationStrategy.IMPLEMENTATION: {
                "level_adjustment": 0,  # Standard enforcement
                "suggestions": ["Follow established patterns", "Write tests alongside code", "Keep functions focused"],
                "allow_shortcuts": False,
            },
            AdaptationStrategy.DOCUMENTATION: {
                "level_adjustment": -2,  # Very lenient
                "suggestions": [
                    "Keep documentation clear and concise",
                    "Update examples if needed",
                    "Consider the audience",
                ],
                "allow_shortcuts": True,
            },
            AdaptationStrategy.REFACTORING: {
                "level_adjustment": 1,  # Stricter
                "suggestions": [
                    "Ensure tests pass before and after",
                    "Make incremental changes",
                    "Preserve existing behavior",
                ],
                "allow_shortcuts": False,
            },
            AdaptationStrategy.HOTFIX: {
                "level_adjustment": -1,  # More lenient due to urgency
                "suggestions": [
                    "Focus on fixing the immediate issue",
                    "Add tests for the bug",
                    "Plan proper fix for later",
                ],
                "allow_shortcuts": True,
            },
            AdaptationStrategy.EXPERIMENTATION: {
                "level_adjustment": -2,  # Very lenient
                "suggestions": ["Try different approaches", "Document what works", "Clean up before committing"],
                "allow_shortcuts": True,
            },
        }

    def detect_strategy(self, context: EnforcementContext) -> AdaptationStrategy:
        """Detect the appropriate adaptation strategy from context."""
        intent = context.user_intent.lower()
        file_path = (context.file_path or "").lower()

        # Intent-based detection
        if "test" in intent or "test" in file_path:
            return AdaptationStrategy.TESTING
        elif "doc" in intent or "readme" in file_path:
            return AdaptationStrategy.DOCUMENTATION
        elif "refactor" in intent or "clean" in intent:
            return AdaptationStrategy.REFACTORING
        elif "fix" in intent or "hotfix" in intent or "urgent" in intent:
            return AdaptationStrategy.HOTFIX
        elif "experiment" in intent or "try" in intent:
            return AdaptationStrategy.EXPERIMENTATION
        elif context.workflow_phase == "research":
            return AdaptationStrategy.RESEARCH
        else:
            return AdaptationStrategy.IMPLEMENTATION

    def adapt_enforcement_level(self, base_level: EnforcementLevel, context: EnforcementContext) -> EnforcementLevel:
        """Adapt enforcement level based on context."""
        # Start with base level
        level_value = base_level.value

        # Apply strategy adjustment (don't dilute with weight for major adjustments)
        strategy = self.detect_strategy(context)
        strategy_config = self.strategies[strategy]
        level_value += strategy_config["level_adjustment"]

        # Apply experience adjustment
        if context.developer_experience > 0.8:
            level_value -= 0.5 * self.factors.experience_weight
        elif context.developer_experience < 0.3:
            level_value += 0.5 * self.factors.experience_weight

        # Apply time pressure adjustment
        if context.time_pressure > 0.8:
            level_value -= 1.0 * self.factors.pressure_weight
        elif context.time_pressure < 0.2:
            level_value += 0.5 * self.factors.pressure_weight

        # Apply workflow phase adjustment
        if context.workflow_phase == "research":
            level_value -= 0.5 * self.factors.phase_weight
        elif context.workflow_phase == "implementing":
            level_value += 0.5 * self.factors.phase_weight

        # Clamp to valid range
        level_value = max(1, min(4, round(level_value)))

        # Convert back to enum
        for level in EnforcementLevel:
            if level.value == level_value:
                return level

        return base_level  # Fallback

    def get_adapted_suggestions(self, base_suggestions: list[str], context: EnforcementContext) -> list[str]:
        """Get context-adapted suggestions."""
        strategy = self.detect_strategy(context)
        strategy_config = self.strategies[strategy]

        # Combine base and strategy suggestions
        suggestions = list(base_suggestions)
        suggestions.extend(strategy_config["suggestions"])

        # Add context-specific suggestions
        if context.developer_experience < 0.3:
            suggestions.append("Consider pairing with a more experienced developer")

        if context.time_pressure > 0.8:
            suggestions.append("Focus on critical path; plan cleanup for later")

        if context.previous_violations > 3:
            suggestions.append("Review the rule documentation for clarity")

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions[:5]  # Return top 5

    def should_allow_shortcut(self, context: EnforcementContext) -> bool:
        """Determine if shortcuts should be allowed in this context."""
        strategy = self.detect_strategy(context)
        strategy_config = self.strategies[strategy]

        # Check strategy allows shortcuts
        if not strategy_config.get("allow_shortcuts", False):
            return False

        # Additional checks
        if context.previous_violations > 5:
            return False  # Too many violations

        if context.developer_experience < 0.2:
            return False  # Too inexperienced

        return True

    def calculate_confidence_score(self, context: EnforcementContext) -> float:
        """Calculate confidence in the adaptation decision."""
        confidence = 1.0

        # Reduce confidence for ambiguous contexts
        if context.user_intent == "unknown":
            confidence *= 0.7

        # Reduce confidence for extreme adaptations
        strategy = self.detect_strategy(context)
        adjustment = abs(self.strategies[strategy]["level_adjustment"])
        if adjustment > 1:
            confidence *= 1.0 - adjustment * 0.1

        # Increase confidence with more data
        if context.metadata.get("files_examined", 0) > 5:
            confidence *= 1.1

        return min(1.0, confidence)
