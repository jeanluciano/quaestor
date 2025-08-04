#!/usr/bin/env python3
"""Simple mode detection for Quaestor.

Framework mode is active ONLY when executing a Quaestor command.
Drive mode is the default for all other interactions.
"""

import json
from pathlib import Path


def get_command_marker_path() -> Path:
    """Get the path to the command marker file."""
    # Use a temporary file that gets cleaned up
    return Path("/tmp/.quaestor_command_active")


def is_framework_mode() -> bool:
    """Check if we're currently in framework mode (executing a command).

    Returns:
        True if a Quaestor command is currently executing, False otherwise.
    """
    marker = get_command_marker_path()
    if not marker.exists():
        return False

    try:
        # Check if marker is recent (within last 5 minutes)
        # This prevents stale markers from blocking forever
        import time

        age = time.time() - marker.stat().st_mtime
        if age > 300:  # 5 minutes
            marker.unlink()
            return False

        with open(marker) as f:
            data = json.load(f)
            return data.get("active", False)
    except Exception:
        # If we can't read the marker, assume drive mode
        return False


def is_drive_mode() -> bool:
    """Check if we're in drive mode (default).

    Returns:
        True if NOT in framework mode.
    """
    return not is_framework_mode()


def set_framework_mode(command: str, active: bool = True) -> None:
    """Set framework mode state.

    Args:
        command: The command being executed (e.g., "/research", "/impl")
        active: Whether to activate or deactivate framework mode
    """
    marker = get_command_marker_path()

    if active:
        data = {"active": True, "command": command, "timestamp": import_time().time()}
        marker.write_text(json.dumps(data))
    else:
        # Remove the marker when command completes
        if marker.exists():
            marker.unlink()


def get_current_command() -> str | None:
    """Get the currently executing command, if any.

    Returns:
        The command name if in framework mode, None otherwise.
    """
    if not is_framework_mode():
        return None

    marker = get_command_marker_path()
    try:
        with open(marker) as f:
            data = json.load(f)
            return data.get("command")
    except Exception:
        return None


# For backward compatibility
def has_active_work() -> bool:
    """Legacy method - now just checks framework mode."""
    return is_framework_mode()


def import_time():
    """Import time module when needed."""
    import time

    return time
