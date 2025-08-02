#!/usr/bin/env python3
"""Specification progress tracking and validation hook.

This hook monitors specification progress and ensures work is properly
tracked in specifications and MEMORY.md.
"""

import json
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


def check_spec_progress(project_root: Path) -> dict[str, Any]:
    """Check specification progress."""
    try:
        from quaestor.core.specifications import SpecificationManager, SpecStatus

        manager = SpecificationManager(project_root)
        all_specs = manager.list_specifications()

        if not all_specs:
            return {"status": "no_specs", "message": "No specifications found"}

        # Count specs by status
        status_counts = {}
        for status in SpecStatus:
            status_counts[status.value] = sum(1 for s in all_specs if s.status == status)

        completed = sum(
            1 for s in all_specs if s.status in [SpecStatus.IMPLEMENTED, SpecStatus.TESTED, SpecStatus.DEPLOYED]
        )

        progress = int((completed / len(all_specs)) * 100) if all_specs else 0

        return {
            "status": "active",
            "total_specs": len(all_specs),
            "completed_specs": completed,
            "progress": progress,
            "status_counts": status_counts,
            "complete": progress >= 100,
        }

    except ImportError:
        return {"status": "no_spec_system", "message": "Specification system not available"}
    except Exception as e:
        return {"status": "error", "message": f"Error checking specs: {e}"}


def get_recent_work(project_root: Path, hours: int = 6) -> dict[str, Any]:
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
            for f in project_root.glob(pattern):
                # Skip .quaestor directory
                if ".quaestor" in str(f):
                    continue

                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime > recent_cutoff:
                        relative_path = str(f.relative_to(project_root))

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


def check_spec_updates(project_root: Path, hours: int = 6) -> dict[str, Any]:
    """Check for recent specification and memory updates."""
    now = datetime.now()
    recent_cutoff = now - timedelta(hours=hours)

    specs_dir = project_root / ".quaestor" / "specifications"
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    updates = {"spec_files": [], "memory_updated": False, "timestamp": now.isoformat()}

    # Check specification files
    if specs_dir.exists():
        for f in specs_dir.glob("*.yaml"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > recent_cutoff:
                    updates["spec_files"].append(str(f.relative_to(project_root)))
            except OSError:
                continue

    # Check memory file
    try:
        if memory_file.exists():
            mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
            if mtime > recent_cutoff:
                updates["memory_updated"] = True
    except OSError:
        pass

    return updates


def validate_tracking(work_done: dict[str, Any], spec_updates: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate that tracking matches work done."""
    issues = []

    # Determine work type
    has_implementation = bool(work_done["src_files"])
    has_tests = bool(work_done["test_files"])

    # Check spec updates for implementation work
    if has_implementation and not spec_updates["spec_files"]:
        issues.append(
            {
                "type": "missing_spec_update",
                "severity": "high",
                "message": f"Implementation work detected ({len(work_done['src_files'])} files) - no spec update",
                "fix": "Update relevant specifications with progress or status changes",
            }
        )

    # Check memory updates for any significant work
    if (has_implementation or has_tests) and not spec_updates["memory_updated"]:
        issues.append(
            {
                "type": "missing_memory_update",
                "severity": "medium",
                "message": "Work completed but MEMORY.md not updated",
                "fix": "Update MEMORY.md with progress notes",
            }
        )

    return issues


def generate_spec_suggestion(spec_status: dict[str, Any], issues: list[dict[str, Any]]) -> tuple[bool, str]:
    """Generate specification-related suggestions.

    Returns:
        Tuple of (should_block, message)
    """

    # High severity issues should block
    high_severity_issues = [i for i in issues if i["severity"] == "high"]
    if high_severity_issues:
        issue_messages = "\n".join([f"• {issue['message']}" for issue in high_severity_issues])
        fixes = "\n".join([f"• {issue['fix']}" for issue in high_severity_issues])

        return (
            True,
            f"""
🚫 SPECIFICATION TRACKING ISSUES DETECTED!

The following issues must be resolved:
{issue_messages}

Required actions:
{fixes}

Please run: Use the planner agent to update specification tracking

The planner should:
1. Review completed work
2. Update specification status
3. Ensure MEMORY.md reflects current state
4. Mark specifications as implemented/tested where appropriate
""",
        )

    # Check specification completion
    if spec_status.get("complete", False) and spec_status.get("status") == "active":
        total = spec_status.get("total_specs", 0)
        completed = spec_status.get("completed_specs", 0)
        return (
            True,
            f"""
🎉 ALL SPECIFICATIONS COMPLETE: {completed}/{total} specifications done!

Time to wrap up this development phase:

Please run: Use the planner agent to finalize the specification cycle

The planner should:
1. Create a comprehensive completion summary
2. Document lessons learned
3. Update project MEMORY.md
4. Plan next development phase
5. Consider creating a release/PR

Congratulations on completing all specifications!
""",
        )

    # Medium severity issues - provide guidance but don't block
    if issues:
        issue_messages = "\n".join([f"• {issue['message']}" for issue in issues])
        return (
            False,
            f"""
⚠️  Tracking Reminders:
{issue_messages}

Consider updating tracking files when convenient.
""",
        )

    # No blocking suggestion needed
    return False, None


def main():
    """Main hook entry point."""
    project_root = get_project_root()

    # Check specification status
    spec_status = check_spec_progress(project_root)

    # Check for recent work
    work_done = get_recent_work(project_root)

    # Check for specification updates
    spec_updates = check_spec_updates(project_root) if work_done else {"spec_files": [], "memory_updated": False}

    # Validate tracking
    issues = validate_tracking(work_done, spec_updates) if work_done else []

    # Generate suggestions
    should_block, message = generate_spec_suggestion(spec_status, issues)

    if should_block and message:
        print(message.strip(), file=sys.stderr)
        return 1
    elif message:
        print(message.strip())

    # Provide status update if no issues
    if spec_status.get("status") == "active" and not issues:
        progress = spec_status.get("progress", 0)
        total = spec_status.get("total_specs", 0)
        completed = spec_status.get("completed_specs", 0)
        print(f"📊 Specifications: {completed}/{total} complete ({progress}%)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
