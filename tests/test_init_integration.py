"""Integration tests for the init command."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from quaestor.cli.app import app


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_git_project(tmp_path):
    """Create a temporary project with git initialized."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Initialize git
    import subprocess

    subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)

    return project_dir


@pytest.fixture
def project_with_config(temp_git_project):
    """Create a project with existing .quaestor directory."""
    # Create .quaestor directory
    quaestor_dir = temp_git_project / ".quaestor"
    quaestor_dir.mkdir()

    # Create a dummy file to make the directory non-empty
    (quaestor_dir / "README.md").write_text("# Test Project\n\nThis is a test.")

    return temp_git_project


class TestInitIntegration:
    """Test init command integration."""

    def test_init_basic(self, runner, temp_git_project):
        """Test basic initialization."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert "Initialization complete!" in result.output

        # Check directory structure
        assert (temp_git_project / ".quaestor").exists()
        assert (temp_git_project / "CLAUDE.md").exists()

        # Check template files created
        assert (temp_git_project / ".quaestor" / "AGENT.md").exists()
        assert (temp_git_project / ".quaestor" / "ARCHITECTURE.md").exists()
        assert (temp_git_project / ".quaestor" / "RULES.md").exists()

        # Check specs directory structure
        assert (temp_git_project / ".quaestor" / "specs" / "draft").exists()
        assert (temp_git_project / ".quaestor" / "specs" / "active").exists()
        assert (temp_git_project / ".quaestor" / "specs" / "completed").exists()
        assert (temp_git_project / ".quaestor" / "specs" / "archived").exists()

    def test_init_with_existing_config(self, runner, project_with_config):
        """Test initialization with existing .quaestor directory."""
        with patch("quaestor.cli.init.Path.cwd", return_value=project_with_config):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 1
        assert "already initialized" in result.output

    def test_init_with_force_flag(self, runner, project_with_config):
        """Test initialization with --force flag overwrites existing."""
        with patch("quaestor.cli.init.Path.cwd", return_value=project_with_config):
            result = runner.invoke(app, ["init", "--force"])

        assert result.exit_code == 0
        assert "Initialization complete!" in result.output

        # Check that files were created
        assert (project_with_config / ".quaestor" / "AGENT.md").exists()
        assert (project_with_config / ".quaestor" / "ARCHITECTURE.md").exists()

    def test_error_handling(self, runner, temp_git_project):
        """Test error handling during initialization."""
        # Test with non-git directory
        non_git_dir = temp_git_project / "not_git"
        non_git_dir.mkdir()

        with patch("quaestor.cli.init.Path.cwd", return_value=non_git_dir):
            result = runner.invoke(app, ["init"])

        # Should still succeed
        assert result.exit_code == 0

        # Test with permission issues
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("No permission")

            with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
                result = runner.invoke(app, ["init", "--force"])

            # Should handle gracefully
            assert result.exit_code != 0 or "permission" in result.output.lower()

    def test_claude_md_creation(self, runner, temp_git_project):
        """Test CLAUDE.md is created with Quaestor config."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0

        claude_md = temp_git_project / "CLAUDE.md"
        assert claude_md.exists()

        content = claude_md.read_text()
        assert "<!-- QUAESTOR CONFIG START -->" in content
        assert "<!-- QUAESTOR CONFIG END -->" in content
        assert ".quaestor/AGENT.md" in content

    def test_claude_md_merge(self, runner, temp_git_project):
        """Test CLAUDE.md is merged with existing content."""
        # Create existing CLAUDE.md
        claude_md = temp_git_project / "CLAUDE.md"
        claude_md.write_text("# My Custom Config\n\nCustom content here.")

        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0

        content = claude_md.read_text()
        # Check both Quaestor config and original content exist
        assert "<!-- QUAESTOR CONFIG START -->" in content
        assert "My Custom Config" in content
        assert "Custom content here" in content
