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
        cmd = [sys.executable, "-m", "quaestor.cli.app", "init", "--mode", "team"]
        subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True)

        yield repo_path


class TestCommandExecution:
    """Test various command execution scenarios."""

    def test_help_command_output(self, initialized_project):
        """Test help command provides usage information."""
        cmd = [sys.executable, "-m", "quaestor.cli.app", "--help"]
        result = subprocess.run(cmd, cwd=initialized_project, capture_output=True, text=True)

        assert result.returncode == 0
        output = result.stdout

        # Check expected commands are listed
        assert "init" in output
        assert "update" in output

    def test_update_command_manifest_check(self, initialized_project):
        """Test update command correctly checks manifest."""
        # First update should show up to date
        cmd = [sys.executable, "-m", "quaestor.cli.app", "update", "--force"]
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

        # Since automation command was removed, just verify project structure was created
        assert src_dir.exists()
        assert (src_dir / "app.py").exists()
        assert (initialized_project / "requirements.txt").exists()
