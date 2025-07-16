#!/usr/bin/env python3
"""Check milestone completion status."""

import re
import sys
from pathlib import Path


def check_milestone_completion():
    """Check if current milestone is complete based on MEMORY.md."""
    memory_file = Path(".quaestor/MEMORY.md")

    if not memory_file.exists():
        print("ℹ️  MEMORY.md not found")
        return True

    try:
        content = memory_file.read_text()

        # Look for milestone progress
        milestone_pattern = r"current_milestone:\s*['\"]?([^'\"]+)['\"]?"
        progress_pattern = r"progress:\s*(\d+)%"

        milestone_match = re.search(milestone_pattern, content)
        progress_match = re.search(progress_pattern, content)

        if milestone_match and progress_match:
            milestone = milestone_match.group(1)
            progress = int(progress_match.group(1))

            if progress >= 100:
                print(f"🎉 Milestone '{milestone}' is complete! Consider creating a PR.")
            else:
                print(f"📊 Milestone '{milestone}' is {progress}% complete")
        else:
            print("ℹ️  No active milestone found")

        return True

    except Exception as e:
        print(f"❌ Error checking milestone: {e}")
        return False


if __name__ == "__main__":
    success = check_milestone_completion()
    sys.exit(0 if success else 1)
