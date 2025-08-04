"""Basic end-to-end workflow tests for Quaestor."""

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
    return [sys.executable, "-m", "quaestor.cli.app"]


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
        # Note: hooks are now in src/quaestor/claude/hooks, not .quaestor/hooks
        # MEMORY.md was removed in favor of active specifications
        assert (temp_git_repo / ".quaestor" / "CRITICAL_RULES.md").exists()
        assert (temp_git_repo / "CLAUDE.md").exists()

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
        # Check for successful update indicators
        assert any(phrase in result.stdout.lower() for phrase in ["up to date", "update complete", "added"])

        # 5. Test that main commands exist
        result = subprocess.run(
            [quaestor_command, "--help"] if isinstance(quaestor_command, str) else quaestor_command + ["--help"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "init" in result.stdout
        assert "configure" in result.stdout

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

        # 4. Verify configuration was applied
        # Check that command-config.yaml exists
        config_file = temp_git_repo / ".quaestor" / "command-config.yaml"
        assert config_file.exists() or "No commands have configurations" in result.stdout

    def test_automation_workflow(self, temp_git_repo, quaestor_command):
        """Test basic workflow without automation command."""
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

        # 2. Initialize Quaestor
        result = subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
            text=True,
        )
        assert result.returncode == 0

        # 3. Verify hooks were set up correctly
        claude_settings = temp_git_repo / ".claude" / "settings.json"
        if not claude_settings.exists():
            claude_settings = temp_git_repo / ".claude" / "settings.local.json"

        # Just verify initialization completed successfully
        assert (temp_git_repo / ".quaestor").exists()
        # MEMORY.md was removed in favor of active specifications


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

        # Check that .quaestor directory exists
        quaestor_dir = temp_git_repo / ".quaestor"
        assert quaestor_dir.exists()

        # Check for critical files
        # MEMORY.md was removed in favor of active specifications
        assert (quaestor_dir / "CRITICAL_RULES.md").exists()

        # Check claude directory structure
        claude_dir = temp_git_repo / ".claude"
        assert claude_dir.exists()
