#!/usr/bin/env python3
"""Shared utilities for Quaestor hook scripts."""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class WorkflowState:
    """Track the current workflow state across hooks."""

    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / ".quaestor" / ".workflow_state"
        self.state = self._load_state()

    def _load_state(self):
        """Load workflow state from file."""
        if not self.state_file.exists():
            return {
                "phase": "idle",
                "last_research": None,
                "last_plan": None,
                "files_examined": 0,
                "research_files": [],
                "implementation_files": [],
            }

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception:
            return {"phase": "idle", "files_examined": 0, "research_files": [], "implementation_files": []}

    def _save_state(self):
        """Save workflow state to file atomically."""
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)

            # Write to temp file first
            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(self.state, f, indent=2)

            # Atomic rename
            temp_file.replace(self.state_file)
        except Exception as e:
            print(f"Warning: Could not save workflow state: {e}")
            # Clean up temp file if it exists
            temp_file = self.state_file.with_suffix(".tmp")
            if temp_file.exists():
                temp_file.unlink()

    def set_phase(self, phase, message=None):
        """Set workflow phase with optional message."""
        self.state["phase"] = phase
        if message:
            print(message)
        self._save_state()

    def track_research(self, file_path=None):
        """Track research activity."""
        if self.state["phase"] == "idle":
            self.set_phase("researching", "🔍 Started research phase")

        self.state["last_research"] = datetime.now().isoformat()
        if file_path:
            research_files = self.state.get("research_files", [])
            if file_path not in research_files:
                research_files.append(file_path)
                self.state["research_files"] = research_files

        self._save_state()

    def track_implementation(self, file_path=None):
        """Track implementation activity."""
        if self.state["phase"] == "researching":
            self.set_phase("implementing", "🛠️  Moved to implementation phase")

        if file_path:
            impl_files = self.state.get("implementation_files", [])
            if file_path not in impl_files:
                impl_files.append(file_path)
                self.state["implementation_files"] = impl_files

        self._save_state()

    def check_can_implement(self):
        """Check if implementation is allowed."""
        if self.state["phase"] == "idle":
            print("💡 Reminder: Consider researching existing code patterns before implementing")
            print("   Use Read/Grep tools to understand the codebase first")
            return True  # Don't block, just remind

        return True  # Allow implementation in all phases for now


def detect_project_type(project_root="."):
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


