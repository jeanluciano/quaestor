"""Tests for automation functionality."""

import json
from unittest.mock import patch

from quaestor.automation import HookResult, detect_project_type, get_project_root, load_quaestor_config, run_hook


class TestHookResult:
    """Test HookResult class."""

    def test_init_defaults(self):
        """Test default initialization."""
        result = HookResult(success=True)
        assert result.success is True
        assert result.message == ""
        assert result.data == {}

    def test_init_with_values(self):
        """Test initialization with values."""
        result = HookResult(success=False, message="Test failed", data={"error": "details"})
        assert result.success is False
        assert result.message == "Test failed"
        assert result.data == {"error": "details"}

    def test_to_exit_code(self):
        """Test exit code conversion."""
        success_result = HookResult(success=True)
        assert success_result.to_exit_code() == 0

        failure_result = HookResult(success=False)
        assert failure_result.to_exit_code() == 1

    def test_to_json(self):
        """Test JSON conversion."""
        result = HookResult(success=True, message="Success", data={"key": "value"})
        json_str = result.to_json()
        data = json.loads(json_str)

        assert data["success"] is True
        assert data["message"] == "Success"
        assert data["data"] == {"key": "value"}


class TestProjectFunctions:
    """Test project-related functions."""

    def test_get_project_root_found(self, tmp_path):
        """Test finding project root with .quaestor directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        quaestor_dir = project_dir / ".quaestor"
        quaestor_dir.mkdir()

        # Create a subdirectory
        sub_dir = project_dir / "src"
        sub_dir.mkdir()

        with patch("pathlib.Path.cwd", return_value=sub_dir):
            root = get_project_root()
            assert root == project_dir

    def test_get_project_root_not_found(self, tmp_path):
        """Test when .quaestor directory is not found."""
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            root = get_project_root()
            assert root == tmp_path

    def test_detect_project_type_python(self, tmp_path):
        """Test detecting Python project."""
        (tmp_path / "pyproject.toml").touch()
        assert detect_project_type(tmp_path) == "python"

        # Also test with requirements.txt
        (tmp_path / "pyproject.toml").unlink()
        (tmp_path / "requirements.txt").touch()
        assert detect_project_type(tmp_path) == "python"

    def test_detect_project_type_javascript(self, tmp_path):
        """Test detecting JavaScript project."""
        (tmp_path / "package.json").touch()
        assert detect_project_type(tmp_path) == "javascript"

    def test_detect_project_type_rust(self, tmp_path):
        """Test detecting Rust project."""
        (tmp_path / "Cargo.toml").touch()
        assert detect_project_type(tmp_path) == "rust"

    def test_detect_project_type_go(self, tmp_path):
        """Test detecting Go project."""
        (tmp_path / "go.mod").touch()
        assert detect_project_type(tmp_path) == "go"

    def test_detect_project_type_unknown(self, tmp_path):
        """Test unknown project type."""
        assert detect_project_type(tmp_path) == "unknown"

    def test_load_quaestor_config(self, tmp_path):
        """Test loading Quaestor configuration."""
        # Create project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        quaestor_dir = project_dir / ".quaestor"
        quaestor_dir.mkdir()

        # Create CRITICAL_RULES.md
        (quaestor_dir / "CRITICAL_RULES.md").write_text("# Rules")

        # Create pyproject.toml
        (project_dir / "pyproject.toml").touch()

        with patch("quaestor.automation.get_project_root", return_value=project_dir):
            config = load_quaestor_config()

            assert config["project_type"] == "python"
            assert config["has_critical_rules"] is True
            assert config["has_memory"] is False


class TestRunHook:
    """Test the run_hook function."""

    def test_run_hook_enforcement(self):
        """Test running enforcement hook."""
        with patch("quaestor.automation.enforcement.run_enforcement_hook") as mock_run:
            mock_run.return_value = HookResult(success=True, message="Enforcement passed")

            result = run_hook("enforce_test", {"data": "test"})

            assert result.success is True
            assert result.message == "Enforcement passed"
            mock_run.assert_called_once_with("enforce_test", {"data": "test"})

    def test_run_hook_automation(self):
        """Test running automation hook."""
        with patch("quaestor.automation.workflow.run_automation_hook") as mock_run:
            mock_run.return_value = HookResult(success=True, message="Automation completed")

            result = run_hook("auto_test", {"data": "test"})

            assert result.success is True
            assert result.message == "Automation completed"
            mock_run.assert_called_once_with("auto_test", {"data": "test"})

    def test_run_hook_intelligence(self):
        """Test running intelligence hook."""
        with patch("quaestor.automation.intelligence.run_intelligence_hook") as mock_run:
            mock_run.return_value = HookResult(success=True, message="Intelligence processed")

            result = run_hook("intel_test", {"data": "test"})

            assert result.success is True
            assert result.message == "Intelligence processed"
            mock_run.assert_called_once_with("intel_test", {"data": "test"})

    def test_run_hook_unknown(self):
        """Test running unknown hook."""
        result = run_hook("unknown_hook", {})

        assert result.success is False
        assert "Unknown hook" in result.message
