#!/usr/bin/env python3
"""Load active specifications into session context at startup.

This hook injects the full content of active specifications into Claude's
context at session start, ensuring important project context survives
chat compaction and is immediately available in new sessions.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.core.specifications import Specification, SpecificationManager, SpecStatus


class SessionContextLoaderHook(BaseHook):
    """Inject active specifications as context at session start."""

    def __init__(self):
        super().__init__("session_context_loader")
        self.start_time = time.time()
        self.project_root = get_project_root()
        self.spec_manager = SpecificationManager(self.project_root)
        self.performance_target_ms = 50  # Target: <50ms

    def execute(self):
        """Load and inject active specifications into session context."""
        start_time = time.time()

        # Support both SessionStart and PostCompact events
        event_name = self.input_data.get("hook_event_name", "")
        if event_name not in ["SessionStart", "PostCompact"]:
            self.output_success(f"Not a session event: {event_name}")
            return

        # Track source for context customization
        source = self.input_data.get("source", "startup")  # startup, resume, compact

        try:
            # Generate context with event awareness
            context = self.generate_specification_context(event_name, source)

            # Performance tracking
            execution_time = (time.time() - start_time) * 1000
            if execution_time > self.performance_target_ms:
                self.logger.warning(
                    f"Performance target missed: {execution_time:.1f}ms > {self.performance_target_ms}ms"
                )

            # Output as additional context for session
            output = {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                    "metadata": {
                        "execution_time_ms": execution_time,
                        "performance_target_met": execution_time <= self.performance_target_ms,
                    },
                }
            }

            self.output_json(output, exit_code=0)

        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}")
            self.output_error(f"Session context loader failed: {str(e)}")

    def generate_specification_context(self, event_name: str, source: str) -> str:
        """Generate context containing full active specifications."""
        try:
            context_parts = []

            # Add consistent header for all sessions
            context_parts.append("<!-- QUAESTOR SESSION CONTEXT -->")

            # Header similar to CLAUDE.md
            context_parts.extend(
                [
                    "",
                    "<!-- QUAESTOR ACTIVE SPECIFICATIONS -->",
                    "> [!IMPORTANT]",
                    "> **Active Specifications**: The following specifications are currently being worked on.",
                    "> These define the current implementation tasks and acceptance criteria.",
                    "",
                ]
            )
            # Get active specifications
            active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)

            if active_specs:
                context_parts.append(f"## 📋 Active Specifications ({len(active_specs)})")
                context_parts.append("")

                # Load and inject each active specification with enhanced formatting
                for i, spec in enumerate(active_specs, 1):
                    spec_content = self._format_specification(spec, i)
                    context_parts.extend(spec_content)

                    # Add collapsible Markdown content
                    spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec.id}.md"
                    if spec_path.exists():
                        context_parts.extend(
                            ["<details>", "<summary>View Full Specification</summary>", "", "```markdown"]
                        )
                        with open(spec_path) as f:
                            context_parts.append(f.read().strip())
                        context_parts.extend(["```", "</details>", "", "---", ""])
            else:
                context_parts.extend(
                    [
                        "## 📋 No Active Specifications",
                        "",
                        "No specifications are currently active. Use `/plan` to create new specifications.",
                        "",
                    ]
                )

            # Git context functionality removed for simplicity

            context_parts.append("<!-- END QUAESTOR CONTEXT -->")

            return "\n".join(context_parts)

        except Exception as e:
            self.logger.error(f"Failed to generate context: {e}")
            return self._generate_fallback_context(str(e))

    def _format_specification(self, spec: Specification, index: int) -> list[str]:
        """Format specification with detailed progress breakdown."""
        content = []

        # Calculate detailed progress
        criteria_completed = sum(1 for c in spec.acceptance_criteria if "✓" in c or "completed" in c.lower())
        criteria_total = len(spec.acceptance_criteria)
        progress = (criteria_completed / criteria_total * 100) if criteria_total > 0 else 0

        # Simple progress display as percentage text

        content.extend(
            [
                f"### 📋 Specification {index}: {spec.title}",
                f"**ID**: {spec.id}",
                f"**Progress**: {progress:.0%}",
                f"├─ Criteria: {criteria_completed}/{criteria_total} completed",
                f"├─ Status: {spec.status.value}",
                f"├─ Priority: {spec.priority.value}",
                f"└─ Branch: {spec.branch or 'Not set'}",
                "",
            ]
        )

        # Add reminder about automatic tracking
        if progress < 1.0:
            content.extend(
                [
                    "<!-- AUTOMATIC TRACKING REMINDER -->",
                    "💡 **Progress tracks automatically**: Complete TODOs to update acceptance criteria",
                    "<!-- END REMINDER -->",
                    "",
                ]
            )

        # Show acceptance criteria with visual status
        if spec.acceptance_criteria:
            content.append("**Acceptance Criteria:**")
            for i, criterion in enumerate(spec.acceptance_criteria, 1):
                # Check if criterion is completed
                if "✓" in criterion or "completed" in criterion.lower():
                    content.append(f"  {i}. [x] ~~{criterion}~~")
                else:
                    content.append(f"  {i}. [ ] {criterion}")
            content.append("")

        # Test status summary if available
        if hasattr(spec, "test_scenarios") and spec.test_scenarios:
            passed = sum(1 for t in spec.test_scenarios if getattr(t, "passed", False))
            total = len(spec.test_scenarios)
            content.append(f"**Test Status**: {passed}/{total} passing")
            content.append("")

        # Show next actionable items if not complete
        if progress < 1.0:
            next_items = self._get_next_actionable_items(spec)
            if next_items:
                content.append("**🎯 Next Steps:**")
                for item in next_items[:3]:  # Show top 3
                    content.append(f"  → {item}")
                content.append("")

        return content

    def _get_next_actionable_items(self, spec: Specification) -> list[str]:
        """Get next actionable items for the specification."""
        next_items = []

        # Find uncompleted acceptance criteria
        for criterion in spec.acceptance_criteria:
            if "✓" not in criterion and "completed" not in criterion.lower():
                # Clean up the criterion text
                clean_criterion = criterion.replace("[ ]", "").strip()
                next_items.append(clean_criterion)

        # Add test-related items if criteria are mostly done
        if hasattr(spec, "test_scenarios") and spec.test_scenarios:
            failed_tests = [t for t in spec.test_scenarios if not getattr(t, "passed", False)]
            if failed_tests and len(next_items) < 3:
                next_items.append(f"Fix failing tests ({len(failed_tests)} remaining)")

        # Add generic items if needed
        if not next_items:
            if spec.status.value == "ACTIVE":
                next_items.append("Review implementation against spec")
                next_items.append("Run tests and verify functionality")

        return next_items

    def _generate_fallback_context(self, error: str) -> str:
        """Generate minimal fallback context on error."""
        return f"""<!-- QUAESTOR SESSION CONTEXT (FALLBACK MODE) -->
<!-- Error: {error} -->

## ⚠️ Context Loading Error

Could not load active specifications. Operating in fallback mode.

**Error**: {error}

**Quick Actions**:
- Check specs directory: `.quaestor/specs/active/`
- Use `/plan` to create new specifications
- Review existing specs: `/plan --list`

<!-- END FALLBACK CONTEXT -->"""


def main():
    """Main hook entry point."""
    hook = SessionContextLoaderHook()
    hook.run()


if __name__ == "__main__":
    main()
