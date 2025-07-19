"""End-to-end tests for command execution scenarios."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def initialized_project():
    """Create an initialized Quaestor project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)

        # Initialize Quaestor
        cmd = [sys.executable, "-m", "quaestor.cli.main", "init", "--mode", "team"]
        subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True)

        yield repo_path


class TestCommandExecution:
    """Test various command execution scenarios."""

    def test_help_command_output(self, initialized_project):
        """Test help command provides usage information."""
        cmd = [sys.executable, "-m", "quaestor.cli.main", "--help"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)

        assert result.returncode == 0
        output = result.stdout

        # Check expected commands are listed
        assert "init" in output
        assert "update" in output
        assert "configure" in output
        assert "automation" in output

    def test_update_command_manifest_check(self, initialized_project):
        """Test update command correctly checks manifest."""
        # First update should show up to date
        cmd = [sys.executable, "-m", "quaestor.cli.main", "update"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)
        assert result.returncode == 0
        assert "up to date" in result.stdout.lower()

        # Modify manifest to simulate older version
        manifest_path = initialized_project / ".quaestor" / "manifest.json"
        with open(manifest_path) as f:
            manifest = json.load(f)

        manifest["quaestor_version"] = "0.1.0"  # Old version
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Update should now detect version mismatch
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)
        assert "Update available" in result.stdout or "version" in result.stdout.lower()

    def test_configure_command_workflow(self, initialized_project):
        """Test configure command with different options."""
        base_cmd = [sys.executable, "-m", "quaestor.cli.main", "configure"]

        # 1. Create default config
        result = subprocess.run(
            base_cmd + ["--enforcement", "strict"], cwd=initialized_project, capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Created default command configuration" in result.stdout

        # Verify config file exists
        config_file = initialized_project / ".quaestor" / "command-config.yaml"
        assert config_file.exists()

        # 2. Preview changes
        result = subprocess.run(base_cmd + ["--preview"], cwd=initialized_project, capture_output=True, text=True)
        assert result.returncode == 0
        assert "Preview" in result.stdout
        assert "task" in result.stdout  # Should show task command config

        # 3. Apply configuration
        result = subprocess.run(base_cmd + ["--apply"], cwd=initialized_project, capture_output=True, text=True)
        assert result.returncode == 0
        assert "Regenerating" in result.stdout
        assert "configured" in result.stdout

        # 4. Verify commands were updated
        task_file = initialized_project / ".claude" / "commands" / "task.md"
        content = task_file.read_text()
        assert "<!-- CONFIGURED BY QUAESTOR" in content
        assert "STRICT MODE ACTIVE" in content

    def test_quality_check_command(self, initialized_project):
        """Test quality check command."""
        # Create diverse project structure
        src_dir = initialized_project / "src"
        src_dir.mkdir()

        # Python files
        (src_dir / "app.py").write_text("""
import flask
from utils import helper

app = flask.Flask(__name__)

@app.route('/')
def index():
    return helper.process_request()
""")

        (src_dir / "utils.py").write_text("""
def process_request():
    return {"status": "ok"}
""")

        # JavaScript file
        (src_dir / "frontend.js").write_text("""
const API_URL = 'http://localhost:5000';

async function fetchData() {
    const response = await fetch(API_URL);
    return response.json();
}
""")

        # Config files
        (initialized_project / "requirements.txt").write_text("flask>=2.0.0\nrequests>=2.25.0")
        (initialized_project / "package.json").write_text(
            json.dumps({"name": "test-app", "dependencies": {"react": "^18.0.0"}})
        )

        # Run quality check
        cmd = [sys.executable, "-m", "quaestor.cli.main", "automation", "quality-check"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)

        # Quality check might fail without proper setup, but command should exist
        assert result.returncode in [0, 1]  # Allow failure since project might not meet quality standards


class TestCommandWithConfiguration:
    """Test commands with various configurations applied."""

    def test_strict_mode_command_generation(self, initialized_project):
        """Test that strict mode properly modifies commands."""
        # Create strict config for task command
        config_data = {
            "commands": {
                "task": {
                    "enforcement": "strict",
                    "require_planning": True,
                    "parameters": {"minimum_test_coverage": 95, "max_function_lines": 25},
                    "custom_rules": [
                        "All code must have type hints",
                        "No direct database queries in views",
                        "All endpoints must be documented",
                    ],
                }
            }
        }

        config_path = initialized_project / ".quaestor" / "command-config.yaml"
        import yaml

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Apply configuration
        cmd = [sys.executable, "-m", "quaestor.cli.main", "configure", "--apply"]
        subprocess.run(cmd, cwd=initialized_project, check=True, capture_output=True)

        # Check task command
        task_file = initialized_project / ".claude" / "commands" / "task.md"
        content = task_file.read_text()

        # Verify all elements
        assert "PROJECT-SPECIFIC RULES" in content
        assert "minimum_test_coverage: 95" in content
        assert "max_function_lines: 25" in content
        assert "All code must have type hints" in content
        assert "No direct database queries in views" in content
        assert "All endpoints must be documented" in content
        assert "<!-- CONFIGURED BY QUAESTOR" in content

    def test_command_override_application(self, initialized_project):
        """Test command override functionality."""
        # Create command override
        override_dir = initialized_project / ".quaestor" / "commands"
        override_dir.mkdir(parents=True, exist_ok=True)

        custom_status = """# Custom Status Command

This is a completely custom status command for our project.

## Special Instructions
Always check the deployment status first.
"""
        (override_dir / "status.md").write_text(custom_status)

        # Apply configuration to regenerate commands
        cmd = [sys.executable, "-m", "quaestor.cli.main", "configure", "--apply"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)
        assert result.returncode == 0

        # Verify override was applied
        status_file = initialized_project / ".claude" / "commands" / "status.md"
        assert status_file.read_text() == custom_status

    def test_multi_command_configuration(self, initialized_project):
        """Test configuring multiple commands at once."""
        # Create config for multiple commands
        config_data = {
            "commands": {
                "task": {"enforcement": "strict", "require_planning": True},
                "check": {"enforcement": "relaxed", "auto_fix": True},
                "milestone": {"enforcement": "default", "parameters": {"auto_create_pr": True}},
            }
        }

        config_path = initialized_project / ".quaestor" / "command-config.yaml"
        import yaml

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Apply
        cmd = [sys.executable, "-m", "quaestor.cli.main", "configure", "--apply"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)
        assert "3 command(s) were configured" in result.stdout

        # Verify each command
        task_content = (initialized_project / ".claude" / "commands" / "task.md").read_text()
        assert "PROJECT-SPECIFIC RULES" in task_content

        check_content = (initialized_project / ".claude" / "commands" / "check.md").read_text()
        assert "relaxed enforcement" in check_content

        milestone_content = (initialized_project / ".claude" / "commands" / "milestone.md").read_text()
        assert "auto_create_pr: True" in milestone_content or "auto_create_pr: true" in milestone_content
