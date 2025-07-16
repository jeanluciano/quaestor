#!/usr/bin/env python3
"""Connect TodoWrite updates to milestone tracking."""

import os
import sys
from datetime import datetime
from pathlib import Path

import yaml


class TodoMilestoneConnector:
    """Connect todo updates to milestone tracking."""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.milestones_dir = self.project_root / ".quaestor" / "milestones"
        self.memory_file = self.project_root / ".quaestor" / "MEMORY.md"

    def extract_todo_context(self):
        """Extract context from environment variables passed by Claude."""
        # Claude passes todo information via environment variables
        todo_content = os.environ.get("CLAUDE_TODO_CONTENT", "")
        todo_status = os.environ.get("CLAUDE_TODO_STATUS", "")

        # Parse todo content for milestone references
        milestone_keywords = ["phase", "task:", "subtask:", "vector", "ingestion", "knowledge"]

        context = {"content": todo_content, "status": todo_status, "detected_milestone": None}

        # Try to detect which milestone this relates to
        content_lower = todo_content.lower()
        for keyword in milestone_keywords:
            if keyword in content_lower:
                context["detected_milestone"] = keyword
                break

        return context

    def find_related_task(self, todo_context):
        """Find milestone task related to the todo."""
        if not todo_context["detected_milestone"]:
            return None, None

        keyword = todo_context["detected_milestone"]

        # Search milestone files for matching tasks
        for tasks_file in self.milestones_dir.rglob("tasks.yaml"):
            try:
                with open(tasks_file) as f:
                    data = yaml.safe_load(f)

                for task in data.get("tasks", []):
                    task_text = f"{task.get('name', '')} {task.get('id', '')}".lower()
                    if keyword in task_text or any(keyword in str(s).lower() for s in task.get("subtasks", [])):
                        return tasks_file, task
            except Exception:
                continue

        return None, None

    def suggest_milestone_update(self, todo_context, tasks_file, task):
        """Suggest how to update the milestone based on todo."""
        print("\n🔗 TODO-MILESTONE CONNECTION DETECTED")
        print(f"   Todo: {todo_context['content'][:50]}...")
        print(f"   Related task: {task.get('name')} ({task.get('id')})")
        print(f"   Milestone file: {tasks_file.parent.name}/tasks.yaml")

        if todo_context["status"] == "completed":
            print("\n📋 SUGGESTED MILESTONE UPDATE:")
            print("   1. Mark the related subtask as '# COMPLETED'")
            print("   2. Update progress percentage")
            print("   3. Add note with completion date")
            print("   4. Update MEMORY.md with progress log")

            # Show exact command
            print("\n💡 Quick update command:")
            print(f"   Edit {tasks_file} and mark subtask complete")

    def check_tracking_compliance(self):
        """Check if milestone tracking is up to date."""
        # Check for recent implementation files
        recent_files = []
        for pattern in ["*.py", "test_*.py"]:
            for f in self.project_root.rglob(pattern):
                try:
                    if (datetime.now().timestamp() - f.stat().st_mtime) < 3600:  # Last hour
                        recent_files.append(f)
                except OSError:
                    pass

        if recent_files and len(recent_files) > 2:
            print("\n⚠️  TRACKING REMINDER:")
            print(f"   Found {len(recent_files)} recently modified files")
            print("   Don't forget to update:")
            print("   - [ ] Milestone tasks.yaml")
            print("   - [ ] MEMORY.md progress log")
            print("   - [ ] Mark completed subtasks")

    def run(self):
        """Main connector logic."""
        # Extract todo context
        todo_context = self.extract_todo_context()

        if not todo_context["content"]:
            # No todo context, just check compliance
            self.check_tracking_compliance()
            return

        # Find related milestone task
        tasks_file, task = self.find_related_task(todo_context)

        if task:
            self.suggest_milestone_update(todo_context, tasks_file, task)
        else:
            print("💡 No specific milestone task detected for this todo")

        # Always check compliance
        self.check_tracking_compliance()


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    connector = TodoMilestoneConnector(project_root)
    connector.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
