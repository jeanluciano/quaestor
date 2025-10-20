"""Utilities for managing CLAUDE.md integration."""

import importlib.resources as pkg_resources
from pathlib import Path

from quaestor.constants import QUAESTOR_CONFIG_END, QUAESTOR_CONFIG_START


def merge_claude_md(target_dir: Path) -> dict:
    """Merge Quaestor include section with existing CLAUDE.md or create new one.

    Args:
        target_dir: Project root directory

    Returns:
        Dict with status and message
    """
    claude_path = target_dir / "CLAUDE.md"

    try:
        # Get the include template
        try:
            include_content = pkg_resources.read_text("quaestor", "include.md")
        except Exception:
            # Fallback if template is missing
            include_content = """<!-- QUAESTOR CONFIG START -->
[!IMPORTANT]
**Claude:** This project uses Quaestor for AI context management.
Please read the following files in order:
@.quaestor/AGENT.md - AI behavioral rules and workflow enforcement
@.quaestor/ARCHITECTURE.md - System design, structure, and quality guidelines
@.quaestor/specs/active/ - Active specifications and implementation details
<!-- QUAESTOR CONFIG END -->

<!-- Your custom content below -->
"""

        if claude_path.exists():
            existing_content = claude_path.read_text()

            if QUAESTOR_CONFIG_START in existing_content:
                # Update existing config section
                start_idx = existing_content.find(QUAESTOR_CONFIG_START)
                end_idx = existing_content.find(QUAESTOR_CONFIG_END)

                if end_idx == -1:
                    # Invalid markers - backup and replace
                    backup_path = target_dir / "CLAUDE.md.backup"
                    claude_path.rename(backup_path)
                    claude_path.write_text(include_content)
                    return {
                        "success": True,
                        "action": "replaced",
                        "message": f"Invalid markers found. Created backup at {backup_path.name}",
                    }
                else:
                    # Extract config section from template
                    config_start = include_content.find(QUAESTOR_CONFIG_START)
                    config_end = include_content.find(QUAESTOR_CONFIG_END) + len(QUAESTOR_CONFIG_END)
                    new_config = include_content[config_start:config_end]

                    # Replace old config with new
                    new_content = (
                        existing_content[:start_idx]
                        + new_config
                        + existing_content[end_idx + len(QUAESTOR_CONFIG_END) :]
                    )
                    claude_path.write_text(new_content)
                    return {
                        "success": True,
                        "action": "updated",
                        "message": "Updated Quaestor config in existing CLAUDE.md",
                    }
            else:
                # Prepend Quaestor config to existing content
                template_lines = include_content.strip().split("\n")
                if template_lines[-1] == "<!-- Your custom content below -->":
                    template_lines = template_lines[:-1]

                merged_content = "\n".join(template_lines) + "\n\n" + existing_content
                claude_path.write_text(merged_content)
                return {
                    "success": True,
                    "action": "prepended",
                    "message": "Added Quaestor config to existing CLAUDE.md",
                }
        else:
            # Create new file
            claude_path.write_text(include_content)
            return {"success": True, "action": "created", "message": "Created CLAUDE.md with Quaestor config"}

    except Exception as e:
        return {"success": False, "action": "failed", "message": f"Failed to handle CLAUDE.md: {e}"}
