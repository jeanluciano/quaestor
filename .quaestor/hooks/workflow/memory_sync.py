#!/usr/bin/env python3
"""Enhanced memory and milestone tracking hook."""

import sys
from datetime import datetime
from pathlib import Path

import yaml


class MilestoneTracker:
    """Track and update milestones based on completed work."""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.memory_file = self.project_root / ".quaestor" / "MEMORY.md"
        self.milestones_dir = self.project_root / ".quaestor" / "milestones"
        self.workflow_state = self.project_root / ".quaestor" / ".workflow_state"

    def find_active_milestone(self):
        """Find the currently active milestone and task."""
        if not self.milestones_dir.exists():
            return None, None

        # Look for tasks.yaml files with in_progress tasks
        for tasks_file in self.milestones_dir.rglob("tasks.yaml"):
            try:
                with open(tasks_file) as f:
                    data = yaml.safe_load(f)

                for task in data.get("tasks", []):
                    if task.get("status") == "in_progress":
                        return tasks_file, task
            except Exception:
                continue

        return None, None

    def detect_completed_work(self):
        """Detect what was completed based on recent file changes."""
        completed = []

        # Check for new files in src/ and tests/
        src_files = list((self.project_root / "src").rglob("*.py")) if (self.project_root / "src").exists() else []
        test_files = (
            list((self.project_root / "tests").rglob("test_*.py")) if (self.project_root / "tests").exists() else []
        )

        # This is simplified - in reality would check git status
        if src_files or test_files:
            completed.append(
                {
                    "type": "implementation",
                    "src_files": [str(f.relative_to(self.project_root)) for f in src_files[-5:]],
                    "test_files": [str(f.relative_to(self.project_root)) for f in test_files[-5:]],
                }
            )

        return completed

    def update_milestone_task(self, tasks_file, task, completed_work):
        """Update the milestone task with completion info."""
        try:
            with open(tasks_file) as f:
                data = yaml.safe_load(f)

            # Find and update the task
            for t in data.get("tasks", []):
                if t.get("id") == task.get("id"):
                    # Mark first incomplete subtask as complete
                    if "subtasks" in t:
                        for i, subtask in enumerate(t["subtasks"]):
                            if "# COMPLETED" not in str(subtask):
                                t["subtasks"][i] = f"{subtask} # COMPLETED"
                                break

                    # Update progress
                    completed_subtasks = sum(1 for s in t.get("subtasks", []) if "# COMPLETED" in str(s))
                    total_subtasks = len(t.get("subtasks", []))
                    if total_subtasks > 0:
                        t["progress"] = f"{int(completed_subtasks / total_subtasks * 100)}%"

                    # Add notes
                    if "notes" not in t:
                        t["notes"] = ""
                    t["notes"] += f"\n- {datetime.now().strftime('%Y-%m-%d')}: Progress update via hook"

                    # Update status if all complete
                    if completed_subtasks == total_subtasks:
                        t["status"] = "completed"

            # Write back
            with open(tasks_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            return True
        except Exception as e:
            print(f"Error updating milestone: {e}")
            return False

    def update_memory_simple(self):
        """Simple memory update for backwards compatibility."""
        if not self.memory_file.exists():
            print("⚠️  MEMORY.md not found")
            return True

        try:
            content = self.memory_file.read_text()
            today = datetime.now().strftime("%Y-%m-%d")

            # Remove duplicate generic entries
            lines = content.split("\n")
            filtered_lines = []

            for i, line in enumerate(lines):
                if line.strip() == "- Completed tasks from TODO list":
                    # Skip this generic line and check if we should skip the date header too
                    if i > 0 and lines[i - 1].startswith("### ") and lines[i - 1].strip() == f"### {today}":
                        # Also remove the date header if it only has this generic entry
                        filtered_lines = filtered_lines[:-1]
                    continue
                filtered_lines.append(line)

            content = "\n".join(filtered_lines)

            # Add to existing progress log
            if "## Progress Log" in content:
                progress_marker = "## Progress Log"
                insert_pos = content.find(progress_marker) + len(progress_marker)
                new_entry = f"\n\n### {today}\n- ✅ TodoWrite tasks completed\n"
                content = content[:insert_pos] + new_entry + content[insert_pos:]
            else:
                content += f"\n\n## Progress Log\n\n### {today}\n- ✅ TodoWrite tasks completed\n"

            self.memory_file.write_text(content)
            print(f"✅ Updated MEMORY.md with progress for {today}")
            return True

        except Exception as e:
            print(f"❌ Error updating memory: {e}")
            return False

    def update_memory_enhanced(self, task, completed_work):
        """Add meaningful progress entry to MEMORY.md."""
        try:
            content = self.memory_file.read_text()
            today = datetime.now().strftime("%Y-%m-%d")

            # Build progress entry
            entry = f"\n### {today}\n"
            entry += f"- **TASK**: {task.get('name', 'Unknown')} ({task.get('id', 'unknown')})\n"

            if completed_work:
                for work in completed_work:
                    if work["type"] == "implementation":
                        if work["src_files"]:
                            entry += f"  - Created {len(work['src_files'])} source files\n"
                            for f in work["src_files"][:3]:  # Show first 3
                                entry += f"    - `{f}`\n"
                        if work["test_files"]:
                            entry += f"  - Added {len(work['test_files'])} test files\n"
                            for f in work["test_files"][:3]:
                                entry += f"    - `{f}`\n"

            entry += f"  - Status: {task.get('progress', '0%')} complete\n"
            entry += "  - Next: Continue with remaining subtasks\n"

            # Remove duplicate progress log entries
            lines = content.split("\n")
            filtered_lines = []

            for i, line in enumerate(lines):
                if line.strip() == "- Completed tasks from TODO list":
                    # Skip this generic line and check if we should skip the date header too
                    if i > 0 and lines[i - 1].startswith("### "):
                        # Also remove the date header if it only has this generic entry
                        filtered_lines = filtered_lines[:-1]
                    continue
                filtered_lines.append(line)

            content = "\n".join(filtered_lines)

            # Insert after Progress Log header
            if "## Progress Log" in content:
                marker = "## Progress Log"
                pos = content.find(marker) + len(marker)
                content = content[:pos] + "\n" + entry + content[pos:]
            else:
                content += f"\n\n## Progress Log\n{entry}"

            self.memory_file.write_text(content)
            print("✅ Updated MEMORY.md with detailed progress")
            return True

        except Exception as e:
            print(f"Error updating memory: {e}")
            return False

    def run_enhanced(self):
        """Enhanced tracking logic."""
        print("🔗 Enhanced milestone tracking hook triggered")

        # Find active milestone
        tasks_file, task = self.find_active_milestone()

        if not task:
            print("💡 No active milestone task found")
            print("   Tip: Update a task status to 'in_progress' in .quaestor/milestones/*/tasks.yaml")
            # Fall back to simple update
            self.update_memory_simple()
            return

        print(f"📋 Active task: {task.get('name')}")

        # Detect what was completed
        completed_work = self.detect_completed_work()

        # Update milestone
        if self.update_milestone_task(tasks_file, task, completed_work):
            print(f"✅ Updated milestone: {tasks_file.parent.name}")

        # Update memory
        self.update_memory_enhanced(task, completed_work)

        # Provide next steps
        print("\n🎯 Next steps:")
        print("   1. Review the updated milestone file")
        print("   2. Check MEMORY.md progress log")
        print("   3. Continue with next subtask")


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    # Check if --from-todos flag is passed (existing behavior)
    if "--from-todos" in sys.argv:
        tracker = MilestoneTracker(project_root)
        tracker.run_enhanced()
    else:
        # Fallback to simple behavior
        tracker = MilestoneTracker(project_root)
        tracker.update_memory_simple()

    sys.exit(0)


if __name__ == "__main__":
    main()
