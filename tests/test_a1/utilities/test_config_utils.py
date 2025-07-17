"""Tests for configuration management utilities."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from a1.utilities.config import (
    AppConfig,
    BaseConfig,
    ConfigError,
    ConfigFormat,
    ConfigManager,
    DatabaseConfig,
    FeatureFlags,
    UserPreferences,
    create_config_schema,
    load_config,
    parse_bool,
    parse_list,
)


class TestParseFunctions:
    """Test parsing utility functions."""

    def test_parse_bool(self):
        """Test boolean parsing."""
        # True values
        assert parse_bool(True) is True
        assert parse_bool("true") is True
        assert parse_bool("True") is True
        assert parse_bool("TRUE") is True
        assert parse_bool("yes") is True
        assert parse_bool("1") is True
        assert parse_bool("on") is True
        assert parse_bool("enabled") is True

        # False values
        assert parse_bool(False) is False
        assert parse_bool("false") is False
        assert parse_bool("False") is False
        assert parse_bool("no") is False
        assert parse_bool("0") is False
        assert parse_bool("off") is False
        assert parse_bool("") is False

    def test_parse_list(self):
        """Test list parsing."""
        # Already a list
        assert parse_list([1, 2, 3]) == [1, 2, 3]

        # Comma-separated
        assert parse_list("a,b,c") == ["a", "b", "c"]
        assert parse_list("a, b, c") == ["a", "b", "c"]

        # Semicolon-separated
        assert parse_list("a;b;c") == ["a", "b", "c"]
        assert parse_list("a; b; c") == ["a", "b", "c"]

        # Empty cases
        assert parse_list("") == []
        assert parse_list([]) == []

        # Single value
        assert parse_list(42) == [42]


class TestBaseConfig:
    """Test BaseConfig functionality."""

    def test_from_dict(self):
        """Test creating config from dictionary."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = "default"
            count: int = 0
            enabled: bool = False

        config = TestConfig.from_dict(
            {
                "name": "test",
                "count": 42,
                "enabled": True,
                "unknown": "ignored",  # Should be ignored
            }
        )

        assert config.name == "test"
        assert config.count == 42
        assert config.enabled is True

    def test_from_env(self):
        """Test creating config from environment variables."""

        @dataclass
        class TestConfig(BaseConfig):
            api_key: str = ""
            port: int = 8080
            debug: bool = False
            tags: list = field(default_factory=list)

        # Set environment variables
        os.environ["API_KEY"] = "secret123"
        os.environ["PORT"] = "9000"
        os.environ["DEBUG"] = "true"
        os.environ["TAGS"] = "web,api,v2"

        try:
            config = TestConfig.from_env()

            assert config.api_key == "secret123"
            assert config.port == 9000
            assert config.debug is True
            assert config.tags == ["web", "api", "v2"]

        finally:
            # Cleanup
            for key in ["API_KEY", "PORT", "DEBUG", "TAGS"]:
                os.environ.pop(key, None)

    def test_from_env_with_prefix(self):
        """Test creating config from environment with prefix."""

        @dataclass
        class TestConfig(BaseConfig):
            host: str = "localhost"
            port: int = 5432

        os.environ["DB_HOST"] = "db.example.com"
        os.environ["DB_PORT"] = "3306"

        try:
            config = TestConfig.from_env("DB_")

            assert config.host == "db.example.com"
            assert config.port == 3306

        finally:
            os.environ.pop("DB_HOST", None)
            os.environ.pop("DB_PORT", None)

    def test_from_file_json(self):
        """Test loading config from JSON file."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = ""
            version: str = ""
            features: list = field(default_factory=list)

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text(
                json.dumps({"name": "test-app", "version": "1.0.0", "features": ["feature1", "feature2"]})
            )

            config = TestConfig.from_file(config_file)

            assert config.name == "test-app"
            assert config.version == "1.0.0"
            assert config.features == ["feature1", "feature2"]

    def test_from_file_yaml(self):
        """Test loading config from YAML file."""

        @dataclass
        class TestConfig(BaseConfig):
            database: str = ""
            timeout: int = 30

        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_file.write_text(yaml.dump({"database": "postgres", "timeout": 60}))

            config = TestConfig.from_file(config_file)

            assert config.database == "postgres"
            assert config.timeout == 60

    def test_from_file_not_found(self):
        """Test loading from non-existent file."""
        with pytest.raises(ConfigError) as exc_info:
            BaseConfig.from_file("nonexistent.json")

        assert "not found" in str(exc_info.value)

    def test_to_dict(self):
        """Test converting config to dictionary."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = "test"
            count: int = 42

        config = TestConfig()
        data = config.to_dict()

        assert data == {"name": "test", "count": 42}

    def test_to_file_json(self):
        """Test saving config to JSON file."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = "test"
            values: list = field(default_factory=lambda: [1, 2, 3])

        with TemporaryDirectory() as tmpdir:
            config = TestConfig()
            output_file = Path(tmpdir) / "output.json"

            config.to_file(output_file)

            # Verify file contents
            data = json.loads(output_file.read_text())
            assert data["name"] == "test"
            assert data["values"] == [1, 2, 3]

    def test_to_file_yaml(self):
        """Test saving config to YAML file."""

        @dataclass
        class TestConfig(BaseConfig):
            host: str = "localhost"
            port: int = 8080

        with TemporaryDirectory() as tmpdir:
            config = TestConfig()
            output_file = Path(tmpdir) / "output.yaml"

            config.to_file(output_file, ConfigFormat.YAML)

            # Verify file contents
            data = yaml.safe_load(output_file.read_text())
            assert data["host"] == "localhost"
            assert data["port"] == 8080

    def test_update(self):
        """Test updating configuration values."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = "original"
            count: int = 0

        config = TestConfig()
        config.update({"name": "updated", "count": 100, "unknown": "ignored"})

        assert config.name == "updated"
        assert config.count == 100

    def test_nested_config(self):
        """Test nested configuration handling."""

        @dataclass
        class NestedConfig(BaseConfig):
            value: str = "nested"

        @dataclass
        class ParentConfig(BaseConfig):
            name: str = "parent"
            nested: NestedConfig = field(default_factory=NestedConfig)

        # From dict with nested dict
        config = ParentConfig.from_dict({"name": "test", "nested": {"value": "custom"}})

        assert config.name == "test"
        assert config.nested.value == "custom"


