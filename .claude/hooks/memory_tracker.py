#!/usr/bin/env python3
"""Memory and specification synchronization hook.

This hook updates MEMORY.md and specification files based on TODO completions
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


def extract_completed_specs(hook_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract completed specifications from hook data."""
    completed_specs = []

    # Check if this is a specification update event
    tool_name = hook_data.get("toolName", "")
    if tool_name not in ["Edit", "Write", "MultiEdit"]:
        return completed_specs

    # Check if we're updating specification status
    params = hook_data.get("params", {})
    if isinstance(params, dict):
        file_path = params.get("file_path", "")
        if "specifications" in file_path or "MEMORY.md" in file_path:
            # Extract spec status updates from content
            new_content = params.get("new_string", "")
            if "IMPLEMENTED" in new_content or "TESTED" in new_content:
                # Parse spec ID from content
                spec_id_match = re.search(r'spec[_-]id["\']?:\s*["\']?([a-zA-Z]+-[a-zA-Z0-9-]+)', new_content)
                if spec_id_match:
                    completed_specs.append(
                        {
                            "id": spec_id_match.group(1),
                            "content": f"Implemented specification {spec_id_match.group(1)}",
                            "priority": "high",
                        }
                    )

    return completed_specs


def update_memory_file(
    project_root: Path, completed_specs: list[dict[str, Any]], spec_info: dict[str, Any] | None = None
) -> bool:
    """Update MEMORY.md with completed specifications."""
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

        # Add completed specifications
        if completed_specs:
            spec_section = "\n**Completed Specifications:**\n"
            for spec in completed_specs:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                    spec["priority"], "⚪"
                )
                spec_section += f"- {priority_emoji} {spec['content']}\n"

            # Insert after today's header
            today_match = re.search(rf"(###\s+{today})", content)
            if today_match:
                insert_pos = today_match.end()
                # Skip any existing newlines
                while insert_pos < len(content) and content[insert_pos] == "\n":
                    insert_pos += 1
                content = content[:insert_pos] + spec_section + content[insert_pos:]

        # Update specification progress if provided
        if spec_info:
            spec_id = spec_info.get("id", "")
            progress = spec_info.get("progress", 0)

            # Update specification status in memory
            spec_pattern = rf"(current_specification:\s*['\"]?){re.escape(spec_id)}(['\"]?)"
            content = re.sub(spec_pattern, rf"\1{spec_id}\2", content)

            # Update progress
            progress_pattern = r"progress:\s*\d+%"
            content = re.sub(progress_pattern, f"progress: {progress}%", content)

        # Write back
        memory_file.write_text(content)

        return True

    except Exception as e:
        print(f"❌ Error updating MEMORY.md: {e}")
        return False


