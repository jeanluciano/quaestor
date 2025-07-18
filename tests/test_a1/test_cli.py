"""Tests for V2.1 CLI commands."""

import pytest
from typer.testing import CliRunner

from a1.cli import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestV21CLI:
    """Test V2.1 CLI basic functionality."""

    def test_version_command(self, runner):
        """Test version command shows V2.1 info."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Quaestor A1" in result.stdout
        assert "vA1.0" in result.stdout
        assert "Core Components" in result.stdout
        assert "79% reduction" in result.stdout

    def test_status_command(self, runner):
        """Test status command shows system health."""
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "A1 System Status" in result.stdout
        assert "Core Components" in result.stdout
        assert "Extensions" in result.stdout
        assert "Performance" in result.stdout

    def test_help_command(self, runner):
        """Test help command shows available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Quaestor A1" in result.stdout
        assert "event" in result.stdout
        assert "context" in result.stdout
        assert "quality" in result.stdout
        assert "extensions" in result.stdout

    def test_no_command_shows_help(self, runner):
        """Test running without command shows help."""
        result = runner.invoke(app, [])

        # Typer exits with code 2 when no command is provided, which is expected
        assert result.exit_code == 2


class TestEventCommands:
    """Test event bus commands."""

    def test_event_status(self, runner):
        """Test event status command."""
        result = runner.invoke(app, ["event", "status"])

        assert result.exit_code == 0
        assert "Event Bus Status" in result.stdout

    def test_event_monitor(self, runner):
        """Test event monitor command (should start and stop quickly)."""
        # Use input to simulate Ctrl+C
        result = runner.invoke(app, ["event", "monitor"], input="\x03")

        # Should exit gracefully (might be 0 or 1 depending on KeyboardInterrupt handling)
        assert result.exit_code in [0, 1]
        assert "Event Bus Monitor" in result.stdout


class TestContextCommands:
    """Test context management commands."""

    def test_context_list(self, runner):
        """Test context list command."""
        result = runner.invoke(app, ["context", "list"])

        assert result.exit_code == 0
        assert "Available Contexts" in result.stdout

    def test_context_switch(self, runner):
        """Test context switch command."""
        result = runner.invoke(app, ["context", "switch", "test"])

        assert result.exit_code == 0
        assert "Switching to context: test" in result.stdout
        assert "Switched to context: test" in result.stdout


class TestQualityCommands:
    """Test quality management commands."""

    def test_quality_check(self, runner):
        """Test quality check command."""
        result = runner.invoke(app, ["quality", "check"])

        assert result.exit_code == 0
        assert "Quality Check" in result.stdout
        assert "Running quality checks" in result.stdout or "Code Style" in result.stdout

    def test_quality_check_with_path(self, runner, tmp_path):
        """Test quality check with specific path."""
        result = runner.invoke(app, ["quality", "check", str(tmp_path)])

        assert result.exit_code == 0
        # Path might be wrapped across lines in terminal output, so check for the basename
        assert tmp_path.name in result.stdout

    def test_quality_report(self, runner):
        """Test quality report command."""
        result = runner.invoke(app, ["quality", "report"])

        assert result.exit_code == 0
        assert "Quality Report" in result.stdout


class TestExtensionCommands:
    """Test extension management commands."""

    def test_extensions_list(self, runner):
        """Test extensions list command."""
        result = runner.invoke(app, ["extensions", "list"])

        assert result.exit_code == 0
        assert "A1 Extensions" in result.stdout
        assert "prediction" in result.stdout
        assert "hooks" in result.stdout
        assert "state" in result.stdout
        assert "workflow" in result.stdout
        assert "persistence" in result.stdout

    def test_extensions_status(self, runner):
        """Test extensions status command."""
        result = runner.invoke(app, ["extensions", "status"])

        assert result.exit_code == 0
        assert "All Extensions Status" in result.stdout

    def test_extensions_status_specific(self, runner):
        """Test extensions status for specific extension."""
        result = runner.invoke(app, ["extensions", "status", "prediction"])

        assert result.exit_code == 0
        assert "Extension Status: prediction" in result.stdout


class TestConfigCommands:
    """Test configuration commands."""

    def test_config_show(self, runner):
        """Test config show command."""
        result = runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0
        assert "A1 Configuration" in result.stdout

    def test_config_init(self, runner):
        """Test config init command."""
        result = runner.invoke(app, ["config", "init"])

        assert result.exit_code == 0
        assert "Initializing A1 Configuration" in result.stdout
        # Should either initialize or warn about existing config
        assert (
            "configuration initialized successfully" in result.stdout or "Configuration already exists" in result.stdout
        )


