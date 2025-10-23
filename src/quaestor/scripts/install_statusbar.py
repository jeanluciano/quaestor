#!/usr/bin/env python3
"""Installer for Quaestor status bar integration with Claude Code.

This script configures Claude Code's .claude/settings.json to display
active Quaestor specifications in the status bar.

Usage:
    python3 install_statusbar.py [workspace_dir]

The script is idempotent and safe to run multiple times.
"""

import contextlib
import json
import sys
from pathlib import Path


def get_status_bar_config(workspace_dir: Path) -> dict:
    """Generate the status bar configuration.

    Args:
        workspace_dir: Root directory of the workspace

    Returns:
        Status bar configuration dictionary
    """
    # Use absolute path to the status bar script
    script_path = workspace_dir / "src" / "quaestor" / "scripts" / "status_bar.py"

    # Use uv run to ensure correct Python version (3.12+) is used
    return {"statusLine": {"type": "command", "command": f"uv run python {script_path}", "padding": 0}}


def install_status_bar(workspace_dir: Path) -> bool:
    """Install status bar configuration for Claude Code.

    Args:
        workspace_dir: Root directory of the workspace

    Returns:
        True if installation succeeded, False otherwise
    """
    try:
        # Ensure .claude directory exists
        claude_dir = workspace_dir / ".claude"
        claude_dir.mkdir(exist_ok=True)

        # Path to settings file
        settings_path = claude_dir / "settings.json"

        # Read existing settings or start with empty dict
        if settings_path.exists():
            try:
                with open(settings_path) as f:
                    settings = json.load(f)
            except json.JSONDecodeError:
                # Corrupted JSON, back it up and start fresh
                backup_path = claude_dir / "settings.json.backup"
                if settings_path.exists():
                    settings_path.rename(backup_path)
                    print(f"⚠️  Backed up corrupted settings to {backup_path}", file=sys.stderr)
                settings = {}
        else:
            settings = {}

        # Generate status bar config
        status_bar_config = get_status_bar_config(workspace_dir)

        # Merge status bar config into settings
        settings.update(status_bar_config)

        # Write settings back
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)

        return True

    except Exception as e:
        print(f"❌ Failed to install status bar: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for the installer."""
    # Get workspace directory from argument or use current directory
    workspace_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

    # Verify we're in a valid workspace
    quaestor_dir = workspace_dir / ".quaestor"
    if not quaestor_dir.exists():
        print("❌ Not a Quaestor project (no .quaestor directory found)", file=sys.stderr)
        print(f"   Searched in: {workspace_dir}", file=sys.stderr)
        sys.exit(1)

    # Verify status bar script exists
    script_path = workspace_dir / "src" / "quaestor" / "scripts" / "status_bar.py"
    if not script_path.exists():
        print(f"❌ Status bar script not found at {script_path}", file=sys.stderr)
        sys.exit(1)

    # Make script executable
    with contextlib.suppress(Exception):
        script_path.chmod(0o755)

    # Install status bar
    if install_status_bar(workspace_dir):
        print("✅ Status bar installed successfully!")
        print(f"   Configuration: {workspace_dir / '.claude' / 'settings.json'}")
        print("   Claude Code will now display active specs in the status bar.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
