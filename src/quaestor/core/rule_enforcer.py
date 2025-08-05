"""Simplified rule enforcement system for Claude hooks.

This module provides basic rule structures for the rule_injection hook
to enforce key behavioral patterns.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RulePriority(Enum):
    """Priority levels for rule enforcement."""

    CRITICAL = "critical"  # Must be enforced - hard stops
    IMPORTANT = "important"  # Should be enforced - strong warnings
    SUGGESTED = "suggested"  # Nice to follow - gentle reminders


class RuleType(Enum):
    """Types of enforcement rules."""

    WORKFLOW = "workflow"  # Process rules (e.g., Research → Plan → Implement)
    CLARIFICATION = "clarification"  # When to ask for more info
    COMPLEXITY = "complexity"  # Code complexity limits
    SAFETY = "safety"  # Safety boundaries
    QUALITY = "quality"  # Production quality standards
    COMPLIANCE = "compliance"  # Hook and specification compliance


@dataclass
class Rule:
    """Individual enforcement rule."""

    id: str
    type: RuleType
    priority: RulePriority
    description: str
    violation_response: str
    circuit_breaker: bool = False  # If True, this rule always stops execution
    triggers: list[str] | None = None


class RuleEnforcer:
    """Simplified rule enforcement engine that returns static rules."""

    def __init__(self, project_root: Path):
        """Initialize the rule enforcer.

        Args:
            project_root: Path to project root (kept for compatibility)
        """
        self.project_root = project_root
        self.rules = self._get_static_rules()

    def _get_static_rules(self) -> list[Rule]:
        """Return static list of core enforcement rules."""
        return [
            # Circuit breakers
            Rule(
                id="clarification_needed",
                type=RuleType.CLARIFICATION,
                priority=RulePriority.CRITICAL,
                description="Request is vague or ambiguous",
                violation_response="I need clarification on [specific aspect]",
                circuit_breaker=True,
                triggers=["vague", "unclear", "ambiguous"],
            ),
            Rule(
                id="workflow_compliance",
                type=RuleType.WORKFLOW,
                priority=RulePriority.CRITICAL,
                description="Never jump straight to implementation",
                violation_response="Let me research the codebase and create a plan before implementing.",
                circuit_breaker=True,
            ),
            # Standard rules
            Rule(
                id="production_quality",
                type=RuleType.QUALITY,
                priority=RulePriority.CRITICAL,
                description="All code must be production-ready",
                violation_response="Let me add proper error handling and validation.",
            ),
            Rule(
                id="specification_tracking",
                type=RuleType.COMPLIANCE,
                priority=RulePriority.IMPORTANT,
                description="Track work in specification system",
                violation_response="Let me check the current specification and declare which task I'm working on.",
            ),
            Rule(
                id="complexity_check",
                type=RuleType.COMPLEXITY,
                priority=RulePriority.IMPORTANT,
                description="Avoid overly complex implementations",
                violation_response="This seems complex. Let me step back and ask for guidance.",
            ),
        ]

    def get_circuit_breakers(self) -> list[Rule]:
        """Get all circuit breaker rules (hard stops)."""
        return [r for r in self.rules if r.circuit_breaker]

    def get_rules_by_priority(self, priority: RulePriority) -> list[Rule]:
        """Get all rules of a specific priority."""
        return [r for r in self.rules if r.priority == priority]

    def get_rules_for_mode(self, mode: str) -> list[Rule]:
        """Get rules applicable to a specific mode (framework/drive).

        In drive mode, only safety and critical circuit breakers apply.
        """
        if mode == "drive":
            return [r for r in self.rules if r.circuit_breaker or r.type == RuleType.SAFETY]
        return self.rules  # All rules apply in framework mode
