#!/usr/bin/env python3
"""Enforce Research → Plan → Implement workflow."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
hook_parent = Path(__file__).parent.parent
if str(hook_parent) not in sys.path:
    sys.path.insert(0, str(hook_parent))

# Import shared utilities
from shared_utils import WorkflowState, get_project_root  # noqa: E402


def check_workflow_compliance(workflow):
    """Check workflow compliance and provide guidance."""
    # Basic implementation check is handled by shared utility
    if not workflow.check_can_implement():
        return False

    # Additional workflow-specific checks
    if workflow.state["phase"] == "planning":
        print("📋 Reminder: You're in the planning phase")
        print("   Consider completing your implementation plan first")

    # Check if research is stale
    if workflow.state.get("last_research"):
        try:
            last_research = datetime.fromisoformat(workflow.state["last_research"])
            if datetime.now() - last_research > timedelta(hours=2):
                print("⚠️  Note: Your research is over 2 hours old")
                print("   Consider refreshing your understanding if needed")
        except Exception:
            pass

    # If implementing, check research depth
    if workflow.state["phase"] == "implementing":
        files_examined = workflow.state.get("files_examined", 0)
        if files_examined < 3:
            print(f"💡 Tip: You've only examined {files_examined} files")
            print("   Consider researching more of the codebase for better context")

    return True  # Always allow, just provide guidance


def main():
    """Main entry point."""
    # Get project root from command line or auto-detect
    project_root = sys.argv[1] if len(sys.argv) > 1 else get_project_root()

    # Check workflow state using shared utilities
    workflow = WorkflowState(project_root)
    check_workflow_compliance(workflow)

    # Always exit 0 to not block operations
    sys.exit(0)


if __name__ == "__main__":
    main()
