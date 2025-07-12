#!/usr/bin/env python3
"""Track implementation phase and provide guidance."""

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
                "implementation_started": None,
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
        except Exception:
            pass

    def track_implementation(self):
        """Track that implementation has started."""
        # If first implementation, mark the transition
        if self.state["phase"] in ["planning", "researching"]:
            self.state["phase"] = "implementing"
            self.state["implementation_started"] = datetime.now().isoformat()

            files_examined = self.state.get("files_examined", 0)
            if files_examined > 0:
                print(f"🚀 Implementation phase started (researched {files_examined} files)")
            else:
                print("🚀 Implementation phase started")

        self._save_state()


def main():
    """Main entry point."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Track implementation
    workflow = WorkflowState(project_root)
    workflow.track_implementation()

    sys.exit(0)


if __name__ == "__main__":
    main()