class TestFeatureFlags:
    """Test FeatureFlags functionality."""

    def test_enable_disable(self):
        """Test enabling and disabling features."""
        flags = FeatureFlags()

        assert not flags.is_enabled("feature1")

        flags.enable("feature1")
        assert flags.is_enabled("feature1")

        flags.disable("feature1")
        assert not flags.is_enabled("feature1")

    def test_toggle(self):
        """Test toggling features."""
        flags = FeatureFlags()

        flags.toggle("feature1")
        assert flags.is_enabled("feature1")

        flags.toggle("feature1")
        assert not flags.is_enabled("feature1")

    def test_from_dict(self):
        """Test creating from dictionary."""
        flags = FeatureFlags.from_dict({"enabled_features": ["feature1", "feature2"]})

        assert flags.is_enabled("feature1")
        assert flags.is_enabled("feature2")
        assert not flags.is_enabled("feature3")


class TestUserPreferences:
    """Test UserPreferences functionality."""

    def test_get_set_remove(self):
        """Test getting, setting, and removing preferences."""
        prefs = UserPreferences()

        # Get with default
        assert prefs.get("theme") is None
        assert prefs.get("theme", "light") == "light"

        # Set and get
        prefs.set("theme", "dark")
        assert prefs.get("theme") == "dark"

        # Remove
        prefs.remove("theme")
        assert prefs.get("theme") is None

    def test_typed_getters(self):
        """Test typed preference getters."""
        prefs = UserPreferences()

        # Boolean
        prefs.set("notifications", "true")
        assert prefs.get_bool("notifications") is True
        assert prefs.get_bool("missing", True) is True

        # Integer
        prefs.set("max_items", "100")
        assert prefs.get_int("max_items") == 100
        assert prefs.get_int("missing", 50) == 50

        # Invalid integer
        prefs.set("invalid", "not_a_number")
        assert prefs.get_int("invalid", 0) == 0

        # List
        prefs.set("tags", "python,testing,config")
        assert prefs.get_list("tags") == ["python", "testing", "config"]
        assert prefs.get_list("missing", ["default"]) == ["default"]


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_register_and_get(self):
        """Test registering and retrieving configurations."""
        manager = ConfigManager()

        app_config = AppConfig(name="test-app")
        db_config = DatabaseConfig(host="db.test.com")

        manager.register("app", app_config)
        manager.register("database", db_config)

        assert manager.get("app") == app_config
        assert manager.get("database") == db_config
        assert manager.get("nonexistent") is None

    def test_validation(self):
        """Test configuration validation."""
        manager = ConfigManager()

        # Invalid configs
        app_config = AppConfig(max_workers=0, log_level="INVALID")
        db_config = DatabaseConfig(port=99999)

        manager.register("app", app_config)
        manager.register("database", db_config)

        errors = manager.validate_all()

        assert "app" in errors
        assert "database" in errors
        assert any("max_workers" in e for e in errors["app"])
        assert any("log_level" in e for e in errors["app"])
        assert any("port" in e for e in errors["database"])

    def test_custom_validators(self):
        """Test adding custom validators."""
        manager = ConfigManager()

        config = AppConfig(name="x")  # Short name
        manager.register("app", config)

        # Add custom validator
        def name_length_validator(cfg):
            errors = []
            if len(cfg.name) < 3:
                errors.append("name must be at least 3 characters")
            return errors

        manager.add_validator("app", name_length_validator)

        errors = manager.validate_all()
        assert "app" in errors
        assert any("at least 3 characters" in e for e in errors["app"])

    def test_save_and_load_directory(self):
        """Test saving and loading configurations from directory."""
        with TemporaryDirectory() as tmpdir:
            manager = ConfigManager()

            # Register configs
            features = FeatureFlags()
            features.enable("feature1")
            features.enable("feature2")

            prefs = UserPreferences()
            prefs.set("theme", "dark")

            manager.register("features", features)
            manager.register("preferences", prefs)

            # Save all
            manager.save_all(tmpdir)

            # Verify files created
            assert (Path(tmpdir) / "features.yaml").exists()
            assert (Path(tmpdir) / "preferences.yaml").exists()

            # Load into new manager
            new_manager = ConfigManager()
            new_manager.load_from_directory(tmpdir)

            loaded_features = new_manager.get("features")
            assert loaded_features is not None
            # A1FeatureFlags has default features
            assert loaded_features.is_enabled("advanced_prediction")
            assert loaded_features.is_enabled("state_management")


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_load_config(self):
        """Test loading config from multiple sources."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str = "default"
            port: int = 8080
            debug: bool = False

        with TemporaryDirectory() as tmpdir:
            # Create config file
            config_file = Path(tmpdir) / "config.json"
            config_file.write_text(json.dumps({"name": "from_file", "port": 9000}))

            # Set environment variable (should override file)
            os.environ["DEBUG"] = "true"

            try:
                config = load_config(TestConfig, config_file=config_file, defaults={"name": "from_defaults"})

                # File overrides defaults
                assert config.name == "from_file"
                assert config.port == 9000
                # Env overrides everything
                assert config.debug is True

            finally:
                os.environ.pop("DEBUG", None)

    def test_create_config_schema(self):
        """Test generating JSON schema."""

        @dataclass
        class TestConfig(BaseConfig):
            name: str
            count: int = 0
            enabled: bool = False
            tags: list = field(default_factory=list)

        schema = create_config_schema(TestConfig)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        # Check property types
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["count"]["type"] == "integer"
        assert schema["properties"]["enabled"]["type"] == "boolean"
        assert schema["properties"]["tags"]["type"] == "array"

        # Only name is required (no default)
        assert schema["required"] == ["name"]


class TestExampleConfigurations:
    """Test example configuration classes."""

    def test_app_config_validation(self):
        """Test AppConfig validation."""
        # Valid config
        config = AppConfig()
        assert config.validate() == []

        # Invalid config
        config = AppConfig(max_workers=0, timeout_seconds=-1, log_level="INVALID")

        errors = config.validate()
        assert len(errors) == 3
        assert any("max_workers" in e for e in errors)
        assert any("timeout_seconds" in e for e in errors)
        assert any("log_level" in e for e in errors)

    def test_database_config_validation(self):
        """Test DatabaseConfig validation."""
        # Valid config
        config = DatabaseConfig(host="localhost", username="user")
        assert config.validate() == []

        # Invalid config
        config = DatabaseConfig(host="", port=70000, database="", pool_size=0)

        errors = config.validate()
        assert len(errors) == 4

    def test_database_connection_string(self):
        """Test database connection string generation."""
        # Without auth
        config = DatabaseConfig(host="db.example.com")
        assert config.connection_string == "postgresql://db.example.com:5432/quaestor"

        # With username only
        config = DatabaseConfig(host="db.example.com", username="user")
        assert config.connection_string == "postgresql://user@db.example.com:5432/quaestor"

        # With full auth
        config = DatabaseConfig(host="db.example.com", username="user", password="pass")
        assert config.connection_string == "postgresql://user:pass@db.example.com:5432/quaestor"
