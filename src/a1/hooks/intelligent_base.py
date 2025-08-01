"""Intelligent hook base class that bridges A1 rules with Quaestor hooks."""

import sys
from pathlib import Path
from typing import Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, WorkflowState, get_project_root

from ..enforcement import EnforcementContext, EnforcementLevel, RuleEnforcer
from ..enforcement.enforcement_history import EnforcementHistory
from ..enforcement.override_system import OverrideSystem
from .context_builder import ContextBuilder


class IntelligentHook(BaseHook):
    """Base class for hooks with intelligent rule enforcement."""

    def __init__(self, hook_name: str, rule_enforcer: RuleEnforcer | None = None):
        super().__init__(hook_name)
        self.project_root = get_project_root()
        self.workflow_state = WorkflowState(self.project_root)
        self.history = EnforcementHistory()
        self.override_system = OverrideSystem()
        self.context_builder = ContextBuilder(self.workflow_state)
        self.rule_enforcer = rule_enforcer

    def build_enforcement_context(self) -> EnforcementContext:
        """Build enforcement context from current state and input."""
        return self.context_builder.build(
            input_data=self.input_data, workflow_state=self.workflow_state, project_root=self.project_root
        )

    def handle_enforcement_result(self, result: Any) -> None:
        """Handle the enforcement result and map to Quaestor's output format."""
        # Check for override first
        if not result.allowed and result.override_allowed:
            context_dict = self.context_builder.to_dict(self.build_enforcement_context())
            override = self.override_system.check_override(result.rule_id, context_dict)

            if override:
                self.logger.info(f"Override found for rule {result.rule_id}: {override.justification}")
                self.output_success(
                    f"ℹ️  {result.rule_id}: Proceeding with override: {override.justification}",
                    data={"override_id": override.id},
                )
                return

        # Map enforcement levels to Quaestor responses
        if result.level == EnforcementLevel.INFORM:
            # Informational - always allow
            self.output_success(result.message, data={"level": "inform"})

        elif result.level == EnforcementLevel.WARN:
            # Warning - allow but show message
            self.output_success(result.message, data={"level": "warn", "suggestions": result.suggestions})

        elif result.level == EnforcementLevel.JUSTIFY:
            # Justification required - block with override option
            message = result.message
            if result.suggestions:
                message += "\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in result.suggestions)
            message += "\n\nTo override: Provide justification with --justify flag"

            self.output_error(message, blocking=True)

        elif result.level == EnforcementLevel.BLOCK:
            # Hard block - but still allow override with strong justification
            message = result.message
            if result.suggestions:
                message += "\n\nRequired actions:\n" + "\n".join(f"• {s}" for s in result.suggestions)

            if result.override_allowed:
                message += "\n\nTo override: Provide strong justification with --override flag"

            self.output_error(message, blocking=True)

    def check_for_override_request(self) -> str | None:
        """Check if user is requesting an override."""
        # Check for override flags in input
        if "--justify" in self.input_data.get("args", []):
            return self.input_data.get("justification", "User requested override")

        if "--override" in self.input_data.get("args", []):
            return self.input_data.get("justification", "Strong override requested")

        return None

    def execute(self):
        """Execute hook with intelligent enforcement."""
        if not self.rule_enforcer:
            # No rule enforcer, fall back to standard execution
            self.execute_hook_logic()
            return

        # Build enforcement context
        context = self.build_enforcement_context()

        # Check for override request
        justification = self.check_for_override_request()
        if justification:
            self.rule_enforcer.record_override(context, justification)
            self.override_system.request_override(
                self.rule_enforcer.rule_id,
                justification,
                self.context_builder.to_dict(context),
                duration_hours=4,  # 4 hour override window
            )
            self.output_success(
                f"✅ Override recorded for {self.rule_enforcer.rule_name}", data={"override_recorded": True}
            )
            return

        # Run enforcement
        result = self.rule_enforcer.enforce(context)

        # Handle result
        self.handle_enforcement_result(result)

        # If allowed, execute the actual hook logic
        if result.allowed:
            self.execute_hook_logic()

    def execute_hook_logic(self):
        """Override this method to implement actual hook logic."""
        self.output_success("Hook executed successfully")

    def get_enforcement_stats(self) -> dict[str, Any]:
        """Get enforcement statistics for this hook."""
        if not self.rule_enforcer:
            return {}

        return {
            "rule_id": self.rule_enforcer.rule_id,
            "rule_name": self.rule_enforcer.rule_name,
            "base_level": self.rule_enforcer.base_level.name,
            "history_stats": self.history.get_enforcement_stats(hours=24),
            "override_stats": self.override_system.get_override_stats(),
        }
