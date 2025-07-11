#!/usr/bin/env python3
"""Enforce Research → Plan → Implement workflow."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def check_workflow_state():
    """Check if research has been done before implementation."""
    workflow_file = Path(".quaestor/.workflow_state")

    if not workflow_file.exists():
        return False, "❌ BLOCKED: Must research before implementing. Use Read/Grep tools first."

    try:
        with open(workflow_file) as f:
            state = json.load(f)

        # Check if research was done
        if state.get("phase") != "implementing":
            return False, "❌ BLOCKED: Must complete research phase first. Examine relevant files."

        # Check if research is still valid (2 hour expiry)
        last_research = datetime.fromisoformat(state.get("last_research", "2000-01-01"))
        if datetime.now() - last_research > timedelta(hours=2):
            return False, "❌ BLOCKED: Research expired. Re-examine files before implementing."

        # Check minimum files examined
        if state.get("files_examined", 0) < 3:
            files_examined = state.get("files_examined", 0)
            return (
                False,
                f"❌ BLOCKED: Only examined {files_examined} files. Examine at least 3 relevant files first.",
            )

        return True, "✅ Research requirements satisfied"

    except Exception as e:
        return False, f"❌ Error checking workflow state: {e}"


if __name__ == "__main__":
    tool = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    allowed, message = check_workflow_state()

    print(message)
    sys.exit(0 if allowed else 1)
