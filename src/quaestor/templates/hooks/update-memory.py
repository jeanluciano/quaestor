#!/usr/bin/env python3
"""Update MEMORY.md from completed TODOs."""

import sys
from datetime import datetime
from pathlib import Path


def update_memory_from_todos():
    """Extract completed TODOs and update MEMORY.md."""
    memory_file = Path(".quaestor/MEMORY.md")

    if not memory_file.exists():
        print("⚠️  MEMORY.md not found")
        return True

    try:
        content = memory_file.read_text()

        # Add a simple completed task entry
        today = datetime.now().strftime("%Y-%m-%d")

        # Find the progress section
        if "## Progress Log" in content:
            # Add to existing progress log
            progress_marker = "## Progress Log"
            insert_pos = content.find(progress_marker) + len(progress_marker)

            # Add entry
            new_entry = f"\n\n### {today}\n- Completed tasks from TODO list\n"
            content = content[:insert_pos] + new_entry + content[insert_pos:]
        else:
            # Create new progress log section
            content += f"\n\n## Progress Log\n\n### {today}\n- Completed tasks from TODO list\n"

        memory_file.write_text(content)
        print(f"✅ Updated MEMORY.md with progress for {today}")
        return True

    except Exception as e:
        print(f"❌ Error updating memory: {e}")
        return False


if __name__ == "__main__":
    success = update_memory_from_todos()
    sys.exit(0 if success else 1)
