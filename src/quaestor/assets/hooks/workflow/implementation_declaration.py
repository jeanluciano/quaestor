#!/usr/bin/env python3
"""Force declaration of which milestone task is being worked on."""

import sys
from pathlib import Path

import yaml


def check_active_task_declared():
    """Ensure the AI has declared which task they're working on."""

    milestones_dir = Path(".quaestor/milestones")

    # Check if there's an active task declared
    active_tasks = []

    if milestones_dir.exists():
        for tasks_file in milestones_dir.rglob("tasks.yaml"):
            try:
                with open(tasks_file) as f:
                    data = yaml.safe_load(f)

                for task in data.get("tasks", []):
                    if task.get("status") == "in_progress":
                        active_tasks.append({"file": tasks_file, "task": task})
            except Exception:
                continue

    if not active_tasks:
        print("🚨 NO ACTIVE TASK DECLARED")
        print("   Before implementing, you must:")
        print("   1. Check .quaestor/milestones/ for the current phase")
        print("   2. Update a task status to 'in_progress'")
        print("   3. Declare which subtask you're working on")
        print("\n💡 Example declaration:")
        print("   'Working on Phase 1 > vector_store > Create VectorStore abstraction'")
        print("\n🔧 To fix:")
        print("   Edit the relevant tasks.yaml file and set status: 'in_progress'")

        # Don't block completely, but make it very clear
        return True

    print(f"✅ Active task declared: {active_tasks[0]['task'].get('name')}")
    return True


if __name__ == "__main__":
    check_active_task_declared()
    sys.exit(0)