def run_command(
    cmd: list[str], description: str | None = None, capture_output: bool = True, timeout_seconds: int = 30
) -> tuple[bool, str, str]:
    """Run a command with timeout and return success status and output.

    Args:
        cmd: Command and arguments as a list
        description: Optional description for logging
        capture_output: Whether to capture stdout/stderr
        timeout_seconds: Maximum execution time in seconds

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=timeout_seconds)
        if description:
            if result.returncode == 0:
                print(f"✅ {description} passed")
            else:
                print(f"❌ {description} failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")

        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after {timeout_seconds} seconds: {' '.join(cmd)}"
        if description:
            print(f"⏱️  {description} timed out after {timeout_seconds}s")
        return False, "", error_msg
    except FileNotFoundError:
        if description:
            print(f"⚠️  {description} command not found - skipping")
        return False, "", f"Command not found: {' '.join(cmd)}"
    except Exception as e:
        error_msg = f"Unexpected error running command: {e}"
        if description:
            print(f"❌ {description} error: {e}")
        return False, "", error_msg


def get_quality_commands(project_type):
    """Get quality check commands for the given project type."""
    commands = {
        "python": [
            ("ruff check", ["ruff", "check", "."]),
            ("ruff format", ["ruff", "format", "--check", "."]),
        ],
        "rust": [
            ("cargo clippy", ["cargo", "clippy", "--", "-D", "warnings"]),
            ("cargo fmt", ["cargo", "fmt", "--check"]),
        ],
        "javascript": [
            ("eslint", ["npx", "eslint", "."]),
            ("prettier", ["npx", "prettier", "--check", "."]),
        ],
        "go": [
            ("go fmt", ["go", "fmt", "./..."]),
            ("go vet", ["go", "vet", "./..."]),
        ],
    }

    return commands.get(project_type, [])


def run_quality_checks(project_root: str = ".", block_on_fail: bool = False, timeout_per_check: int = 60) -> bool:
    """Run quality checks for the detected project type with timeout protection.

    Args:
        project_root: Project root directory
        block_on_fail: Whether to exit if checks fail
        timeout_per_check: Timeout for each individual check

    Returns:
        True if all checks passed, False otherwise
    """
    project_type = detect_project_type(project_root)
    commands = get_quality_commands(project_type)

    if not commands:
        print(f"ℹ️  No quality checks configured for {project_type} project")
        return True

    all_passed = True
    failed_checks = []

    for description, cmd in commands:
        # Change to project root for command execution
        original_cwd = Path.cwd()
        try:
            os.chdir(project_root)
            success, stdout, stderr = run_command(cmd, description, timeout_seconds=timeout_per_check)
            if not success:
                all_passed = False
                failed_checks.append(description)
        finally:
            os.chdir(original_cwd)

    if not all_passed:
        print(f"\n❌ {len(failed_checks)} quality check(s) failed: {', '.join(failed_checks)}")
        if block_on_fail:
            print("Please fix issues before proceeding.")
            sys.exit(1)

    return all_passed


def load_quaestor_config(project_root="."):
    """Load Quaestor configuration using unified config system."""
    try:
        # Try to use unified configuration system
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from quaestor.config_manager import get_project_config

        config_manager = get_project_config(Path(project_root))
        return config_manager.get_merged_config()

    except Exception:
        # Fallback to legacy JSON config loading
        config_path = Path(project_root) / ".quaestor" / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}


def get_project_root():
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()  # Fallback to current directory


def is_hook_enabled(hook_name, config=None, category="enforcement"):
    """Check if a specific hook is enabled in configuration."""
    try:
        # Try to use unified config system
        if config is None:
            import sys

            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from quaestor.config_manager import get_project_config

            config_manager = get_project_config(get_project_root())
            return config_manager.is_hook_enabled(hook_name, category)

    except Exception:
        # Fallback to legacy config checking
        if config is None:
            config = load_quaestor_config()

        hooks_config = config.get("hooks", {})
        if isinstance(hooks_config, dict) and category in hooks_config:
            category_config = hooks_config[category]
            return category_config.get("hooks", {}).get(hook_name, {}).get("enabled", True)

        return hooks_config.get(hook_name, {}).get("enabled", True)


def parse_hook_input():
    """Parse Claude hook input from stdin.

    Returns:
        dict: Parsed hook data including tool name, args, etc.
    """
    try:
        # Read from stdin
        input_data = sys.stdin.read()
        if input_data:
            return json.loads(input_data)

        # If no stdin, check environment variables
        env_data = os.environ.get("CLAUDE_HOOK_DATA")
        if env_data:
            return json.loads(env_data)

        return {}
    except Exception as e:
        print(f"Warning: Could not parse hook input: {e}")
        return {}


def call_automation_hook(hook_name, context=None):
    """Call a hook from the quaestor.automation module.

    Args:
        hook_name: Name of the hook to call (e.g., 'auto_commit')
        context: Optional context dictionary to pass to the hook

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Add quaestor to path
        quaestor_root = Path(__file__).parent.parent.parent
        if str(quaestor_root) not in sys.path:
            sys.path.insert(0, str(quaestor_root))

        # Import automation module
        from quaestor.automation import HookResult, run_hook

        # Call the hook
        context = context or {}
        result = run_hook(hook_name, context)

        # Handle result
        if isinstance(result, HookResult):
            print(result.message)
            return result.to_exit_code()
        else:
            # Legacy support
            return 0 if result else 1

    except ImportError as e:
        print(f"Error: Could not import quaestor.automation: {e}")
        print("Make sure Quaestor is installed: pip install -e /path/to/quaestor")
        return 1
    except Exception as e:
        print(f"Error calling automation hook '{hook_name}': {e}")
        return 1


if __name__ == "__main__":
    # Test the utilities
    print(f"Project type: {detect_project_type()}")
    print(f"Project root: {get_project_root()}")

    # Test workflow state
    workflow = WorkflowState(get_project_root())
    print(f"Current phase: {workflow.state['phase']}")
