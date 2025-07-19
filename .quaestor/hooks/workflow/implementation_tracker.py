#!/usr/bin/env python3
"""Track implementation phase and provide guidance."""

import sys
from pathlib import Path

# Import shared utilities
try:
    from ..shared_utils import WorkflowState, get_project_root
except ImportError:
    # Fallback for when run as standalone script
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from shared_utils import WorkflowState, get_project_root


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
