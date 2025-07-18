#!/usr/bin/env python3
"""Track file changes and remind about milestone updates."""

import sys
from datetime import datetime, timedelta
from pathlib import Path


def track_file_changes():
    """Detect recent file changes and remind about milestone tracking."""

    project_root = Path(".")
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)

    # Track different types of changes
    changes = {"src_files": [], "test_files": [], "config_files": [], "doc_files": []}

    # Check for recent changes
    for pattern_info in [
        ("src/**/*.py", "src_files"),
        ("tests/**/*.py", "test_files"),
        ("**/*.yaml", "config_files"),
        ("**/*.md", "doc_files"),
    ]:
        pattern, category = pattern_info
        for file_path in project_root.glob(pattern):
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime > one_hour_ago:
                    changes[category].append(str(file_path))
            except OSError:
                continue

    # Analyze changes
    total_changes = sum(len(files) for files in changes.values())

    if total_changes == 0:
        return  # No recent changes

    print(f"\n📁 DETECTED {total_changes} RECENT FILE CHANGES:")

    for category, files in changes.items():
        if files:
            print(f"   {category}: {len(files)} files")
            for f in files[:3]:  # Show first 3
                print(f"     - {f}")
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more")

    # Smart reminders based on change types
    if changes["src_files"] or changes["test_files"]:
        print("\n🎯 MILESTONE UPDATE REQUIRED:")
        print("   Implementation detected - please update:")
        print("   1. Mark completed subtasks in .quaestor/milestones/*/tasks.yaml")
        print("   2. Update progress percentage")
        print("   3. Add progress log entry to .quaestor/MEMORY.md")

        if changes["test_files"]:
            print("   4. Document test coverage improvements")

    # Check if milestone files were also updated
    milestone_updated = any("milestones" in f for f in changes["config_files"])
    memory_updated = any("MEMORY.md" in f for f in changes["doc_files"])

    if not milestone_updated:
        print("\n⚠️  MISSING: Milestone files not updated")
        print("   You changed implementation files but didn't update milestones")

    if not memory_updated:
        print("\n⚠️  MISSING: MEMORY.md not updated")
        print("   Add a progress log entry for your changes")

    if milestone_updated and memory_updated:
        print("\n✅ Good tracking! Both milestones and memory updated")


if __name__ == "__main__":
    track_file_changes()
    sys.exit(0)
