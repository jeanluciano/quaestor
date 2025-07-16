#!/usr/bin/env python3
"""Validate that milestone tracking matches actual work done."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml


class MilestoneValidator:
    """Validate milestone tracking compliance."""

    def __init__(self):
        self.project_root = Path(".")
        self.milestones_dir = self.project_root / ".quaestor" / "milestones"
        self.memory_file = self.project_root / ".quaestor" / "MEMORY.md"

    def get_recent_work(self):
        """Detect recent implementation work."""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=6)  # Last 6 hours

        work_detected = {"src_files": [], "test_files": [], "timestamp": now}

        # Check for recent files
        for pattern in ["src/**/*.py", "tests/**/*.py"]:
            for f in self.project_root.glob(pattern):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime > recent_cutoff:
                        if "test" in str(f):
                            work_detected["test_files"].append(str(f))
                        else:
                            work_detected["src_files"].append(str(f))
                except OSError:
                    continue

        return work_detected if work_detected["src_files"] or work_detected["test_files"] else None

    def get_milestone_updates(self):
        """Get recent milestone file updates."""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=6)

        updates = {"milestone_files": [], "memory_updated": False}

        # Check milestone files
        for f in self.milestones_dir.rglob("tasks.yaml"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > recent_cutoff:
                    updates["milestone_files"].append(str(f))
            except OSError:
                continue

        # Check memory file
        try:
            if self.memory_file.exists():
                mtime = datetime.fromtimestamp(self.memory_file.stat().st_mtime)
                if mtime > recent_cutoff:
                    updates["memory_updated"] = True
        except OSError:
            pass

        return updates

    def validate_tracking_completeness(self, work_done, milestone_updates):
        """Validate that tracking matches work done."""
        issues = []

        # If work was done but no milestone updates
        if work_done and not milestone_updates["milestone_files"]:
            issues.append(
                {
                    "type": "missing_milestone_update",
                    "severity": "high",
                    "message": "Implementation work detected but no milestone files updated",
                }
            )

        # If work was done but no memory update
        if work_done and not milestone_updates["memory_updated"]:
            issues.append(
                {
                    "type": "missing_memory_update",
                    "severity": "high",
                    "message": "Implementation work detected but MEMORY.md not updated",
                }
            )

        # Check for active tasks
        active_tasks = self.get_active_tasks()
        if work_done and not active_tasks:
            issues.append(
                {
                    "type": "no_active_task",
                    "severity": "medium",
                    "message": "Work done but no task marked as 'in_progress'",
                }
            )

        return issues

    def get_active_tasks(self):
        """Find tasks marked as in_progress."""
        active_tasks = []

        for tasks_file in self.milestones_dir.rglob("tasks.yaml"):
            try:
                with open(tasks_file) as f:
                    data = yaml.safe_load(f)

                for task in data.get("tasks", []):
                    if task.get("status") == "in_progress":
                        active_tasks.append({"file": tasks_file, "task": task})
            except Exception:
                continue

        return active_tasks

    def run_validation(self):
        """Run comprehensive validation."""
        print("🔍 Validating milestone tracking compliance...")

        # Get recent work and updates
        work_done = self.get_recent_work()
        milestone_updates = self.get_milestone_updates()

        if not work_done:
            print("✅ No recent implementation work detected")
            return True

        print("📁 Recent work detected:")
        print(f"   - {len(work_done['src_files'])} source files")
        print(f"   - {len(work_done['test_files'])} test files")

        # Validate tracking
        issues = self.validate_tracking_completeness(work_done, milestone_updates)

        if not issues:
            print("✅ Milestone tracking is complete and up-to-date!")
            return True

        # Report issues
        print(f"\n⚠️  Found {len(issues)} tracking issues:")

        for issue in issues:
            severity_icon = "🚨" if issue["severity"] == "high" else "⚠️"
            print(f"   {severity_icon} {issue['message']}")

        # Provide fix suggestions
        print("\n🔧 To fix these issues:")
        if any(i["type"] == "missing_milestone_update" for i in issues):
            print("   1. Edit .quaestor/milestones/*/tasks.yaml")
            print("      - Mark completed subtasks with '# COMPLETED'")
            print("      - Update progress percentage")
            print("      - Add notes with timestamp")

        if any(i["type"] == "missing_memory_update" for i in issues):
            print("   2. Add entry to .quaestor/MEMORY.md")
            print("      - Use format: ### YYYY-MM-DD")
            print("      - Document what was completed")
            print("      - List files created/modified")

        if any(i["type"] == "no_active_task" for i in issues):
            print("   3. Update task status to 'in_progress'")
            print("      - Find the relevant task in milestones/")
            print("      - Set status: 'in_progress'")

        return len([i for i in issues if i["severity"] == "high"]) == 0


def main():
    """Run validation."""
    validator = MilestoneValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
