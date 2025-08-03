#!/usr/bin/env python3
"""Track research phase activities with dual-mode behavior.

This hook tracks file exploration and research patterns. Adapts behavior based on session mode:
- Framework mode: Enforce Research → Plan → Implement phases
- Drive mode: Silent tracking without phase enforcement
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, WorkflowState, get_project_root


class ResearchWorkflowTrackerHook(BaseHook):
    """Research workflow tracking hook with mode-aware behavior."""

    def __init__(self):
        super().__init__("research_workflow_tracker")
        self.project_root = get_project_root()

    def execute(self):
        """Execute research tracking with mode-aware behavior."""
        # Get file path from input if provided
        file_path = (
            self.input_data.get("filePath")
            or self.input_data.get("file_path")
            or self.input_data.get("tool_input", {}).get("file_path")
        )

        # Initialize workflow state (use enhanced manager if available)
        try:
            from .state_manager import WorkflowStateManager

            workflow_state = WorkflowStateManager(self.project_root)
        except ImportError:
            workflow_state = WorkflowState(self.project_root)

        # Track research activity
        self.track_research_activity(workflow_state, file_path)

        # Get current state
        state = workflow_state.state
        files_examined = len(state.get("research_files", []))

        # Track silently in drive mode
        if self.is_drive_mode():
            self.silent_track(
                "research_activity",
                {
                    "phase": state["phase"],
                    "files_examined": files_examined,
                    "file_path": file_path,
                    "research_files": state.get("research_files", []),
                },
            )

        # Generate mode-appropriate phase transition suggestion
        should_block, message = self.generate_mode_aware_suggestion(state, files_examined)

        # Prepare response data
        response_data = {
            "phase": state["phase"],
            "files_examined": files_examined,
            "research_files": state.get("research_files", []),
        }

        if should_block and message:
            self.output_error(message.strip(), blocking=True)
        elif message:
            # Add response data to the message
            self.output_success(message.strip(), data=response_data)
        else:
            # Regular progress update
            self.output_success(self._generate_progress_message(state, files_examined), data=response_data)

    def track_research_activity(self, workflow_state: WorkflowState, file_path: str | None):
        """Track research activity in workflow state."""
        # In framework mode, track phases
        if self.is_framework_mode():
            if workflow_state.state["phase"] == "idle":
                workflow_state.set_phase("researching", "🔍 Started research phase")

        workflow_state.state["last_research"] = datetime.now().isoformat()
        if file_path:
            research_files = workflow_state.state.get("research_files", [])
            if file_path not in research_files:
                research_files.append(file_path)
                workflow_state.state["research_files"] = research_files

        workflow_state._save_state()

    def generate_mode_aware_suggestion(self, state: dict[str, Any], files_examined: int) -> tuple[bool, str]:
        """Generate mode-appropriate phase transition suggestions."""
        if self.is_drive_mode():
            return self._generate_drive_mode_suggestion(state, files_examined)
        else:
            return self._generate_framework_mode_suggestion(state, files_examined)

    def _generate_drive_mode_suggestion(self, state: dict[str, Any], files_examined: int) -> tuple[bool, str]:
        """Generate non-intrusive suggestions for drive mode."""
        # In drive mode, no phase enforcement or transition blocking
        # Just track silently and provide minimal feedback

        if files_examined > 10:
            # Gentle hint for extensive research
            return (
                False,
                self.format_drive_hint(f"Extensive research detected ({files_examined} files)", show_command=True),
            )

        # No message needed in drive mode
        return False, None

    def _generate_framework_mode_suggestion(self, state: dict[str, Any], files_examined: int) -> tuple[bool, str]:
        """Generate framework mode suggestions with phase enforcement."""
        phase = state.get("phase", "idle")

        # Research complete, transition to planning
        if files_examined >= 5 and phase == "researching":
            research_files = state.get("research_files", [])[-5:]  # Last 5 files
            files_summary = "\n".join([f"- {f}" for f in research_files])

            # Update phase (use enhanced manager if available)
            try:
                from .state_manager import WorkflowStateManager

                workflow_state = WorkflowStateManager(self.project_root)
            except ImportError:
                workflow_state = WorkflowState(self.project_root)
            workflow_state.set_phase("planning")

            return (
                True,
                f"""✅ Research Phase Complete! Examined {files_examined} files.

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

        # Stuck in research phase too long
        elif files_examined >= 10 and phase == "researching":
            return (
                True,
                f"""⚠️ EXTENSIVE RESEARCH: You've examined {files_examined} files!

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

        # Starting implementation without research
        elif phase == "idle" and files_examined == 0:
            # Don't block on first file read, but provide guidance
            return (
                False,
                """🔍 Starting fresh! Remember the Quaestor workflow:

1. Research Phase: Use the researcher agent to understand existing patterns
2. Planning Phase: Use the planner agent to design your approach
3. Implementation Phase: Use the implementer agent to write code

This structured approach leads to better outcomes.
""",
            )

        # Planning phase complete, ready for implementation
        elif phase == "planning" and state.get("last_plan") is not None:
            plan_age = (datetime.now() - datetime.fromisoformat(state["last_plan"])).total_seconds() / 60
            if plan_age < 30:  # Plan created in last 30 minutes
                return (
                    True,
                    """📋 Planning Complete! Ready to implement.

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

    def _generate_progress_message(self, state: dict[str, Any], files_examined: int) -> str:
        """Generate progress message based on current state."""
        phase = state.get("phase", "idle")

        if phase == "researching":
            remaining = max(0, 3 - files_examined)
            message = f"Research in progress. Examined {files_examined} files."
            if remaining > 0 and self.is_framework_mode():
                message += f" Need to examine {remaining} more files."
        elif phase == "planning":
            message = "Planning phase active. Create your implementation plan."
        elif phase == "implementing":
            message = "Implementation phase active."
        else:
            message = "Ready to start research phase."

        return message


def main():
    """Main hook entry point."""
    hook = ResearchWorkflowTrackerHook()
    hook.run()


if __name__ == "__main__":
    main()
