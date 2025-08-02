#!/usr/bin/env python3
"""Track research phase activities with improved reliability."""

import json
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


class WorkflowState:
    """Track the current workflow state across hooks."""

    def __init__(self, project_root: Path | str):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".quaestor" / ".workflow_state"
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load workflow state from file."""
        if not self.state_file.exists():
            return {
                "phase": "idle",
                "last_research": None,
                "last_plan": None,
                "files_examined": 0,
                "research_files": [],
                "implementation_files": [],
            }

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception:
            return {"phase": "idle", "files_examined": 0, "research_files": [], "implementation_files": []}

    def _save_state(self):
        """Save workflow state to file atomically."""
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)

            # Write to temp file first
            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(self.state, f, indent=2)

            # Atomic rename
            temp_file.replace(self.state_file)
        except Exception as e:
            print(f"Warning: Could not save workflow state: {e}")
            # Clean up temp file if it exists
            temp_file = self.state_file.with_suffix(".tmp")
            if temp_file.exists():
                temp_file.unlink()

    def set_phase(self, phase: str, message: str | None = None):
        """Set workflow phase with optional message."""
        self.state["phase"] = phase
        if message:
            print(message)
        self._save_state()

    def track_research(self, file_path: str | None = None):
        """Track research activity."""
        if self.state["phase"] == "idle":
            self.set_phase("researching", "🔍 Started research phase")

        self.state["last_research"] = datetime.now().isoformat()
        if file_path:
            research_files = self.state.get("research_files", [])
            if file_path not in research_files:
                research_files.append(file_path)
                self.state["research_files"] = research_files

        self._save_state()


def generate_phase_transition_suggestion(state: dict[str, Any], files_examined: int) -> tuple[bool, str]:
    """Generate agent suggestions for workflow phase transitions.

    Returns:
        Tuple of (should_block, message)
    """
    phase = state.get("phase", "idle")

    # Scenario 1: Research complete, transition to planning
    if files_examined >= 5 and phase == "researching":
        research_files = state.get("research_files", [])[-5:]  # Last 5 files
        files_summary = "\n".join([f"- {f}" for f in research_files])

        return (
            True,
            f"""
✅ Research Phase Complete! Examined {files_examined} files.

Key files researched:
{files_summary}

NEXT STEP: Create an implementation plan based on your research.

Please run: Use the planner agent to create a detailed implementation plan

The planner agent should:
1. Review the {files_examined} researched files and findings
2. Identify implementation approach and patterns to follow
3. Create a specification with clear objectives
4. Break down work into manageable subtasks
5. Estimate effort and identify risks
6. Define success criteria and test strategy

This ensures a structured approach before writing code.
""",
        )

    # Scenario 2: Stuck in research phase too long
    elif files_examined >= 10 and phase == "researching":
        return (
            True,
            f"""
⚠️ EXTENSIVE RESEARCH: You've examined {files_examined} files!

This might indicate analysis paralysis. Time to move forward.

Please run: Use the planner agent to synthesize findings and create a plan

The planner should:
1. Summarize key findings from research
2. Identify the core patterns to follow
3. Make architectural decisions
4. Create an MVP implementation plan
5. Note areas for future investigation

Sometimes perfect understanding isn't needed to start.
""",
        )

    # Scenario 3: Starting implementation without research
    elif phase == "idle" and files_examined == 0:
        # Don't block on first file read, but provide guidance
        return (
            False,
            """
🔍 Starting fresh! Remember the Quaestor workflow:

1. Research Phase: Use the researcher agent to understand existing patterns
2. Planning Phase: Use the planner agent to design your approach
3. Implementation Phase: Use the implementer agent to write code

This structured approach leads to better outcomes.
""",
        )

    # Scenario 4: Planning phase complete, ready for implementation
    elif phase == "planning" and state.get("last_plan") is not None:
        plan_age = (datetime.now() - datetime.fromisoformat(state["last_plan"])).total_seconds() / 60
        if plan_age < 30:  # Plan created in last 30 minutes
            return (
                True,
                """
📋 Planning Complete! Ready to implement.

Please run: Use the implementer agent to start building based on your plan

The implementer agent should:
1. Follow the implementation plan created
2. Use patterns discovered during research
3. Write clean, tested code
4. Update TODOs as work progresses
5. Commit regularly with clear messages

Remember to maintain the patterns you discovered during research.
""",
            )

    # No blocking suggestion needed
    return False, None


def main():
    """Main entry point for research tracking hook."""
    # Parse input
    input_data = parse_hook_input()

    # Get project root
    project_root = Path(input_data.get("projectRoot", get_project_root()))

    # Validate project root
    if not project_root.exists():
        output = {"error": f"Project root does not exist: {project_root}", "blocking": True}
        json.dump(output, sys.stdout)
        sys.exit(2)

    # Get file path from input if provided
    file_path = (
        input_data.get("filePath") or input_data.get("file_path") or input_data.get("tool_input", {}).get("file_path")
    )

    # Initialize workflow state
    workflow_state = WorkflowState(project_root)

    # Track research activity
    workflow_state.track_research(file_path)

    # Get current state
    state = workflow_state.state
    files_examined = len(state.get("research_files", []))

    # Generate phase transition suggestion
    should_block, agent_message = generate_phase_transition_suggestion(state, files_examined)

    if should_block and agent_message:
        # Block with agent suggestion
        print(agent_message.strip(), file=sys.stderr)
        sys.exit(2)

    # Prepare response data
    response_data = {
        "phase": state["phase"],
        "files_examined": files_examined,
        "research_files": state.get("research_files", []),
    }

    # Regular progress reporting
    if files_examined >= 3 and state["phase"] == "researching":
        workflow_state.set_phase("planning")

        # Success with transition message
        output = {
            "message": f"✅ Good research! Examined {files_examined} files. Ready to create an implementation plan.",
            "data": {
                **response_data,
                "phase": "planning",
                "next_action": "Create an implementation plan based on research",
            },
        }
    else:
        # Success with progress update
        remaining = max(0, 3 - files_examined)
        message = f"Research in progress. Examined {files_examined} files."
        if remaining > 0:
            message += f" Need to examine {remaining} more files."

        output = {
            "message": message,
            "data": {**response_data, "remaining_files": remaining, "ready_for_planning": False},
        }

    # Add non-blocking agent message if any
    if not should_block and agent_message:
        output["agent_suggestion"] = agent_message.strip()

    # Output JSON response
    json.dump(output, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
