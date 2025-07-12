#!/usr/bin/env python3
"""Track research phase activities."""

import json
import sys
from datetime import datetime
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
            return {"phase": "idle", "files_examined": 0, "research_files": []}

    def _save_state(self):
        """Save workflow state to file."""
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception:
            pass

    def track_research(self, file_path=None):
        """Track that research is being done."""
        # Move to research phase if idle
        if self.state["phase"] == "idle":
            self.state["phase"] = "researching"
            print("🔍 Started research phase")

        # Update research timestamp
        self.state["last_research"] = datetime.now().isoformat()

        # Track examined files
        if file_path and file_path not in self.state["research_files"]:
            self.state["research_files"].append(file_path)
            self.state["files_examined"] = len(self.state["research_files"])

        # If enough files examined, suggest moving to planning
        if self.state["files_examined"] >= 3 and self.state["phase"] == "researching":
            self.state["phase"] = "planning"
            print(f"✅ Good research! Examined {self.state['files_examined']} files")
            print("📋 Ready to create an implementation plan")

        self._save_state()


def main():
    """Main entry point."""
    # Get project root and file path from environment or args
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    file_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Track research activity
    workflow = WorkflowState(project_root)
    workflow.track_research(file_path)

    sys.exit(0)


if __name__ == "__main__":
    main()
