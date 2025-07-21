"""Enforcement level definitions for graduated rule enforcement."""

from enum import Enum, auto
from typing import NamedTuple


class EnforcementLevel(Enum):
    """Graduated enforcement levels from least to most restrictive."""

    INFORM = auto()  # Log information, no action required
    WARN = auto()  # Show warning, allow continuation
    JUSTIFY = auto()  # Require justification to proceed
    BLOCK = auto()  # Block action unless override provided

    def __lt__(self, other: "EnforcementLevel") -> bool:
        """Allow comparison of enforcement levels."""
        if not isinstance(other, EnforcementLevel):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: "EnforcementLevel") -> bool:
        """Allow comparison of enforcement levels."""
        if not isinstance(other, EnforcementLevel):
            return NotImplemented
        return self.value <= other.value

    @property
    def requires_action(self) -> bool:
        """Check if this level requires user action."""
        return self in (EnforcementLevel.JUSTIFY, EnforcementLevel.BLOCK)

    @property
    def allows_continuation(self) -> bool:
        """Check if this level allows continuation without override."""
        return self in (EnforcementLevel.INFORM, EnforcementLevel.WARN)


class EnforcementConfig(NamedTuple):
    """Configuration for enforcement behavior."""

    level: EnforcementLevel
    message_template: str
    require_justification: bool = False
    allow_override: bool = True
    log_to_history: bool = True

    @classmethod
    def for_level(cls, level: EnforcementLevel) -> "EnforcementConfig":
        """Get default configuration for an enforcement level."""
        configs = {
            EnforcementLevel.INFORM: cls(
                level=level,
                message_template="ℹ️  {rule_name}: {message}",
                require_justification=False,
                allow_override=True,
                log_to_history=True,
            ),
            EnforcementLevel.WARN: cls(
                level=level,
                message_template="⚠️  {rule_name}: {message}",
                require_justification=False,
                allow_override=True,
                log_to_history=True,
            ),
            EnforcementLevel.JUSTIFY: cls(
                level=level,
                message_template="🔒 {rule_name}: {message}\n   Justification required to proceed.",
                require_justification=True,
                allow_override=True,
                log_to_history=True,
            ),
            EnforcementLevel.BLOCK: cls(
                level=level,
                message_template="❌ {rule_name}: {message}\n   Action blocked. Override required.",
                require_justification=True,
                allow_override=True,
                log_to_history=True,
            ),
        }
        return configs[level]
