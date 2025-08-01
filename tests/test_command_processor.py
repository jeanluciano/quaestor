"""Tests for command processor functionality."""

from unittest.mock import patch

import pytest

from quaestor.command_processor import CommandProcessor


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / ".quaestor").mkdir()
    return project_dir


@pytest.fixture
def sample_command_content():
    """Sample command content for testing."""
    return """---
allowed-tools: [Read, Write]
description: "Test command"
---

# Test Command

This is a test command.
"""


@pytest.fixture
def sample_config():
    """Sample command configuration."""
    return {
        "commands": {
            "test": {
                "enforcement": "strict",
                "parameters": {"test_param": 100},
                "custom_rules": ["Always test your code", "Never skip validation"],
            }
        }
    }


class TestCommandProcessor:
    """Test command processor functionality."""

    def test_init(self, temp_project):
        """Test processor initialization."""
        processor = CommandProcessor(temp_project)
        assert processor.project_dir == temp_project
        assert hasattr(processor, "loader")
        from quaestor.command_config import CommandLoader

        assert isinstance(processor.loader, CommandLoader)

    def test_load_base_command_success(self, temp_project):
        """Test loading base command content."""
        processor = CommandProcessor(temp_project)

        with patch("importlib.resources.read_text") as mock_read:
            mock_read.return_value = "# Test Command"
            content = processor._load_base_command("test")

            mock_read.assert_called_once_with("quaestor.claude.commands", "test.md")
            assert content == "# Test Command"

    def test_load_base_command_error(self, temp_project):
        """Test error handling when loading command."""
        processor = CommandProcessor(temp_project)

        with patch("importlib.resources.read_text") as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")

            with pytest.raises(ValueError, match="Command not found: missing"):
                processor._load_base_command("missing")

    def test_apply_configuration(self, temp_project, sample_command_content):
        """Test applying configuration to command."""
        processor = CommandProcessor(temp_project)

        config = {"enforcement": "strict", "rules": ["Always test", "Never skip validation"]}

        result = processor._apply_configuration(sample_command_content, config)

        # Should inject header after title
        assert "PROJECT-SPECIFIC" in result
        assert "STRICT ENFORCEMENT ENABLED" in result
        assert "Always test" in result
        assert "Never skip validation" in result

    def test_has_configuration(self, temp_project):
        """Test checking if command has configuration."""
        processor = CommandProcessor(temp_project)

        # Mock the loader's config methods
        with (
            patch.object(processor.loader.config, "get_command_config") as mock_get_config,
            patch.object(processor.loader.config, "has_override") as mock_has_override,
        ):
            # No config or override
            mock_get_config.return_value = {}
            mock_has_override.return_value = False
            assert not processor.has_configuration("test")

            # Has config
            mock_get_config.return_value = {"enforcement": "strict"}
            assert processor.has_configuration("test")

            # Has override
            mock_get_config.return_value = {}
            mock_has_override.return_value = True
            assert processor.has_configuration("test")

    def test_process_command_no_config(self, temp_project, sample_command_content):
        """Test processing command without configuration."""
        processor = CommandProcessor(temp_project)

        with (
            patch.object(processor, "_load_base_command") as mock_load,
            patch.object(processor.loader, "load_command") as mock_loader,
        ):
            mock_load.return_value = sample_command_content
            mock_loader.return_value = sample_command_content  # No changes

            result = processor.process_command("test")

            # Should not add marker if no changes
            # No configuration marker expected when using new implementation
            assert "PROJECT-SPECIFIC" not in result
            assert result == sample_command_content

    def test_process_command_with_config(self, temp_project, sample_command_content):
        """Test processing command with configuration."""
        processor = CommandProcessor(temp_project)

        # Mock to have configuration
        with (
            patch.object(processor, "_load_base_command") as mock_load,
            patch.object(processor.loader, "get_override") as mock_override,
            patch.object(processor.loader, "get_configuration") as mock_config,
        ):
            mock_load.return_value = sample_command_content
            mock_override.return_value = None  # No override
            mock_config.return_value = {"enforcement": "strict", "rules": ["Always test", "Never skip validation"]}

            result = processor.process_command("test")

            # Should have PROJECT-SPECIFIC marker when configured
            assert "PROJECT-SPECIFIC" in result

    def test_get_configured_commands(self, temp_project):
        """Test getting list of configured commands."""
        processor = CommandProcessor(temp_project)

        # Create a config file with some commands
        config_path = temp_project / ".quaestor" / "command-config.yaml"
        config_path.write_text("""
        commands:
            task:
                enforcement: strict
            check:
                enforcement: relaxed
        """)

        configured = processor.get_configured_commands()

        assert "task" in configured
        assert "check" in configured

    def test_preview_configuration(self, temp_project, sample_command_content):
        """Test previewing configuration changes."""
        processor = CommandProcessor(temp_project)
        modified_content = sample_command_content + "\n## Configuration Applied"

        with (
            patch.object(processor, "_load_base_command") as mock_load,
            patch.object(processor, "process_command") as mock_process,
        ):
            mock_load.return_value = sample_command_content
            mock_process.return_value = modified_content

            preview = processor.preview_configuration("test")

            assert preview["base"] == sample_command_content
            assert preview["configured"] == modified_content
            assert preview["has_changes"] is True

            # Test no changes
            mock_process.return_value = sample_command_content
            preview_no_change = processor.preview_configuration("test")
            assert preview_no_change["has_changes"] is False


class TestCommandProcessorIntegration:
    """Integration tests with real CommandConfig."""

    def test_full_processing_workflow(self, temp_project):
        """Test complete command processing workflow."""
        # Create a real config file
        config_path = temp_project / ".quaestor" / "command-config.yaml"
        config_path.write_text("""
commands:
  task:
    enforcement: strict
    parameters:
      max_lines: 30
    custom_rules:
      - "Use type hints"
""")

        # Create command override
        override_dir = temp_project / ".quaestor" / "commands"
        override_dir.mkdir(parents=True)
        override_path = override_dir / "check.md"
        override_path.write_text("# Custom Check Command")

        processor = CommandProcessor(temp_project)

        # Test with base command content
        base_task = """---
allowed-tools: [Read, Write]
---
# Task Command

max_lines: 50
"""

        with patch("importlib.resources.read_text") as mock_read:
            mock_read.return_value = base_task

            # Process task command (has config)
            task_result = processor.process_command("task")
            # Should have configuration applied
            assert "PROJECT-SPECIFIC" in task_result or "Use type hints" in task_result

            # Process check command (has override)
            check_result = processor.process_command("check")
            # Override is applied directly
            assert "# Custom Check Command" in check_result

    def test_error_handling(self, temp_project):
        """Test error handling in various scenarios."""
        processor = CommandProcessor(temp_project)

        # Test missing command
        with pytest.raises(ValueError, match="Command not found"):
            processor.process_command("nonexistent")

        # Test with malformed config
        config_path = temp_project / ".quaestor" / "command-config.yaml"
        config_path.write_text("invalid: yaml: content:")

        # Should handle gracefully
        with patch("importlib.resources.read_text") as mock_read:
            mock_read.return_value = "# Test"
            result = processor.process_command("test")
            assert result == "# Test"  # Falls back to base
