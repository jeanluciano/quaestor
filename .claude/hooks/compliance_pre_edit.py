#!/usr/bin/env python3
"""Check compliance before edits and suggest appropriate agents.

This hook enforces Quaestor's workflow requirements before allowing file edits.
It ensures proper research and planning phases are completed before implementation.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.mode_detector import is_drive_mode


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


def is_implementation_file(file_path: str) -> bool:
    """Check if the file is an implementation file (not test/docs/config)."""
    path = Path(file_path)

    # Skip non-implementation files
    if any(part in path.parts for part in [".quaestor", ".claude", "tests", "test", "docs", "__pycache__"]):
        return False

    # Skip configuration, setup, and build files
    if path.name in ["setup.py", "pyproject.toml", "package.json", "Makefile", "requirements.txt"]:
        return False

    # Skip hook files specifically
    if "hooks" in path.parts:
        return False

    # Check if it's a source code file
    implementation_extensions = {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c"}
    return path.suffix in implementation_extensions and "src" in str(path)


def check_specification_awareness(project_root: Path) -> dict[str, Any]:
    """Check if there's an active specification being worked on."""
    specs_dir = project_root / ".quaestor" / "specs"

    if not specs_dir.exists():
        return {"has_active": False, "reason": "No specifications directory"}

    # Look for in_progress tasks
    for spec_file in specs_dir.rglob("*.yaml"):
        try:
            with open(spec_file) as f:
                content = f.read()
                if "status: in_progress" in content or "status: 'in_progress'" in content:
                    return {"has_active": True, "specification": spec_file.stem, "file": str(spec_file)}
        except Exception:
            continue

    return {"has_active": False, "reason": "No active specification tasks"}


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Extract file path
    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        # No file path, allow operation
        sys.exit(0)

    # CRITICAL: Check if we're in drive mode - if so, skip ALL enforcement
    if is_drive_mode():
        # In drive mode, users have full control
        sys.exit(0)

    # We're in framework mode - enforce workflow rules

    # Skip checks for non-implementation files
    if not is_implementation_file(file_path):
        sys.exit(0)

    # Check specification status
    specification_status = check_specification_awareness(project_root)

    # In framework mode, we require an active specification
    if not specification_status["has_active"]:
        message = f"""
⚠️ FRAMEWORK MODE: No active specification found.

File to edit: {file_path}

In framework mode, all implementation work must be tracked in a specification.

Please run: Use the planner agent to create a specification for this work

The planner should:
1. Define the scope of changes
2. Break down into subtasks
3. Set success criteria
4. Create specification in .quaestor/specs/

This ensures proper tracking and helps with PR creation later.
"""
        print(message.strip(), file=sys.stderr)
        sys.exit(2)

    # If we get here, the edit is allowed in framework mode
    print(f"✅ Framework mode: Specification '{specification_status['specification']}' is active")
    sys.exit(0)


if __name__ == "__main__":
    main()
