#!/usr/bin/env python3
"""Track research phase activities with improved reliability.

This is an example of a refactored hook using the new base class.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from quaestor.hooks.base import BaseHook

    from ..shared_utils import WorkflowState, get_project_root
except ImportError:
    # Fallback for development
    from shared_utils import WorkflowState, get_project_root

    try:
        from quaestor.hooks.base import BaseHook
    except ImportError:
        # Create a dummy BaseHook if not available
        class BaseHook:
            def __init__(self, name):
                self.name = name

            def run(self):
                pass


class ResearchTracker(BaseHook):
    """Track research activities with proper error handling and JSON I/O."""

    def __init__(self):
        super().__init__("track-research")
        self.workflow_state = None
        self.project_root = None

    def execute(self):
        """Main execution logic."""
        # Get project root from input or use default
        self.project_root = Path(self.input_data.get("projectRoot", get_project_root()))

        # Validate project root
        if not self.project_root.exists():
            self.output_error(f"Project root does not exist: {self.project_root}", blocking=True)
            return

        # Get file path from input if provided
        file_path = self.input_data.get("filePath") or self.input_data.get("file_path")

        # Validate file path if provided
        if file_path:
            try:
                validated_path = self.validate_path(file_path)
                file_path = str(validated_path)
            except Exception as e:
                self.logger.warning(f"Invalid file path: {e}")
                file_path = None

        # Initialize workflow state
        self.workflow_state = WorkflowState(self.project_root)

        # Track research activity
        self.workflow_state.track_research(file_path)

        # Get current state
        state = self.workflow_state.state
        files_examined = len(state.get("research_files", []))

        # Prepare response data
        response_data = {
            "phase": state["phase"],
            "files_examined": files_examined,
            "research_files": state.get("research_files", []),
        }

        # Check if ready to move to planning phase
        if files_examined >= 3 and state["phase"] == "researching":
            self.workflow_state.set_phase("planning")

            # Success with transition message
            self.output_success(
                f"✅ Good research! Examined {files_examined} files. Ready to create an implementation plan.",
                data={
                    **response_data,
                    "phase": "planning",
                    "next_action": "Create an implementation plan based on research",
                },
            )
        else:
            # Success with progress update
            remaining = max(0, 3 - files_examined)
            message = f"Research in progress. Examined {files_examined} files."
            if remaining > 0:
                message += f" Need to examine {remaining} more files."

            self.output_success(
                message, data={**response_data, "remaining_files": remaining, "ready_for_planning": False}
            )


def main():
    """Main entry point."""
    tracker = ResearchTracker()
    tracker.run()


if __name__ == "__main__":
    main()
