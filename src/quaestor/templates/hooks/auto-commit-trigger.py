#!/usr/bin/env python3
"""Trigger auto-commit when TODO items are marked as completed."""

import json
import sys
from pathlib import Path


def parse_todo_output():
    """Parse TodoWrite output to find completed items."""
    try:
        # Read the tool output from stdin or environment
        # In actual implementation, this would get the TodoWrite output
        # For now, we'll check if there are any completed TODOs

        # This is a placeholder - in reality, the hook would receive
        # the TodoWrite output and parse it for completed items
        print("🔍 Checking for completed TODO items...")

        # Would parse actual TodoWrite output here
        # Example structure:
        # {
        #   "todos": [
        #     {"id": "1", "content": "Task", "status": "completed", ...}
        #   ]
        # }

        return []  # Placeholder

    except Exception as e:
        print(f"⚠️  Could not parse TODO output: {e}")
        return []


def check_auto_commit_enabled(project_root):
    """Check if auto-commit is enabled in settings."""
    settings_file = Path(project_root) / ".quaestor" / "settings.json"

    if not settings_file.exists():
        return True  # Default to enabled

    try:
        with open(settings_file) as f:
            settings = json.load(f)
            return settings.get("auto_commit", {}).get("enabled", True)
    except Exception:
        return True


def trigger_auto_commit(todo_item, project_root):
    """Trigger the auto-commit command for a completed TODO."""
    try:
        print(f"🚀 Triggering auto-commit for: {todo_item.get('content', 'Unknown task')}")

        # In real implementation, would call:
        # subprocess.run(["quaestor", "auto-commit", "--todo-id", str(todo_item['id'])],
        #                cwd=project_root)

        # For now, just log the action
        print(f"   Would run: quaestor auto-commit --todo-id {todo_item.get('id')}")

    except Exception as e:
        print(f"❌ Failed to trigger auto-commit: {e}")


def main():
    """Main entry point."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Check if auto-commit is enabled
    if not check_auto_commit_enabled(project_root):
        print("ℹ️  Auto-commit is disabled")
        return 0

    # Parse TODO output
    completed_todos = parse_todo_output()

    if not completed_todos:
        # No completed TODOs, nothing to do
        return 0

    print(f"✅ Found {len(completed_todos)} completed TODO(s)")

    # Trigger auto-commit for each completed item
    for todo in completed_todos:
        trigger_auto_commit(todo, project_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
