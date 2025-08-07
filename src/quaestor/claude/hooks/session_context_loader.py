#!/usr/bin/env python3
"""Load active specifications into session context at startup.

This hook injects the full content of active specifications into Claude's
context at session start, ensuring important project context survives
chat compaction and is immediately available in new sessions.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Any

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

            # Add event-specific header
            if source == "resume":
                context_parts.append("<!-- SESSION RESUMED AFTER COMPACTION -->")
            elif event_name == "PostCompact":
                context_parts.append("<!-- POST-COMPACTION CONTEXT RELOAD -->")
            else:
                context_parts.append("<!-- NEW SESSION -->")

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

                    # Add collapsible YAML content
                    spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec.id}.yaml"
                    if spec_path.exists():
                        context_parts.extend(
                            ["<details>", "<summary>View Full Specification YAML</summary>", "", "```yaml"]
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

            # Add enhanced git status
            git_context = self.get_git_context()
            if git_context["has_changes"] or not git_context.get("spec_branch_alignment", True):
                context_parts.extend(self._format_git_context(git_context))

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

        # Enhanced progress display with tree structure
        progress_bar = self._create_progress_bar(progress)

        content.extend(
            [
                f"### 📋 Specification {index}: {spec.title}",
                f"**ID**: {spec.id}",
                f"**Progress**: {progress_bar} {progress:.0%}",
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
            test_progress = passed / total if total > 0 else 0
            test_bar = self._create_progress_bar(test_progress, width=10)
            content.append(f"**Test Status**: {test_bar} {passed}/{total} passing")
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

    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create visual progress bar."""
        filled = int(progress * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    def get_git_context(self) -> dict[str, Any]:
        """Get comprehensive git context for session awareness."""
        result = {
            "has_changes": False,
            "change_count": 0,
            "current_branch": None,
            "spec_branch_alignment": True,
            "modified_files": [],
            "commit_needed": False,
        }

        try:
            # Get current branch
            branch_cmd = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, cwd=self.project_root, timeout=3
            )
            if branch_cmd.returncode == 0:
                result["current_branch"] = branch_cmd.stdout.strip()

            # Get changed files with more detail
            status_cmd = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.project_root, timeout=3
            )

            if status_cmd.returncode == 0 and status_cmd.stdout.strip():
                changes = status_cmd.stdout.strip().split("\n")
                result["has_changes"] = True
                result["change_count"] = len(changes)
                result["modified_files"] = [change.split()[-1] for change in changes[:5]]  # First 5 files
                result["commit_needed"] = any(change.startswith(("M ", "A ", "D ")) for change in changes)

            # Check branch alignment with active specs
            active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)
            if active_specs and result["current_branch"]:
                spec_branches = [spec.branch for spec in active_specs if spec.branch]
                if spec_branches and result["current_branch"] not in spec_branches:
                    result["spec_branch_alignment"] = False

        except Exception as e:
            self.logger.warning(f"Git context extraction failed: {e}")

        return result

    def _format_git_context(self, git_context: dict[str, Any]) -> list[str]:
        """Format git context for display."""
        content = ["## 🔄 Git Status", ""]

        if git_context["current_branch"]:
            content.append(f"**Current Branch**: `{git_context['current_branch']}`")

        if not git_context["spec_branch_alignment"]:
            content.append("⚠️ **Warning**: Current branch doesn't match any active specification branches")

        if git_context["has_changes"]:
            content.append(f"**Uncommitted Changes**: {git_context['change_count']} files")
            if git_context["modified_files"]:
                content.append("**Modified Files**:")
                for file in git_context["modified_files"]:
                    content.append(f"  - {file}")
                if git_context["change_count"] > 5:
                    content.append(f"  - ... and {git_context['change_count'] - 5} more")

            if git_context["commit_needed"]:
                content.append("")
                content.append("💡 **Tip**: Consider committing your changes")

        content.append("")
        return content

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
