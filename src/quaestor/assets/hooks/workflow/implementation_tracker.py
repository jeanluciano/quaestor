#!/usr/bin/env python3
"""Track implementation phase and provide guidance."""

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
    # Get project root from command line or auto-detect
    project_root = sys.argv[1] if len(sys.argv) > 1 else get_project_root()

    # Track implementation using shared utilities
    workflow = WorkflowState(project_root)
    workflow.track_implementation()

    # Additional implementation-specific logic
    if workflow.state["phase"] == "implementing":
        files_examined = workflow.state.get("files_examined", 0)
        if files_examined > 0:
            print(f"🚀 Implementation phase started (researched {files_examined} files)")
        else:
            print("🚀 Implementation phase started")

    sys.exit(0)


if __name__ == "__main__":
    main()
