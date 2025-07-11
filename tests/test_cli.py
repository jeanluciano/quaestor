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

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.templates", "CLAUDE_INCLUDE.md"): (
                        "<!-- BEGIN QUAESTOR CONFIG -->\nQuaestor config\n<!-- END QUAESTOR CONFIG -->"
                    ),
                    ("quaestor", "QUAESTOR_CLAUDE.md"): "# QUAESTOR_CLAUDE.md test content",
                    ("quaestor", "CRITICAL_RULES.md"): "# CRITICAL_RULES test content",
                    ("quaestor.manifest", "ARCHITECTURE.md"): "# ARCHITECTURE manifest",
                    ("quaestor.manifest", "MEMORY.md"): "# MEMORY manifest",
                    ("quaestor.commands", "project-init.md"): "# project-init.md",
                    ("quaestor.commands", "task-py.md"): "# task-py.md",
                    ("quaestor.commands", "task-rs.md"): "# task-rs.md",
                    ("quaestor.commands", "check.md"): "# check.md",
                    ("quaestor.commands", "compose.md"): "# compose.md",
                    ("quaestor.commands", "milestone-commit.md"): "# milestone-commit.md",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert (temp_dir / "CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "QUAESTOR_CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "ARCHITECTURE.md").exists()
            assert (temp_dir / ".quaestor" / "MEMORY.md").exists()
            # Commands are now installed to ~/.claude/commands
            assert "Installing command files to ~/.claude/commands" in result.output

    def test_init_with_existing_directory_prompts_user(self, runner, temp_dir):
        """Test that init prompts when .quaestor already exists."""
        # Create existing .quaestor directory and manifest
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()

        # Create a manifest to simulate existing installation
        manifest_path = quaestor_dir / "manifest.json"
        manifest_path.write_text('{"version": "1.0", "files": {}}')

        # Simulate user saying no to update
        result = runner.invoke(app, ["init", str(temp_dir)], input="n\n")

        assert result.exit_code == 0
        assert "Checking for updates" in result.output or "already exists" in result.output
        assert "cancelled" in result.output

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
                    ("quaestor.templates", "ARCHITECTURE.template.md"): "# AI ARCHITECTURE template",
                    ("quaestor.templates", "MEMORY.template.md"): "# AI MEMORY template",
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
        expected_commands = [
            "help.md",
            "project-init.md",
            "task.md",
            "status.md",
            "check.md",
            "milestone.md",
            "milestone-commit.md",
        ]

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.templates", "CLAUDE_INCLUDE.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "QUAESTOR_CLAUDE.md"): "# QUAESTOR_CLAUDE.md",
                    ("quaestor", "CRITICAL_RULES.md"): "# CRITICAL_RULES.md",
                    ("quaestor.templates", "ARCHITECTURE.template.md"): "# ARCHITECTURE",
                    ("quaestor.templates", "MEMORY.template.md"): "# MEMORY",
                }
                if package == "quaestor.commands":
                    return f"# {resource}"
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            # Commands are now installed globally
            assert "Commands installed to ~/.claude/commands" in result.output

            for cmd in expected_commands:
                assert f"Installed {cmd}" in result.output

    def test_init_converts_manifest_files_to_ai_format(
        self, runner, temp_dir, sample_architecture_manifest, sample_memory_manifest
    ):
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
            assert "Copied ARCHITECTURE.md" in result.output
            assert "Copied MEMORY.md" in result.output

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

    def test_init_merges_with_existing_claude_md(self, runner, temp_dir):
        """Test that init merges with existing CLAUDE.md instead of overwriting."""
        # Create existing CLAUDE.md with custom content
        existing_claude = temp_dir / "CLAUDE.md"
        existing_claude.write_text("# My Custom Claude Config\n\nThis is my custom content.")

        with patch("quaestor.cli.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.templates", "CLAUDE_INCLUDE.md"): (
                        "<!-- BEGIN QUAESTOR CONFIG -->\nQuaestor config\n"
                        "<!-- END QUAESTOR CONFIG -->\n\n<!-- Your custom content below -->"
                    ),
                    ("quaestor", "QUAESTOR_CLAUDE.md"): "# QUAESTOR_CLAUDE.md test content",
                    ("quaestor", "CRITICAL_RULES.md"): "# CRITICAL_RULES test content",
                    ("quaestor.templates", "ARCHITECTURE.template.md"): "# AI ARCHITECTURE template",
                    ("quaestor.templates", "MEMORY.template.md"): "# AI MEMORY template",
                }
                if package == "quaestor.commands":
                    return f"# {resource} content"
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0

            # Check that CLAUDE.md exists and contains both Quaestor config and original content
            updated_content = existing_claude.read_text()
            assert "<!-- BEGIN QUAESTOR CONFIG -->" in updated_content
            assert "<!-- END QUAESTOR CONFIG -->" in updated_content
            assert "My Custom Claude Config" in updated_content
            assert "This is my custom content." in updated_content

            # Ensure Quaestor config is at the beginning
            assert updated_content.startswith("<!-- BEGIN QUAESTOR CONFIG -->")


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
