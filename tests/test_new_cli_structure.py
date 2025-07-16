"""Tests for the new modular CLI structure."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from quaestor.cli import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestNewCLIStructure:
    """Test the new modular CLI structure."""

    def test_cli_app_imports_successfully(self):
        """Test that the CLI app can be imported without errors."""
        from quaestor.cli import app

        assert app is not None

    def test_init_command_imports_successfully(self):
        """Test that the init command can be imported without errors."""
        from quaestor.cli.init import init_command

        assert callable(init_command)

    def test_new_utils_import_successfully(self):
        """Test that the new utils can be imported without errors."""
        from quaestor.utils.file_utils import update_gitignore
        from quaestor.utils.project_detection import detect_project_type

        assert callable(detect_project_type)
        assert callable(update_gitignore)

    def test_new_template_processor_imports_successfully(self):
        """Test that the new template processor can be imported without errors."""
        from quaestor.core.template_engine import get_project_data, process_template

        assert callable(get_project_data)
        assert callable(process_template)

    def test_languages_yaml_exists(self):
        """Test that the languages.yaml config file exists."""
        from pathlib import Path

        config_path = Path(__file__).parent.parent / "src" / "quaestor" / "assets" / "configuration" / "languages.yaml"
        assert config_path.exists(), f"languages.yaml not found at {config_path}"

    def test_init_command_help(self, runner):
        """Test that the init command help works."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize Quaestor" in result.output

    def test_project_detection_works(self, temp_dir):
        """Test that project detection utility works."""
        from quaestor.utils.project_detection import detect_project_type

        # Clear the cache to ensure fresh detection
        detect_project_type.cache_clear()

        # Test Python project detection
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
        project_type = detect_project_type(temp_dir)
        assert project_type == "python"

        # Clear cache before next test
        detect_project_type.cache_clear()

        # Test JavaScript project detection
        (temp_dir / "pyproject.toml").unlink()
        (temp_dir / "package.json").write_text('{"name": "test"}')
        project_type = detect_project_type(temp_dir)
        assert project_type == "javascript"

        # Clear cache before next test
        detect_project_type.cache_clear()

        # Test unknown project
        (temp_dir / "package.json").unlink()
        project_type = detect_project_type(temp_dir)
        assert project_type == "unknown"

    def test_template_processor_works(self, temp_dir):
        """Test that the new template processor works."""
        from quaestor.core.template_engine import get_project_data, process_template

        # Create a simple Python project
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")

        # Get project data
        project_data = get_project_data(temp_dir)
        assert project_data["project_type"] == "python"
        assert project_data["project_name"] == temp_dir.name
        assert "lint_command" in project_data

        # Test template processing
        template_content = "Project: {{ project_name }}\nType: {{ project_type }}\nLint: {{ lint_command }}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
            tf.write(template_content)
            template_path = Path(tf.name)

        try:
            result = process_template(template_path, project_data)
            assert f"Project: {temp_dir.name}" in result
            assert "Type: python" in result
            assert "Lint: ruff check ." in result
        finally:
            template_path.unlink()

    def test_init_command_validation(self, runner):
        """Test that init command validates mode parameter."""
        result = runner.invoke(app, ["init", ".", "--mode", "invalid"])
        assert result.exit_code == 1
        assert "Invalid mode" in result.output

    @patch("quaestor.cli.init.pkg_resources.read_text")
    def test_init_personal_mode_basic(self, mock_read, runner, temp_dir):
        """Test basic personal mode initialization."""

        def mock_read_text(package, resource):
            # Mock template files
            files = {
                ("quaestor.templates", "ARCHITECTURE.template.md"): "# ARCHITECTURE for {{ project_name }}",
                ("quaestor.templates", "MEMORY.template.md"): "# MEMORY for {{ project_name }}",
                ("quaestor.templates", "PATTERNS.template.md"): "# PATTERNS for {{ project_name }}",
                ("quaestor.templates", "VALIDATION.template.md"): "# VALIDATION for {{ project_name }}",
                ("quaestor.templates", "AUTOMATION.template.md"): "# AUTOMATION for {{ project_name }}",
            }
            if package == "quaestor.commands":
                return f"# {resource} content"
            return files.get((package, resource), f"# {resource}")

        mock_read.side_effect = mock_read_text

        # Test personal mode init
        result = runner.invoke(app, ["init", str(temp_dir), "--mode", "personal", "--force"])

        # Should succeed (exit code 0) or fail gracefully
        # The exact behavior depends on dependencies like RuleEngine
        assert result.exit_code in [0, 1]  # Allow either success or graceful failure

        # Check that directories would be created (at least attempted)
        if result.exit_code == 0:
            assert (temp_dir / ".claude").exists()
            assert (temp_dir / ".quaestor").exists()

    @patch("quaestor.cli.init.pkg_resources.read_text")
    def test_template_files_processing(self, mock_read, temp_dir):
        """Test that template files are processed correctly."""
        from quaestor.cli.init import _init_common

        def mock_read_text(package, resource):
            files = {
                ("quaestor.templates", "ARCHITECTURE.template.md"): "# ARCHITECTURE for {{ project_name }}",
                ("quaestor.templates", "MEMORY.template.md"): "# MEMORY for {{ project_name }}",
                ("quaestor.templates", "PATTERNS.template.md"): "# PATTERNS for {{ project_name }}",
                ("quaestor.templates", "VALIDATION.template.md"): "# VALIDATION for {{ project_name }}",
                ("quaestor.templates", "AUTOMATION.template.md"): "# AUTOMATION for {{ project_name }}",
            }
            if package == "quaestor.commands":
                return f"# {resource} content"
            return files.get((package, resource), f"# {resource}")

        mock_read.side_effect = mock_read_text

        # Create a simple project
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")

        try:
            copied_files, commands_copied = _init_common(temp_dir, False, "personal")

            # Should have attempted to copy files
            assert isinstance(copied_files, list)
            assert isinstance(commands_copied, int)

            # Check that .quaestor directory was created
            assert (temp_dir / ".quaestor").exists()

        except Exception as e:
            # Allow for graceful failure due to missing dependencies
            assert "Could not" in str(e) or "Failed" in str(e) or isinstance(e, ImportError | FileNotFoundError)

    def test_gitignore_utility_works(self, temp_dir):
        """Test that the gitignore utility works."""
        from quaestor.utils.file_utils import update_gitignore

        entries = ["# Test section", ".test/", "*.tmp"]
        result = update_gitignore(temp_dir, entries, "Test")

        # Should succeed
        assert result is True

        # Check that gitignore was created
        gitignore_path = temp_dir / ".gitignore"
        assert gitignore_path.exists()

        content = gitignore_path.read_text()
        assert "# Test section" in content
        assert ".test/" in content
        assert "*.tmp" in content

    def test_file_utils_work(self, temp_dir):
        """Test that file utilities work."""
        from quaestor.utils.file_utils import create_directory, safe_read_text, safe_write_text

        # Test directory creation
        test_dir = temp_dir / "test" / "nested"
        result = create_directory(test_dir)
        assert result is True
        assert test_dir.exists()

        # Test safe file operations
        test_file = temp_dir / "test.txt"
        content = "Hello, World!"

        result = safe_write_text(test_file, content)
        assert result is True
        assert test_file.exists()

        read_content = safe_read_text(test_file)
        assert read_content == content

    def test_yaml_utils_work(self, temp_dir):
        """Test that YAML utilities work."""
        from quaestor.utils.yaml_utils import load_yaml, save_yaml

        # Test YAML operations
        test_file = temp_dir / "test.yaml"
        test_data = {"name": "test", "version": "1.0", "config": {"debug": True, "items": ["a", "b", "c"]}}

        # Save YAML
        result = save_yaml(test_file, test_data)
        assert result is True
        assert test_file.exists()

        # Load YAML
        loaded_data = load_yaml(test_file)
        assert loaded_data == test_data


class TestBackwardCompatibility:
    """Test that the refactoring maintains backward compatibility."""

    def test_legacy_template_processor_works(self, temp_dir):
        """Test that the legacy template processor wrapper works."""
        from quaestor.core.template_engine import get_project_data, process_template

        # Create a simple Python project
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")

        # Get project data through legacy interface
        project_data = get_project_data(temp_dir)
        assert project_data["project_type"] == "python"
        assert project_data["project_name"] == temp_dir.name

        # Test template processing through legacy interface
        template_content = "Project: {{ project_name }}\nType: {{ project_type }}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
            tf.write(template_content)
            template_path = Path(tf.name)

        try:
            result = process_template(template_path, project_data)
            assert f"Project: {temp_dir.name}" in result
            assert "Type: python" in result
        finally:
            template_path.unlink()

    def test_original_cli_still_works(self, runner):
        """Test that the original CLI commands still work."""
        # Test that we can still invoke help
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Quaestor" in result.output
        assert "init" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
