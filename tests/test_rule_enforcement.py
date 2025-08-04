"""Tests for rule enforcement system."""

import tempfile
from pathlib import Path

import pytest

from quaestor.core.rule_enforcer import (
    Rule,
    RuleEnforcer,
    RulePriority,
    RuleType,
    RuleViolation,
)


class TestRuleEnforcer:
    """Test rule enforcement functionality."""

    def test_rule_matching_vague_request(self):
        """Test that vague requests trigger clarification rules."""
        rule = Rule(
            id="clarification_needed",
            type=RuleType.CLARIFICATION,
            priority=RulePriority.CRITICAL,
            description="Need clarification on vague requests",
            check_condition="Request is vague",
            violation_response="I need clarification on the specific requirements.",
            circuit_breaker=True,
        )

        # Vague request should match
        context = {"user_request": "implement user auth somehow"}
        assert rule.matches(context) is True

        # Clear request should not match
        context = {"user_request": "implement JWT authentication with 24h expiry"}
        assert rule.matches(context) is False

    def test_workflow_violation_detection(self):
        """Test detection of workflow violations."""
        rule = Rule(
            id="workflow_compliance",
            type=RuleType.WORKFLOW,
            priority=RulePriority.CRITICAL,
            description="Follow Research → Plan → Implement",
            check_condition="Implementation without research",
            violation_response="Let me research first before implementing.",
            circuit_breaker=True,
        )

        # Implementation request without proper phase
        context = {"user_request": "implement the feature", "request_type": "implementation", "workflow_phase": "idle"}
        assert rule.matches(context) is True

        # Implementation in correct phase
        context["workflow_phase"] = "implementing"
        assert rule.matches(context) is False

    def test_rule_priority_ordering(self):
        """Test that rules are ordered by priority."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            quaestor_dir = project_root / ".quaestor"
            quaestor_dir.mkdir()

            # Create minimal CONTEXT.md
            rules_content = """# CRITICAL RULES
```yaml
before_any_action:
  mandatory_checks:
    - id: "workflow_compliance"
      check: "Follow workflow"
      on_violation: "STOP"
    - id: "clarification_needed"
      check: "Need clarity"
      on_violation: "ASK"
```"""
            (quaestor_dir / "CONTEXT.md").write_text(rules_content)

            enforcer = RuleEnforcer(project_root)

            # Should have loaded and sorted rules
            assert len(enforcer.rules) >= 2
            # All loaded rules should be CRITICAL priority
            for rule in enforcer.rules:
                if rule.id in ["workflow_compliance", "clarification_needed"]:
                    assert rule.priority == RulePriority.CRITICAL

    def test_circuit_breaker_stops_checking(self):
        """Test that circuit breakers stop further rule checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            quaestor_dir = project_root / ".quaestor"
            quaestor_dir.mkdir()

            enforcer = RuleEnforcer(project_root)

            # Manually add rules for testing
            enforcer.rules = [
                Rule(
                    id="circuit_breaker",
                    type=RuleType.CLARIFICATION,
                    priority=RulePriority.CRITICAL,
                    description="Circuit breaker rule",
                    check_condition="Always matches",
                    violation_response="STOP HERE",
                    circuit_breaker=True,
                ),
                Rule(
                    id="never_reached",
                    type=RuleType.QUALITY,
                    priority=RulePriority.CRITICAL,
                    description="Should not be reached",
                    check_condition="Also matches",
                    violation_response="SHOULD NOT SEE THIS",
                    circuit_breaker=False,
                ),
            ]

            # Override matches to always return True for testing
            for rule in enforcer.rules:
                rule.matches = lambda ctx: True

            context = {"user_request": "test"}
            violations = enforcer.check_violations(context)

            # Should only have one violation due to circuit breaker
            assert len(violations) == 1
            assert violations[0].rule.id == "circuit_breaker"

    def test_enforcement_response_blocking(self):
        """Test that blocking violations prevent proceeding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            enforcer = RuleEnforcer(project_root)

            # Create a blocking violation
            violation = RuleViolation(
                rule=Rule(
                    id="blocker",
                    type=RuleType.SAFETY,
                    priority=RulePriority.CRITICAL,
                    description="Blocking rule",
                    check_condition="Block",
                    violation_response="You must stop",
                    circuit_breaker=True,
                ),
                context={},
                severity=RulePriority.CRITICAL,
                required_response="You must stop",
                blocking=True,
            )

            response = enforcer.get_enforcement_response([violation])

            assert response["should_proceed"] is False
            assert response["required_response"] == "You must stop"
            assert "blocker" in response["violations"]

    def test_mode_specific_rules(self):
        """Test that drive mode only enforces circuit breakers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            enforcer = RuleEnforcer(project_root)

            # Add various rules
            enforcer.rules = [
                Rule(
                    id="circuit_breaker",
                    type=RuleType.SAFETY,
                    priority=RulePriority.CRITICAL,
                    description="Safety rule",
                    check_condition="Safety",
                    violation_response="STOP",
                    circuit_breaker=True,
                ),
                Rule(
                    id="workflow_rule",
                    type=RuleType.WORKFLOW,
                    priority=RulePriority.CRITICAL,
                    description="Workflow rule",
                    check_condition="Workflow",
                    violation_response="Follow workflow",
                    circuit_breaker=False,
                ),
                Rule(
                    id="quality_rule",
                    type=RuleType.QUALITY,
                    priority=RulePriority.IMPORTANT,
                    description="Quality rule",
                    check_condition="Quality",
                    violation_response="Improve quality",
                    circuit_breaker=False,
                ),
            ]

            # Drive mode rules
            drive_rules = enforcer.get_rules_for_mode("drive")
            assert len(drive_rules) == 1
            assert drive_rules[0].id == "circuit_breaker"

            # Framework mode rules (all rules)
            framework_rules = enforcer.get_rules_for_mode("framework")
            assert len(framework_rules) == 3

    def test_vague_indicator_detection(self):
        """Test detection of vague language indicators."""
        rule = Rule(
            id="vague_check",
            type=RuleType.CLARIFICATION,
            priority=RulePriority.CRITICAL,
            description="Check vagueness",
            check_condition="Vague",
            violation_response="Clarify",
            circuit_breaker=True,
        )

        vague_requests = [
            "do it somehow",
            "probably implement auth",
            "maybe add that feature",
            "just figure it out",
            "whatever works best",
        ]

        clear_requests = [
            "implement JWT authentication",
            "add user profile endpoint",
            "create login form with email validation",
        ]

        for request in vague_requests:
            context = {"user_request": request}
            assert rule.matches(context) is True, f"Should match vague: {request}"

        for request in clear_requests:
            context = {"user_request": request}
            assert rule.matches(context) is False, f"Should not match clear: {request}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
