#!/usr/bin/env python3
"""Memory and specification synchronization hook with dual-mode behavior.

This hook updates MEMORY.md and specification files based on TODO completions
and detected work progress. Adapts behavior based on session mode:
- Framework mode: Enforce MEMORY.md updates, block on missing progress documentation
- Drive mode: Silent progress tracking, gentle reminders without blocking
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root


class MemoryTrackerHook(BaseHook):
    """Memory tracking hook with mode-aware behavior."""

    def __init__(self):
        super().__init__("memory_tracker")
        self.project_root = get_project_root()

    def execute(self):
        """Execute memory tracking with mode-aware behavior."""
        # Extract completed specifications
        completed_specs = self.extract_completed_specs()

        # Get recent work and memory status
        recent_work = self.detect_recent_work()
        memory_staleness = self.check_memory_staleness()
        spec_info = self.get_active_specification_info()

        # Track silently in drive mode
        if self.is_drive_mode():
            self.silent_track(
                "memory_status",
                {
                    "completed_specs": len(completed_specs),
                    "has_recent_work": recent_work is not None,
                    "memory_stale": memory_staleness.get("is_stale", False),
                    "spec_progress": spec_info.get("progress", 0) if spec_info else 0,
                },
            )

        # Generate mode-appropriate suggestions
        should_block, message = self.generate_mode_aware_suggestion(
            completed_specs, recent_work, memory_staleness, spec_info
        )

        if should_block and message:
            self.output_error(message.strip(), blocking=True)
        elif message:
            self.output_success(message.strip())
        else:
            # Update memory if appropriate
            if completed_specs and self.is_framework_mode():
                self.update_memory_file(completed_specs, spec_info)
                self.output_success(f"Updated MEMORY.md with {len(completed_specs)} completed specifications")
            else:
                self.output_success("Memory tracking analysis complete")

    def extract_completed_specs(self) -> list[dict[str, Any]]:
        """Extract completed specifications from hook data."""
        completed_specs = []

        # Check if this is a specification update event
        tool_name = self.input_data.get("tool_name", "")
        if tool_name not in ["Edit", "Write", "MultiEdit"]:
            return completed_specs

        # Check if we're updating specification status
        tool_input = self.input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        if "specifications" in file_path or "MEMORY.md" in file_path:
            # Extract spec status updates from content
            new_content = tool_input.get("new_string", "")
            if new_content and ("IMPLEMENTED" in new_content or "TESTED" in new_content):
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

    def detect_recent_work(self, hours: int = 6) -> dict[str, Any] | None:
        """Detect recent implementation work."""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=hours)

        work_detected = {
            "src_files": [],
            "test_files": [],
            "config_files": [],
            "doc_files": [],
            "timestamp": now.isoformat(),
        }

        # Define patterns to check
        patterns = {
            "src": ["src/**/*.py", "src/**/*.js", "src/**/*.ts", "src/**/*.go", "src/**/*.rs"],
            "test": ["tests/**/*.py", "test/**/*.js", "**/*_test.go", "**/*.test.ts"],
            "config": ["*.json", "*.yaml", "*.yml", "*.toml"],
            "docs": ["**/*.md", "docs/**/*"],
        }

        # Check for recent files
        for category, file_patterns in patterns.items():
            for pattern in file_patterns:
                for f in self.project_root.glob(pattern):
                    # Skip .quaestor directory
                    if ".quaestor" in str(f):
                        continue

                    try:
                        mtime = datetime.fromtimestamp(f.stat().st_mtime)
                        if mtime > recent_cutoff:
                            relative_path = str(f.relative_to(self.project_root))

                            if category == "src":
                                work_detected["src_files"].append(relative_path)
                            elif category == "test":
                                work_detected["test_files"].append(relative_path)
                            elif category == "config":
                                work_detected["config_files"].append(relative_path)
                            elif category == "docs":
                                work_detected["doc_files"].append(relative_path)
                    except OSError:
                        continue

        # Check if any work was detected
        has_work = any(
            [
                work_detected["src_files"],
                work_detected["test_files"],
                work_detected["config_files"],
                work_detected["doc_files"],
            ]
        )

        return work_detected if has_work else None

    def check_memory_staleness(self) -> dict[str, Any]:
        """Check if MEMORY.md is stale compared to recent activity."""
        memory_file = self.project_root / ".quaestor" / "MEMORY.md"

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

    def get_active_specification_info(self) -> dict[str, Any] | None:
        """Get information about the currently active specification."""
        memory_file = self.project_root / ".quaestor" / "MEMORY.md"

        if not memory_file.exists():
            return None

        try:
            content = memory_file.read_text()
            spec_match = re.search(r"current_specification:\s*['\"]?([^'\"]+)['\"]?", content)
            progress_match = re.search(r"progress:\s*(\d+)%", content)

            if spec_match:
                return {"id": spec_match.group(1), "progress": int(progress_match.group(1)) if progress_match else 0}
        except Exception:
            pass

        return None

    def update_memory_file(
        self, completed_specs: list[dict[str, Any]], spec_info: dict[str, Any] | None = None
    ) -> bool:
        """Update MEMORY.md with completed specifications."""
        memory_file = self.project_root / ".quaestor" / "MEMORY.md"

        if not memory_file.exists():
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

        except Exception:
            return False

    def generate_mode_aware_suggestion(
        self,
        completed_specs: list[dict[str, Any]],
        recent_work: dict[str, Any] | None,
        memory_staleness: dict[str, Any],
        spec_info: dict[str, Any] | None,
    ) -> tuple[bool, str]:
        """Generate mode-appropriate documentation suggestions."""
        if self.is_drive_mode():
            return self._generate_drive_mode_suggestion(completed_specs, recent_work, memory_staleness, spec_info)
        else:
            return self._generate_framework_mode_suggestion(completed_specs, recent_work, memory_staleness, spec_info)

    def _generate_drive_mode_suggestion(
        self,
        completed_specs: list[dict[str, Any]],
        recent_work: dict[str, Any] | None,
        memory_staleness: dict[str, Any],
        spec_info: dict[str, Any] | None,
    ) -> tuple[bool, str]:
        """Generate non-intrusive suggestions for drive mode."""
        # In drive mode, provide gentle hints without blocking

        # Only hint if memory is very stale
        if memory_staleness.get("is_stale") and memory_staleness.get("hours_old", 0) > 48:
            return (
                False,  # Never block in drive mode
                self.format_drive_hint("Project memory could use an update when convenient"),
            )

        # Hint if lots of work without documentation
        if recent_work:
            work_count = sum([len(recent_work.get("src_files", [])), len(recent_work.get("test_files", []))])
            if work_count > 10:
                return (
                    False,
                    self.format_drive_hint(f"Consider documenting recent work ({work_count} files modified)"),
                )

        # No message needed
        return False, None

    def _generate_framework_mode_suggestion(
        self,
        completed_specs: list[dict[str, Any]],
        recent_work: dict[str, Any] | None,
        memory_staleness: dict[str, Any],
        spec_info: dict[str, Any] | None,
    ) -> tuple[bool, str]:
        """Generate framework mode suggestions with enforcement."""
        # Scenario 1: Many specifications completed but memory is stale
        if len(completed_specs) > 3 and memory_staleness.get("is_stale", False):
            return (
                True,
                f"""📚 DOCUMENTATION LAG DETECTED!

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

        # Scenario 2: Significant work without memory updates
        if recent_work and memory_staleness.get("is_stale"):
            work_count = sum([len(recent_work.get("src_files", [])), len(recent_work.get("test_files", []))])

            if work_count > 5:
                return (
                    True,
                    f"""📝 MEMORY UPDATE REQUIRED!

Detected {work_count} file changes but MEMORY.md is stale: {memory_staleness.get("reason", "not updated")}.

Please run: Update MEMORY.md with recent progress

Key areas to document:
1. What was implemented/changed
2. Key design decisions made
3. Problems encountered and solutions
4. Progress on current specification
5. Next steps planned

This ensures continuity and knowledge retention.
""",
                )

        # Scenario 3: Specification nearing completion without proper documentation
        if spec_info and spec_info.get("progress", 0) >= 80:
            return (
                True,
                f"""📖 SPECIFICATION DOCUMENTATION NEEDED!

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

        # Scenario 4: Pattern changes detected
        high_priority_completed = sum(1 for t in completed_specs if t.get("priority") == "high")
        if high_priority_completed >= 3:
            spec_content = "\n".join([f"- {t.get('content', '')}" for t in completed_specs[:5]])

            if any(word in spec_content.lower() for word in ["refactor", "redesign", "migrate", "update pattern"]):
                return (
                    True,
                    f"""🏗️ ARCHITECTURAL CHANGES DETECTED!

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
    hook = MemoryTrackerHook()
    hook.run()


if __name__ == "__main__":
    main()
