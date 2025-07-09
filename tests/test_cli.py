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
        """Test that init creates .quaestor directory and installs commands to ~/.claude."""
        # Patch package resources to return test content
        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",  # CLAUDE.md
                "# ARCHITECTURE manifest",  # manifest/ARCHITECTURE.md
                "# MEMORY manifest",  # manifest/MEMORY.md
                "# project-init.md",  # commands/project-init.md
                "# task-py.md",  # commands/task-py.md
                "# task-rs.md",  # commands/task-rs.md
                "# check.md",  # commands/check.md
                "# compose.md",  # commands/compose.md
            ]

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert (temp_dir / "CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "ARCHITECTURE.md").exists()
            assert (temp_dir / ".quaestor" / "MEMORY.md").exists()
            # Commands are now installed to ~/.claude/commands
            assert "Installing command files to ~/.claude/commands" in result.output

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
                "# task-py.md",
                "# task-rs.md",
                "# check.md",
                "# compose.md",
            ]

            result = runner.invoke(app, ["init", str(temp_dir), "--force"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "Initialization complete!" in result.output

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
                "# task-py.md",
                "# task-rs.md",
                "# check.md",
                "# compose.md",
            ]

            result = runner.invoke(app, ["init", str(custom_dir)])

            assert result.exit_code == 0
            assert (custom_dir / ".quaestor").exists()
            assert (custom_dir / "CLAUDE.md").exists()

    def test_init_copies_all_command_files(self, runner, temp_dir):
        """Test that all command files are installed to ~/.claude/commands."""
        expected_commands = ["project-init.md", "task-py.md", "task-rs.md", "check.md", "compose.md"]

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md",
                "# CRITICAL_RULES.md",
                "# ARCHITECTURE",
                "# MEMORY",
                *[f"# {cmd}" for cmd in expected_commands],
            ]

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            # Commands are now installed globally
            assert "Commands installed to ~/.claude/commands" in result.output

            for cmd in expected_commands:
                assert f"Installed {cmd}" in result.output

    def test_init_converts_manifest_files_to_ai_format(self, runner, temp_dir, sample_architecture_manifest, sample_memory_manifest):
        """Test that init properly converts manifest files to AI format."""
        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:
            def side_effect(package, filename):
                if package == "quaestor" and filename == "CLAUDE.md":
                    return "# CLAUDE.md test content"
                elif package == "quaestor" and filename == "CRITICAL_RULES.md":
                    return "# CRITICAL_RULES.md test content"
                elif package == "quaestor.manifest" and filename == "ARCHITECTURE.md":
                    return sample_architecture_manifest
                elif package == "quaestor.manifest" and filename == "MEMORY.md":
                    return sample_memory_manifest
                elif package == "quaestor.commands":
                    return f"# {filename} content"
                raise FileNotFoundError(f"Unknown file: {package}/{filename}")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert "Converting manifest files to AI format" in result.output
            assert "Converted and copied ARCHITECTURE.md" in result.output
            assert "Converted and copied MEMORY.md" in result.output

            # Check ARCHITECTURE.md was converted properly
            arch_content = (temp_dir / ".quaestor" / "ARCHITECTURE.md").read_text()
            assert "<!-- META:document:architecture -->" in arch_content
            assert "<!-- META:version:1.0 -->" in arch_content
            assert "<!-- META:ai-optimized:true -->" in arch_content
            assert "<!-- SECTION:architecture:overview:START -->" in arch_content
            assert "<!-- DATA:architecture-pattern:START -->" in arch_content
            assert 'pattern: "Domain-Driven Design (DDD)"' in arch_content
            assert "Domain Layer" in arch_content  # Original content preserved
            assert "Infrastructure Layer" in arch_content

            # Check MEMORY.md was converted properly
            mem_content = (temp_dir / ".quaestor" / "MEMORY.md").read_text()
            assert "<!-- META:document:memory -->" in mem_content
            assert "<!-- META:version:1.0 -->" in mem_content
            assert "<!-- META:ai-optimized:true -->" in mem_content
            assert "<!-- SECTION:memory:status:START -->" in mem_content
            assert "<!-- DATA:project-status:START -->" in mem_content
            assert 'last_updated: "2024-01-15"' in mem_content
            assert 'current_phase: "Development"' in mem_content
            assert 'overall_progress: "60%"' in mem_content
            assert "Milestone 1: Core Features" in mem_content  # Original content preserved
            assert "Payment integration" in mem_content


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
