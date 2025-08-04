"""Base hook class for reliable Claude Code integration.

This module provides a robust foundation for all Quaestor hooks with:
- Timeout protection
- JSON input/output handling
- Comprehensive error handling
- Execution logging
- Input validation
"""

import json
import logging
import signal
import sys
import time
from collections.abc import Callable
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

# Configure logging
LOG_DIR = Path.home() / ".quaestor" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / f"hooks_{datetime.now().strftime('%Y%m%d')}.log"), logging.StreamHandler()],
)


class TimeoutError(Exception):
    """Raised when a hook execution times out."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


@contextmanager
def timeout(seconds: int):
    """Context manager for timeout protection."""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    # Set the signal handler and alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Restore the original handler and cancel the alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retry logic with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise

            raise last_exception

        return wrapper

    return decorator


class BaseHook:
    """Base class for all Quaestor hooks."""

    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.logger = logging.getLogger(f"quaestor.hooks.{hook_name}")
        self.start_time = time.time()
        self.input_data: dict[str, Any] = {}
        self.output_data: dict[str, Any] = {}

    def read_input(self) -> dict[str, Any]:
        """Read and validate JSON input from stdin."""
        try:
            # Read from stdin with timeout
            with timeout(5):  # 5 second timeout for reading input
                raw_input = sys.stdin.read()

            if not raw_input:
                self.logger.warning("No input received from stdin")
                return {}

            # Parse JSON
            data = json.loads(raw_input)

            # Validate basic structure
            if not isinstance(data, dict):
                raise ValidationError("Input must be a JSON object")

            # Log received input (sanitized)
            self.logger.info(f"Received input for {self.hook_name}")
            self.input_data = data

            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON input: {e}")
            raise ValidationError(f"Invalid JSON input: {e}") from e
        except TimeoutError:
            self.logger.error("Timeout reading input")
            raise
        except Exception as e:
            self.logger.error(f"Error reading input: {e}")
            raise

    def validate_path(self, path: str) -> Path:
        """Validate and sanitize file paths."""
        try:
            # Convert to Path object
            p = Path(path).resolve()

            # Check for path traversal attempts
            if ".." in path:
                raise ValidationError(f"Path traversal detected: {path}")

            # Ensure path is within project or home directory
            cwd = Path.cwd()
            home = Path.home()

            if not (p.is_relative_to(cwd) or p.is_relative_to(home)):
                raise ValidationError(f"Path outside allowed directories: {path}")

            return p

        except Exception as e:
            raise ValidationError(f"Invalid path: {path} - {e}") from e

    def output_json(self, data: dict[str, Any], exit_code: int = 0):
        """Output JSON response and exit."""
        try:
            # Add execution metadata
            data["_metadata"] = {
                "hook": self.hook_name,
                "execution_time": time.time() - self.start_time,
                "timestamp": datetime.now().isoformat(),
            }

            # Log output
            self.logger.info(f"Hook {self.hook_name} completed with exit code {exit_code}")

            # Output JSON
            json.dump(data, sys.stdout, indent=2)
            sys.stdout.flush()

            # Exit with appropriate code
            sys.exit(exit_code)

        except Exception as e:
            self.logger.error(f"Error outputting JSON: {e}")
            sys.exit(1)

    def output_error(self, message: str, blocking: bool = False):
        """Output error response."""
        exit_code = 2 if blocking else 1
        self.output_json({"error": message, "blocking": blocking}, exit_code)

    def output_success(self, message: str = "Success", data: dict[str, Any] | None = None):
        """Output success response."""
        response = {"message": message}
        if data:
            response.update(data)
        self.output_json(response, 0)

    def output_json_blocking(self, reason: str):
        """Block action with feedback to Claude."""
        output = {"decision": "block", "reason": reason}
        print(json.dumps(output))
        sys.exit(0)

    def output_suggestion(self, message: str, suggest_agent: str = None):
        """Provide suggestion with optional agent recommendation."""
        if suggest_agent:
            message += f"\n\nPlease run: Use the {suggest_agent} agent to handle this task"
        output = {"decision": "block", "reason": message}
        print(json.dumps(output))
        sys.exit(0)

    def is_drive_mode(self) -> bool:
        """Check if session is in drive mode."""
        from quaestor.claude.hooks.mode_detector import is_drive_mode

        return is_drive_mode()

    def is_framework_mode(self) -> bool:
        """Check if session is in framework mode."""
        from quaestor.claude.hooks.mode_detector import is_framework_mode

        return is_framework_mode()

    def run_with_timeout(self, func: Callable, timeout_seconds: int = 60) -> Any:
        """Run a function with timeout protection."""
        try:
            with timeout(timeout_seconds):
                return func()
        except TimeoutError as e:
            self.logger.error(f"Timeout in {self.hook_name}: {e}")
            self.output_error(str(e), blocking=True)
        except Exception as e:
            self.logger.error(f"Error in {self.hook_name}: {e}", exc_info=True)
            raise

    def execute(self):
        """Main execution method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")

    def run(self):
        """Main entry point for hook execution."""
        try:
            # Read input
            self.read_input()

            # Execute hook logic with timeout
            self.run_with_timeout(lambda: self.execute(), timeout_seconds=55)  # 55s to stay under Claude's 60s

        except ValidationError as e:
            self.output_error(f"Validation error: {e}", blocking=True)
        except TimeoutError as e:
            self.output_error(f"Timeout: {e}", blocking=True)
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.hook_name}: {e}", exc_info=True)
            self.output_error(f"Unexpected error: {e}", blocking=False)

    # Context-aware utility for checking active work

    def has_active_work(self) -> bool:
        """Check if there's active work in progress.

        Returns:
            True if in framework mode (executing a command)
        """
        from quaestor.claude.hooks.mode_detector import has_active_work

        return has_active_work()


# Utility functions for common operations


def sanitize_command(cmd: list[str]) -> list[str]:
    """Sanitize command arguments to prevent injection."""
    sanitized = []
    for arg in cmd:
        # Remove potentially dangerous characters
        clean_arg = arg.replace(";", "").replace("&", "").replace("|", "")
        sanitized.append(clean_arg)
    return sanitized


def atomic_write(file_path: Path, content: str):
    """Write file atomically to prevent corruption."""
    temp_path = file_path.with_suffix(".tmp")
    try:
        # Write to temporary file
        temp_path.write_text(content, encoding="utf-8")

        # Atomic rename
        temp_path.replace(file_path)

    except Exception:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise


def get_claude_session_info(input_data: dict[str, Any]) -> dict[str, Any]:
    """Extract Claude session information from input."""
    return {
        "session_id": input_data.get("sessionId", "unknown"),
        "tool_name": input_data.get("toolName", "unknown"),
        "event_type": input_data.get("eventType", "unknown"),
        "timestamp": input_data.get("timestamp", datetime.now().isoformat()),
    }


# Essential utilities for self-contained hooks


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()  # Fallback to current directory


def detect_project_type(project_root: Path | str = ".") -> str:
    """Detect project type from files in the given directory."""
    root = Path(project_root)

    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        return "python"
    elif (root / "Cargo.toml").exists():
        return "rust"
    elif (root / "package.json").exists():
        return "javascript"
    elif (root / "go.mod").exists():
        return "go"
    elif (root / "pom.xml").exists() or (root / "build.gradle").exists():
        return "java"
    return "unknown"


# WorkflowState class removed - no longer needed with new mode detection system
