#!/usr/bin/env python3
"""Memory and milestone synchronization hook.

This hook updates MEMORY.md and milestone files based on TODO completions
and detected work progress. It ensures project memory stays in sync with
actual development activities.
"""

import json
import re
import sys
from datetime import datetime, timedelta
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


def extract_completed_todos(hook_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract completed TODOs from TodoWrite output."""
    completed_todos = []

    # Check if this is a TodoWrite event
    if hook_data.get("toolName") != "TodoWrite":
        return completed_todos

    # Get the todos from the output
    output = hook_data.get("output", {})
    todos = output.get("todos", [])

    # Find completed items
    for todo in todos:
        if todo.get("status") == "completed":
            completed_todos.append(
                {
                    "id": todo.get("id"),
                    "content": todo.get("content", "Completed task"),
                    "priority": todo.get("priority", "medium"),
                }
            )

    return completed_todos


def update_memory_file(
    project_root: Path, completed_todos: list[dict[str, Any]], milestone_info: dict[str, Any] | None = None
) -> bool:
    """Update MEMORY.md with completed work."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    if not memory_file.exists():
        print("❌ MEMORY.md not found")
        return False

    try:
        # Read current content
        content = memory_file.read_text()

        # Find or create today's section
        today = datetime.now().strftime("%Y-%m-%d")
        today_pattern = rf"###\s+{today}"

        if not re.search(today_pattern, content):
            # Add today's section
            progress_section = f"\n\n### {today}\n\n"

            # Find where to insert (after most recent date or at end)
            date_pattern = r"###\s+(\d{4}-\d{2}-\d{2})"
            dates = re.findall(date_pattern, content)

            if dates:
                # Insert after the most recent date section
                last_date = sorted(dates)[-1]
                last_date_pattern = rf"(###\s+{last_date}.*?)(?=###|\Z)"
                match = re.search(last_date_pattern, content, re.DOTALL)
                if match:
                    insert_pos = match.end()
                    content = content[:insert_pos] + progress_section + content[insert_pos:]
                else:
                    content += progress_section
            else:
                content += progress_section

        # Add completed todos
        if completed_todos:
            todo_section = "\n**Completed TODOs:**\n"
            for todo in completed_todos:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo["priority"], "⚪")
                todo_section += f"- {priority_emoji} {todo['content']}\n"

            # Insert after today's header
            today_match = re.search(rf"(###\s+{today})", content)
            if today_match:
                insert_pos = today_match.end()
                # Skip any existing newlines
                while insert_pos < len(content) and content[insert_pos] == "\n":
                    insert_pos += 1
                content = content[:insert_pos] + todo_section + content[insert_pos:]

        # Update milestone progress if provided
        if milestone_info:
            milestone_name = milestone_info.get("name", "")
            progress = milestone_info.get("progress", 0)

            # Update milestone status in memory
            milestone_pattern = rf"(current_milestone:\s*['\"]?){re.escape(milestone_name)}(['\"]?)"
            content = re.sub(milestone_pattern, rf"\1{milestone_name}\2", content)

            # Update progress
            progress_pattern = r"progress:\s*\d+%"
            content = re.sub(progress_pattern, f"progress: {progress}%", content)

        # Write back
        memory_file.write_text(content)

        return True

    except Exception as e:
        print(f"❌ Error updating MEMORY.md: {e}")
        return False


