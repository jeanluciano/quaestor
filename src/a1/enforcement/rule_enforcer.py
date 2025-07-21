"""Base rule enforcer implementation with graduated enforcement."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .enforcement_history import EnforcementEvent, EnforcementHistory
from .enforcement_levels import EnforcementConfig, EnforcementLevel


@dataclass
class EnforcementContext:
    """Context information for rule enforcement."""

    user_intent: str
    workflow_phase: str  # research, planning, implementing
    file_path: str | None = None
    tool_name: str | None = None
    developer_experience: float = 0.5  # 0-1 scale
    time_pressure: float = 0.5  # 0-1 scale
    previous_violations: int = 0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EnforcementResult:
    """Result of rule enforcement check."""

    allowed: bool
    level: EnforcementLevel
    message: str
    rule_id: str
    justification_required: bool = False
    override_allowed: bool = True
    suggestions: list[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class RuleEnforcer(ABC):
    """Base class for rule enforcement with graduated levels."""

    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        base_level: EnforcementLevel = EnforcementLevel.WARN,
        history: EnforcementHistory | None = None,
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.base_level = base_level
        self.history = history or EnforcementHistory()
        self._override_cache: dict[str, float] = {}  # Cache overrides with timestamps

    @abstractmethod
    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check if rule is satisfied. Returns (passed, message)."""
        pass

    @abstractmethod
    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get suggestions for fixing the rule violation."""
        pass

    def enforce(self, context: EnforcementContext) -> EnforcementResult:
        """Enforce the rule with appropriate level based on context."""
        # Check the rule
        passed, message = self.check_rule(context)

        if passed:
            return EnforcementResult(
                allowed=True,
                level=EnforcementLevel.INFORM,
                message=f"✅ {self.rule_name}: Rule satisfied",
                rule_id=self.rule_id,
            )

        # Determine enforcement level based on context
        level = self._determine_enforcement_level(context)
        config = EnforcementConfig.for_level(level)

        # Get suggestions
        suggestions = self.get_suggestions(context)

        # Format message
        formatted_message = config.message_template.format(rule_name=self.rule_name, message=message)

        # Create result
        result = EnforcementResult(
            allowed=level.allows_continuation,
            level=level,
            message=formatted_message,
            rule_id=self.rule_id,
            justification_required=config.require_justification,
            override_allowed=config.allow_override,
            suggestions=suggestions,
        )

        # Log to history if configured
        if config.log_to_history:
            event = EnforcementEvent(
                id=str(uuid4()),
                timestamp=time.time(),
                rule_id=self.rule_id,
                level=level,
                context=context,
                result=result,
                message=message,
            )
            self.history.add_event(event)

        return result

    def _determine_enforcement_level(self, context: EnforcementContext) -> EnforcementLevel:
        """Determine appropriate enforcement level based on context."""
        level = self.base_level

        # Adapt based on workflow phase
        if context.workflow_phase == "research":
            # Be more lenient during research
            if level > EnforcementLevel.WARN:
                level = EnforcementLevel.WARN
        elif context.workflow_phase == "implementing":
            # Be stricter during implementation
            if level < EnforcementLevel.JUSTIFY and context.previous_violations > 2:
                level = EnforcementLevel.JUSTIFY

        # Adapt based on developer experience
        if context.developer_experience > 0.8:
            # More experienced developers get more flexibility
            if level > EnforcementLevel.WARN:
                level = EnforcementLevel.WARN
        elif context.developer_experience < 0.3:
            # Less experienced developers get more guidance
            if level < EnforcementLevel.JUSTIFY:
                level = EnforcementLevel.JUSTIFY

        # Adapt based on time pressure
        if context.time_pressure > 0.8:
            # High time pressure, be less strict
            if level > EnforcementLevel.WARN:
                level = EnforcementLevel.WARN

        # Check for recent overrides
        if self._has_recent_override(context):
            # If recently overridden, reduce level
            if level > EnforcementLevel.INFORM:
                level = EnforcementLevel.INFORM

        return level

    def _has_recent_override(self, context: EnforcementContext) -> bool:
        """Check if this rule was recently overridden in similar context."""
        # Simple implementation - can be enhanced
        cache_key = f"{context.user_intent}:{context.workflow_phase}"
        if cache_key in self._override_cache:
            # Check if override is less than 2 hours old
            override_time = self._override_cache[cache_key]
            return (time.time() - override_time) < 7200
        return False

    def record_override(self, context: EnforcementContext, justification: str) -> None:
        """Record that this rule was overridden."""
        cache_key = f"{context.user_intent}:{context.workflow_phase}"
        self._override_cache[cache_key] = time.time()

        # Also record in history
        event = EnforcementEvent(
            id=str(uuid4()),
            timestamp=time.time(),
            rule_id=self.rule_id,
            level=EnforcementLevel.BLOCK,  # Overrides are typically for blocks
            context=context,
            result=None,
            message=f"Override: {justification}",
            metadata={"override": True, "justification": justification},
        )
        self.history.add_event(event)
