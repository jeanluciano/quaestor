#!/usr/bin/env python3
"""Comprehensive compliance check for all Quaestor requirements."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml


class ComplianceChecker:
    """Check all Quaestor compliance requirements."""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.milestones_dir = self.project_root / ".quaestor" / "milestones"
        self.memory_file = self.project_root / ".quaestor" / "MEMORY.md"
        self.critical_rules = self.project_root / ".quaestor" / "CRITICAL_RULES.md"
        self.workflow_state = self.project_root / ".quaestor" / ".workflow_state"

    def check_milestone_awareness(self):
        """Check if there's an active milestone task."""
        issues = []

        if not self.milestones_dir.exists():
            issues.append(
                {
                    "type": "missing_milestones",
                    "severity": "medium",
                    "message": "No .quaestor/milestones directory found",
                }
            )
            return issues

        # Look for active tasks
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

        if not active_tasks:
            issues.append(
                {
                    "type": "no_active_task",
                    "severity": "high",
                    "message": "No task marked as 'in_progress' in milestone files",
                    "fix": "Update a task status to 'in_progress' before starting work",
                }
            )

        return issues

    def check_recent_work_tracking(self):
        """Check if recent work has been tracked properly."""
        issues = []
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=2)

        # Check for recent files
        recent_files = []
        for pattern in ["src/**/*.py", "tests/**/*.py", "**/*.md"]:
            for f in self.project_root.glob(pattern):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime > recent_cutoff:
                        recent_files.append((f, mtime))
                except OSError:
                    continue

        if not recent_files:
            return issues  # No recent work

        # Check if milestone files were also updated
        milestone_updated = False
        memory_updated = False

        for f, _mtime in recent_files:
            if "milestones" in str(f) and f.name == "tasks.yaml":
                milestone_updated = True
            if f.name == "MEMORY.md":
                memory_updated = True

        # Filter out only implementation files
        impl_files = [f for f, mtime in recent_files if str(f).endswith(".py") and "src/" in str(f)]

        if impl_files and not milestone_updated:
            issues.append(
                {
                    "type": "untracked_implementation",
                    "severity": "high",
                    "message": f"Found {len(impl_files)} recently modified source files but no milestone updates",
                    "fix": "Update relevant .quaestor/milestones/*/tasks.yaml with completed subtasks",
                }
            )

        if impl_files and not memory_updated:
            issues.append(
                {
                    "type": "missing_memory_entry",
                    "severity": "high",
                    "message": "Implementation work done but MEMORY.md not updated",
                    "fix": "Add progress log entry to .quaestor/MEMORY.md",
                }
            )

        return issues

    def check_memory_quality(self):
        """Check quality of MEMORY.md entries."""
        issues = []

        if not self.memory_file.exists():
            issues.append({"type": "missing_memory", "severity": "medium", "message": "MEMORY.md file not found"})
            return issues

        try:
            content = self.memory_file.read_text()
            today = datetime.now().strftime("%Y-%m-%d")

            # Check for generic entries
            generic_entries = content.count("- Completed tasks from TODO list")
            if generic_entries > 0:
                issues.append(
                    {
                        "type": "generic_memory_entries",
                        "severity": "medium",
                        "message": f"Found {generic_entries} generic memory entries",
                        "fix": "Replace with specific progress details",
                    }
                )

            # Check for recent detailed entries
            if f"### {today}" in content:
                today_section = content.split(f"### {today}")[-1]
                if len(today_section.strip()) < 100:  # Very short entry
                    issues.append(
                        {
                            "type": "insufficient_detail",
                            "severity": "medium",
                            "message": "Today's memory entry lacks detail",
                            "fix": "Add more specific information about what was completed",
                        }
                    )

        except Exception as e:
            issues.append(
                {"type": "memory_read_error", "severity": "low", "message": f"Could not analyze MEMORY.md: {e}"}
            )

        return issues

    def check_workflow_state(self):
        """Check workflow state consistency."""
        issues = []

        if not self.workflow_state.exists():
            return issues  # Optional file

        try:
            import json

            with open(self.workflow_state) as f:
                state = json.load(f)

            phase = state.get("phase", "idle")
            files_examined = state.get("files_examined", 0)

            if phase == "implementing" and files_examined < 3:
                issues.append(
                    {
                        "type": "insufficient_research",
                        "severity": "medium",
                        "message": f"In implementation phase but only examined {files_examined} files",
                        "fix": "Research more of the codebase before continuing",
                    }
                )

        except Exception:
            pass  # Ignore workflow state issues

        return issues

    def generate_report(self):
        """Generate comprehensive compliance report."""
        print("🔍 COMPREHENSIVE COMPLIANCE CHECK")
        print("=" * 50)

        all_issues = []

        # Run all checks
        checks = [
            ("Milestone Awareness", self.check_milestone_awareness),
            ("Work Tracking", self.check_recent_work_tracking),
            ("Memory Quality", self.check_memory_quality),
            ("Workflow State", self.check_workflow_state),
        ]

        for check_name, check_func in checks:
            print(f"\n📋 {check_name}...")
            issues = check_func()
            all_issues.extend(issues)

            if not issues:
                print(f"   ✅ {check_name}: COMPLIANT")
            else:
                for issue in issues:
                    severity_icon = (
                        "🚨" if issue["severity"] == "high" else "⚠️" if issue["severity"] == "medium" else "💡"
                    )
                    print(f"   {severity_icon} {issue['message']}")
                    if "fix" in issue:
                        print(f"      Fix: {issue['fix']}")

        # Summary
        high_issues = [i for i in all_issues if i["severity"] == "high"]
        medium_issues = [i for i in all_issues if i["severity"] == "medium"]

        print("\n📊 COMPLIANCE SUMMARY:")
        print(f"   🚨 High Priority Issues: {len(high_issues)}")
        print(f"   ⚠️  Medium Priority Issues: {len(medium_issues)}")
        print(f"   💡 Low Priority Issues: {len(all_issues) - len(high_issues) - len(medium_issues)}")

        if not all_issues:
            print("\n🎉 FULL COMPLIANCE ACHIEVED!")
            print("   All Quaestor requirements are being followed correctly.")
        else:
            print("\n🔧 ACTION REQUIRED:")
            print(f"   Please address the {len(high_issues)} high priority issues first.")

        return len(high_issues) == 0


def main():
    """Run comprehensive compliance check."""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    checker = ComplianceChecker(project_root)
    success = checker.generate_report()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
