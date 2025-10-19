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

    def test_init_workflow(self, temp_git_repo, quaestor_command):
        """Test complete initialization workflow."""
        # 1. Initialize
        result = subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Initialization complete!" in result.stdout

        # 2. Verify directory structure
        assert (temp_git_repo / ".quaestor").exists()
        assert (temp_git_repo / ".quaestor" / "AGENT.md").exists()
        assert (temp_git_repo / ".quaestor" / "ARCHITECTURE.md").exists()
        assert (temp_git_repo / ".quaestor" / "RULES.md").exists()
        assert (temp_git_repo / "CLAUDE.md").exists()

        # 3. Verify specs directory structure
        assert (temp_git_repo / ".quaestor" / "specs" / "draft").exists()
        assert (temp_git_repo / ".quaestor" / "specs" / "active").exists()
        assert (temp_git_repo / ".quaestor" / "specs" / "completed").exists()
        assert (temp_git_repo / ".quaestor" / "specs" / "archived").exists()

        # 4. Test that main commands exist
        result = subprocess.run(
            [quaestor_command, "--help"] if isinstance(quaestor_command, str) else quaestor_command + ["--help"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "init" in result.stdout

    def test_reinitialize_with_force(self, temp_git_repo, quaestor_command):
        """Test reinitializing with --force flag."""
        # 1. Initialize first time
        result = subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # 2. Try to initialize again without force
        result = subprocess.run(
            [quaestor_command, "init"] if isinstance(quaestor_command, str) else quaestor_command + ["init"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "already initialized" in result.stdout

        # 3. Initialize with --force
        result = subprocess.run(
            [quaestor_command, "init", "--force"]
            if isinstance(quaestor_command, str)
            else quaestor_command + ["init", "--force"],
            cwd=temp_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Initialization complete!" in result.stdout

    def test_basic_workflow(self, temp_git_repo, quaestor_command):
        """Test basic initialization workflow."""
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

        # 3. Verify initialization completed successfully
        assert (temp_git_repo / ".quaestor").exists()
        assert (temp_git_repo / ".quaestor" / "AGENT.md").exists()
        assert (temp_git_repo / "CLAUDE.md").exists()


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
            # Should still succeed
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
        assert result.returncode == 1
        assert "already initialized" in result.stdout


class TestHookIntegration:
    """Test initialization integration scenarios."""

    def test_initialization_structure(self, temp_git_repo, quaestor_command):
        """Test that initialization creates correct structure."""
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
        assert (quaestor_dir / "AGENT.md").exists()
        assert (quaestor_dir / "ARCHITECTURE.md").exists()
        assert (quaestor_dir / "RULES.md").exists()

        # Check CLAUDE.md in project root
        assert (temp_git_repo / "CLAUDE.md").exists()
