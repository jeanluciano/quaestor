#!/usr/bin/env python3
"""Enforce research before implementation - PreToolUse hook for Write/Edit/MultiEdit.

This hook is called by Claude Code before using code modification tools.
It ensures that proper research has been done before implementation.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_utils import call_automation_hook, parse_hook_input


def main():
    """Main entry point for the hook."""
    # Parse hook input
    hook_data = parse_hook_input()

    # Get the tool being used
    tool = hook_data.get("tool", "")

    # Prepare context for enforcement hook
    context = {"tool": tool, "hook_data": hook_data}

    # Call the enforcement hook
    return call_automation_hook("enforce_research_before_code", context)


if __name__ == "__main__":
    sys.exit(main())
