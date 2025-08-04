#!/usr/bin/env python3
"""Load session context with dual-mode behavior at startup.

This hook runs at session start to analyze project state and inject
helpful context. Adapts behavior based on session mode:
- Framework mode: Full workflow state and agent recommendations
- Drive mode: Minimal context loading, simple mode indicator
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.claude.hooks.mode_detector import get_current_command


class SessionContextLoaderHook(BaseHook):
    """Session context loader hook with mode-aware behavior."""

    def __init__(self):
        super().__init__("session_context_loader")
        self.project_root = get_project_root()

    def execute(self):
        """Execute session context loading with mode-aware behavior."""
        # Get event details
        event_name = self.input_data.get("hook_event_name", "")
        source = self.input_data.get("source", "startup")

        # Only process SessionStart events
        if event_name != "SessionStart":
            self.output_success("Not a SessionStart event")
            return

        # Gather project state
        spec_status = self.check_current_specification()
        recent_activity = self.analyze_recent_changes()

        # Track silently in drive mode
        if self.is_drive_mode():
            self.silent_track(
                "session_start",
                {
                    "spec_active": spec_status["active"],
                    "mode": "drive",
                    "has_uncommitted_changes": recent_activity["has_uncommitted_changes"],
                    "source": source,
                },
            )

        # Generate mode-appropriate context
        context = self.generate_mode_aware_context(spec_status, recent_activity, source)

        # Output as JSON for SessionStart hook
        output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}

        # Use output_json to handle the response properly
        self.output_json(output, exit_code=0)

    def check_current_specification(self) -> dict[str, Any]:
        """Check current specification status from active specification files."""
        specs_dir = self.project_root / ".quaestor" / "specifications"
        active_dir = specs_dir / "active"

        result = {"active": False, "id": "", "progress": 0, "remaining_tasks": 0, "in_progress_task": None}

        # Check active folder for specifications
        if active_dir.exists():
            try:
                # Get all active specification files
                active_specs = list(active_dir.glob("*.yaml"))

                if active_specs:
                    # Use the first active spec (should be limited to 3 by FolderManager)
                    spec_file = active_specs[0]
                    result["active"] = True
                    result["id"] = spec_file.stem

                    # Parse specification content
                    with open(spec_file) as f:
                        content = f.read()

                    # Extract progress from phases
                    import yaml

                    try:
                        spec_data = yaml.safe_load(content)
                        phases = spec_data.get("phases", {})
                        if phases:
                            completed_phases = sum(
                                1
                                for phase in phases.values()
                                if isinstance(phase, dict) and phase.get("status") == "completed"
                            )
                            total_phases = len(phases)
                            result["progress"] = int((completed_phases / total_phases) * 100) if total_phases > 0 else 0
                    except:
                        # Fallback to simple parsing
                        pass

                    # Count remaining tasks (simplified parsing)
                    pending_count = content.count("status: pending") + content.count("status: 'pending'")
                    in_progress_count = content.count("status: in_progress") + content.count("status: 'in_progress'")

                    result["remaining_tasks"] = pending_count + in_progress_count

                    # Find in-progress task
                    if in_progress_count > 0:
                        # Try to extract task name
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if "status: in_progress" in line or "status: 'in_progress'" in line:
                                # Look backwards for task name
                                for j in range(i - 1, max(0, i - 10), -1):
                                    if "name:" in lines[j]:
                                        task_name = lines[j].split("name:")[-1].strip().strip("\"'")
                                        result["in_progress_task"] = task_name
                                        break
                                break
            except Exception:
                pass

        return result

    def analyze_recent_changes(self) -> dict[str, Any]:
        """Analyze recent file changes and git status."""
        result = {
            "has_uncommitted_changes": False,
            "modified_files": [],
            "new_files": [],
            "hours_since_last_commit": None,
        }

        try:
            # Check git status
            git_status = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.project_root, timeout=5
            )

            if git_status.returncode == 0:
                for line in git_status.stdout.strip().split("\n"):
                    if not line:
                        continue

                    status = line[:2]
                    file_path = line[3:]

                    if "M" in status:
                        result["modified_files"].append(file_path)
                    elif "A" in status or "?" in status:
                        result["new_files"].append(file_path)

                result["has_uncommitted_changes"] = bool(result["modified_files"] or result["new_files"])

            # Check last commit time
            last_commit = subprocess.run(
                ["git", "log", "-1", "--format=%ct"], capture_output=True, text=True, cwd=self.project_root, timeout=5
            )

            if last_commit.returncode == 0 and last_commit.stdout.strip():
                commit_timestamp = int(last_commit.stdout.strip())
                hours_ago = (datetime.now().timestamp() - commit_timestamp) / 3600
                result["hours_since_last_commit"] = round(hours_ago, 1)

        except Exception:
            pass

        return result

    def generate_mode_aware_context(
        self, spec_status: dict[str, Any], recent_activity: dict[str, Any], source: str
    ) -> str:
        """Generate context message based on mode."""
        if self.is_framework_mode():
            return self._generate_framework_context(spec_status, recent_activity, source)
        else:
            return self._generate_drive_context(spec_status, recent_activity, source)

    def _generate_drive_context(self, spec_status: dict[str, Any], recent_activity: dict[str, Any], source: str) -> str:
        """Generate minimal context for drive mode."""
        context_parts = []

        # Simple header
        context_parts.append("=== DRIVE MODE ===")

        # Show if there are uncommitted changes
        if recent_activity["has_uncommitted_changes"]:
            change_count = len(recent_activity["modified_files"]) + len(recent_activity["new_files"])
            context_parts.append(f"Uncommitted changes: {change_count} files")

        # Simple hint
        context_parts.append("Ready to help! Use Quaestor commands (/research, /plan, /impl) for guided workflow.")

        context_parts.append("=" * 30)

        return "\n".join(context_parts)

    def _generate_framework_context(
        self, spec_status: dict[str, Any], recent_activity: dict[str, Any], source: str
    ) -> str:
        """Generate comprehensive context for framework mode."""
        context_parts = []

        # Get current command
        current_command = get_current_command()

        # Header based on mode and source
        if source == "resume":
            context_parts.append("=== RESUMED SESSION - FRAMEWORK MODE ===")
        else:
            context_parts.append("=== FRAMEWORK MODE ===")

        if current_command:
            context_parts.append(f"Current command: {current_command}")

        # Active specification information
        if spec_status["active"]:
            spec_info = [f"\nACTIVE SPECIFICATION: {spec_status['id']} ({spec_status['progress']}% complete)"]

            if spec_status["remaining_tasks"] > 0:
                spec_info.append(f"- Remaining tasks: {spec_status['remaining_tasks']}")

            if spec_status["in_progress_task"]:
                spec_info.append(f"- Current task: {spec_status['in_progress_task']}")

            if spec_status["progress"] >= 80:
                spec_info.append("- 🎯 Nearing completion! Consider using 'reviewer' agent to prepare for PR")
            else:
                spec_info.append("- Suggested: Use appropriate agents for the current phase")

            context_parts.append("\n".join(spec_info))
        else:
            context_parts.append(
                "\nNO ACTIVE SPECIFICATION\n" + "- Required: Use 'planner' agent to create a specification"
            )

        # Recent activity information
        if recent_activity["has_uncommitted_changes"]:
            changes_info = ["\nUNCOMMITTED CHANGES DETECTED"]

            if recent_activity["modified_files"]:
                changes_info.append(f"- Modified files: {len(recent_activity['modified_files'])}")
                for file in recent_activity["modified_files"][:3]:
                    changes_info.append(f"  • {file}")
                if len(recent_activity["modified_files"]) > 3:
                    changes_info.append(f"  • ... and {len(recent_activity['modified_files']) - 3} more")

            if recent_activity["new_files"]:
                changes_info.append(f"- New files: {len(recent_activity['new_files'])}")

            changes_info.append("- Suggested: Use 'reviewer' agent to review changes before committing")

            context_parts.append("\n".join(changes_info))

        # Time-based suggestions
        if recent_activity["hours_since_last_commit"] is not None:
            if recent_activity["hours_since_last_commit"] > 4:
                context_parts.append(
                    f"\n⏰ COMMIT REMINDER: {recent_activity['hours_since_last_commit']:.1f} hours since last commit\n"
                    + "- Consider committing completed work\n"
                    + "- Use 'reviewer' agent for pre-commit review"
                )

        # Command-specific recommendations
        recommendations = ["\nFRAMEWORK MODE RECOMMENDATIONS:"]

        if current_command == "/research":
            recommendations.extend(
                [
                    "1. Use 'researcher' agent to explore the codebase",
                    "2. Document findings for planning phase",
                    "3. Focus on understanding existing patterns",
                ]
            )
        elif current_command == "/plan":
            recommendations.extend(
                [
                    "1. Use 'planner' agent to create specifications",
                    "2. Break down work into clear tasks",
                    "3. Define success criteria",
                ]
            )
        elif current_command == "/impl":
            recommendations.extend(
                [
                    "1. Use 'implementer' agent for complex features",
                    "2. Follow the approved plan",
                    "3. Update TODO status as you progress",
                ]
            )
        elif current_command == "/review":
            recommendations.extend(
                [
                    "1. Use 'reviewer' agent for comprehensive checks",
                    "2. Verify all tests pass",
                    "3. Prepare for PR creation",
                ]
            )
        else:
            recommendations.extend(
                [
                    "1. Follow research → plan → implement workflow",
                    "2. Use specialized agents for each phase",
                    "3. Maintain specification tracking",
                ]
            )

        context_parts.append("\n".join(recommendations))

        # Footer
        context_parts.append("\n" + "=" * 30)

        return "\n".join(context_parts)

    def silent_track(self, event: str, data: dict[str, Any]):
        """Silently track events without output."""
        # This is a placeholder for silent tracking
        # Could write to a log file or metrics system
        pass


def main():
    """Main hook entry point."""
    hook = SessionContextLoaderHook()
    hook.run()


if __name__ == "__main__":
    main()
