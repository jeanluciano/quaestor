#!/usr/bin/env python3
"""Comprehensive milestone tracking and validation hook.

This hook combines milestone progress checking and validation to ensure
work is properly tracked in milestone files and MEMORY.md.
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


def check_milestone_completion(project_root: Path) -> dict[str, Any]:
    """Check if current milestone is complete based on MEMORY.md."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    if not memory_file.exists():
        return {"status": "no_memory", "message": "MEMORY.md not found"}

    try:
        content = memory_file.read_text()

        # Look for milestone progress
        milestone_pattern = r"current_milestone:\s*['\"]?([^'\"]+)['\"]?"
        progress_pattern = r"progress:\s*(\d+)%"

        milestone_match = re.search(milestone_pattern, content)
        progress_match = re.search(progress_pattern, content)

        if milestone_match and progress_match:
            milestone = milestone_match.group(1)
            progress = int(progress_match.group(1))

            return {"status": "active", "milestone": milestone, "progress": progress, "complete": progress >= 100}
        else:
            return {"status": "no_milestone", "message": "No active milestone found"}

    except Exception as e:
        return {"status": "error", "message": f"Error checking milestone: {e}"}


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


def check_milestone_updates(project_root: Path, hours: int = 6) -> dict[str, Any]:
    """Check for recent milestone and memory updates."""
    now = datetime.now()
    recent_cutoff = now - timedelta(hours=hours)

    milestones_dir = project_root / ".quaestor" / "milestones"
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    updates = {"milestone_files": [], "memory_updated": False, "timestamp": now.isoformat()}

    # Check milestone files
    if milestones_dir.exists():
        for f in milestones_dir.rglob("tasks.yaml"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > recent_cutoff:
                    updates["milestone_files"].append(str(f.relative_to(project_root)))
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


def validate_tracking(work_done: dict[str, Any], milestone_updates: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate that tracking matches work done."""
    issues = []

    # Determine work type
    has_implementation = bool(work_done["src_files"])
    has_tests = bool(work_done["test_files"])
    has_docs = bool(work_done["doc_files"])

    # Check milestone updates for implementation work
    if has_implementation and not milestone_updates["milestone_files"]:
        issues.append(
            {
                "type": "missing_milestone_update",
                "severity": "high",
                "message": f"Implementation work detected ({len(work_done['src_files'])} files) but no milestone files updated",
                "fix": "Update relevant .quaestor/milestones/*/tasks.yaml with progress",
            }
        )

    # Check memory updates for any significant work
    if (has_implementation or has_tests) and not milestone_updates["memory_updated"]:
        issues.append(
            {
                "type": "missing_memory_update",
                "severity": "high",
                "message": "Implementation/test work detected but MEMORY.md not updated",
                "fix": "Add progress entry to .quaestor/MEMORY.md",
            }
        )

    # Documentation work is lower priority
    if has_docs and not has_implementation and not milestone_updates["memory_updated"]:
        issues.append(
            {
                "type": "undocumented_docs",
                "severity": "low",
                "message": "Documentation updates not tracked in MEMORY.md",
                "fix": "Consider adding a note about documentation updates",
            }
        )

    return issues


def generate_agent_suggestion(
    milestone_status: dict[str, Any], work_done: dict[str, Any] | None, issues: list[dict[str, Any]]
) -> tuple[bool, str]:
    """Generate agent suggestions based on milestone and work status.

    Returns:
        Tuple of (should_block, message)
    """

    # Scenario 1: Milestone complete - suggest PR creation
    if milestone_status.get("complete", False):
        milestone_name = milestone_status.get("milestone", "current milestone")
        return (
            True,
            f"""
🎉 Milestone '{milestone_name}' is 100% complete!

REQUIRED: Create a pull request for this completed milestone.

Please run: Use the milestone-manager agent to create a PR for the completed milestone '{milestone_name}'

The milestone-manager agent should:
1. Generate a comprehensive PR description from milestone objectives
2. List all completed tasks and features
3. Include test coverage information
4. Document any breaking changes
5. Create the PR using gh CLI
6. Update MEMORY.md with completion details
7. Archive the milestone and suggest next steps

This ensures proper documentation and review of your completed work.
""",
        )

    # Scenario 2: High severity tracking issues
    high_severity_issues = [i for i in issues if i["severity"] == "high"]
    if high_severity_issues:
        issue_descriptions = "\n".join([f"- {i['message']}" for i in high_severity_issues[:3]])
        return (
            True,
            f"""
⚠️ CRITICAL: Milestone tracking issues detected!

Found {len(high_severity_issues)} high-priority tracking issues:
{issue_descriptions}

Please run: Use the compliance-enforcer agent to fix milestone tracking issues

The compliance-enforcer agent should:
1. Update milestone files with current progress
2. Sync MEMORY.md with completed work
3. Mark completed subtasks appropriately
4. Calculate accurate progress percentages
5. Document any deviations from plan

Proper tracking ensures project visibility and helps with PR creation.
""",
        )

    # Scenario 3: Significant work without milestone
    if work_done and milestone_status["status"] == "no_milestone" and len(work_done.get("src_files", [])) > 3:
        return (
            True,
            f"""
📋 NO MILESTONE: Significant implementation work detected without an active milestone!

Found changes in:
- {len(work_done.get("src_files", []))} source files
- {len(work_done.get("test_files", []))} test files

Please run: Use the planner agent to create a milestone for this work

The planner agent should:
1. Analyze the scope of changes
2. Create a milestone in .quaestor/milestones/
3. Define objectives and success criteria
4. Break down into trackable subtasks
5. Set initial progress based on completed work

This ensures all work is properly tracked and documented.
""",
        )

    # Scenario 4: Approaching milestone completion
    if milestone_status["status"] == "active" and 80 <= milestone_status.get("progress", 0) < 100:
        milestone_name = milestone_status.get("milestone", "current milestone")
        return (
            False,
            f"""
🏁 Approaching Completion: Milestone '{milestone_name}' is {milestone_status["progress"]}% complete!

Consider using the milestone-manager agent to:
- Review remaining tasks
- Ensure all objectives are met
- Prepare for PR creation
- Plan the next milestone

You're almost there! Keep up the great work.
""",
        )

    # No blocking suggestion needed
    return False, None


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Check milestone status
    milestone_status = check_milestone_completion(project_root)

    # Check for recent work
    work_done = get_recent_work(project_root)

    # Check for milestone updates
    milestone_updates = (
        check_milestone_updates(project_root) if work_done else {"milestone_files": [], "memory_updated": False}
    )

    # Validate tracking
    issues = validate_tracking(work_done, milestone_updates) if work_done else []

    # Generate agent suggestion first
    should_block, agent_message = generate_agent_suggestion(milestone_status, work_done, issues)

    if should_block and agent_message:
        # Block with agent suggestion
        print(agent_message.strip(), file=sys.stderr)
        return 2

    # Regular status reporting (non-blocking)

    # Print milestone status
    if milestone_status["status"] == "active":
        milestone = milestone_status["milestone"]
        progress = milestone_status["progress"]

        if milestone_status["complete"]:
            print(f"🎉 Milestone '{milestone}' is complete! Consider creating a PR.")
        else:
            print(f"📊 Milestone '{milestone}' is {progress}% complete")
    elif milestone_status["status"] == "no_milestone":
        print("ℹ️  No active milestone found in MEMORY.md")

    if not work_done:
        print("✅ No recent implementation work detected")
    else:
        # Report recent work
        print("\n📁 Recent work detected:")
        if work_done["src_files"]:
            print(f"   - {len(work_done['src_files'])} source files")
        if work_done["test_files"]:
            print(f"   - {len(work_done['test_files'])} test files")
        if work_done["config_files"]:
            print(f"   - {len(work_done['config_files'])} config files")
        if work_done["doc_files"]:
            print(f"   - {len(work_done['doc_files'])} documentation files")

    if not issues:
        if work_done:
            print("\n✅ Milestone tracking is complete and up-to-date!")
    else:
        # Report non-critical issues
        medium_issues = [i for i in issues if i["severity"] == "medium"]
        if medium_issues:
            print("\n⚠️  Tracking suggestions:")
            for issue in medium_issues:
                print(f"   - {issue['message']}")
                print(f"     Fix: {issue['fix']}")

        # Low severity issues
        low_severity = [i for i in issues if i["severity"] == "low"]
        if low_severity:
            print("\n💡 Minor suggestions:")
            for issue in low_severity:
                print(f"   - {issue['message']}")

    # Add non-blocking agent message if any
    if not should_block and agent_message:
        print(f"\n{agent_message.strip()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
