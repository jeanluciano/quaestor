"""Rule enforcement system for Claude template compliance.

This module parses and enforces rules from Quaestor templates to ensure
Claude follows project-specific requirements regardless of base training.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


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
    SAFETY = "safety"  # Safety boundaries (even in drive mode)
    QUALITY = "quality"  # Production quality standards
    COMPLIANCE = "compliance"  # Hook and specification compliance


@dataclass
class Rule:
    """Individual enforcement rule."""

    id: str
    type: RuleType
    priority: RulePriority
    description: str
    check_condition: str
    violation_response: str
    triggers: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)
    circuit_breaker: bool = False  # If True, this rule always stops execution

    def matches(self, context: dict[str, Any]) -> bool:
        """Check if this rule is triggered by the current context."""
        # Check for trigger keywords in user request
        if self.triggers:
            user_request = context.get("user_request", "").lower()
            for trigger in self.triggers:
                if trigger.lower() in user_request:
                    return True

        # Check for specific conditions
        if self.type == RuleType.WORKFLOW:
            return self._check_workflow_violation(context)
        elif self.type == RuleType.CLARIFICATION:
            return self._check_needs_clarification(context)
        elif self.type == RuleType.COMPLEXITY:
            return self._check_complexity_violation(context)

        return False

    def _check_workflow_violation(self, context: dict[str, Any]) -> bool:
        """Check for workflow violations like skipping research."""
        phase = context.get("workflow_phase", "idle")
        request_type = context.get("request_type", "")

        # Implementation request without research
        if request_type == "implementation" and phase != "implementing":
            return True

        return False

    def _check_needs_clarification(self, context: dict[str, Any]) -> bool:
        """Check if the request is too vague."""
        vague_indicators = [
            "somehow",
            "probably",
            "maybe",
            "figure it out",
            "just do it",
            "whatever works",
            "you decide",
        ]

        user_request = context.get("user_request", "").lower()
        return any(indicator in user_request for indicator in vague_indicators)

    def _check_complexity_violation(self, context: dict[str, Any]) -> bool:
        """Check for complexity threshold violations."""
        complexity_score = context.get("complexity_score", 0)
        return complexity_score > 0.7


@dataclass
class RuleViolation:
    """Details about a rule violation."""

    rule: Rule
    context: dict[str, Any]
    severity: RulePriority
    required_response: str
    blocking: bool = False


class RuleEnforcer:
    """Main rule enforcement engine."""

    def __init__(self, project_root: Path):
        """Initialize the rule enforcer.

        Args:
            project_root: Path to project root containing .quaestor/
        """
        self.project_root = project_root
        self.quaestor_dir = project_root / ".quaestor"
        self.rules: list[Rule] = []
        self._load_rules()

    def _load_rules(self):
        """Load rules from template files."""
        # Load from consolidated CONTEXT.md
        context_path = self.quaestor_dir / "CONTEXT.md"
        if context_path.exists():
            self._parse_rules(context_path)
            self._parse_quaestor_rules(context_path)

        # Sort rules by priority
        self.rules.sort(
            key=lambda r: (
                0 if r.priority == RulePriority.CRITICAL else 1 if r.priority == RulePriority.IMPORTANT else 2
            )
        )

    def _parse_rules(self, path: Path):
        """Parse rules from CONTEXT.md."""
        content = path.read_text()

        # Extract YAML blocks
        yaml_blocks = re.findall(r"```yaml\n(.*?)\n```", content, re.DOTALL)

        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)

                # Parse mandatory checks
                if "mandatory_checks" in data.get("before_any_action", {}):
                    for check in data["before_any_action"]["mandatory_checks"]:
                        rule = self._create_rule_from_check(check)
                        if rule:
                            self.rules.append(rule)

                # Parse circuit breakers
                if "circuit_breakers" in data:
                    for breaker in data["circuit_breakers"]:
                        rule = self._create_circuit_breaker(breaker)
                        if rule:
                            self.rules.append(rule)

            except yaml.YAMLError:
                continue

    def _create_rule_from_check(self, check_data: dict) -> Rule | None:
        """Create a Rule object from check data."""
        rule_id = check_data.get("id", "")
        if not rule_id:
            return None

        # Map rule IDs to types
        type_mapping = {
            "workflow_compliance": RuleType.WORKFLOW,
            "clarification_needed": RuleType.CLARIFICATION,
            "complexity_check": RuleType.COMPLEXITY,
            "production_quality": RuleType.QUALITY,
            "specification_tracking_compliance": RuleType.COMPLIANCE,
            "hook_compliance": RuleType.COMPLIANCE,
        }

        rule_type = type_mapping.get(rule_id, RuleType.COMPLIANCE)

        return Rule(
            id=rule_id,
            type=rule_type,
            priority=RulePriority.CRITICAL,  # All rules in RULES are critical
            description=check_data.get("check", ""),
            check_condition=check_data.get("check", ""),
            violation_response=check_data.get("on_violation", ""),
            triggers=check_data.get("triggers", []),
            required_actions=check_data.get("required_actions", []),
            circuit_breaker=rule_id in ["clarification_needed", "workflow_compliance"],
        )

    def _create_circuit_breaker(self, breaker_data: dict) -> Rule | None:
        """Create a circuit breaker rule from YAML data."""
        rule_id = breaker_data.get("id", "")
        if not rule_id:
            return None

        # Determine rule type based on ID
        if "vague" in rule_id or "clarification" in rule_id:
            rule_type = RuleType.CLARIFICATION
        elif "destructive" in rule_id:
            rule_type = RuleType.SAFETY
        else:
            rule_type = RuleType.SAFETY

        # Parse priority
        priority_str = breaker_data.get("priority", "critical").lower()
        priority = (
            RulePriority.CRITICAL
            if priority_str == "critical"
            else RulePriority.IMPORTANT
            if priority_str == "important"
            else RulePriority.SUGGESTED
        )

        return Rule(
            id=rule_id,
            type=rule_type,
            priority=priority,
            description=breaker_data.get("description", ""),
            check_condition=breaker_data.get("description", ""),
            violation_response=breaker_data.get("response", ""),
            triggers=breaker_data.get("triggers", []),
            circuit_breaker=True,  # All circuit breakers are hard stops
        )

    def _parse_quaestor_rules(self, path: Path):
        """Parse additional rules from CONTEXT.md."""
        content = path.read_text()

        # Look for specific enforcement patterns
        if "NEVER JUMP STRAIGHT TO CODING" in content:
            self.rules.append(
                Rule(
                    id="no_direct_coding",
                    type=RuleType.WORKFLOW,
                    priority=RulePriority.CRITICAL,
                    description="Never jump straight to implementation",
                    check_condition="Implementation requested without research",
                    violation_response="Let me research the codebase and create a plan before implementing.",
                    circuit_breaker=True,
                )
            )

        if "Stop and validate" in content:
            self.rules.append(
                Rule(
                    id="reality_checkpoint",
                    type=RuleType.QUALITY,
                    priority=RulePriority.IMPORTANT,
                    description="Regular validation checkpoints",
                    check_condition="After implementing a complete feature",
                    violation_response="Let me validate what we've built so far.",
                    circuit_breaker=False,
                )
            )

    def check_violations(self, context: dict[str, Any]) -> list[RuleViolation]:
        """Check for rule violations in the current context.

        Args:
            context: Current execution context including:
                - user_request: The user's request
                - workflow_phase: Current workflow phase
                - request_type: Type of request (implementation, research, etc.)
                - complexity_score: Estimated complexity (0-1)
                - mode: Current mode (framework/drive)

        Returns:
            List of rule violations found
        """
        violations = []

        for rule in self.rules:
            if rule.matches(context):
                violation = RuleViolation(
                    rule=rule,
                    context=context,
                    severity=rule.priority,
                    required_response=rule.violation_response,
                    blocking=rule.circuit_breaker or rule.priority == RulePriority.CRITICAL,
                )
                violations.append(violation)

                # Stop checking if we hit a circuit breaker
                if rule.circuit_breaker:
                    break

        return violations

    def get_enforcement_response(self, violations: list[RuleViolation]) -> dict[str, Any]:
        """Generate enforcement response for violations.

        Args:
            violations: List of rule violations

        Returns:
            Dictionary with:
                - should_proceed: Whether to continue with the request
                - required_response: What Claude must say
                - violations: List of violation details
        """
        if not violations:
            return {"should_proceed": True, "required_response": None, "violations": []}

        # Find the highest priority violation
        blocking_violation = next((v for v in violations if v.blocking), None)

        if blocking_violation:
            return {
                "should_proceed": False,
                "required_response": blocking_violation.required_response,
                "violations": [v.rule.id for v in violations],
            }

        # Non-blocking violations
        return {
            "should_proceed": True,
            "required_response": None,
            "violations": [v.rule.id for v in violations],
            "warnings": [v.required_response for v in violations],
        }

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
