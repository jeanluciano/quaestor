"""
Comprehensive tests for V2.1 Configuration System

Tests all aspects of the centralized configuration management:
- Configuration loading and saving
- Environment variable overrides
- Validation
- CLI integration
- Component integration
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from a1.utilities.config import (
    A1CLIConfig,
    A1ExtensionsConfig,
    A1FeatureFlags,
    A1SystemConfig,
    ConfigError,
    ConfigManager,
    get_config_manager,
    get_config_value,
    init_config,
    save_config,
    set_config_value,
)


class TestConfigurationClasses:
    """Test individual configuration classes."""

    def test_system_config_defaults(self):
        """Test system configuration defaults."""
        config = A1SystemConfig()
        assert config.version == "A1.0"
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.data_dir == ".quaestor"
        assert config.max_workers == 4

    def test_system_config_validation(self):
        """Test system configuration validation."""
        config = A1SystemConfig(max_workers=0, log_level="INVALID")
        errors = config.validate()
        assert len(errors) == 2
        assert "max_workers must be at least 1" in errors
        assert "log_level must be one of" in errors[1]

    def test_extensions_config_defaults(self):
        """Test extensions configuration defaults."""
        config = A1ExtensionsConfig()
        assert config.state.enabled is True
        assert config.state.max_snapshots == 50
        assert config.hooks.enabled is True
        assert config.prediction.confidence_threshold == 0.7

    def test_cli_config_validation(self):
        """Test CLI configuration validation."""
        config = A1CLIConfig(output_format="invalid", theme="invalid")
        errors = config.validate()
        assert len(errors) == 2
        assert "output_format must be one of" in errors[0]
        assert "theme must be one of" in errors[1]

    def test_feature_flags_functionality(self):
        """Test feature flags operations."""
        features = A1FeatureFlags()

        # Test default features are enabled
        assert features.is_enabled("advanced_prediction")
        assert features.is_enabled("state_management")

        # Test enable/disable
        features.disable("advanced_prediction")
        assert not features.is_enabled("advanced_prediction")

        features.enable("experimental_feature")
        assert features.is_enabled("experimental_feature")

        # Test toggle
        features.toggle("experimental_feature")
        assert not features.is_enabled("experimental_feature")


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_config_manager_initialization(self):
        """Test ConfigManager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)

            # Should create default configurations
            config_manager.ensure_loaded()

            assert config_manager.get("system") is not None
            assert config_manager.get("extensions") is not None
            assert config_manager.get("cli") is not None

    def test_config_value_access(self):
        """Test configuration value access with dot notation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            config_manager.ensure_loaded()

            # Test getting values
            log_level = config_manager.get_value("system.log_level")
            assert log_level == "INFO"

            max_snapshots = config_manager.get_value("extensions.state.max_snapshots")
            assert max_snapshots == 50

            # Test setting values
            config_manager.set_value("system.debug", True)
            debug_value = config_manager.get_value("system.debug")
            assert debug_value is True

    def test_config_validation(self):
        """Test configuration validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            config_manager.ensure_loaded()

            # Should pass validation initially
            errors = config_manager.validate_all()
            assert len(errors) == 0

            # Introduce validation error
            config_manager.set_value("system.max_workers", -1)
            errors = config_manager.validate_all()
            assert len(errors) > 0
            assert "system" in errors

    def test_config_file_loading(self):
        """Test loading configuration from YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"

            # Create test configuration
            test_config = {
                "system": {"debug": True, "log_level": "DEBUG"},
                "extensions": {"state": {"max_snapshots": 100}},
            }

            with open(config_file, "w") as f:
                yaml.safe_dump(test_config, f)

            # Load configuration
            config_manager = ConfigManager(temp_dir)
            config_manager.load_from_file(config_file)
            # Mark as loaded to prevent ensure_loaded from overwriting
            config_manager._loaded = True

            assert config_manager.get_value("system.debug") is True
            assert config_manager.get_value("system.log_level") == "DEBUG"
            assert config_manager.get_value("extensions.state.max_snapshots") == 100

    def test_config_file_saving(self):
        """Test saving configuration to YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            config_manager.ensure_loaded()

            # Modify configuration
            config_manager.set_value("system.debug", True)
            config_manager.set_value("extensions.state.max_snapshots", 75)

            # Save configuration
            config_manager.save_main_config()

            # Verify file was created and contains correct data
            config_file = Path(temp_dir) / "a1_config.yaml"
            assert config_file.exists()

            with open(config_file) as f:
                saved_config = yaml.safe_load(f)

            assert saved_config["system"]["debug"] is True
            assert saved_config["extensions"]["state"]["max_snapshots"] == 75


