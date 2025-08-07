"""Integration tests for the init command with command processing."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from quaestor.cli.app import app
from quaestor.constants import COMMAND_FILES


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
    """Test init command with command processing integration."""

    def test_personal_mode_init_basic(self, runner, temp_git_project):
        """Test basic personal mode initialization."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init", "--mode", "personal"])

        assert result.exit_code == 0
        assert "Personal mode initialization complete!" in result.output

        # Check directory structure
        assert (temp_git_project / ".claude").exists()
        assert (temp_git_project / ".quaestor").exists()
        assert (temp_git_project / "CLAUDE.md").exists()

        # Check settings.local.json
        settings_file = temp_git_project / ".claude" / "settings.local.json"
        assert settings_file.exists()

        # Check hooks installed to .quaestor/hooks
        hooks_dir = temp_git_project / ".quaestor" / "hooks"
        assert hooks_dir.exists()
        # Check for individual hook files instead of subdirectories
        assert (hooks_dir / "base.py").exists()
        assert (hooks_dir / "session_context_loader.py").exists()
        assert (hooks_dir / "todo_spec_progress.py").exists()

    def test_team_mode_init_basic(self, runner, temp_git_project):
        """Test basic team mode initialization."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init", "--mode", "team"])

        assert result.exit_code == 0
        assert "Team mode initialization complete!" in result.output

        # Check directory structure
        assert (temp_git_project / ".claude" / "commands").exists()
        assert (temp_git_project / ".quaestor").exists()
        assert (temp_git_project / "CLAUDE.md").exists()

        # Check settings.json (not .local)
        settings_file = temp_git_project / ".claude" / "settings.json"
        assert settings_file.exists()

        # Check manifest created
        manifest_file = temp_git_project / ".quaestor" / "manifest.json"
        assert manifest_file.exists()

        # Check template files created
        assert (temp_git_project / ".quaestor" / "CONTEXT.md").exists()
        assert (temp_git_project / ".quaestor" / "ARCHITECTURE.md").exists()

    def test_init_with_existing_config(self, runner, project_with_config):
        """Test initialization with existing command configuration."""
        with patch("quaestor.cli.init.Path.cwd", return_value=project_with_config):
            result = runner.invoke(app, ["init", "--mode", "team", "--force"])

        assert result.exit_code == 0

        # Check that commands were installed
        assert "Installed impl.md" in result.output

        # Check command exists and has content
        impl_file = project_with_config / ".claude" / "commands" / "impl.md"
        assert impl_file.exists()
        impl_content = impl_file.read_text()

        # Verify the file has content
        assert len(impl_content) > 0
        # Commands are now copied directly without modification

        # Commands are copied directly without any overrides or modifications

    def test_personal_mode_commands_location(self, runner, temp_git_project):
        """Test personal mode installs commands to ~/.claude/commands."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            # Mock home directory
            mock_home = temp_git_project / "mock_home"
            mock_home.mkdir()
            mock_claude_dir = mock_home / ".claude"
            mock_commands_dir = mock_claude_dir / "commands"

            # Patch the DEFAULT_COMMANDS_DIR constant directly
            with patch("quaestor.cli.init.DEFAULT_COMMANDS_DIR", mock_commands_dir):
                result = runner.invoke(app, ["init", "--mode", "personal"])

            assert result.exit_code == 0
            assert "Installing to ~/.claude/commands (personal commands)" in result.output

            # Commands should be in mock home
            assert mock_commands_dir.exists()

            # Verify all commands installed
            for cmd_file in COMMAND_FILES:
                assert (mock_commands_dir / cmd_file).exists()

    def test_init_update_scenario(self, runner, temp_git_project):
        """Test init behavior when updating existing installation."""
        # First init
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result1 = runner.invoke(app, ["init", "--mode", "team"])
        assert result1.exit_code == 0

        # Modify a file to simulate user changes
        arch_file = temp_git_project / ".quaestor" / "ARCHITECTURE.md"
        original_content = arch_file.read_text()
        arch_file.write_text(original_content + "\n## User Notes\nCustom content")

        # Second init should trigger update check
        with (
            patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project),
            patch("rich.prompt.Confirm.ask", return_value=False),
        ):
            result2 = runner.invoke(app, ["init", "--mode", "team"])

        assert "Checking for updates" in result2.output
        # Since no files changed, it should say everything is up to date
        assert "Everything is up to date" in result2.output

    def test_gitignore_behavior(self, runner, temp_git_project):
        """Test gitignore modifications for each mode."""
        # Test personal mode
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            runner.invoke(app, ["init", "--mode", "personal"])

        gitignore = temp_git_project / ".gitignore"
        assert gitignore.exists()
        gitignore_content = gitignore.read_text()

        # Personal mode ignores .quaestor and settings.local.json
        assert ".quaestor/" in gitignore_content
        assert ".claude/settings.local.json" in gitignore_content

        # Clean up
        gitignore.unlink()

        # Test team mode
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            runner.invoke(app, ["init", "--mode", "team", "--force"])

        # Team mode should not modify gitignore
        assert not gitignore.exists()

    def test_hook_installation(self, runner, temp_git_project):
        """Test hook files are properly installed."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            result = runner.invoke(app, ["init", "--mode", "team"])

        assert result.exit_code == 0
        # Check that hooks are configured (uvx commands, no files to copy in team mode)
        assert "Hooks configured to use uvx commands" in result.output or "hook" in result.output.lower()

        # Check that settings.json was created with hook configuration
        settings_file = temp_git_project / ".claude" / "settings.json"
        assert settings_file.exists()
        # New implementation uses settings.json to reference hooks in src/quaestor/claude/hooks

    def test_settings_json_paths(self, runner, temp_git_project):
        """Test settings.json has correct hook paths."""
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            runner.invoke(app, ["init", "--mode", "team"])

        settings_file = temp_git_project / ".claude" / "settings.json"
        settings_content = settings_file.read_text()

        # Check for new hook structure - uvx commands
        assert "session-context-loader" in settings_content
        assert "todo-spec-progress" in settings_content

        # Should not have old paths
        assert "hooks/implementation_declaration.py" not in settings_content
        assert "hooks/research_tracker.py" not in settings_content

    def test_error_handling(self, runner, temp_git_project):
        """Test error handling during initialization."""
        # Test with non-git directory
        non_git_dir = temp_git_project / "not_git"
        non_git_dir.mkdir()

        with patch("quaestor.cli.init.Path.cwd", return_value=non_git_dir):
            result = runner.invoke(app, ["init"])

        # Should still succeed but with appropriate handling
        assert result.exit_code == 0

        # Test with permission issues
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("No permission")

            with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
                result = runner.invoke(app, ["init", "--force"])

            # Should handle gracefully
            assert result.exit_code != 0 or "permission" in result.output.lower()


class TestCommandInstallation:
    """Test command installation during initialization."""

    def test_command_files_copied(self, runner, project_with_config):
        """Test that command files are copied correctly."""
        with patch("importlib.resources.read_text") as mock_read:
            # Mock command content
            mock_read.return_value = """---
