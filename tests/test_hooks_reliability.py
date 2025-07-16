"""Tests for hook reliability improvements."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quaestor.automation.base import BaseHook, TimeoutError, ValidationError, atomic_write, retry, timeout


class TestBaseHook:
    """Test the base hook class functionality."""

    def test_timeout_context_manager(self):
        """Test that timeout context manager works."""
        # Should complete without timeout
        with timeout(2):
            time.sleep(0.1)
            result = "success"
        assert result == "success"

        # Should raise TimeoutError
        with pytest.raises(TimeoutError), timeout(1):
            time.sleep(2)

    def test_retry_decorator(self):
        """Test retry decorator with backoff."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1, backoff=2.0)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_exhausted(self):
        """Test retry decorator when attempts are exhausted."""

        @retry(max_attempts=3, delay=0.1, backoff=1.0)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_base_hook_read_input(self):
        """Test reading JSON input from stdin."""
        test_input = {"toolName": "Write", "sessionId": "test123", "filePath": "/tmp/test.txt"}

        with patch("sys.stdin.read", return_value=json.dumps(test_input)):
            hook = BaseHook("test-hook")
            data = hook.read_input()

            assert data == test_input
            assert hook.input_data == test_input

    def test_base_hook_invalid_json(self):
        """Test handling of invalid JSON input."""
        with patch("sys.stdin.read", return_value="invalid json"):
            hook = BaseHook("test-hook")
            with pytest.raises(ValidationError):
                hook.read_input()

    def test_path_validation(self):
        """Test path validation and sanitization."""
        hook = BaseHook("test-hook")

        # Valid paths
        valid_path = hook.validate_path(str(Path.home() / "test.txt"))
        assert valid_path.is_absolute()

        # Path traversal attempt
        with pytest.raises(ValidationError):
            hook.validate_path("../../../etc/passwd")

        # Path outside allowed directories
        with pytest.raises(ValidationError):
            hook.validate_path("/etc/passwd")

    def test_json_output(self, capsys):
        """Test JSON output functionality."""
        hook = BaseHook("test-hook")

        with pytest.raises(SystemExit) as exc_info:
            hook.output_success("Test success", {"key": "value"})

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["message"] == "Test success"
        assert output["key"] == "value"
        assert "_metadata" in output
        assert output["_metadata"]["hook"] == "test-hook"

    def test_error_output(self, capsys):
        """Test error output functionality."""
        hook = BaseHook("test-hook")

        with pytest.raises(SystemExit) as exc_info:
            hook.output_error("Test error", blocking=True)

        assert exc_info.value.code == 2  # Blocking error
        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["error"] == "Test error"
        assert output["blocking"] is True

    def test_atomic_write(self):
        """Test atomic file writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "Test content"

            # Write file atomically
            atomic_write(file_path, content)
            assert file_path.read_text() == content

            # Temp file should not exist
            temp_path = file_path.with_suffix(".tmp")
            assert not temp_path.exists()


class TestHookUtilsImprovement:
    """Test improvements to hook utilities."""

    def test_subprocess_timeout(self):
        """Test subprocess calls have timeout protection."""

        # This would normally be in hook_utils.py
        def run_command_with_timeout(cmd, timeout_seconds=30):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
                return result.returncode == 0, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return False, "", f"Command timed out after {timeout_seconds} seconds"
            except Exception as e:
                return False, "", str(e)

        # Test normal command
        success, stdout, stderr = run_command_with_timeout(["echo", "test"], timeout_seconds=1)
        assert success is True
        assert stdout.strip() == "test"

        # Test timeout
        success, stdout, stderr = run_command_with_timeout(["sleep", "5"], timeout_seconds=1)
        assert success is False
        assert "timed out" in stderr


class TestAutomationHooksImprovement:
    """Test improvements to automation hooks."""

    @patch("subprocess.run")
    def test_quality_check_timeout(self, mock_run):
        """Test that quality checks have timeout protection."""
        from quaestor.automation.workflow import run_python_checks

        # Simulate timeout
        mock_run.side_effect = subprocess.TimeoutExpired(["ruff"], 60)

        result = run_python_checks(Path("/tmp"), fix=False)

        assert result["success"] is False
        assert "timed out" in result["message"]
        assert result["name"] == "Ruff (linting)"

    @patch("subprocess.run")
    def test_git_operation_timeout(self, mock_run):
        """Test that git operations have timeout protection."""
        from quaestor.automation import HookResult
        from quaestor.automation.workflow import create_atomic_commit

        # Simulate timeout on git add
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "add"], 30)

        result = create_atomic_commit("test commit")

        assert isinstance(result, HookResult)
        assert result.success is False
        assert "timed out" in result.message


class TestIntelligenceHooksImprovement:
    """Test improvements to intelligence hooks."""

    @patch("subprocess.run")
    def test_git_log_retry(self, mock_run):
        """Test that git log has retry logic."""
        from quaestor.automation.intelligence import ContextManager

        # Mock the root directory to exist
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "file1.py"
            test_file.touch()

            # First two calls fail, third succeeds
            mock_run.side_effect = [
                subprocess.TimeoutExpired(["git", "log"], 10),
                subprocess.TimeoutExpired(["git", "log"], 10),
                MagicMock(returncode=0, stdout="file1.py\nfile2.py\n"),
            ]

            with patch("quaestor.automation.intelligence.get_project_root", return_value=Path(tmpdir)):
                manager = ContextManager()
                files = manager._get_recently_modified_files()

            # Should have retried and eventually succeeded
            assert mock_run.call_count == 3
            assert len(files) == 1  # Only file1.py exists in our mock

    @patch("subprocess.run")
    def test_git_status_timeout_handling(self, mock_run):
        """Test that git status timeout doesn't crash suggestions."""
        from quaestor.automation.intelligence import suggest_next_action

        # Simulate timeout
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "status"], 10)

        result = suggest_next_action({})

        # Should still return result without git status info
        assert result.success is True
        assert "suggestions" in result.data


class TestWorkflowStateImprovement:
    """Test improvements to workflow state handling."""

    def test_atomic_state_save(self):
        """Test that workflow state is saved atomically."""
        # Import shared utils from assets
        from quaestor.assets.hooks.shared_utils import WorkflowState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = WorkflowState(tmpdir)

            # Modify state
            state.state["phase"] = "testing"
            state.state["files_examined"] = 5
            state._save_state()

            # Check file exists and temp file doesn't
            state_file = Path(tmpdir) / ".quaestor" / ".workflow_state"
            temp_file = state_file.with_suffix(".tmp")

            assert state_file.exists()
            assert not temp_file.exists()

            # Verify content
            with open(state_file) as f:
                saved_state = json.load(f)
            assert saved_state["phase"] == "testing"
            assert saved_state["files_examined"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