class TestEnvironmentVariables:
    """Test environment variable configuration overrides."""

    def test_system_env_overrides(self):
        """Test system configuration environment overrides."""
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {
                "QUAESTOR_A1_SYSTEM_DEBUG": "true",
                "QUAESTOR_A1_SYSTEM_LOG_LEVEL": "DEBUG",
                "QUAESTOR_A1_SYSTEM_MAX_WORKERS": "8",
            },
        ):
            config_manager = ConfigManager(temp_dir)
            config_manager.ensure_loaded()

            # Environment variables should override defaults
            assert config_manager.get_value("system.debug") is True
            assert config_manager.get_value("system.log_level") == "DEBUG"
            assert config_manager.get_value("system.max_workers") == 8



class TestGlobalConfigFunctions:
    """Test global configuration functions."""

    def test_global_config_functions(self):
        """Test global configuration accessor functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize with custom directory
            init_config(temp_dir)

            # Test global functions
            log_level = get_config_value("system.log_level")
            assert log_level == "INFO"

            # Test setting values
            set_config_value("system.debug", True)
            debug_value = get_config_value("system.debug")
            assert debug_value is True

            # Test saving
            save_config()

            # Verify file was created
            config_file = Path(temp_dir) / "a1_config.yaml"
            assert config_file.exists()

    def test_config_manager_singleton(self):
        """Test global config manager singleton behavior."""
        # Clear global instance
        import a1.utilities.config as config_module

        config_module._config_manager = None

        # Get manager instances
        manager1 = get_config_manager()
        manager2 = get_config_manager()

        # Should be the same instance
        assert manager1 is manager2


class TestConfigurationEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_config_path(self):
        """Test handling of invalid configuration paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)
            config_manager.ensure_loaded()

            # Test getting non-existent path
            value = config_manager.get_value("nonexistent.path", "default")
            assert value == "default"

            # Test setting invalid path
            with pytest.raises(ConfigError):
                config_manager.set_value("invalid", "value")

    def test_corrupted_config_file(self):
        """Test handling of corrupted configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "a1_config.yaml"

            # Create corrupted YAML file
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: [\n")

            config_manager = ConfigManager(temp_dir)

            # Should handle corrupted file gracefully
            with pytest.raises(ConfigError):
                config_manager.load_from_file(config_file)

    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = ConfigManager(temp_dir)

            # Should create default configuration when file is missing
            config_manager.ensure_loaded()

            assert config_manager.get("system") is not None
            assert config_manager.get_value("system.log_level") == "INFO"


class TestConfigurationIntegration:
    """Test configuration integration with V2.1 components."""

    def test_component_configuration_integration(self):
        """Test that components can access configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            init_config(temp_dir)

            # Set component-specific configuration
            set_config_value("extensions.state.max_snapshots", 200)
            set_config_value("extensions.prediction.confidence_threshold", 0.9)

            # Verify components can access their configuration
            assert get_config_value("extensions.state.max_snapshots") == 200
            assert get_config_value("extensions.prediction.confidence_threshold") == 0.9

    def test_feature_flags_integration(self):
        """Test feature flags integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_manager = init_config(temp_dir)

            # Get feature flags
            features = config_manager.get("features")
            assert features is not None

            # Test feature checking
            assert features.is_enabled("state_management")
            assert features.is_enabled("advanced_prediction")

            # Disable a feature
            features.disable("advanced_prediction")
            assert not features.is_enabled("advanced_prediction")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
