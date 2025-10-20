#!/usr/bin/env python3
# /// script
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Load active specifications into session context at startup.

This hook injects the full content of active specifications into Claude's
context at session start, ensuring important project context survives
chat compaction and is immediately available in new sessions.

UV single-file script - no external dependencies on Quaestor package.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    # Fallback if yaml not available
    yaml = None


def read_input() -> dict[str, Any]:
    """Read JSON input from stdin."""
    if not sys.stdin.isatty():
        try:
            return json.loads(sys.stdin.read())
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def output_json(data: dict, exit_code: int = 0):
    """Output JSON to stdout and exit."""
    print(json.dumps(data, indent=2))
    sys.exit(exit_code)


def get_project_root() -> Path:
    """Find project root by looking for .quaestor directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def read_spec_frontmatter(spec_path: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from specification file."""
    if not spec_path.exists():
        return {}

    try:
        content = spec_path.read_text()

        # Simple frontmatter extraction (between --- delimiters)
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                if yaml:
                    return yaml.safe_load(frontmatter) or {}
                # Fallback: simple parsing
                return _parse_simple_yaml(frontmatter)
    except Exception as e:
        print(f"Warning: Could not read spec {spec_path}: {e}", file=sys.stderr)

    return {}


def _parse_simple_yaml(content: str) -> dict[str, Any]:
    """Simple YAML parser for basic key: value pairs."""
    result = {}
    for line in content.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def list_active_specs(project_root: Path) -> list[Path]:
    """List all active specification files."""
    specs_dir = project_root / ".quaestor" / "specs" / "active"
    if not specs_dir.exists():
        return []

    return sorted(specs_dir.glob("*.md"))


def generate_specification_context(project_root: Path, event_name: str) -> str:
    """Generate context containing full active specifications."""
    context_parts = [
        "<!-- QUAESTOR SESSION CONTEXT -->",
        "",
        "<!-- QUAESTOR ACTIVE SPECIFICATIONS -->",
        "> [!IMPORTANT]",
        "> **Active Specifications**: The following specifications are currently being worked on.",
        "> These define the current implementation tasks and acceptance criteria.",
        "",
    ]

    active_specs = list_active_specs(project_root)

    if active_specs:
        context_parts.append(f"## 📋 Active Specifications ({len(active_specs)})")
        context_parts.append("")

        for i, spec_path in enumerate(active_specs, 1):
            spec_content = format_specification(spec_path, i)
            context_parts.extend(spec_content)
    else:
        context_parts.extend(
            [
                "## 📋 No Active Specifications",
                "",
                "No specifications are currently active. Use `/plan` to create new specifications.",
                "",
            ]
        )

    context_parts.append("<!-- END QUAESTOR CONTEXT -->")

    return "\n".join(context_parts)


def format_specification(spec_path: Path, index: int) -> list[str]:
    """Format specification with progress information."""
    content = []

    # Read frontmatter
    frontmatter = read_spec_frontmatter(spec_path)

    title = frontmatter.get("title", spec_path.stem)
    spec_id = frontmatter.get("id", spec_path.stem)
    status = frontmatter.get("status", "ACTIVE")
    priority = frontmatter.get("priority", "MEDIUM")
    branch = frontmatter.get("branch", "Not set")

    # Parse acceptance criteria from frontmatter or file content
    acceptance_criteria = frontmatter.get("acceptance_criteria", [])
    if isinstance(acceptance_criteria, str):
        acceptance_criteria = [c.strip() for c in acceptance_criteria.split("\n") if c.strip()]

    # Calculate progress
    criteria_completed = sum(1 for c in acceptance_criteria if "✓" in c or "completed" in c.lower())
    criteria_total = len(acceptance_criteria)
    progress = (criteria_completed / criteria_total * 100) if criteria_total > 0 else 0

    content.extend(
        [
            f"### 📋 Specification {index}: {title}",
            f"**ID**: {spec_id}",
            f"**Progress**: {progress:.0f}%",
            f"├─ Criteria: {criteria_completed}/{criteria_total} completed",
            f"├─ Status: {status}",
            f"├─ Priority: {priority}",
            f"└─ Branch: {branch}",
            "",
        ]
    )

    # Show acceptance criteria
    if acceptance_criteria:
        content.append("**Acceptance Criteria:**")
        for i, criterion in enumerate(acceptance_criteria, 1):
            if "✓" in criterion or "completed" in criterion.lower():
                content.append(f"  {i}. [x] ~~{criterion}~~")
            else:
                content.append(f"  {i}. [ ] {criterion}")
        content.append("")

    # Add collapsible full spec
    if spec_path.exists():
        content.extend(["<details>", "<summary>View Full Specification</summary>", "", "```markdown"])
        content.append(spec_path.read_text().strip())
        content.extend(["```", "</details>", "", "---", ""])

    return content


def main():
    """Main hook entry point."""
    start_time = time.time()

    # Read input from Claude
    input_data = read_input()

    # Check event type
    event_name = input_data.get("hook_event_name", "")
    if event_name not in ["SessionStart", "PostCompact"]:
        output_json({"hookSpecificOutput": {"message": f"Not a session event: {event_name}"}})
        return

    try:
        # Find project root
        project_root = get_project_root()

        # Generate context
        context = generate_specification_context(project_root, event_name)

        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000

        # Output context for Claude
        output_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                    "metadata": {
                        "execution_time_ms": round(execution_time, 2),
                        "performance_target_met": execution_time <= 50,
                    },
                }
            }
        )

    except Exception as e:
        # Fallback on error
        output_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": f"""<!-- QUAESTOR SESSION CONTEXT (ERROR) -->

## ⚠️ Context Loading Error

Could not load active specifications.

**Error**: {str(e)}

**Quick Actions**:
- Check specs directory: `.quaestor/specs/active/`
- Use `/plan` to create new specifications

<!-- END CONTEXT -->""",
                    "error": str(e),
                }
            },
            exit_code=0,
        )  # Don't fail the hook, just provide fallback context


if __name__ == "__main__":
    main()