allowed-tools: [Read, Write]
---
# Task Command

minimum_test_coverage: 80
"""

            with patch("quaestor.cli.init.Path.cwd", return_value=project_with_config):
                result = runner.invoke(app, ["init", "--mode", "team", "--force"])

        assert result.exit_code == 0

        # Verify command was copied
        impl_file = project_with_config / ".claude" / "commands" / "impl.md"
        content = impl_file.read_text()

        # The impl.md command exists and has content
        assert impl_file.exists()
        assert len(content) > 0
        # Commands are now copied directly without modification

    def test_manifest_tracking(self, runner, temp_git_project):
        """Test manifest properly tracks files in both modes."""
        # Test personal mode (should have manifest now)
        with patch("quaestor.cli.init.Path.cwd", return_value=temp_git_project):
            runner.invoke(app, ["init", "--mode", "personal"])

        manifest_file = temp_git_project / ".quaestor" / "manifest.json"
        assert manifest_file.exists()

        import json

        with open(manifest_file) as f:
            manifest = json.load(f)

        assert "version" in manifest
        assert "quaestor_version" in manifest
        assert "files" in manifest

        # Check tracked files
        tracked_files = manifest["files"]
        assert ".quaestor/CONTEXT.md" in tracked_files
        assert ".quaestor/ARCHITECTURE.md" in tracked_files
