#!/usr/bin/env python3
"""Check compliance before edits and suggest appropriate agents.

This hook enforces Quaestor's workflow requirements before allowing file edits.
It ensures proper research and planning phases are completed before implementation.
"""

import json
import sys
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


def load_workflow_state(project_root: Path) -> dict[str, Any]:
    """Load workflow state from file."""
    state_file = project_root / ".quaestor" / ".workflow_state"

    if not state_file.exists():
        return {
            "phase": "idle",
            "last_research": None,
            "last_plan": None,
            "files_examined": 0,
            "research_files": [],
            "implementation_files": [],
        }

    try:
        with open(state_file) as f:
            return json.load(f)
    except Exception:
        return {"phase": "idle", "files_examined": 0}


def is_implementation_file(file_path: str) -> bool:
    """Check if the file is an implementation file (not test/docs/config)."""
    path = Path(file_path)

    # Skip non-implementation files
    if any(part in path.parts for part in [".quaestor", ".claude", "tests", "test", "docs", "__pycache__"]):
        return False

    # Skip configuration, setup, and build files
    if path.name in ["setup.py", "pyproject.toml", "package.json", "Makefile", "requirements.txt"]:
        return False

    # Skip hook files specifically
    if "hooks" in path.parts:
        return False

    # Check if it's a source code file
    implementation_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c"}
    return path.suffix in implementation_extensions and "src" in str(path)


def check_milestone_awareness(project_root: Path) -> dict[str, Any]:
    """Check if there's an active milestone being worked on."""
    milestones_dir = project_root / ".quaestor" / "milestones"

    if not milestones_dir.exists():
        return {"has_active": False, "reason": "No milestones directory"}

    # Look for in_progress tasks
    for tasks_file in milestones_dir.rglob("tasks.yaml"):
        try:
            with open(tasks_file) as f:
                content = f.read()
                if "status: in_progress" in content or "status: 'in_progress'" in content:
                    return {"has_active": True, "milestone": tasks_file.parent.name, "file": str(tasks_file)}
        except Exception:
            continue

    return {"has_active": False, "reason": "No active milestone tasks"}


def generate_workflow_violation_message(
    workflow_state: dict[str, Any], file_path: str, milestone_status: dict[str, Any]
) -> str:
    """Generate appropriate message for workflow violations."""

    phase = workflow_state["phase"]
    files_examined = workflow_state.get("files_examined", 0)

    if phase == "idle" and is_implementation_file(file_path):
        return f"""
⚠️ WORKFLOW VIOLATION: Attempting to edit implementation files without proper research!

File: {file_path}
Current phase: {phase}
Files researched: {files_examined}

REQUIRED WORKFLOW:
1. Research phase: Understand existing patterns and dependencies
2. Planning phase: Create implementation strategy
3. Implementation phase: Make code changes

Please run: Use the researcher agent to analyze the codebase before making changes

The researcher should examine:
- Current implementation patterns in similar files
- Dependencies and imports used
- Related test files and test patterns
- Similar components or modules
- Configuration requirements

Example: Use the researcher agent to understand codebase patterns before implementing changes
"""

    elif phase == "researching" and files_examined < 3:
        return f"""
⚠️ INSUFFICIENT RESEARCH: Only examined {files_examined} files so far.

File to edit: {file_path}
Current phase: {phase}
Minimum required: 3-5 files

RECOMMENDATION: Continue research before implementation

Please run: Use the researcher agent to examine more related files

Focus on:
- Files that import or are imported by {Path(file_path).name}
- Similar components in the codebase
- Test files for the module
- Configuration or setup files

You've examined: {", ".join(workflow_state.get("research_files", [])[-3:])}
"""

    elif not milestone_status["has_active"]:
        return f"""
⚠️ NO ACTIVE MILESTONE: Starting implementation without a tracked milestone.

File to edit: {file_path}

BEST PRACTICE: All implementation work should be tracked in a milestone

Please run: Use the planner agent to create a milestone for this work

The planner should:
1. Define the scope of changes
2. Break down into subtasks
3. Set success criteria
4. Create milestone in .quaestor/milestones/

This ensures proper tracking and helps with PR creation later.
"""

    # If we get here, allow the edit but provide guidance
    return None


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Extract file path
    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # Skip checks for non-implementation files
    if not is_implementation_file(file_path):
        sys.exit(0)

    # Load workflow state
    workflow_state = load_workflow_state(project_root)

    # Check milestone status
    milestone_status = check_milestone_awareness(project_root)

    # Generate violation message if needed
    violation_message = generate_workflow_violation_message(workflow_state, file_path, milestone_status)

    if violation_message:
        # Block the edit and provide guidance
        print(violation_message.strip(), file=sys.stderr)
        sys.exit(2)

    # If we get here, the edit is allowed
    # Provide helpful context based on current state
    if workflow_state["phase"] == "implementing":
        suggestions = []

        if Path(file_path).suffix == ".py":
            suggestions.append("Remember to follow Python type hints and docstring conventions")

        if "test" not in file_path.lower():
            suggestions.append("Consider writing tests for this implementation")

        if suggestions:
            print("✅ Implementation phase confirmed. Suggestions:\n" + "\n".join(f"  • {s}" for s in suggestions))

    sys.exit(0)


if __name__ == "__main__":
    main()
