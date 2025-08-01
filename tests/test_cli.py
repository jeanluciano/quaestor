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
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.claude.templates", "CLAUDE_INCLUDE.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "QUAESTOR_CLAUDE.md"): "# QUAESTOR_CLAUDE.md test content",
                    ("quaestor", "CRITICAL_RULES.md"): "# CRITICAL_RULES test content",
                    ("quaestor.claude.templates", "ARCHITECTURE.template.md"): "# ARCHITECTURE template",
                    ("quaestor.claude.templates", "MEMORY.template.md"): "# MEMORY template",
                    ("quaestor.claude.templates", "PATTERNS.template.md"): "# PATTERNS template",
                    ("quaestor.claude.templates", "VALIDATION.template.md"): "# VALIDATION template",
                    ("quaestor.claude.templates", "AUTOMATION.template.md"): "# AUTOMATION template",
                    ("quaestor.claude.commands", "project-init.md"): "# project-init.md",
                    ("quaestor.claude.commands", "research.md"): "# research.md",
                    ("quaestor.claude.commands", "plan.md"): "# plan.md",
                    ("quaestor.claude.commands", "task.md"): "# task.md",
                    ("quaestor.claude.commands", "debug.md"): "# debug.md",
                    ("quaestor.claude.commands", "review.md"): "# review.md",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir), "--mode", "team", "--no-contextual"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert (temp_dir / "CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "QUAESTOR_CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "ARCHITECTURE.md").exists()
            assert (temp_dir / ".quaestor" / "MEMORY.md").exists()
            # Commands are installed to .claude/commands in team mode
            assert "Installing to .claude/commands (project commands)" in result.output

    def test_init_with_existing_directory_prompts_user(self, runner, temp_dir):
        """Test that init prompts when .quaestor already exists."""
        # Create existing .quaestor directory and manifest
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()

        # Create a manifest to simulate existing installation
        manifest_path = quaestor_dir / "manifest.json"
        manifest_path.write_text('{"version": "1.0", "files": {}}')

        # Simulate user saying no to update
        result = runner.invoke(app, ["init", str(temp_dir), "--mode", "team"], input="n\n")

        assert result.exit_code == 0
        assert "Checking for updates" in result.output or "already exists" in result.output
        assert "cancelled" in result.output

    def test_init_with_force_flag_overwrites(self, runner, temp_dir):
        """Test that --force flag overwrites existing directory."""
        # Create existing .quaestor directory with a file
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        (quaestor_dir / "existing.txt").write_text("existing content")

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",
                "# ARCHITECTURE template",
                "# MEMORY template",
                "# PATTERNS template",
                "# VALIDATION template",
                "# AUTOMATION template",
                "# project-init.md",
                "# task-py.md",
                "# task-rs.md",
                "# check.md",
                "# compose.md",
            ]

            result = runner.invoke(app, ["init", str(temp_dir), "--mode", "team", "--force"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "Team mode initialization complete!" in result.output

    def test_init_handles_missing_manifest_files(self, runner, temp_dir):
        """Test fallback to AI templates when manifest files are missing."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:
            # Simulate manifest files not found, but AI templates exist
            def side_effect(package, filename):
                files = {
                    ("quaestor", "CLAUDE.md"): "# CLAUDE.md content",
                    ("quaestor.templates", "ARCHITECTURE.template.md"): "# AI ARCHITECTURE template",
                    ("quaestor.templates", "MEMORY.template.md"): "# AI MEMORY template",
                }
                if (package, filename) in files:
                    return files[(package, filename)]
                elif package == "quaestor.claude.templates":
                    return f"# {filename} template"
                elif package == "quaestor.claude.commands":
                    return f"# {filename} content"
                raise FileNotFoundError(f"Unknown file: {package}/{filename}")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            # In personal mode, template files are processed automatically
            assert "Created ARCHITECTURE.md" in result.output or "Setting up documentation files" in result.output

    def test_init_handles_resource_errors_gracefully(self, runner, temp_dir):
        """Test that init handles missing resources gracefully."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:
            # All reads fail
            mock_read.side_effect = FileNotFoundError("Resource not found")

            result = runner.invoke(app, ["init", str(temp_dir)])

            # Should still create directories but warn about missing files
            assert (temp_dir / ".claude").exists() or (temp_dir / ".quaestor").exists()
            assert "Could not" in result.output or "Failed" in result.output

    def test_init_with_custom_path(self, runner, temp_dir):
        """Test init with a custom directory path."""
        custom_dir = temp_dir / "my-project"
        custom_dir.mkdir()

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:
            mock_read.side_effect = [
                "# CLAUDE.md test content",
                "# ARCHITECTURE template",
                "# MEMORY template",
                "# PATTERNS template",
                "# VALIDATION template",
                "# AUTOMATION template",
                "# project-init.md",
                "# task-py.md",
                "# task-rs.md",
                "# check.md",
                "# compose.md",
            ]

            result = runner.invoke(app, ["init", str(custom_dir)])

            assert result.exit_code == 0
            # Personal mode creates .claude directory
            assert (custom_dir / ".claude").exists()
            # CLAUDE.md is in project root, not in .claude
            assert (custom_dir / "CLAUDE.md").exists()

    def test_init_copies_all_command_files(self, runner, temp_dir):
        """Test that all command files are installed to ~/.claude/commands."""
        expected_commands = [
            "project-init.md",
            "research.md",
            "plan.md",
            "task.md",
            "debug.md",
            "review.md",
        ]

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.claude.templates", "CLAUDE_INCLUDE.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "QUAESTOR_CLAUDE.md"): "# QUAESTOR_CLAUDE.md",
                    ("quaestor", "CRITICAL_RULES.md"): "# CRITICAL_RULES.md",
                    ("quaestor.claude.templates", "ARCHITECTURE.template.md"): "# ARCHITECTURE",
                    ("quaestor.claude.templates", "MEMORY.template.md"): "# MEMORY",
                    ("quaestor.claude.templates", "PATTERNS.template.md"): "# PATTERNS",
                    ("quaestor.claude.templates", "VALIDATION.template.md"): "# VALIDATION",
                    ("quaestor.claude.templates", "AUTOMATION.template.md"): "# AUTOMATION",
                }
                if package == "quaestor.claude.commands":
                    return f"# {resource}"
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            # Personal mode installs commands to ~/.claude/commands
            assert "Installing to ~/.claude/commands (personal commands)" in result.output

            for cmd in expected_commands:
                assert f"Installed {cmd}" in result.output

    def test_init_processes_template_files(
        self, runner, temp_dir, sample_architecture_manifest, sample_memory_manifest
    ):
        """Test that init properly processes template files."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def side_effect(package, filename):
                if package == "quaestor.claude.templates" and filename == "quaestor_claude.md":
                    return "# QUAESTOR_CLAUDE.md test content"
                elif package == "quaestor.claude.templates" and filename == "critical_rules.md":
                    return "# CRITICAL_RULES.md test content"
                elif package == "quaestor.claude.templates" and filename == "claude_include.md":
                    return (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n"
                        "<!-- QUAESTOR CONFIG END -->\n\n<!-- Your custom content below -->"
                    )
                elif package == "quaestor.claude.templates" and filename == "architecture.md":
                    return sample_architecture_manifest
                elif package == "quaestor.claude.templates" and filename == "memory.md":
                    return sample_memory_manifest
                elif package == "quaestor.claude.hooks" and filename == "automation_base.json":
                    return '{"hooks": {}}'
                elif package == "quaestor.claude.commands":
                    return f"# {filename} content"
                raise FileNotFoundError(f"Unknown file: {package}/{filename}")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir), "--mode", "team"])

            assert result.exit_code == 0
            assert "Setting up documentation files" in result.output
            assert "Created ARCHITECTURE.md" in result.output
            assert "Created MEMORY.md" in result.output

            # Check that template files were processed and files created
            arch_content = (temp_dir / ".quaestor" / "ARCHITECTURE.md").read_text()
            assert "Domain Layer" in arch_content  # Original content preserved
            assert "Infrastructure Layer" in arch_content

            # Check MEMORY.md was processed
            mem_content = (temp_dir / ".quaestor" / "MEMORY.md").read_text()
            assert "Payment integration" in mem_content  # Original content preserved

    def test_init_merges_with_existing_claude_md(self, runner, temp_dir):
        """Test that init merges with existing CLAUDE.md instead of overwriting."""
        # Create existing CLAUDE.md with custom content
        existing_claude = temp_dir / "CLAUDE.md"
        existing_claude.write_text("# My Custom Claude Config\n\nThis is my custom content.")

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor.claude.templates", "claude_include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n"
                        "<!-- QUAESTOR CONFIG END -->\n\n<!-- Your custom content below -->"
                    ),
                    ("quaestor.claude.templates", "quaestor_claude.md"): ("# QUAESTOR_CLAUDE.md test content"),
                    ("quaestor.claude.templates", "critical_rules.md"): "# CRITICAL_RULES test content",
                    ("quaestor.claude.templates", "architecture.md"): "# AI ARCHITECTURE template",
                    ("quaestor.claude.templates", "memory.md"): "# AI MEMORY template",
                }
                if package == "quaestor.claude.commands":
                    return f"# {resource} content"
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir), "--mode", "team", "--no-contextual"])

            assert result.exit_code == 0

            # Check that CLAUDE.md exists and contains both Quaestor config and original content
            updated_content = existing_claude.read_text()
            assert "<!-- QUAESTOR CONFIG START -->" in updated_content
            assert "<!-- QUAESTOR CONFIG END -->" in updated_content
            assert "My Custom Claude Config" in updated_content
            assert "This is my custom content." in updated_content

            # Ensure Quaestor config is at the beginning
            assert updated_content.startswith("<!-- QUAESTOR CONFIG START -->")


class TestCLIApp:
    """Tests for the CLI app itself."""

    def test_app_has_init_command(self, runner):
        """Test that the app has init command registered."""
        # Check that init command exists by trying to get its help
        result = runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize Quaestor" in result.output

    def test_help_displays_correctly(self, runner):
        """Test that help text displays correctly."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Quaestor - Context management" in result.output
        assert "init" in result.output
        assert "Initialize Quaestor" in result.output
