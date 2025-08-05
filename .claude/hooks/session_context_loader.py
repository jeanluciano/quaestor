#!/usr/bin/env python3
"""Load active specifications into session context at startup.

This hook injects the full content of active specifications into Claude's
context at session start, ensuring important project context survives
chat compaction and is immediately available in new sessions.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.core.specifications import SpecificationManager, SpecStatus


class SessionContextLoaderHook(BaseHook):
    """Inject active specifications as context at session start."""

    def __init__(self):
        super().__init__("session_context_loader")
        self.project_root = get_project_root()
        self.spec_manager = SpecificationManager(self.project_root)

    def execute(self):
        """Load and inject active specifications into session context."""
        # Only process SessionStart events
        event_name = self.input_data.get("hook_event_name", "")
        if event_name != "SessionStart":
            self.output_success("Not a SessionStart event")
            return

        # Generate context with active specifications
        context = self.generate_specification_context()

        # Output as additional context for session
        output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}

        self.output_json(output, exit_code=0)

    def generate_specification_context(self) -> str:
        """Generate context containing full active specifications."""
        context_parts = []

        # Header similar to CLAUDE.md
        context_parts.extend(
            [
                "<!-- QUAESTOR ACTIVE SPECIFICATIONS -->",
                "> [!IMPORTANT]",
                "> **Active Specifications**: The following specifications are currently being worked on.",
                "> These define the current implementation tasks and acceptance criteria.",
                "",
            ]
        )

        try:
            # Get active specifications
            active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)

            if active_specs:
                context_parts.append(f"## 📋 Active Specifications ({len(active_specs)})")
                context_parts.append("")

                # Load and inject each active specification's full content
                for i, spec in enumerate(active_specs, 1):
                    spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec.id}.yaml"

                    if spec_path.exists():
                        context_parts.extend(
                            [
                                f"### Specification {i}: {spec.title}",
                                f"**ID**: {spec.id}",
                                f"**Type**: {spec.type.value}",
                                f"**Priority**: {spec.priority.value}",
                                "",
                                "```yaml",
                            ]
                        )

                        # Include the full YAML content
                        with open(spec_path) as f:
                            content = f.read()
                            context_parts.append(content.strip())

                        context_parts.extend(["```", ""])

                        # Add progress summary
                        total_criteria = len(spec.acceptance_criteria)
                        completed = sum(1 for c in spec.acceptance_criteria if "✓" in c or "completed" in c.lower())
                        progress = int((completed / total_criteria) * 100) if total_criteria > 0 else 0

                        context_parts.extend(
                            [
                                f"**Progress**: {progress}% ({completed}/{total_criteria} criteria completed)",
                                f"**Branch**: {spec.branch or 'Not set'}",
                                "",
                                "---",
                                "",
                            ]
                        )
            else:
                context_parts.extend(
                    [
                        "## 📋 No Active Specifications",
                        "",
                        "No specifications are currently active. Use `/plan` to create new specifications",
                        "or `/plan --activate <spec-id>` to activate a draft specification.",
                        "",
                    ]
                )

        except Exception as e:
            self.logger.warning(f"Failed to load specifications: {e}")
            context_parts.extend(
                ["## ⚠️ Error Loading Specifications", "", f"Could not load active specifications: {str(e)}", ""]
            )

        # Add basic git status
        git_status = self.get_git_status()
        if git_status["has_changes"]:
            context_parts.extend(
                ["## 🔄 Uncommitted Changes", f"**Files with changes**: {git_status['change_count']}", ""]
            )

        # Add session info
        source = self.input_data.get("source", "startup")
        if source == "resume":
            context_parts.insert(0, "<!-- SESSION RESUMED AFTER COMPACTION -->")
        else:
            context_parts.insert(0, "<!-- NEW SESSION -->")

        context_parts.append("<!-- END QUAESTOR CONTEXT -->")

        return "\n".join(context_parts)

    def get_git_status(self) -> dict[str, Any]:
        """Get basic git status information."""
        result = {"has_changes": False, "change_count": 0}

        try:
            git_status = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.project_root, timeout=3
            )

            if git_status.returncode == 0 and git_status.stdout.strip():
                changes = git_status.stdout.strip().split("\n")
                result["has_changes"] = True
                result["change_count"] = len(changes)

        except Exception:
            pass

        return result


def main():
    """Main hook entry point."""
    hook = SessionContextLoaderHook()
    hook.run()


if __name__ == "__main__":
    main()
