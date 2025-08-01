#!/usr/bin/env python3
"""Connect TODO changes to milestone tracking and suggest PRs when milestones complete.

This hook is called by Claude Code when TodoWrite is used.
It checks milestone progress and suggests PR creation when milestones are completed.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def parse_hook_input() -> dict[str, Any]:
    """Parse Claude hook input from stdin."""
    try:
        input_data = sys.stdin.read()
        if input_data:
            return json.loads(input_data)
        return {}
    except Exception:
        return {}


def count_completed_todos(hook_data: dict[str, Any]) -> tuple[int, int]:
    """Count completed vs total TODOs from hook data.

    Returns:
        Tuple of (completed_count, total_count)
    """
    if hook_data.get("toolName") != "TodoWrite":
        return 0, 0

    output = hook_data.get("output", {})
    todos = output.get("todos", [])

    total = len(todos)
    completed = sum(1 for todo in todos if todo.get("status") == "completed")

    return completed, total


def check_memory_milestone_status(project_root: Path) -> dict[str, Any]:
    """Check milestone status from MEMORY.md."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    if not memory_file.exists():
        return {"status": "no_memory"}

    try:
        content = memory_file.read_text()

        # Look for milestone info
        milestone_pattern = r"current_milestone:\s*['\"]?([^'\"]+)['\"]?"
        progress_pattern = r"progress:\s*(\d+)%"

        milestone_match = re.search(milestone_pattern, content)
        progress_match = re.search(progress_pattern, content)

        if milestone_match and progress_match:
            return {"status": "active", "name": milestone_match.group(1), "progress": int(progress_match.group(1))}

        return {"status": "no_milestone"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def suggest_pr_creation(milestone_name: str, progress: int) -> bool:
    """Suggest PR creation and optionally create it.

    Returns:
        True if PR was created, False otherwise
    """
    print(f"\n🎉 Milestone '{milestone_name}' is {progress}% complete!")

    if progress >= 100:
        print("\n💡 This milestone appears to be complete! You can create a PR with:")
        print(f"   gh pr create --title 'feat: Complete milestone - {milestone_name}'")

        # Check if gh CLI is available
        try:
            subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=5)

            # Offer to create PR
            print("\n🤖 I can create the PR for you now. Type 'yes' to proceed (or press Enter to skip):")

            # Note: In a hook context, we can't actually wait for user input
            # So we'll just provide the command
            return False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("\n💡 Install GitHub CLI to create PRs: https://cli.github.com")
            return False

    return False


def main():
    """Main entry point for the hook."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Count TODOs
    completed, total = count_completed_todos(hook_data)

    if total == 0:
        # Not a TodoWrite event or no TODOs
        return 0

    # Report TODO status
    print(f"📊 TODO Status: {completed}/{total} completed ({int(completed / total * 100)}%)")

    # Check milestone status
    milestone_status = check_memory_milestone_status(project_root)

    if milestone_status["status"] == "active":
        milestone_name = milestone_status["name"]
        milestone_progress = milestone_status["progress"]

        print(f"📊 Milestone '{milestone_name}': {milestone_progress}% complete")

        # If all TODOs are complete, suggest checking milestone
        if completed == total and completed > 0:
            print("\n✅ All TODOs completed! Consider:")
            print("   1. Update milestone progress in MEMORY.md")
            print("   2. Run 'quaestor update' to sync milestone files")

            # If milestone is also complete, suggest PR
            if milestone_progress >= 100:
                suggest_pr_creation(milestone_name, milestone_progress)

    elif milestone_status["status"] == "no_milestone":
        if completed == total and total > 0:
            print("\n✅ All TODOs completed! Consider creating a milestone to track this work.")

    # Always successful
    return 0


if __name__ == "__main__":
    sys.exit(main())
