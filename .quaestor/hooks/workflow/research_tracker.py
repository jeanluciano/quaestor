#!/usr/bin/env python3
"""Track research phase activities."""

import sys
from pathlib import Path

# Add parent directory to path for imports
hook_parent = Path(__file__).parent.parent
if str(hook_parent) not in sys.path:
    sys.path.insert(0, str(hook_parent))

# Import shared utilities
from shared_utils import WorkflowState, get_project_root  # noqa: E402


def main():
    """Main entry point."""
    # Get project root and file path from environment or args
    project_root = sys.argv[1] if len(sys.argv) > 1 else get_project_root()
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Track research activity using shared WorkflowState
    workflow = WorkflowState(project_root)
    workflow.track_research(file_path)

    # Additional logic specific to research tracking
    if workflow.state["files_examined"] >= 3 and workflow.state["phase"] == "researching":
        workflow.set_phase(
            "planning",
            f"✅ Good research! Examined {workflow.state['files_examined']} files\n"
            "📋 Ready to create an implementation plan",
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
