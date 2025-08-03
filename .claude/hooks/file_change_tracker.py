#!/usr/bin/env python3
"""Track file changes and remind about specification updates."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from quaestor.claude.hooks.base import BaseHook
from quaestor.claude.hooks.shared_utils import (
    format_drive_hint,
    format_framework_guidance,
    get_session_mode,
    measure_performance,
    should_show_hint,
    silent_track,
)


class FileChangeTracker(BaseHook):
    """Track file changes with mode-aware notifications."""

    def __init__(self):
        super().__init__("file_change_tracker")
        self.project_root = Path(".")

    def execute(self):
        """Track file changes with mode-aware behavior."""
        with measure_performance("file_change_tracking") as metrics:
            self._track_changes()

        # Log performance if it exceeded target
        if metrics.get("exceeded_target"):
            self.logger.warning(f"File tracking took {metrics['duration_ms']:.1f}ms")

    def _track_changes(self):
        """Detect recent file changes and provide appropriate guidance."""
        mode = get_session_mode()
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # Track different types of changes
        changes = {"src_files": [], "test_files": [], "config_files": [], "doc_files": []}

        # Check for recent changes with performance tracking
        with measure_performance("file_scanning"):
            for pattern_info in [
                ("src/**/*.py", "src_files"),
                ("tests/**/*.py", "test_files"),
                ("**/*.yaml", "config_files"),
                ("**/*.md", "doc_files"),
            ]:
                pattern, category = pattern_info
                for file_path in self.project_root.glob(pattern):
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

        # Track changes silently for analysis
        silent_track(
            hook_name=self.hook_name,
            event_type="files_changed",
            data={
                "total_changes": total_changes,
                "src_files": len(changes["src_files"]),
                "test_files": len(changes["test_files"]),
                "config_files": len(changes["config_files"]),
                "doc_files": len(changes["doc_files"]),
            },
        )

        # Mode-specific behavior
        if mode == "drive":
            self._handle_drive_mode(changes, total_changes)
        else:
            self._handle_framework_mode(changes, total_changes)

    def _handle_drive_mode(self, changes: dict, total_changes: int):
        """Handle file changes in drive mode (minimal intervention)."""
        # Only show hints for significant changes
        if total_changes < 5:
            return

        # Check if we should show hints
        if not should_show_hint(self.hook_name, "file_changes", timedelta(minutes=30)):
            return

        # Check if specification updates are missing
        specification_updated = any("specs" in f for f in changes["config_files"])

        if (changes["src_files"] or changes["test_files"]) and not specification_updated:
            hint = format_drive_hint(
                f"You've changed {len(changes['src_files']) + len(changes['test_files'])} implementation files",
                level="minimal",
                context={"suggested_command": "review"},
            )
            print(hint)

            # Track that we showed a hint
            silent_track(
                hook_name=self.hook_name,
                event_type="hint_shown",
                data={"hint_type": "missing_specs", "file_count": total_changes},
            )

    def _handle_framework_mode(self, changes: dict, total_changes: int):
        """Handle file changes in framework mode (full assistance)."""
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
            guidance = format_framework_guidance(
                "Implementation detected - please update specifications",
                urgency="high" if total_changes > 10 else "medium",
                context={"current_phase": "implementation", "next_action": "Update specs and MEMORY.md"},
            )
            print(f"\n{guidance}")

            print("   1. Mark completed subtasks in .quaestor/specs/*.yaml")
            print("   2. Update progress percentage")
            print("   3. Add progress log entry to .quaestor/MEMORY.md")

            if changes["test_files"]:
                print("   4. Document test coverage improvements")

        # Check if specification files were also updated
        specification_updated = any("specs" in f for f in changes["config_files"])
        memory_updated = any("MEMORY.md" in f for f in changes["doc_files"])

        if not specification_updated:
            print("\n⚠️  MISSING: Specification files not updated")
            print("   You changed implementation files but didn't update specifications")

        if not memory_updated:
            print("\n⚠️  MISSING: MEMORY.md not updated")
            print("   Add a progress log entry for your changes")

        if specification_updated and memory_updated:
            print("\n✅ Good tracking! Both specifications and memory updated")


def track_file_changes():
    """Legacy entry point for backward compatibility."""
    tracker = FileChangeTracker()
    tracker.run()


if __name__ == "__main__":
    track_file_changes()
    sys.exit(0)
