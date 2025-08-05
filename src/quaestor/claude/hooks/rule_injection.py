#!/usr/bin/env python3
"""Hook for injecting enforcement rules into Claude's context.

This hook ensures that critical rules are prominently displayed in Claude's
context to increase compliance with template requirements.
"""

import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.core.rule_enforcer import RuleEnforcer, RulePriority


class RuleInjectionHook(BaseHook):
    """Hook for injecting rules into context."""

    def __init__(self):
        super().__init__("rule_injection")
        self.project_root = get_project_root()
        self.rule_enforcer = RuleEnforcer(self.project_root)

    def execute(self):
        """Execute rule injection logic."""
        # Get event details
        event_name = self.input_data.get("hook_event_name", "")

        # This hook can run on multiple events
        if event_name not in ["SessionStart", "UserPromptSubmit"]:
            self.output_success()
            return

        # Generate rule injection context
        context = self._generate_rule_context()

        # For SessionStart, inject into additional context
        if event_name == "SessionStart":
            output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
            self.output_json(output, exit_code=0)
        else:
            # For UserPromptSubmit, provide guidance
            self.output_success(context)

    def _generate_rule_context(self) -> str:
        """Generate context with injected rules."""
        lines = []

        # Header - VERY prominent
        lines.extend(["=" * 50, "🛑 MANDATORY BEHAVIORAL RULES - OVERRIDE ALL ELSE 🛑", "=" * 50, ""])

        # Critical circuit breakers
        circuit_breakers = self.rule_enforcer.get_circuit_breakers()
        if circuit_breakers:
            lines.append("⚡ CIRCUIT BREAKERS (IMMEDIATE STOP CONDITIONS):")
            for rule in circuit_breakers:
                lines.append(f"  • {rule.description}")
                lines.append(f"    → RESPONSE: {rule.violation_response}")
            lines.append("")

        # Workflow enforcement
        lines.extend(
            [
                "🚦 WORKFLOW ENFORCEMENT:",
                "  • Never jump straight to implementation",
                "    → RESPONSE: Use the workflow-coordinator agent to manage Research → Plan → Implement",
                "",
            ]
        )

        # Critical rules
        critical_rules = self.rule_enforcer.get_rules_by_priority(RulePriority.CRITICAL)
        if critical_rules:
            lines.append("🔴 CRITICAL RULES (MUST FOLLOW):")
            for rule in critical_rules[:5]:  # Top 5 to avoid context bloat
                lines.append(f"  • {rule.description}")
                if rule.triggers:
                    lines.append(f"    Triggers: {', '.join(rule.triggers)}")
            lines.append("")

        # General reminders (mode detection removed)
        lines.extend(
            [
                "📋 WORKFLOW REMINDER:",
                "  • Use Quaestor commands (/research, /plan, /impl) for structured workflow",
                "  • Commands automatically enforce Research → Plan → Implement sequence",
                "  • Direct edits allowed outside of commands",
                "",
            ]
        )

        # Quick reference
        lines.extend(
            [
                "🎯 QUICK CHECKS BEFORE ANY ACTION:",
                "  □ Is the request clear and specific?",
                "  □ Have I researched if this is code-related?",
                "  □ Am I following the required workflow?",
                "  □ Do I need to ask for clarification?",
                "",
            ]
        )

        # Footer
        lines.append("=" * 50)

        return "\n".join(lines)

    def _check_request_context(self) -> dict[str, Any]:
        """Analyze the current request context."""
        user_prompt = self.input_data.get("user_prompt", "")

        # Detect request type
        implementation_keywords = [
            "implement",
            "create",
            "build",
            "add",
            "write",
            "code",
            "develop",
            "make",
            "fix",
            "update",
        ]

        research_keywords = ["research", "analyze", "understand", "explore", "investigate", "find", "look", "check"]

        request_type = "unknown"
        if any(kw in user_prompt.lower() for kw in implementation_keywords):
            request_type = "implementation"
        elif any(kw in user_prompt.lower() for kw in research_keywords):
            request_type = "research"

        # Estimate complexity
        complexity_indicators = [
            ("system", 0.3),
            ("architecture", 0.3),
            ("refactor", 0.4),
            ("multiple", 0.2),
            ("entire", 0.3),
            ("framework", 0.3),
        ]

        complexity_score = 0.0
        for indicator, weight in complexity_indicators:
            if indicator in user_prompt.lower():
                complexity_score += weight

        complexity_score = min(complexity_score, 1.0)

        return {
            "user_request": user_prompt,
            "request_type": request_type,
            "complexity_score": complexity_score,
            "workflow_phase": "idle",  # Mode detection removed
            "mode": "drive",  # Always in drive mode now
        }

    def _get_workflow_phase(self) -> str:
        """Get current workflow phase from state."""
        # Mode detection removed - workflow managed by agents
        return "idle"


def main():
    """Main hook entry point."""
    hook = RuleInjectionHook()
    hook.run()


if __name__ == "__main__":
    main()