def find_active_specification(project_root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    """Find the currently active specification and task."""
    specs_dir = project_root / ".quaestor" / "specs"

    if not specs_dir.exists():
        return None, None

    # Look for specification files with in_progress tasks
    for spec_file in specs_dir.glob("*.yaml"):
        try:
            # Simple YAML parsing (avoid external dependency)
            with open(spec_file) as f:
                content = f.read()

            # Look for in_progress status
            if (
                "status: in_progress" in content
                or "status: 'in_progress'" in content
                or 'status: "in_progress"' in content
            ):
                # Extract basic task info
                task_info = {
                    "file": spec_file,
                    "specification": spec_file.stem,
                }
                return spec_file, task_info
        except Exception:
            continue

    return None, None


def update_specification_progress(spec_file: Path, completed_specs: list[dict[str, Any]]) -> dict[str, Any]:
    """Update specification progress based on completed tasks."""
    try:
        with open(spec_file) as f:
            content = f.read()

        # Count subtasks (simplified - looks for list items)
        subtask_pattern = r"^\s*-\s+.+$"
        all_subtasks = re.findall(subtask_pattern, content, re.MULTILINE)
        completed_pattern = r"^\s*-\s+.+#\s*COMPLETED"
        completed_subtasks = re.findall(completed_pattern, content, re.MULTILINE)

        # Mark some subtasks as complete based on completed specs
        specs_to_mark = min(len(completed_specs), len(all_subtasks) - len(completed_subtasks))

        if specs_to_mark > 0:
            # Find incomplete subtasks and mark them
            lines = content.split("\n")
            marked = 0

            for i, line in enumerate(lines):
                if marked >= specs_to_mark:
                    break

                # Check if this is an incomplete subtask
                if re.match(r"^\s*-\s+", line) and "# COMPLETED" not in line:
                    lines[i] = f"{line} # COMPLETED"
                    marked += 1

            content = "\n".join(lines)

        # Calculate new progress
        total = len(all_subtasks)
        completed = len(completed_subtasks) + specs_to_mark
        progress = int((completed / total * 100) if total > 0 else 0)

        # Update progress in file
        content = re.sub(r"progress:\s*\d+%", f"progress: {progress}%", content)

        # Add notes about the update
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = f"\n- {timestamp}: Updated via memory sync - {len(completed_specs)} specs completed"

        # Insert note after notes: line
        notes_match = re.search(r"notes:\s*\n", content)
        if notes_match:
            insert_pos = notes_match.end()
            content = content[:insert_pos] + note + "\n" + content[insert_pos:]

        # Write back
        with open(spec_file, "w") as f:
            f.write(content)

        return {
            "id": spec_file.stem,
            "progress": progress,
            "completed_count": completed,
            "total_count": total,
        }

    except Exception as e:
        print(f"❌ Error updating specification: {e}")
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
    completed_specs: list[dict[str, Any]], memory_staleness: dict[str, Any], spec_info: dict[str, Any] | None
) -> tuple[bool, str]:
    """Generate agent suggestions for documentation tasks.

    Returns:
        Tuple of (should_block, message)
    """

    # Scenario 1: Many specifications completed but memory is stale
    if len(completed_specs) > 3 and memory_staleness.get("is_stale", False):
        return (
            True,
            f"""
📚 DOCUMENTATION LAG DETECTED!

Completed {len(completed_specs)} specifications but {memory_staleness.get("reason", "documentation is out of date")}.

Please run: Use the architect agent to update project documentation and memory

The architect agent should:
1. Review all {len(completed_specs)} completed specifications
2. Update MEMORY.md with architectural decisions made
3. Document any new patterns or conventions introduced
4. Add implementation details for complex features
5. Update component relationships if changed
6. Record lessons learned or gotchas discovered

Keeping documentation current ensures knowledge retention and helps onboard team members.
""",
        )

    # Scenario 2: Specification nearing completion without proper documentation
    if spec_info and spec_info.get("progress", 0) >= 80:
        return (
            True,
            f"""
📖 SPECIFICATION DOCUMENTATION NEEDED!

Specification '{spec_info.get("id", "current")}' is {spec_info.get("progress", 0)}% complete.

Please run: Use the architect agent to create comprehensive specification documentation

The architect agent should:
1. Document all architectural decisions made during this specification
2. Create or update design diagrams
3. List all APIs or interfaces created/modified
4. Document configuration changes
5. Note any technical debt incurred
6. Prepare knowledge transfer documentation

This ensures the specification's learnings are captured before moving on.
""",
        )

    # Scenario 3: Pattern changes detected
    high_priority_completed = sum(1 for t in completed_specs if t.get("priority") == "high")
    if high_priority_completed >= 3:
        spec_content = "\n".join([f"- {t.get('content', '')}" for t in completed_specs[:5]])

        if any(word in spec_content.lower() for word in ["refactor", "redesign", "migrate", "update pattern"]):
            return (
                True,
                f"""
🏗️ ARCHITECTURAL CHANGES DETECTED!

High-priority refactoring/redesign work completed:
{spec_content}

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

    # Extract completed specifications
    completed_specs = extract_completed_specs(hook_data)

    if not completed_specs:
        # No completed specifications, check for other triggers
        tool_name = hook_data.get("toolName", "")
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            print("💡 Remember to update specification status after implementation work")
        return 0

    # Check memory staleness
    memory_staleness = check_memory_staleness(project_root)

    # Find active specification
    spec_file, task_info = find_active_specification(project_root)

    spec_info = None
    if spec_file and task_info:
        spec_info = update_specification_progress(spec_file, completed_specs)

    # Generate documentation agent suggestion
    should_block, agent_message = generate_documentation_suggestion(completed_specs, memory_staleness, spec_info)

    if should_block and agent_message:
        # Block with agent suggestion
        print(agent_message.strip(), file=sys.stderr)
        return 2

    # Regular processing
    print(f"📝 Found {len(completed_specs)} completed specification(s)")

    if spec_file and task_info:
        print(f"📊 Updating specification: {task_info['specification']}")

        if spec_info and spec_info.get("progress", 0) >= 100:
            print(f"🎉 Specification '{spec_info['id']}' is now complete!")
            print("💡 Consider creating a PR with: gh pr create")

    # Update MEMORY.md
    print("📝 Updating MEMORY.md...")
    if update_memory_file(project_root, completed_specs, spec_info):
        print("✅ MEMORY.md updated successfully")

    # Summary
    if spec_info:
        progress = spec_info.get("progress", 0)
        completed = spec_info.get("completed_count", 0)
        total = spec_info.get("total_count", 0)
        print(f"\n📊 Specification Progress: {completed}/{total} tasks ({progress}%)")

    # Add staleness warning if not blocking
    if memory_staleness.get("is_stale") and not should_block:
        print(f"\n⚠️  Documentation reminder: {memory_staleness.get('reason', 'MEMORY.md needs update')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
