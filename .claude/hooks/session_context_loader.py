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

from quaestor.claude.hooks.base import BaseHook, WorkflowState, get_project_root


class SessionContextLoaderHook(BaseHook):
    """Session context loader hook with mode-aware behavior."""

    def __init__(self):
        super().__init__("session_context_loader")
        self.project_root = get_project_root()

    def execute(self):
        """Execute session context loading with mode-aware behavior."""
        # Get event details
        event_name = self.input_data.get("hook_event_name", "")

        # Only process SessionStart events
        if event_name != "SessionStart":
            self.output_success("Not a SessionStart event")
            return

        # Gather project state
        spec_status = self.check_current_specification()
        # Use enhanced manager if available
        try:
            from .state_manager import WorkflowStateManager

            workflow_state_obj = WorkflowStateManager(self.project_root)
        except ImportError:
            workflow_state_obj = WorkflowState(self.project_root)
        workflow_state = workflow_state_obj.state
        recent_activity = self.analyze_recent_changes()

        # Generate context based on current state
        context = self.generate_context(spec_status, workflow_state, recent_activity)

        # Output as JSON for SessionStart hook
        output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}

        # Use output_json to handle the response properly
        self.output_json(output, exit_code=0)

    def check_current_specification(self) -> dict[str, Any]:
        """Check current specification status from active specification files."""
        specs_dir = self.project_root / ".quaestor" / "specs"
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

    def generate_context(
        self, spec_status: dict[str, Any], workflow_state: dict[str, Any], recent_activity: dict[str, Any]
    ) -> str:
        """Generate context message based on active work."""
        if self.has_active_work():
            return self._generate_active_work_context(spec_status, workflow_state, recent_activity)
        else:
            return self._generate_minimal_context(spec_status, workflow_state, recent_activity)

    def _generate_minimal_context(
        self, spec_status: dict[str, Any], workflow_state: dict[str, Any], recent_activity: dict[str, Any], source: str
    ) -> str:
        """Generate minimal context when no active work."""
        context_parts = []

        # Simple header
        context_parts.append("=== SESSION CONTEXT ===")

        # Show if there are uncommitted changes
        if recent_activity["has_uncommitted_changes"]:
            change_count = len(recent_activity["modified_files"]) + len(recent_activity["new_files"])
            context_parts.append(f"Uncommitted changes: {change_count} files")

        # Simple hint
        context_parts.append("Ready to help! Use '/plan' to start a new specification.")

        context_parts.append("=" * 30)

        return "\n".join(context_parts)

    def _generate_active_work_context(
        self, spec_status: dict[str, Any], workflow_state: dict[str, Any], recent_activity: dict[str, Any]
    ) -> str:
        """Generate comprehensive context when there's active work."""
        context_parts = []

        # Simple header for active work
        context_parts.append("=== SESSION CONTEXT ===")

        # Active specification information
        if spec_status["active"]:
            spec_info = [f"ACTIVE SPECIFICATION: {spec_status['id']} ({spec_status['progress']}% complete)"]

            if spec_status["remaining_tasks"] > 0:
                spec_info.append(f"- Remaining tasks: {spec_status['remaining_tasks']}")

            if spec_status["in_progress_task"]:
                spec_info.append(f"- Current task: {spec_status['in_progress_task']}")

            if spec_status["progress"] >= 80:
                spec_info.append("- 🎯 Nearing completion! Consider using 'reviewer' agent to prepare for PR")
            else:
                spec_info.append("- Suggested: Use 'planner' agent to review progress")

            context_parts.append("\n".join(spec_info))
        else:
            context_parts.append(
                "NO ACTIVE SPECIFICATION\n" + "- Suggested: Use 'planner' agent to create a specification for your work"
            )

        # Workflow state information
        if workflow_state.get("phase", "idle") != "idle":
            workflow_info = [f"\nWORKFLOW STATE: Currently in {workflow_state['phase']} phase"]

            files_examined = len(workflow_state.get("research_files", []))
            if files_examined > 0:
                workflow_info.append(f"- Files examined: {files_examined}")

            next_step = self._get_next_workflow_step(workflow_state)
            workflow_info.append(f"- Next step: {next_step}")

            # Phase-specific recommendations
            if workflow_state["phase"] == "researching":
                workflow_info.append("- Use 'researcher' agent to continue exploration")
            elif workflow_state["phase"] == "planning":
                workflow_info.append("- Use 'planner' agent to structure implementation")
            elif workflow_state["phase"] == "implementing":
                workflow_info.append("- Use 'implementer' agent for complex features")

            context_parts.append("\n".join(workflow_info))

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

        # Workflow recommendations
        recommendations = ["\nQUAESTOR WORKFLOW RECOMMENDATIONS:"]

        if not spec_status["active"] and workflow_state.get("phase", "idle") == "idle":
            recommendations.extend(
                [
                    "1. Start with 'researcher' agent to understand the codebase",
                    "2. Use 'planner' agent to create implementation strategy",
                    "3. Track work with specifications and TODOs",
                    "4. Use active specifications to track progress",
                ]
            )
        elif workflow_state.get("phase") == "implementing" and recent_activity["has_uncommitted_changes"]:
            recommendations.extend(
                [
                    "1. Use 'qa' agent to test your changes",
                    "2. Use 'reviewer' agent before committing",
                    "3. Update TODOs to track progress",
                    "4. Keep specification status current",
                ]
            )
        else:
            recommendations.extend(
                [
                    "1. Follow research → plan → implement workflow",
                    "2. Use specialized agents for each phase",
                    "3. Maintain specification and TODO tracking",
                    "4. Commit regularly with clear messages",
                ]
            )

        context_parts.append("\n".join(recommendations))

        # Footer
        context_parts.append("\n" + "=" * 30)

        return "\n".join(context_parts)

    def _get_next_workflow_step(self, workflow_state: dict[str, Any]) -> str:
        """Determine next workflow step based on current state."""
        phase = workflow_state.get("phase", "idle")
        files_examined = len(workflow_state.get("research_files", []))

        if phase == "idle":
            return "Start research phase with researcher agent"
        elif phase == "researching":
            if files_examined < 3:
                return f"Continue research ({files_examined}/3 files examined)"
            else:
                return "Move to planning phase with planner agent"
        elif phase == "planning":
            return "Create implementation plan and specifications"
        elif phase == "implementing":
            return "Continue implementation, update TODOs"
        else:
            return "Review current state and plan next steps"


def main():
    """Main hook entry point."""
    hook = SessionContextLoaderHook()
    hook.run()


if __name__ == "__main__":
    main()
