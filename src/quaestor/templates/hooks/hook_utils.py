#!/usr/bin/env python3
"""Shared utilities for Quaestor hook scripts."""

import json
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
        """Save workflow state to file."""
        try:
            self.state_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save workflow state: {e}")

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


def run_command(cmd, description=None, capture_output=True):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True)
        if description:
            if result.returncode == 0:
                print(f"✅ {description} passed")
            else:
                print(f"❌ {description} failed")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")

        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        if description:
            print(f"⚠️  {description} command not found - skipping")
        return False, "", f"Command not found: {' '.join(cmd)}"


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


def run_quality_checks(project_root=".", block_on_fail=False):
    """Run quality checks for the detected project type."""
    project_type = detect_project_type(project_root)
    commands = get_quality_commands(project_type)

    if not commands:
        print(f"ℹ️  No quality checks configured for {project_type} project")
        return True

    all_passed = True
    for description, cmd in commands:
        success, stdout, stderr = run_command(cmd, description)
        if not success:
            all_passed = False

    if not all_passed and block_on_fail:
        print("❌ Quality checks failed. Please fix issues before proceeding.")
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


if __name__ == "__main__":
    # Test the utilities
    print(f"Project type: {detect_project_type()}")
    print(f"Project root: {get_project_root()}")

    # Test workflow state
    workflow = WorkflowState(get_project_root())
    print(f"Current phase: {workflow.state['phase']}")
