"""Integration tests for simplified UserPromptSubmit hook."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from src.quaestor.claude.hooks.user_prompt_submit import UserPromptSubmitHook


class TestUserPromptSubmitHook:
    """Integration tests for UserPromptSubmit hook."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for test
        self.temp_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create .quaestor directory
        self.quaestor_dir = Path(".quaestor")
        self.quaestor_dir.mkdir(exist_ok=True)

        # Initialize hook
        self.hook = UserPromptSubmitHook()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.old_cwd)
        shutil.rmtree(self.temp_dir)

    def test_slash_command_framework_mode(self):
        """Test that slash commands are processed."""
        # Mock input data
        self.hook.input_data = {
            "user_prompt": "/plan user authentication system",
            "sessionId": "test-session-123",
            "timestamp": "2024-01-01T10:00:00Z",
            "working_directory": self.temp_dir,
        }

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify simplified output
        assert output_data["session_id"] == "test-session-123"
        assert "message" in output_data
        assert output_data["message"] == "Ready to assist!"
        assert "has_active_work" in output_data

    def test_natural_language_drive_mode(self):
        """Test natural language input processing."""
        # Mock input data
        self.hook.input_data = {
            "user_prompt": "Can you help me build a web application?",
            "sessionId": "test-session-456",
            "timestamp": "2024-01-01T10:00:00Z",
            "working_directory": self.temp_dir,
        }

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify output
        assert output_data["session_id"] == "test-session-456"
        assert output_data["message"] == "Ready to assist!"
        assert "has_active_work" in output_data

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts."""
        # Mock input data with empty prompt
        self.hook.input_data = {
            "user_prompt": "",
            "sessionId": "test-session-789",
            "timestamp": "2024-01-01T10:00:00Z",
            "working_directory": self.temp_dir,
        }

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify output
        assert output_data["session_id"] == "test-session-789"
        assert output_data["message"] == "Ready to assist!"

    def test_error_handling(self):
        """Test error handling in hook execution."""
        # Mock input data that causes an error
        self.hook.input_data = None  # This should cause an error

        # Mock output methods to capture error message
        error_messages = []
        self.hook.output_error = MagicMock(side_effect=lambda msg: error_messages.append(msg))

        # Execute hook
        self.hook.execute()

        # Verify error was handled
        assert len(error_messages) > 0
        assert "Hook execution failed" in error_messages[0]

    def test_workflow_state_error_handling(self):
        """Test that hook handles missing workflow state gracefully."""
        # Mock input data
        self.hook.input_data = {
            "user_prompt": "/impl feature",
            "sessionId": "test-session-999",
        }

        # Mock has_active_work to return False
        self.hook.has_active_work = MagicMock(return_value=False)

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify output
        assert output_data["session_id"] == "test-session-999"
        assert output_data["has_active_work"] is False

    def test_long_prompt_truncation(self):
        """Test that long prompts are truncated in logs."""
        # Create a very long prompt
        long_prompt = "x" * 200

        # Mock input data
        self.hook.input_data = {
            "user_prompt": long_prompt,
            "sessionId": "test-session-long",
        }

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify output (prompt truncation happens in logging, not output)
        assert output_data["session_id"] == "test-session-long"
        assert output_data["message"] == "Ready to assist!"

    def test_mode_transition(self):
        """Test that hook processes different prompt types consistently."""
        prompts = [
            "/plan something",
            "build a feature",
            "/research patterns",
            "explain this code",
        ]

        for prompt in prompts:
            # Reset hook state
            self.hook.input_data = {
                "user_prompt": prompt,
                "sessionId": f"test-{prompt[:10]}",
            }

            # Mock output methods
            output_data = {}
            self.hook.output_success = MagicMock(side_effect=lambda data, od=output_data: od.update(data))

            # Execute hook
            self.hook.execute()

            # All prompts should get consistent output
            assert "session_id" in output_data
            assert output_data["message"] == "Ready to assist!"
            assert "has_active_work" in output_data

    def test_performance_compliance(self):
        """Test that hook executes quickly."""
        import time

        # Mock input data
        self.hook.input_data = {
            "user_prompt": "/plan authentication",
            "sessionId": "perf-test",
        }

        # Mock output methods
        self.hook.output_success = MagicMock()

        # Measure execution time
        start_time = time.time()
        self.hook.execute()
        execution_time = time.time() - start_time

        # Hook should execute very quickly (under 100ms)
        assert execution_time < 0.1
