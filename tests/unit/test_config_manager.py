"""Tests for the modern configuration management system."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from quaestor.core.config_manager import ConfigManager, ConfigurationError, get_config_manager
from quaestor.core.config_schemas import (
    ConfigurationLayer,
    ConfigValidationResult,
    LanguageConfig,
    LanguagesConfig,
    QuaestorMainConfig,
)
from quaestor.utils.yaml_utils import save_yaml


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.quaestor_dir = self.project_root / ".quaestor"
        self.quaestor_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test ConfigManager initialization."""
        config_manager = ConfigManager(self.project_root)

        assert config_manager.project_root == self.project_root
        assert config_manager.quaestor_dir == self.quaestor_dir
        assert len(config_manager._layers) == 5

        # Check layer priorities
        priorities = [layer.priority for layer in config_manager._layers]
        assert priorities == [1, 2, 3, 4, 5]

    def test_builtin_defaults(self):
        """Test that built-in defaults are properly structured."""
        config_manager = ConfigManager(self.project_root)
        defaults = config_manager._get_builtin_defaults()

        assert "main" in defaults
        assert "languages" in defaults
        assert "unknown" in defaults["languages"]

        # Verify unknown language has required fields
        unknown_lang = defaults["languages"]["unknown"]
        assert unknown_lang["primary_language"] == "unknown"
        assert unknown_lang["commit_prefix"] == "chore"

    def test_get_main_config_defaults(self):
        """Test getting main configuration with defaults."""
        config_manager = ConfigManager(self.project_root)
        main_config = config_manager.get_main_config()

        assert isinstance(main_config, QuaestorMainConfig)
        assert main_config.version == "1.0"
        assert main_config.hooks.enabled is True
        assert main_config.hooks.strict_mode is False

    def test_get_main_config_with_project_override(self):
        """Test main configuration with project-level overrides."""
        # Create project config file
        config_data = {"main": {"hooks": {"enabled": False, "strict_mode": True}}}
        save_yaml(self.quaestor_dir / "config.yaml", config_data)

        config_manager = ConfigManager(self.project_root)
        main_config = config_manager.get_main_config()

        assert main_config.hooks.enabled is False
        assert main_config.hooks.strict_mode is True
        # Version should remain default
        assert main_config.version == "1.0"

    def test_get_main_config_with_runtime_override(self):
        """Test main configuration with runtime overrides."""
        config_manager = ConfigManager(self.project_root)

        runtime_overrides = {"hooks": {"strict_mode": True}}

        main_config = config_manager.get_main_config(runtime_overrides)

        assert main_config.hooks.strict_mode is True
        # Other defaults should remain
        assert main_config.hooks.enabled is True

    def test_get_languages_config_defaults(self):
        """Test getting languages configuration with defaults."""
        config_manager = ConfigManager(self.project_root)

        # The core languages.yaml file should be loaded automatically
        config_manager = ConfigManager(self.project_root)
        languages_config = config_manager.get_languages_config()

        assert isinstance(languages_config, LanguagesConfig)
        assert "python" in languages_config.languages

        python_config = languages_config.get_language_config("python")
        assert python_config.primary_language == "python"
        assert python_config.lint_command == "ruff check ."
        assert python_config.coverage_threshold == 80
        assert python_config.type_checking is True

    def test_get_language_config_with_overrides(self):
        """Test language configuration with project overrides."""
        # Create base language config
        core_languages_data = {
            "languages": {
                "python": {"primary_language": "python", "lint_command": "ruff check .", "coverage_threshold": 80}
            }
        }

        # Create project override
        project_override_data = {"languages": {"python": {"lint_command": "mypy --strict", "coverage_threshold": 95}}}
        save_yaml(self.quaestor_dir / "languages.yaml", project_override_data)

        config_manager = ConfigManager(self.project_root)

        with patch.object(Path, "exists", return_value=True), patch("quaestor.utils.yaml_utils.load_yaml") as mock_load:
            # Return different data based on file path
            def load_yaml_side_effect(path, default=None):
                if "languages.yaml" in str(path) and ".quaestor" in str(path):
                    return project_override_data
                elif "languages.yaml" in str(path):
                    return core_languages_data
                return default or {}

            mock_load.side_effect = load_yaml_side_effect

            python_config = config_manager.get_language_config("python")

        assert python_config is not None
        assert python_config.primary_language == "python"  # From base
        assert python_config.lint_command == "mypy --strict"  # From override
        assert python_config.coverage_threshold == 95  # From override

    def test_get_language_config_unknown_fallback(self):
        """Test fallback to unknown language when language not found."""
        config_manager = ConfigManager(self.project_root)

        with patch.object(config_manager, "project_type", "nonexistent"):
            lang_config = config_manager.get_language_config()

        # Should fall back to unknown language from defaults
        assert lang_config is not None
        assert lang_config.primary_language == "unknown"
        assert lang_config.commit_prefix == "chore"

    def test_deep_merge_configs(self):
        """Test deep merging of configuration dictionaries."""
        config_manager = ConfigManager(self.project_root)

        base = {
            "level1": {
                "level2": {"keep_me": "base_value", "override_me": "base_value"},
                "keep_this_dict": {"key": "value"},
            },
            "array_base": [1, 2, 3],
            "keep_primitive": "base",
        }

        override = {
            "level1": {
                "level2": {"override_me": "override_value", "new_key": "new_value"},
                "new_dict": {"new": "dict"},
            },
            "array_base": [4, 5],  # Should replace, not merge
            "new_primitive": "override",
        }

        result = config_manager._deep_merge_configs(base, override)

        # Check deep merge
        assert result["level1"]["level2"]["keep_me"] == "base_value"
        assert result["level1"]["level2"]["override_me"] == "override_value"
        assert result["level1"]["level2"]["new_key"] == "new_value"

        # Check that untouched nested dicts remain
        assert result["level1"]["keep_this_dict"]["key"] == "value"

        # Check new nested dict
        assert result["level1"]["new_dict"]["new"] == "dict"

        # Check array replacement
        assert result["array_base"] == [4, 5]

        # Check primitives
        assert result["keep_primitive"] == "base"
        assert result["new_primitive"] == "override"

    def test_validation_success(self):
        """Test successful configuration validation."""
        config_manager = ConfigManager(self.project_root)
        result = config_manager.validate_configuration()

        assert isinstance(result, ConfigValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validation_with_warnings(self):
        """Test validation with warnings for unusual values."""
        # Create config with unusual values
        config_data = {
            "languages": {
                "python": {
                    "primary_language": "python",
                    "coverage_threshold": 98,  # High threshold should be allowed but might trigger warning
                }
            }
        }
        save_yaml(self.quaestor_dir / "config.yaml", config_data)

        config_manager = ConfigManager(self.project_root)
        result = config_manager.validate_configuration()

        assert result.valid is True  # Still valid, just potential warnings

    def test_invalid_configuration_error(self):
        """Test handling of invalid configuration."""
        # Create invalid config
        config_data = {
            "main": {
                "version": ["invalid", "version"]  # Should cause validation error - version should be string
            }
        }
        save_yaml(self.quaestor_dir / "config.yaml", config_data)

        config_manager = ConfigManager(self.project_root)

        with pytest.raises(ConfigurationError):
            config_manager.get_main_config()

    def test_get_effective_config(self):
        """Test getting complete effective configuration."""
        config_manager = ConfigManager(self.project_root)

        with patch.object(config_manager, "get_language_config") as mock_lang:
            mock_lang.return_value = LanguageConfig(primary_language="python", lint_command="ruff")

            effective_config = config_manager.get_effective_config()

        assert "main" in effective_config
        assert "languages" in effective_config
        # Note: commands are not part of the current simplified config structure
        assert "current_language" in effective_config
        assert "project_type" in effective_config
        assert "layers" in effective_config

        assert len(effective_config["layers"]) == 5

    def test_save_project_config(self):
        """Test saving project configuration."""
        config_manager = ConfigManager(self.project_root)

        updates = {"hooks": {"enabled": False, "strict_mode": True}}

        success = config_manager.save_project_config(updates, "main")
        assert success is True

        # Verify the file was created and contains expected data
        config_path = self.quaestor_dir / "config.yaml"
        assert config_path.exists()

        from quaestor.utils.yaml_utils import load_yaml

        saved_data = load_yaml(config_path)
        assert saved_data["main"]["hooks"]["enabled"] is False
        assert saved_data["main"]["hooks"]["strict_mode"] is True

    def test_initialize_default_configs(self):
        """Test initialization of default configuration files."""
        config_manager = ConfigManager(self.project_root)

        success = config_manager.initialize_default_configs()
        assert success is True

        # Check that default files were created
        assert (self.quaestor_dir / "config.yaml").exists()

        # Verify content
        from quaestor.utils.yaml_utils import load_yaml

        main_config = load_yaml(self.quaestor_dir / "config.yaml")
        assert main_config["main"]["version"] == "1.0"
        assert main_config["main"]["hooks"]["enabled"] is True


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager with real file system."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.quaestor_dir = self.project_root / ".quaestor"
        self.quaestor_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_layered_configuration_precedence(self):
        """Test that configuration layers have correct precedence."""
        # Create base config (priority 4 equivalent - we'll mock it)
        base_config = {
            "languages": {
                "python": {
                    "primary_language": "python",
                    "lint_command": "base_linter",
                    "coverage_threshold": 70,
                    "custom_field": "base_value",
                }
            }
        }

        # Create project config (priority 3)
        project_config = {"main": {"hooks": {"strict_mode": True}}}
        save_yaml(self.quaestor_dir / "config.yaml", project_config)

        # Create project language overrides (priority 2)
        language_overrides = {"languages": {"python": {"lint_command": "project_linter", "coverage_threshold": 85}}}
        save_yaml(self.quaestor_dir / "languages.yaml", language_overrides)

        # Runtime overrides (priority 1)
        runtime_overrides = {"current_language": {"lint_command": "runtime_linter"}}

        config_manager = ConfigManager(self.project_root)

        # Mock the base languages config
        with patch.object(Path, "exists") as mock_exists:

            def exists_side_effect(self_path):
                return str(self_path).endswith("languages.yaml")

            mock_exists.side_effect = exists_side_effect

            with patch("quaestor.utils.yaml_utils.load_yaml") as mock_load:

                def load_yaml_side_effect(path, default=None):
                    if "languages.yaml" in str(path) and "core" in str(path):
                        return base_config
                    elif "languages.yaml" in str(path) and ".quaestor" in str(path):
                        return language_overrides
                    elif "config.yaml" in str(path):
                        return project_config
                    return default or {}

                mock_load.side_effect = load_yaml_side_effect

                # Test main config (project overrides should apply)
                main_config = config_manager.get_main_config()
                assert main_config.hooks.strict_mode is True  # From project config
                assert main_config.hooks.enabled is True  # From defaults

                # Test language config (should merge base + project overrides)
                python_config = config_manager.get_language_config("python")
                assert python_config.primary_language == "python"  # From base
                assert python_config.lint_command == "project_linter"  # From project override
                assert python_config.coverage_threshold == 85  # From project override

                # Test runtime overrides
                python_config_runtime = config_manager.get_language_config(
                    "python", runtime_overrides.get("current_language")
                )
                assert python_config_runtime.lint_command == "runtime_linter"  # From runtime

    def test_end_to_end_configuration_flow(self):
        """Test complete configuration flow from initialization to usage."""
        # Initialize config manager and default configs
        config_manager = ConfigManager(self.project_root)
        assert config_manager.initialize_default_configs()

        # Validate initial state
        validation_result = config_manager.validate_configuration()
        assert validation_result.valid

        # Update project configuration
        updates = {"hooks": {"strict_mode": True}}
        assert config_manager.save_project_config(updates, "main")

        # Create language override
        lang_overrides = {"python": {"coverage_threshold": 90}}
        assert config_manager.save_project_config(lang_overrides, "languages")

        # Get effective configuration
        effective_config = config_manager.get_effective_config()

        assert effective_config["main"]["hooks"]["strict_mode"] is True

        # Note: Backward compatibility with QuaestorConfig has been removed
        # All functionality is now available directly through ConfigManager


def test_get_config_manager_function():
    """Test the get_config_manager convenience function."""
    with TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        quaestor_dir = project_root / ".quaestor"
        quaestor_dir.mkdir(parents=True)

        # Test with explicit path
        config_manager = get_config_manager(project_root)
        assert isinstance(config_manager, ConfigManager)
        assert config_manager.project_root == project_root

        # Test with language override
        config_manager_override = get_config_manager(project_root, "python")
        assert config_manager_override.language_override == "python"


def test_configuration_layer_sorting():
    """Test that configuration layers sort correctly by priority."""
    layer1 = ConfigurationLayer(priority=3, source="test1", description="test")
    layer2 = ConfigurationLayer(priority=1, source="test2", description="test")
    layer3 = ConfigurationLayer(priority=2, source="test3", description="test")

    layers = [layer1, layer2, layer3]
    sorted_layers = sorted(layers)

    # Should be sorted by priority (1, 2, 3)
    assert sorted_layers[0].priority == 1
    assert sorted_layers[1].priority == 2
    assert sorted_layers[2].priority == 3
