"""Tests for configuration schemas and validation."""

import pytest
from pydantic import ValidationError

from quaestor.core.config_schemas import (
    ConfigurationLayer,
    ConfigValidationResult,
    HooksConfig,
    LanguageConfig,
    LanguagesConfig,
    QuaestorMainConfig,
)


class TestQuaestorMainConfig:
    """Test suite for QuaestorMainConfig schema."""

    def test_default_values(self):
        """Test default configuration values."""
        config = QuaestorMainConfig()

        assert config.version == "1.0"
        assert config.hooks.enabled is True
        assert config.hooks.strict_mode is False

    def test_valid_configuration(self):
        """Test valid configuration creation."""
        config_data = {"version": "2.0", "hooks": {"enabled": False, "strict_mode": True}}

        config = QuaestorMainConfig(**config_data)

        assert config.version == "2.0"
        assert config.hooks.enabled is False
        assert config.hooks.strict_mode is True

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            QuaestorMainConfig(extra_field="not_allowed")

        error = exc_info.value
        assert "extra_field" in str(error)


class TestLanguageConfig:
    """Test suite for LanguageConfig schema."""

    def test_minimal_valid_config(self):
        """Test minimal valid language configuration."""
        config = LanguageConfig(primary_language="python")

        assert config.primary_language == "python"
        assert config.lint_command is None
        assert config.coverage_threshold is None
        assert config.type_checking is False
        assert config.commit_prefix == "feat"

    def test_complete_valid_config(self):
        """Test complete valid language configuration."""
        config_data = {
            "primary_language": "python",
            "lint_command": "ruff check .",
            "format_command": "ruff format .",
            "test_command": "pytest",
            "coverage_command": "pytest --cov",
            "type_check_command": "mypy .",
            "security_scan_command": "bandit -r src/",
            "profile_command": "python -m cProfile",
            "coverage_threshold": 85,
            "type_checking": True,
            "performance_target_ms": 200,
            "commit_prefix": "fix",
            "quick_check_command": "ruff check . && pytest -x",
            "full_check_command": "ruff check . && mypy . && pytest",
            "precommit_install_command": "pre-commit install",
            "doc_style_example": "def example(): pass",
        }

        config = LanguageConfig(**config_data)

        assert config.primary_language == "python"
        assert config.lint_command == "ruff check ."
        assert config.coverage_threshold == 85
        assert config.type_checking is True
        assert config.performance_target_ms == 200
        assert config.commit_prefix == "fix"

    def test_coverage_threshold_validation(self):
        """Test coverage threshold validation."""
        # Valid values
        config = LanguageConfig(primary_language="python", coverage_threshold=85)
        assert config.coverage_threshold == 85

        config = LanguageConfig(primary_language="python", coverage_threshold=100)
        assert config.coverage_threshold == 100

        # Invalid values
        with pytest.raises(ValidationError):
            LanguageConfig(primary_language="python", coverage_threshold=-1)

        with pytest.raises(ValidationError):
            LanguageConfig(primary_language="python", coverage_threshold=101)

    def test_performance_target_validation(self):
        """Test performance target validation."""
        # Valid value
        config = LanguageConfig(primary_language="python", performance_target_ms=100)
        assert config.performance_target_ms == 100

        # Invalid value (must be positive)
        with pytest.raises(ValidationError):
            LanguageConfig(primary_language="python", performance_target_ms=0)

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed in language config."""
        config = LanguageConfig(
            primary_language="python", custom_field="custom_value", another_custom_field={"nested": "value"}
        )

        assert config.primary_language == "python"
        # Extra fields should be accessible via model_dump
        config_dict = config.model_dump()
        assert config_dict["custom_field"] == "custom_value"
        assert config_dict["another_custom_field"]["nested"] == "value"

    def test_high_coverage_threshold_warning_validation(self):
        """Test that high coverage threshold is validated but allowed."""
        # This should not raise an error, just a potential warning in validation
        config = LanguageConfig(primary_language="python", coverage_threshold=98)
        assert config.coverage_threshold == 98


class TestLanguagesConfig:
    """Test suite for LanguagesConfig schema."""

    def test_empty_languages_config(self):
        """Test empty languages configuration."""
        config = LanguagesConfig()

        assert len(config.languages) == 0
        assert config.get_language_config("python") is None
        assert config.has_language("python") is False

    def test_languages_config_with_languages(self):
        """Test languages configuration with language entries."""
        languages = {
            "python": LanguageConfig(primary_language="python", lint_command="ruff"),
            "javascript": LanguageConfig(primary_language="javascript", lint_command="eslint"),
        }

        config = LanguagesConfig(languages=languages)

        assert len(config.languages) == 2
        assert config.has_language("python")
        assert config.has_language("javascript")
        assert not config.has_language("rust")

        python_config = config.get_language_config("python")
        assert python_config is not None
        assert python_config.primary_language == "python"
        assert python_config.lint_command == "ruff"


class TestConfigValidationResult:
    """Test suite for ConfigValidationResult."""

    def test_valid_result(self):
        """Test valid validation result."""
        result = ConfigValidationResult(valid=True)

        assert result.valid is True
        assert len(result.warnings) == 0
        assert len(result.errors) == 0
        assert result.has_issues() is False

    def test_result_with_warnings(self):
        """Test validation result with warnings."""
        result = ConfigValidationResult(valid=True)
        result.add_warning("This is a warning")
        result.add_warning("Another warning")

        assert result.valid is True
        assert len(result.warnings) == 2
        assert len(result.errors) == 0
        assert result.has_issues() is True
        assert "This is a warning" in result.warnings

    def test_result_with_errors(self):
        """Test validation result with errors."""
        result = ConfigValidationResult(valid=True)
        result.add_error("This is an error")

        assert result.valid is False  # Should be automatically set to False
        assert len(result.warnings) == 0
        assert len(result.errors) == 1
        assert result.has_issues() is True
        assert "This is an error" in result.errors

    def test_result_with_mixed_issues(self):
        """Test validation result with both warnings and errors."""
        result = ConfigValidationResult(valid=True)
        result.add_warning("Warning message")
        result.add_error("Error message")

        assert result.valid is False
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert result.has_issues() is True


class TestConfigurationLayer:
    """Test suite for ConfigurationLayer."""

    def test_configuration_layer_creation(self):
        """Test configuration layer creation."""
        layer = ConfigurationLayer(
            priority=1, source="test.yaml", description="Test layer", config_data={"key": "value"}, exists=True
        )

        assert layer.priority == 1
        assert layer.source == "test.yaml"
        assert layer.description == "Test layer"
        assert layer.config_data["key"] == "value"
        assert layer.exists is True
        assert layer.file_path is None

    def test_configuration_layer_sorting(self):
        """Test configuration layer sorting by priority."""
        layer1 = ConfigurationLayer(priority=3, source="layer1", description="Third")
        layer2 = ConfigurationLayer(priority=1, source="layer2", description="First")
        layer3 = ConfigurationLayer(priority=2, source="layer3", description="Second")

        layers = [layer1, layer2, layer3]
        sorted_layers = sorted(layers)

        assert sorted_layers[0].priority == 1
        assert sorted_layers[1].priority == 2
        assert sorted_layers[2].priority == 3
        assert sorted_layers[0].source == "layer2"
        assert sorted_layers[1].source == "layer3"
        assert sorted_layers[2].source == "layer1"


class TestHooksConfig:
    """Test suite for HooksConfig schema."""

    def test_default_hooks_config(self):
        """Test default hooks configuration."""
        config = HooksConfig()

        assert config.enabled is True
        assert config.strict_mode is False

    def test_custom_hooks_config(self):
        """Test custom hooks configuration."""
        config_data = {"enabled": False, "strict_mode": True}

        config = HooksConfig(**config_data)

        assert config.enabled is False
        assert config.strict_mode is True
