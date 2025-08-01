#!/usr/bin/env python3
"""Hook to track specification-to-branch linkage.

This hook monitors git operations to automatically link branches to specifications
and ensure spec-driven development workflow is followed.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from quaestor.core.specifications import SpecificationManager, SpecStatus


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


def get_current_branch() -> str | None:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def extract_spec_id_from_branch(branch: str) -> str | None:
    """Extract specification ID from branch name.

    Expected patterns:
    - feat/spec-{id}-{title}
    - fix/spec-{id}-{title}
    - spec/{id}-{title}
    """
    patterns = [
        r"feat/spec-([a-zA-Z]+-[a-zA-Z0-9-]+)",
        r"fix/spec-([a-zA-Z]+-[a-zA-Z0-9-]+)",
        r"spec/([a-zA-Z]+-[a-zA-Z0-9-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, branch)
        if match:
            return match.group(1)

    return None


def suggest_spec_branch_name(spec_id: str, title: str) -> str:
    """Generate suggested branch name for a specification."""
    # Clean title for branch name
    clean_title = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower())
    clean_title = clean_title.strip("-")[:30]  # Limit length

    # Determine prefix based on spec type
    if spec_id.startswith("feat"):
        prefix = "feat"
    elif spec_id.startswith("fix"):
        prefix = "fix"
    else:
        prefix = "spec"

    return f"{prefix}/spec-{spec_id}-{clean_title}"


def check_branch_spec_linkage(project_root: Path, branch: str) -> dict[str, Any]:
    """Check if branch is properly linked to a specification."""
    spec_manager = SpecificationManager(project_root)

    # Check if branch is already linked
    existing_spec = spec_manager.get_spec_by_branch(branch)
    if existing_spec:
        return {
            "linked": True,
            "spec": existing_spec,
            "message": f"Branch linked to spec: {existing_spec.id} - {existing_spec.title}",
        }

    # Try to extract spec ID from branch name
    spec_id = extract_spec_id_from_branch(branch)
    if spec_id:
        spec = spec_manager.get_specification(spec_id)
        if spec:
            # Auto-link if not already linked
            spec_manager.link_spec_to_branch(spec_id, branch)
            return {
                "linked": True,
                "spec": spec,
                "auto_linked": True,
                "message": f"Auto-linked branch to spec: {spec.id} - {spec.title}",
            }
        else:
            return {
                "linked": False,
                "spec_id": spec_id,
                "error": f"Spec ID '{spec_id}' found in branch name but specification doesn't exist",
            }

    return {
        "linked": False,
        "message": "Branch not linked to any specification",
    }


def check_spec_workflow(hook_data: dict[str, Any]) -> tuple[bool, str | None]:
    """Check specification workflow compliance.

    Returns:
        Tuple of (should_block, message)
    """
    project_root = get_project_root()
    current_branch = get_current_branch()

    if not current_branch or current_branch in ["main", "master", "develop"]:
        return False, None

    # Check branch linkage
    linkage = check_branch_spec_linkage(project_root, current_branch)

    # Check what operation is being performed
    operation = hook_data.get("operation", "unknown")

    if operation == "pre-commit":
        if not linkage["linked"]:
            return (
                True,
                f"""
🚫 SPEC TRACKING: Commits must be associated with a specification!

Current branch '{current_branch}' is not linked to any specification.

Please run: Use the planner agent to create a specification for this work

The planner agent should:
1. Analyze the changes being made
2. Create a specification with clear contract and acceptance criteria
3. Link the specification to this branch
4. Update the branch name if needed to follow spec naming convention

Suggested branch naming: feat/spec-{{id}}-{{brief-title}}
""",
            )

        # Check if spec is in appropriate status
        spec = linkage["spec"]
        if spec.status == SpecStatus.DRAFT:
            return (
                False,
                f"""
⚠️  Spec '{spec.id}' is still in DRAFT status.
Consider updating to IN_PROGRESS before major commits.
""",
            )

    elif operation == "pre-push":
        if not linkage["linked"]:
            return True, "Cannot push changes without specification linkage"

        spec = linkage["spec"]
        if spec.status not in [SpecStatus.IN_PROGRESS, SpecStatus.IMPLEMENTED, SpecStatus.TESTED]:
            return (
                True,
                f"""
🚫 SPEC STATUS: Cannot push specification in {spec.status.value} status!

Spec '{spec.id}' must be IN_PROGRESS or later to push changes.

Please run: Use the spec-manager agent to update specification status

The spec-manager agent should:
1. Review the specification requirements
2. Update status to IN_PROGRESS if work has started
3. Ensure acceptance criteria are clear
4. Document any changes to the specification
""",
            )

    elif operation == "branch-create":
        # Suggest specification creation for new branches
        if not linkage["linked"]:
            return (
                False,
                f"""
💡 NEW BRANCH: Consider creating a specification for '{current_branch}'

Use the planner agent to:
1. Create a specification for your planned work
2. Link it to this branch for tracking
3. Define clear acceptance criteria

This ensures all work is properly documented and tracked.
""",
            )

    # Non-blocking status message
    if linkage.get("auto_linked"):
        return False, linkage["message"]
    elif linkage["linked"]:
        spec = linkage["spec"]
        return False, f"✅ Working on spec '{spec.id}' ({spec.status.value})"

    return False, None


def main():
    """Main hook entry point."""
    hook_data = parse_hook_input()

    # Add current operation context
    if not hook_data.get("operation"):
        # Try to detect operation from git state
        try:
            # Check if we're in a commit
            subprocess.run(["git", "diff", "--cached", "--quiet"], check=True)
            hook_data["operation"] = "unknown"
        except subprocess.CalledProcessError:
            hook_data["operation"] = "pre-commit"

    should_block, message = check_spec_workflow(hook_data)

    if should_block and message:
        print(message.strip(), file=sys.stderr)
        return 1
    elif message:
        print(message.strip())

    return 0


if __name__ == "__main__":
    sys.exit(main())