class TestPredictionCommands:
    """Test prediction engine commands."""

    def test_predict_next_tool(self, runner):
        """Test predict next-tool command."""
        result = runner.invoke(app, ["predict", "next-tool"])

        assert result.exit_code == 0
        assert "Tool Predictions" in result.stdout

    def test_predict_next_tool_with_count(self, runner):
        """Test predict next-tool with custom count."""
        result = runner.invoke(app, ["predict", "next-tool", "--count", "5"])

        assert result.exit_code == 0
        assert "Tool Predictions (top 5)" in result.stdout

    def test_predict_next_file(self, runner):
        """Test predict next-file command."""
        result = runner.invoke(app, ["predict", "next-file"])

        assert result.exit_code == 0
        assert "File Predictions" in result.stdout

    def test_predict_next_file_with_count(self, runner):
        """Test predict next-file with custom count."""
        result = runner.invoke(app, ["predict", "next-file", "-c", "2"])

        assert result.exit_code == 0
        assert "File Predictions (top 2)" in result.stdout


class TestStateCommands:
    """Test state management commands."""

    def test_state_snapshot(self, runner):
        """Test state snapshot command."""
        result = runner.invoke(app, ["state", "snapshot"])

        assert result.exit_code == 0
        assert "Creating Snapshot" in result.stdout
        assert "Snapshot created" in result.stdout

    def test_state_snapshot_with_description(self, runner):
        """Test state snapshot with custom description."""
        result = runner.invoke(app, ["state", "snapshot", "--desc", "Test snapshot"])

        assert result.exit_code == 0
        assert "Creating Snapshot" in result.stdout
        assert "Test snapshot" in result.stdout

    def test_state_list(self, runner):
        """Test state list command."""
        result = runner.invoke(app, ["state", "list"])

        assert result.exit_code == 0
        assert "Available Snapshots" in result.stdout

    def test_state_restore(self, runner):
        """Test state restore command."""
        result = runner.invoke(app, ["state", "restore", "snapshot_001"])

        assert result.exit_code == 0
        assert "Restoring Snapshot: snapshot_001" in result.stdout
        assert "Restored from snapshot" in result.stdout


class TestCommandGroupStructure:
    """Test overall command structure and help."""

    def test_all_subcommands_have_help(self, runner):
        """Test that all subcommand groups have help."""
        subcommands = ["event", "context", "quality", "extensions", "config", "predict", "state"]

        for cmd in subcommands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0
            assert "help" in result.stdout.lower() or "command" in result.stdout.lower()

    def test_invalid_command_shows_error(self, runner):
        """Test that invalid commands show appropriate error."""
        result = runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0

    def test_command_discovery(self, runner):
        """Test that main help shows all command groups."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0

        # Check for command groups
        expected_commands = ["event", "context", "quality", "extensions", "config", "predict", "state"]
        for cmd in expected_commands:
            assert cmd in result.stdout


class TestErrorHandling:
    """Test error handling in CLI."""

    def test_missing_required_argument(self, runner):
        """Test commands that require arguments show error when missing."""
        result = runner.invoke(app, ["context", "switch"])

        assert result.exit_code != 0
        # Typer puts error messages in stderr or they might be in output
        error_output = result.stdout + (result.stderr or "")
        assert "Missing argument" in error_output or "required" in error_output.lower() or result.exit_code == 2

    def test_invalid_option_values(self, runner):
        """Test invalid option values are handled gracefully."""
        result = runner.invoke(app, ["predict", "next-tool", "--count", "invalid"])

        assert result.exit_code != 0


class TestPerformance:
    """Test CLI performance characteristics."""

    def test_version_command_speed(self, runner):
        """Test version command executes quickly."""
        import time

        start_time = time.time()
        result = runner.invoke(app, ["version"])
        execution_time = time.time() - start_time

        assert result.exit_code == 0
        # Should execute in under 2 seconds (generous for CI)
        assert execution_time < 2.0

    def test_status_command_speed(self, runner):
        """Test status command executes quickly."""
        import time

        start_time = time.time()
        result = runner.invoke(app, ["status"])
        execution_time = time.time() - start_time

        assert result.exit_code == 0
        # Should execute in under 3 seconds (includes system initialization)
        assert execution_time < 3.0


class TestIntegration:
    """Test CLI integration with V2.1 components."""

    def test_system_initialization(self, runner):
        """Test that CLI can initialize V2.1 system."""
        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "operational" in result.stdout or "System Status" in result.stdout

    def test_extension_loading(self, runner):
        """Test that extensions can be loaded through CLI."""
        result = runner.invoke(app, ["extensions", "list"])

        assert result.exit_code == 0
        # Should show at least some extensions
        assert "prediction" in result.stdout
        assert "Extension" in result.stdout

    def test_component_access(self, runner):
        """Test that core components are accessible."""
        result = runner.invoke(app, ["event", "status"])

        assert result.exit_code == 0
        assert "Event Bus" in result.stdout or "event" in result.stdout.lower()
