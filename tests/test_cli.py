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
        """Test that init creates .quaestor directory with templates."""
        # Patch package resources to return test content
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor", "include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "agent.md"): "# AGENT.md test content",
                    ("quaestor", "architecture.md"): "# ARCHITECTURE template",
                    ("quaestor", "rules.md"): "# RULES template",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir), "--no-contextual"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert (temp_dir / "CLAUDE.md").exists()
            assert (temp_dir / ".quaestor" / "AGENT.md").exists()
            assert (temp_dir / ".quaestor" / "ARCHITECTURE.md").exists()
            assert (temp_dir / ".quaestor" / "RULES.md").exists()
            # Check specs directory structure
            assert (temp_dir / ".quaestor" / "specs" / "draft").exists()
            assert (temp_dir / ".quaestor" / "specs" / "active").exists()
            assert (temp_dir / ".quaestor" / "specs" / "completed").exists()
            assert (temp_dir / ".quaestor" / "specs" / "archived").exists()

    def test_init_with_existing_directory_prompts_user(self, runner, temp_dir):
        """Test that init warns when .quaestor already exists."""
        # Create existing .quaestor directory
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()

        result = runner.invoke(app, ["init", str(temp_dir)])

        assert result.exit_code == 1
        assert "already initialized" in result.output

    def test_init_with_force_flag_overwrites(self, runner, temp_dir):
        """Test that --force flag overwrites existing directory."""
        # Create existing .quaestor directory with a file
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        (quaestor_dir / "existing.txt").write_text("existing content")

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor", "include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "agent.md"): "# AGENT.md test content",
                    ("quaestor", "architecture.md"): "# ARCHITECTURE template",
                    ("quaestor", "rules.md"): "# RULES template",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir), "--force"])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "Initialization complete!" in result.output

    def test_init_handles_template_processing(self, runner, temp_dir):
        """Test that init processes templates and creates documentation."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def side_effect(package, filename):
                files = {
                    ("quaestor", "include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "agent.md"): "# AGENT.md template",
                    ("quaestor", "architecture.md"): "# ARCHITECTURE template",
                    ("quaestor", "rules.md"): "# RULES template",
                }
                return files.get((package, filename), f"# {filename} template")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert (temp_dir / ".quaestor").exists()
            assert "Created AGENT.md" in result.output or "Generating documentation" in result.output

    def test_init_handles_resource_errors_gracefully(self, runner, temp_dir):
        """Test that init handles missing resources gracefully."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:
            # All reads fail
            mock_read.side_effect = FileNotFoundError("Resource not found")

            result = runner.invoke(app, ["init", str(temp_dir)])

            # Should still create directories but warn about missing files
            assert (temp_dir / ".quaestor").exists()
            assert "Could not" in result.output or "⚠" in result.output

    def test_init_with_custom_path(self, runner, temp_dir):
        """Test init with a custom directory path."""
        custom_dir = temp_dir / "my-project"
        custom_dir.mkdir()

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor", "include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n<!-- QUAESTOR CONFIG END -->"
                    ),
                    ("quaestor", "agent.md"): "# AGENT.md test content",
                    ("quaestor", "architecture.md"): "# ARCHITECTURE template",
                    ("quaestor", "rules.md"): "# RULES template",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(custom_dir)])

            assert result.exit_code == 0
            assert (custom_dir / ".quaestor").exists()
            assert (custom_dir / "CLAUDE.md").exists()

    def test_init_processes_template_files(
        self, runner, temp_dir, sample_architecture_manifest, sample_memory_manifest
    ):
        """Test that init properly processes template files."""
        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def side_effect(package, filename):
                if package == "quaestor" and filename == "agent.md":
                    return "# AGENT.md test content"
                elif package == "quaestor" and filename == "include.md":
                    return (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n"
                        "<!-- QUAESTOR CONFIG END -->\n\n<!-- Your custom content below -->"
                    )
                elif package == "quaestor" and filename == "architecture.md":
                    return sample_architecture_manifest
                elif package == "quaestor" and filename == "rules.md":
                    return "# RULES template"
                raise FileNotFoundError(f"Unknown file: {package}/{filename}")

            mock_read.side_effect = side_effect

            result = runner.invoke(app, ["init", str(temp_dir)])

            assert result.exit_code == 0
            assert "Generating documentation" in result.output or "Created ARCHITECTURE.md" in result.output

            # Check that template files were processed and files created
            arch_content = (temp_dir / ".quaestor" / "ARCHITECTURE.md").read_text()
            assert "Domain Layer" in arch_content  # Original content preserved
            assert "Infrastructure Layer" in arch_content

    def test_init_merges_with_existing_claude_md(self, runner, temp_dir):
        """Test that init merges with existing CLAUDE.md instead of overwriting."""
        # Create existing CLAUDE.md with custom content
        existing_claude = temp_dir / "CLAUDE.md"
        existing_claude.write_text("# My Custom Claude Config\n\nThis is my custom content.")

        with patch("quaestor.cli.init.pkg_resources.read_text") as mock_read:

            def mock_read_text(package, resource):
                files = {
                    ("quaestor", "include.md"): (
                        "<!-- QUAESTOR CONFIG START -->\nQuaestor config\n"
                        "<!-- QUAESTOR CONFIG END -->\n\n<!-- Your custom content below -->"
                    ),
                    ("quaestor", "agent.md"): "# AGENT.md test content",
                    ("quaestor", "architecture.md"): "# ARCHITECTURE template",
                    ("quaestor", "rules.md"): "# RULES template",
                }
                return files.get((package, resource), f"# {resource} content")

            mock_read.side_effect = mock_read_text

            result = runner.invoke(app, ["init", str(temp_dir), "--no-contextual"])

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
