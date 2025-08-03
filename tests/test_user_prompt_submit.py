"""Integration tests for UserPromptSubmit hook."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
        """Test that slash commands trigger framework mode."""
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

        # Verify framework mode detected
        assert output_data["session_mode"] == "framework"
        assert output_data["mode_confidence"] >= 0.95
        assert "Framework mode activated" in output_data["message"]

        # Verify workflow state updated
        state_file = self.quaestor_dir / ".workflow_state"
        assert state_file.exists()

        with open(state_file) as f:
            state = json.load(f)
            assert state["session_mode"] == "framework"
            assert state["mode_confidence"] >= 0.95
            assert "mode_set_at" in state

    def test_natural_language_drive_mode(self):
        """Test that natural language triggers drive mode."""
        # Mock input data
        self.hook.input_data = {
            "user_prompt": "help me fix this typo in the README",
            "sessionId": "test-session-456",
            "timestamp": "2024-01-01T11:00:00Z",
            "working_directory": self.temp_dir,
        }

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Verify drive mode detected
        assert output_data["session_mode"] == "drive"
        assert output_data["mode_confidence"] >= 0.7
        assert "Drive mode activated" in output_data["message"]

        # Verify silent tracking initialized
        assert output_data["workflow_state"]["silent_tracking"] is not None
        assert "files_modified" in output_data["workflow_state"]["silent_tracking"]
        assert "commands_run" in output_data["workflow_state"]["silent_tracking"]

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts."""
        # Mock input data with empty prompt
        self.hook.input_data = {"user_prompt": "", "sessionId": "test-session-789", "timestamp": "2024-01-01T12:00:00Z"}

        # Mock output methods
        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook
        self.hook.execute()

        # Should default to drive mode
        assert output_data["session_mode"] == "drive"
        assert output_data["mode_confidence"] == 0.5
        assert "empty_or_invalid_prompt" in output_data["detection_metadata"]["triggers"]

    def test_mode_detection_error_handling(self):
        """Test error handling when mode detection fails."""
        # Mock a detection failure
        with patch.object(self.hook.mode_detector, "detect_mode", side_effect=Exception("Detection failed")):
            self.hook.input_data = {
                "user_prompt": "/plan feature",
                "sessionId": "test-session",
                "timestamp": "2024-01-01T13:00:00Z",
            }

            output_data = {}
            self.hook.output_success = MagicMock(side_effect=lambda data, od=output_data: od.update(data))

            # Execute hook - should not crash
            self.hook.execute()

            # Should default to drive mode with error info
            assert output_data["session_mode"] == "drive"
            assert output_data["mode_confidence"] == 0.5
            assert "detection_error" in output_data["detection_metadata"]["triggers"]

    def test_workflow_state_error_handling(self):
        """Test error handling when state update fails."""
        # Make .quaestor directory read-only to cause write failure
        os.chmod(self.quaestor_dir, 0o444)

        self.hook.input_data = {
            "user_prompt": "/plan feature",
            "sessionId": "test-session",
            "timestamp": "2024-01-01T14:00:00Z",
        }

        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        # Execute hook - should continue despite state write failure
        self.hook.execute()

        # Should still return detection result
        assert output_data["session_mode"] == "framework"
        assert output_data["mode_confidence"] >= 0.95

        # Restore permissions
        os.chmod(self.quaestor_dir, 0o755)

    def test_existing_workflow_state_preservation(self):
        """Test that existing workflow state is preserved."""
        # Create existing state file
        existing_state = {
            "phase": "researching",
            "last_research": "2024-01-01T09:00:00Z",
            "research_files": ["/src/main.py", "/src/utils.py"],
            "custom_field": "preserved_value",
        }

        state_file = self.quaestor_dir / ".workflow_state"
        with open(state_file, "w") as f:
            json.dump(existing_state, f)

        # Execute hook
        self.hook.input_data = {
            "user_prompt": "/plan new feature",
            "sessionId": "test-session",
            "timestamp": "2024-01-01T15:00:00Z",
        }

        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))

        self.hook.execute()

        # Verify existing fields preserved
        with open(state_file) as f:
            updated_state = json.load(f)
            assert updated_state["phase"] == "researching"
            assert updated_state["last_research"] == "2024-01-01T09:00:00Z"
            assert updated_state["research_files"] == ["/src/main.py", "/src/utils.py"]
            assert updated_state["custom_field"] == "preserved_value"
            # And new fields added
            assert updated_state["session_mode"] == "framework"
            assert "mode_confidence" in updated_state

    def test_mode_transition(self):
        """Test transitioning between modes in same session."""
        # Start with drive mode
        self.hook.input_data = {
            "user_prompt": "quick fix for typo",
            "sessionId": "transition-session",
            "timestamp": "2024-01-01T16:00:00Z",
        }

        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))
        self.hook.execute()

        assert output_data["session_mode"] == "drive"

        # Transition to framework mode
        self.hook.input_data = {
            "user_prompt": "/review code quality",
            "sessionId": "transition-session",
            "timestamp": "2024-01-01T16:05:00Z",
        }

        output_data.clear()
        self.hook.execute()

        assert output_data["session_mode"] == "framework"

        # Verify state reflects transition
        state_file = self.quaestor_dir / ".workflow_state"
        with open(state_file) as f:
            state = json.load(f)
            assert state["session_mode"] == "framework"
            # Silent tracking should still exist from drive mode
            assert "silent_tracking" in state

    def test_input_sanitization(self):
        """Test that user input is sanitized for logging."""
        # Input with potential log injection
        malicious_input = "test\nERROR: Fake error\r\nINFO: Injected log"

        self.hook.input_data = {
            "user_prompt": malicious_input,
            "sessionId": "sanitize-test",
            "timestamp": "2024-01-01T17:00:00Z",
        }

        # Capture log output
        with patch.object(self.hook.logger, "info") as mock_logger:
            output_data = {}
            self.hook.output_success = MagicMock(side_effect=lambda data, od=output_data: od.update(data))
            self.hook.execute()

            # Verify sanitization in logs
            log_call = mock_logger.call_args[0][0]
            assert "\n" not in log_call
            assert "\r" not in log_call
            assert "\\n" in log_call or "\\r" in log_call  # Escaped versions

        # Verify sanitization in workflow state file
        state_file = self.quaestor_dir / ".workflow_state"
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                if "mode_metadata" in state and "prompt_analyzed" in state["mode_metadata"]:
                    assert "\n" not in state["mode_metadata"]["prompt_analyzed"]
                    assert (
                        "\\n" in state["mode_metadata"]["prompt_analyzed"]
                        or "\\r" in state["mode_metadata"]["prompt_analyzed"]
                    )

    def test_performance_compliance(self):
        """Test that hook execution meets performance requirements."""
        import time

        test_prompts = [
            "/plan complex feature",
            "simple question about code",
            "a very long prompt " * 100,
        ]

        for prompt in test_prompts:
            self.hook.input_data = {
                "user_prompt": prompt,
                "sessionId": f"perf-test-{time.time()}",
                "timestamp": "2024-01-01T18:00:00Z",
            }

            output_data = {}
            self.hook.output_success = MagicMock(side_effect=lambda data, od=output_data: od.update(data))

            start_time = time.perf_counter()
            self.hook.execute()
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Total execution should be well under timeout
            assert elapsed_ms < 1000, f"Hook execution took {elapsed_ms:.2f}ms"

            # Detection time should be under 10ms
            detection_time = output_data["detection_metadata"]["detection_time_ms"]
            assert detection_time < 10, f"Detection took {detection_time:.2f}ms"

    def test_metadata_completeness(self):
        """Test that all required metadata is included."""
        self.hook.input_data = {
            "user_prompt": "/plan feature",
            "sessionId": "metadata-test",
            "timestamp": "2024-01-01T19:00:00Z",
            "working_directory": "/test/dir",
        }

        output_data = {}
        self.hook.output_success = MagicMock(side_effect=lambda data: output_data.update(data))
        self.hook.execute()

        # Check top-level fields
        assert "session_mode" in output_data
        assert "mode_confidence" in output_data
        assert "workflow_state" in output_data
        assert "detection_metadata" in output_data
        assert "message" in output_data

        # Check workflow state fields
        ws = output_data["workflow_state"]
        assert "phase" in ws
        assert "session_mode" in ws
        assert "mode_confidence" in ws
        assert "mode_set_at" in ws

        # Check detection metadata
        dm = output_data["detection_metadata"]
        assert "triggers" in dm
        assert "detection_time_ms" in dm
        assert "detector_version" in dm
