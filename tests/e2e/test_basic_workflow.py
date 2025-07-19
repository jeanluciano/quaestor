"""Basic end-to-end workflow tests for Quaestor."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)

        # Create initial commit
        (repo_path / "README.md").write_text("# Test Project")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

        yield repo_path


@pytest.fixture
def quaestor_command():
    """Get the quaestor command path."""
    # Try to find quaestor in PATH first
    result = subprocess.run(["which", "quaestor"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()

    # Otherwise use Python module
    return [sys.executable, "-m", "quaestor.cli.main"]


class TestBasicWorkflow:
    """Test basic Quaestor workflows end-to-end."""

    def test_team_mode_full_workflow(self, temp_git_repo, quaestor_command):
        """Test complete team mode workflow."""
        # 1. Initialize in team mode
        result = subprocess.run(
            [quaestor_command, "init", "--mode", "team"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["init", "--mode", "team"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Team mode initialization complete!" in result.stdout

        # 2. Verify directory structure
        assert (temp_git_repo / ".claude").exists()
        assert (temp_git_repo / ".claude" / "commands").exists()
        assert (temp_git_repo / ".claude" / "settings.json").exists()
        assert (temp_git_repo / ".quaestor").exists()
        assert (temp_git_repo / ".quaestor" / "hooks").exists()
        assert (temp_git_repo / ".quaestor" / "manifest.json").exists()
        assert (temp_git_repo / "CLAUDE.md").exists()

        # 3. Check manifest content
        with open(temp_git_repo / ".quaestor" / "manifest.json") as f:
            manifest = json.load(f)
        assert "version" in manifest
        assert "quaestor_version" in manifest
        assert "files" in manifest

        # 4. Test update command
        result = subprocess.run(
            [quaestor_command, "update", "--force"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["update", "--force"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "up to date" in result.stdout.lower() or "updated" in result.stdout.lower()

        # 5. Test automation subcommand exists
        result = subprocess.run(
            [quaestor_command, "automation", "--help"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["automation", "--help"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "enforce-research" in result.stdout

    def test_personal_mode_workflow(self, temp_git_repo, quaestor_command):
        """Test personal mode workflow."""
        # 1. Initialize in personal mode
        result = subprocess.run(
            [quaestor_command, "init", "--mode", "personal"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["init", "--mode", "personal"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Personal mode initialization complete!" in result.stdout

        # 2. Verify structure
        assert (temp_git_repo / ".claude").exists()
        assert (temp_git_repo / ".claude" / "settings.local.json").exists()
        assert (temp_git_repo / ".quaestor").exists()

        # Note: Commands are installed to user's home ~/.claude/commands in personal mode
        # We can't easily test this in e2e without affecting the real home directory

        # 3. Check gitignore was updated
        gitignore = temp_git_repo / ".gitignore"
        assert gitignore.exists()
        gitignore_content = gitignore.read_text()
        assert ".quaestor/" in gitignore_content
        assert ".claude/settings.local.json" in gitignore_content

    def test_command_configuration_workflow(self, temp_git_repo, quaestor_command):
        """Test command configuration workflow."""
        # 1. Initialize
        subprocess.run(
            [quaestor_command, "init", "--mode", "team"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["init", "--mode", "team"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # 2. Initialize configuration
        result = subprocess.run(
            [quaestor_command, "configure", "--init"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["configure", "--init"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 3. Apply configuration
        result = subprocess.run(
            (
                [quaestor_command, "configure", "--apply"]
                if isinstance(quaestor_command, str)
                else quaestor_command + ["configure", "--apply"]
            ),
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Regenerating" in result.stdout
        assert "Configured commands" in result.stdout or "configurations to" in result.stdout

        # 4. Verify task command has configuration applied
        task_file = temp_git_repo / ".claude" / "commands" / "task.md"
        task_content = task_file.read_text()
        assert "<!-- CONFIGURED BY QUAESTOR" in task_content

    def test_automation_workflow(self, temp_git_repo, quaestor_command):
        """Test automation workflow."""
        # 1. Create some Python files
        src_dir = temp_git_repo / "src"
        src_dir.mkdir()

        (src_dir / "main.py").write_text("""
def main():
    '''Main entry point.'''
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")

        (src_dir / "utils.py").write_text("""
import os

def get_config():
    '''Get configuration.'''
    return {"debug": True}

class Helper:
    '''Helper class.'''
    def process(self, data):
        return data.upper()
""")

        # 2. Initialize Quaestor
        subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # 3. Test update-memory command exists
        result = subprocess.run(
            [quaestor_command, "automation", "update-memory", "--help"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["automation", "update-memory", "--help"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_init_non_git_directory(self, quaestor_command):
        """Test initialization in non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            # Should still succeed but may show warning
            assert result.returncode == 0

    def test_double_init_handling(self, temp_git_repo, quaestor_command):
        """Test handling of double initialization."""
        # First init
        subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Second init without force
        result = subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert "already exists" in result.stdout or "Checking for updates" in result.stdout

    def test_invalid_mode(self, temp_git_repo, quaestor_command):
        """Test invalid mode handling."""
        result = subprocess.run(
            [quaestor_command, "init", "--mode", "invalid"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["init", "--mode", "invalid"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert (
            "invalid" in result.stdout.lower() or "invalid" in result.stderr.lower() or "error" in result.stderr.lower()
        )


class TestHookIntegration:
    """Test hook integration scenarios."""

    def test_hooks_installed_correctly(self, temp_git_repo, quaestor_command):
        """Test that hooks are installed with correct structure."""
        # Initialize
        subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )

        # Check hook files
        hooks_dir = temp_git_repo / ".quaestor" / "hooks"
        assert (hooks_dir / "shared_utils.py").exists()
        assert (hooks_dir / "workflow").exists()
        assert (hooks_dir / "validation").exists()

        # Check settings file has correct paths
        # Personal mode uses settings.local.json, team mode uses settings.json
        settings_file = temp_git_repo / ".claude" / "settings.json"
        if not settings_file.exists():
            settings_file = temp_git_repo / ".claude" / "settings.local.json"

        if settings_file.exists():
            settings_content = settings_file.read_text()
            assert "workflow/implementation_declaration.py" in settings_content

        # Verify hook can be imported
        shared_utils = hooks_dir / "shared_utils.py"
        content = shared_utils.read_text()
        assert "def call_automation_hook" in content
        assert "from quaestor.automation import" in content  # Import is inside the function
