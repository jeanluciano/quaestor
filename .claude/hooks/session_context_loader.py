#!/usr/bin/env python3
"""Load session context with agent recommendations at startup.

This hook runs at session start to analyze project state and inject
helpful context about active work, suggesting appropriate agents.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def parse_hook_input() -> dict[str, Any]:
    """Parse Claude hook input from stdin."""
    try:
        input_data = sys.stdin.read()
        if input_data:
            return json.loads(input_data)
        return {}
    except Exception:
        return {}


def check_current_specification(project_root: Path) -> dict[str, Any]:
    """Check current specification status from MEMORY.md and specification files."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"
    specs_dir = project_root / ".quaestor" / "specs"

    result = {"active": False, "id": "", "progress": 0, "remaining_tasks": 0, "in_progress_task": None}

    # Check MEMORY.md for current specification
    if memory_file.exists():
        try:
            content = memory_file.read_text()
            spec_match = re.search(r"current_specification:\s*['\"]?([^'\"]+)['\"]?", content)
            progress_match = re.search(r"progress:\s*(\d+)%", content)

            if spec_match:
                result["active"] = True
                result["id"] = spec_match.group(1)
                if progress_match:
                    result["progress"] = int(progress_match.group(1))
        except Exception:
            pass

    # Check specification files for in-progress tasks
    if specs_dir.exists() and result["active"]:
        spec_file = specs_dir / f"{result['id']}.yaml"

        if spec_file.exists():
            try:
                with open(spec_file) as f:
                    content = f.read()

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


def load_workflow_state(project_root: Path) -> dict[str, Any]:
    """Load current workflow state."""
    state_file = project_root / ".quaestor" / ".workflow_state"

    if not state_file.exists():
        return {"phase": "idle", "files_examined": 0}

    try:
        with open(state_file) as f:
            return json.load(f)
    except Exception:
        return {"phase": "idle", "files_examined": 0}


def analyze_recent_changes(project_root: Path) -> dict[str, Any]:
    """Analyze recent file changes and git status."""
    result = {"has_uncommitted_changes": False, "modified_files": [], "new_files": [], "hours_since_last_commit": None}

    try:
        # Check git status
        git_status = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=project_root, timeout=5
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
            ["git", "log", "-1", "--format=%ct"], capture_output=True, text=True, cwd=project_root, timeout=5
        )

        if last_commit.returncode == 0 and last_commit.stdout.strip():
            commit_timestamp = int(last_commit.stdout.strip())
            hours_ago = (datetime.now().timestamp() - commit_timestamp) / 3600
            result["hours_since_last_commit"] = round(hours_ago, 1)

    except Exception:
        pass

    return result


def get_next_workflow_step(workflow_state: dict[str, Any]) -> str:
    """Determine next workflow step based on current state."""
    phase = workflow_state.get("phase", "idle")
    files_examined = workflow_state.get("files_examined", 0)

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


def generate_session_context(
    spec_status: dict[str, Any], workflow_state: dict[str, Any], recent_activity: dict[str, Any], source: str
) -> str:
    """Generate context message for session start."""

    context_parts = []

    # Header based on source
    if source == "resume":
        context_parts.append("=== RESUMED SESSION CONTEXT ===")
    else:
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
    if workflow_state["phase"] != "idle":
        workflow_info = [f"\nWORKFLOW STATE: Currently in {workflow_state['phase']} phase"]

        if workflow_state.get("files_examined", 0) > 0:
            workflow_info.append(f"- Files examined: {workflow_state['files_examined']}")

        next_step = get_next_workflow_step(workflow_state)
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

    if not spec_status["active"] and workflow_state["phase"] == "idle":
        recommendations.extend(
            [
                "1. Start with 'researcher' agent to understand the codebase",
                "2. Use 'planner' agent to create implementation strategy",
                "3. Track work with specifications and TODOs",
                "4. Maintain MEMORY.md with progress updates",
            ]
        )
    elif workflow_state["phase"] == "implementing" and recent_activity["has_uncommitted_changes"]:
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


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Get event details
    event_name = hook_data.get("hook_event_name", "")
    source = hook_data.get("source", "startup")

    # Only process SessionStart events
    if event_name != "SessionStart":
        sys.exit(0)

    # Gather project state
    spec_status = check_current_specification(project_root)
    workflow_state = load_workflow_state(project_root)
    recent_activity = analyze_recent_changes(project_root)

    # Generate context
    context = generate_session_context(spec_status, workflow_state, recent_activity, source)

    # Output as JSON for SessionStart hook
    output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
