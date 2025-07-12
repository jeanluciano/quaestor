#!/usr/bin/env python3
"""Enforce Research → Plan → Implement workflow."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


class WorkflowState:
    """Track the current workflow state."""

    def __init__(self, project_root):
        self.state_file = Path(project_root) / ".quaestor" / ".workflow_state"
        self.state = self._load_state()

    def _load_state(self):
        """Load workflow state from file."""
        if not self.state_file.exists():
            return {
                "phase": "idle",
                "last_research": None,
                "last_plan": None,
                "files_examined": 0,
                "research_files": [],
            }

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception:
            return {"phase": "idle", "files_examined": 0}

    def _save_state(self):
        """Save workflow state to file."""
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save workflow state: {e}")

    def check_can_implement(self):
        """Check if implementation is allowed."""
        # If no workflow state exists, just remind to research
        if self.state["phase"] == "idle":
            print("💡 Reminder: Consider researching existing code patterns before implementing")
            print("   Use Read/Grep tools to understand the codebase first")
            return True  # Don't block, just remind

        # If in planning phase, remind to complete plan
        if self.state["phase"] == "planning":
            print("📋 Reminder: You're in the planning phase")
            print("   Consider completing your implementation plan first")
            return True  # Don't block

        # If research is stale, warn but don't block
        if self.state.get("last_research"):
            try:
                last_research = datetime.fromisoformat(self.state["last_research"])
                if datetime.now() - last_research > timedelta(hours=2):
                    print("⚠️  Note: Your research is over 2 hours old")
                    print("   Consider refreshing your understanding if needed")
            except Exception:
                pass

        # If implementing, check if enough research was done
        if self.state["phase"] == "implementing":
            files_examined = self.state.get("files_examined", 0)
            if files_examined < 3:
                print(f"💡 Tip: You've only examined {files_examined} files")
                print("   Consider researching more of the codebase for better context")

        return True  # Always allow, just provide guidance


def main():
    """Main entry point."""
    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Check workflow state
    workflow = WorkflowState(project_root)
    workflow.check_can_implement()

    # Always exit 0 to not block operations
    sys.exit(0)


if __name__ == "__main__":
    main()
