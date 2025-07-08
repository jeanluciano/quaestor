"""Tests for the Quaestor CLI commands."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from quaestor.cli import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_quaestor_directory(self, runner, temp_dir):
        """Test that init creates .quaestor directory."""
        # Patch package resources to return test content
        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",  # CLAUDE.md
                "# ARCHITECTURE manifest",  # manifest/ARCHITECTURE.md
                "# MEMORY manifest",  # manifest/MEMORY.md
                "# project-init.md",  # commands/init.md
                "# task.md",  # commands/task.md
                "# check.md",  # commands/check.md
                "# dispatch.md",  # commands/dispatch.md
            ]

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert (temp_dir / "CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "ARCHITECTURE.md").exists()
            assert (temp_dir / ".quaestor" / "MEMORY.md").exists()
            assert (temp_dir / ".quaestor" / "commands").exists()

    def test_init_with_existing_directory_prompts_user(self, runner, temp_dir):
        """Test that init prompts when .quaestor already exists."""
        # Create existing .quaestor directory
        (temp_dir / ".quaestor").mkdir()

        # Simulate user saying no
        result = runner.invoke(app, ["init", str(temp_dir)], input="n\n")

        assert result.exit_code == 0
        assert "already exists" in result.output
        assert "Initialization cancelled" in result.output

    def test_init_with_force_flag_overwrites(self, runner, temp_dir):
        """Test that --force flag overwrites existing directory."""
        # Create existing .quaestor directory with a file
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        (quaestor_dir / "existing.txt").write_text("existing content")

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",
                "# ARCHITECTURE manifest",
                "# MEMORY manifest",
                "# project-init.md",
                "# task.md",
                "# check.md",
                "# dispatch.md",
            ]

            result = runner.invoke(app, ["init", str(temp_dir), "--force"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "Successfully initialized" in result.output

    def test_init_handles_missing_manifest_files(self, runner, temp_dir):
        """Test fallback to AI templates when manifest files are missing."""
        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            # Simulate manifest files not found, but AI templates exist
            def side_effect(package, filename):
                files = {
                    ("quaestor", "CLAUDE.md"): "# CLAUDE.md content",
                    ("quaestor", "templates_ai_architecture.md"): "# AI ARCHITECTURE template",
                    ("quaestor", "templates_ai_memory.md"): "# AI MEMORY template",
                }
                if (package, filename) in files:
                    return files[(package, filename)]
                elif package == "quaestor.manifest":
                    raise FileNotFoundError("Manifest not found")
                elif package == "quaestor.commands":
                    return f"# {filename} content"
                raise FileNotFoundError(f"Unknown file: {package}/{filename}")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "AI format" in result.output

    def test_init_handles_resource_errors_gracefully(self, runner, temp_dir):
        """Test that init handles missing resources gracefully."""
        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            # All reads fail
            mock_read.side_effect = FileNotFoundError("Resource not found")

            result = runner.invoke(app, ["init", str(temp_dir)])

            # Should still create directory but warn about missing files
            assert (temp_dir / ".quaestor").exists()
            assert "Could not copy" in result.output

    def test_init_with_custom_path(self, runner, temp_dir):
        """Test init with a custom directory path."""
        custom_dir = temp_dir / "my-project"
        custom_dir.mkdir()

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",
                "# ARCHITECTURE manifest",
                "# MEMORY manifest",
                "# project-init.md",
                "# task.md",
                "# check.md",
                "# dispatch.md",
            ]

            result = runner.invoke(app, ["init", str(custom_dir)])

            assert result.exit_code == 0
            assert (custom_dir / ".quaestor").exists()
            assert (custom_dir / "CLAUDE.md").exists()

    def test_init_copies_all_command_files(self, runner, temp_dir):
        """Test that all command files are copied."""
        expected_commands = ["project-init.md", "task.md", "check.md", "dispatch.md"]

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md",
                "# ARCHITECTURE",
                "# MEMORY",
                *[f"# {cmd}" for cmd in expected_commands],
            ]

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            commands_dir = temp_dir / ".quaestor" / "commands"

            for cmd in expected_commands:
                assert (commands_dir / cmd).exists()
                assert f"Copied {cmd}" in result.output


class TestCLIApp:
    """Tests for the CLI app itself."""

    def test_app_has_init_command(self, runner):
        """Test that the app has init command registered."""
        # Check that init command exists by trying to get its help
        result = runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize a .quaestor directory" in result.output

    def test_help_displays_correctly(self, runner):
        """Test that help text displays correctly."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Quaestor - Context management" in result.output
        assert "init" in result.output
        assert "Initialize a .quaestor directory" in result.output
