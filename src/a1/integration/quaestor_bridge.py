"""Bridge between Quaestor's enforcement and A1's intelligent rules."""

from collections.abc import Callable
from typing import Any

from quaestor.automation import HookResult

from ..enforcement import EnforcementContext, EnforcementLevel, RuleEnforcer
from ..enforcement.enforcement_history import EnforcementHistory
from ..enforcement.override_system import OverrideSystem
from ..hooks.context_builder import ContextBuilder


class QuaestorRuleBridge:
    """Bridge Quaestor's HookResult with A1's enforcement system."""

    def __init__(self):
        self.history = EnforcementHistory()
        self.override_system = OverrideSystem()
        self.context_builder = ContextBuilder(None)  # Will be set per call

    def convert_hook_result(self, rule_enforcer: RuleEnforcer, context: dict[str, Any]) -> HookResult:
        """Convert A1 enforcement result to Quaestor HookResult."""
        # Build enforcement context
        enforcement_context = self._build_context_from_dict(context)

        # Check for overrides
        override = self.override_system.check_override(rule_enforcer.rule_id, context)

        if override:
            return HookResult(success=True, message=f"ℹ️  Override active: {override.justification}")

        # Run enforcement
        result = rule_enforcer.enforce(enforcement_context)

        # Map to HookResult
        if result.level <= EnforcementLevel.WARN:
            # Allow with message
            return HookResult(success=True, message=result.message)
        else:
            # Block with message
            message = result.message
            if result.suggestions:
                message += "\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in result.suggestions)

            return HookResult(success=False, message=message)

    def _build_context_from_dict(self, data: dict[str, Any]) -> EnforcementContext:
        """Build enforcement context from dictionary."""
        return EnforcementContext(
            user_intent=data.get("intent", "unknown"),
            workflow_phase=data.get("phase", "unknown"),
            file_path=data.get("file_path"),
            tool_name=data.get("tool"),
            developer_experience=data.get("developer_experience", 0.5),
            time_pressure=data.get("time_pressure", 0.5),
            previous_violations=data.get("violations", 0),
            metadata=data,
        )

    def create_adaptive_enforcer(
        self,
        base_check: Callable[[Any], HookResult],
        rule_id: str,
        rule_name: str,
        base_level: EnforcementLevel = EnforcementLevel.WARN,
    ) -> RuleEnforcer:
        """Create an adaptive rule enforcer from a Quaestor check function."""

        class AdaptiveRule(RuleEnforcer):
            def __init__(self):
                super().__init__(rule_id, rule_name, base_level)
                self.base_check = base_check

            def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
                # Run the original check
                result = self.base_check(context.metadata)

                # Extract pass/fail and message
                if hasattr(result, "success"):
                    return result.success, result.message
                else:
                    # Assume boolean return
                    return result, "Check passed" if result else "Check failed"

            def get_suggestions(self, context: EnforcementContext) -> list[str]:
                # Default suggestions - can be enhanced
                suggestions = []

                if context.workflow_phase == "implementing":
                    suggestions.append("Complete research phase first")
                    suggestions.append("Review existing patterns in the codebase")

                if context.tool_name in ["Write", "Edit"]:
                    suggestions.append("Consider breaking changes into smaller commits")
                    suggestions.append("Write tests for new functionality")

                return suggestions

        return AdaptiveRule()


def wrap_quaestor_hook(
    hook_function: Callable, rule_id: str, rule_name: str, base_level: EnforcementLevel = EnforcementLevel.WARN
) -> Callable:
    """Decorator to add A1 intelligence to existing Quaestor hooks."""
    bridge = QuaestorRuleBridge()

    def wrapped_hook(context: dict[str, Any]) -> HookResult:
        # Create adaptive enforcer
        enforcer = bridge.create_adaptive_enforcer(hook_function, rule_id, rule_name, base_level)

        # Convert and return
        return bridge.convert_hook_result(enforcer, context)

    return wrapped_hook