def find_active_milestone(project_root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    """Find the currently active milestone and task."""
    milestones_dir = project_root / ".quaestor" / "milestones"

    if not milestones_dir.exists():
        return None, None

    # Look for tasks.yaml files with in_progress tasks
    for tasks_file in milestones_dir.rglob("tasks.yaml"):
        try:
            # Simple YAML parsing (avoid external dependency)
            with open(tasks_file) as f:
                content = f.read()

            # Look for in_progress status
            if (
                "status: in_progress" in content
                or "status: 'in_progress'" in content
                or 'status: "in_progress"' in content
            ):
                # Extract basic task info
                task_info = {
                    "file": tasks_file,
                    "milestone": tasks_file.parent.name,
                }
                return tasks_file, task_info
        except Exception:
            continue

    return None, None


def update_milestone_progress(tasks_file: Path, completed_todos: list[dict[str, Any]]) -> dict[str, Any]:
    """Update milestone task progress based on completed TODOs."""
    try:
        with open(tasks_file) as f:
            content = f.read()

        # Count subtasks (simplified - looks for list items)
        subtask_pattern = r"^\s*-\s+.+$"
        all_subtasks = re.findall(subtask_pattern, content, re.MULTILINE)
        completed_pattern = r"^\s*-\s+.+#\s*COMPLETED"
        completed_subtasks = re.findall(completed_pattern, content, re.MULTILINE)

        # Mark some subtasks as complete based on TODOs
        todos_to_mark = min(len(completed_todos), len(all_subtasks) - len(completed_subtasks))

        if todos_to_mark > 0:
            # Find incomplete subtasks and mark them
            lines = content.split("\n")
            marked = 0

            for i, line in enumerate(lines):
                if marked >= todos_to_mark:
                    break

                # Check if this is an incomplete subtask
                if re.match(r"^\s*-\s+", line) and "# COMPLETED" not in line:
                    lines[i] = f"{line} # COMPLETED"
                    marked += 1

            content = "\n".join(lines)

        # Calculate new progress
        total = len(all_subtasks)
        completed = len(completed_subtasks) + todos_to_mark
        progress = int((completed / total * 100) if total > 0 else 0)

        # Update progress in file
        content = re.sub(r"progress:\s*\d+%", f"progress: {progress}%", content)

        # Add notes about the update
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = f"\n- {timestamp}: Updated via memory sync - {len(completed_todos)} TODOs completed"

        # Insert note after notes: line
        notes_match = re.search(r"notes:\s*\n", content)
        if notes_match:
            insert_pos = notes_match.end()
            content = content[:insert_pos] + note + "\n" + content[insert_pos:]

        # Write back
        with open(tasks_file, "w") as f:
            f.write(content)

        return {
            "name": tasks_file.parent.name,
            "progress": progress,
            "completed_count": completed,
            "total_count": total,
        }

    except Exception as e:
        print(f"❌ Error updating milestone: {e}")
        return {}


def check_memory_staleness(project_root: Path) -> dict[str, Any]:
    """Check if MEMORY.md is stale compared to recent activity."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    if not memory_file.exists():
        return {"is_stale": True, "reason": "MEMORY.md not found"}

    try:
        # Check last modification time
        memory_mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
        hours_old = (datetime.now() - memory_mtime).total_seconds() / 3600

        # Check content
        content = memory_file.read_text()
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        has_today = today in content
        has_yesterday = yesterday in content

        # Determine staleness
        if hours_old > 24 and not has_today:
            return {
                "is_stale": True,
                "reason": f"No entry for today, last updated {hours_old:.1f} hours ago",
                "hours_old": hours_old,
            }
        elif hours_old > 48 and not has_yesterday:
            return {"is_stale": True, "reason": "Missing entries for multiple days", "hours_old": hours_old}

        return {"is_stale": False}

    except Exception:
        return {"is_stale": True, "reason": "Error reading MEMORY.md"}


def generate_documentation_suggestion(
    completed_todos: list[dict[str, Any]], memory_staleness: dict[str, Any], milestone_info: dict[str, Any] | None
) -> tuple[bool, str]:
    """Generate agent suggestions for documentation tasks.

    Returns:
        Tuple of (should_block, message)
    """

    # Scenario 1: Many TODOs completed but memory is stale
    if len(completed_todos) > 5 and memory_staleness.get("is_stale", False):
        return (
            True,
            f"""
📚 DOCUMENTATION LAG DETECTED!

Completed {len(completed_todos)} TODOs but {memory_staleness.get("reason", "documentation is out of date")}.

Please run: Use the architect agent to update project documentation and memory

The architect agent should:
1. Review all {len(completed_todos)} completed TODOs
2. Update MEMORY.md with architectural decisions made
3. Document any new patterns or conventions introduced
4. Add implementation details for complex features
5. Update component relationships if changed
6. Record lessons learned or gotchas discovered

Keeping documentation current ensures knowledge retention and helps onboard team members.
""",
        )

    # Scenario 2: Milestone nearing completion without proper documentation
    if milestone_info and milestone_info.get("progress", 0) >= 80:
        return (
            True,
            f"""
📖 MILESTONE DOCUMENTATION NEEDED!

Milestone '{milestone_info.get("name", "current")}' is {milestone_info.get("progress", 0)}% complete.

Please run: Use the architect agent to create comprehensive milestone documentation

The architect agent should:
1. Document all architectural decisions made during this milestone
2. Create or update design diagrams
3. List all APIs or interfaces created/modified  
4. Document configuration changes
5. Note any technical debt incurred
6. Prepare knowledge transfer documentation

This ensures the milestone's learnings are captured before moving on.
""",
        )

    # Scenario 3: Pattern changes detected
    high_priority_completed = sum(1 for t in completed_todos if t.get("priority") == "high")
    if high_priority_completed >= 3:
        todo_content = "\n".join([f"- {t.get('content', '')}" for t in completed_todos[:5]])

        if any(word in todo_content.lower() for word in ["refactor", "redesign", "migrate", "update pattern"]):
            return (
                True,
                f"""
🏗️ ARCHITECTURAL CHANGES DETECTED!

High-priority refactoring/redesign work completed:
{todo_content}

Please run: Use the architect agent to document the architectural changes

The architect agent should:
1. Document why the changes were made
2. Update architecture diagrams
3. Record migration strategies used
4. Document new patterns introduced
5. Update developer guidelines
6. Note any breaking changes

This ensures the team understands the new architecture.
""",
            )

    # No blocking suggestion
    return False, None


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Extract completed TODOs
    completed_todos = extract_completed_todos(hook_data)

    if not completed_todos:
        # No completed TODOs, check for other triggers
        tool_name = hook_data.get("toolName", "")
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            print("💡 Remember to update TODOs and milestones after implementation work")
        return 0

    # Check memory staleness
    memory_staleness = check_memory_staleness(project_root)

    # Find active milestone
    tasks_file, task_info = find_active_milestone(project_root)

    milestone_info = None
    if tasks_file and task_info:
        milestone_info = update_milestone_progress(tasks_file, completed_todos)

    # Generate documentation agent suggestion
    should_block, agent_message = generate_documentation_suggestion(completed_todos, memory_staleness, milestone_info)

    if should_block and agent_message:
        # Block with agent suggestion
        print(agent_message.strip(), file=sys.stderr)
        return 2

    # Regular processing
    print(f"📝 Found {len(completed_todos)} completed TODO(s)")

    if tasks_file and task_info:
        print(f"📊 Updating milestone: {task_info['milestone']}")

        if milestone_info and milestone_info.get("progress", 0) >= 100:
            print(f"🎉 Milestone '{milestone_info['name']}' is now complete!")
            print("💡 Consider creating a PR with: gh pr create")

    # Update MEMORY.md
    print("📝 Updating MEMORY.md...")
    if update_memory_file(project_root, completed_todos, milestone_info):
        print("✅ MEMORY.md updated successfully")

    # Summary
    if milestone_info:
        progress = milestone_info.get("progress", 0)
        completed = milestone_info.get("completed_count", 0)
        total = milestone_info.get("total_count", 0)
        print(f"\n📊 Milestone Progress: {completed}/{total} tasks ({progress}%)")

    # Add staleness warning if not blocking
    if memory_staleness.get("is_stale") and not should_block:
        print(f"\n⚠️  Documentation reminder: {memory_staleness.get('reason', 'MEMORY.md needs update')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
