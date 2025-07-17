"""Usage examples for configuration management utilities.

These examples demonstrate how to use the configuration system
for application settings, feature flags, and user preferences.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from .config import (
    AppConfig,
    BaseConfig,
    ConfigManager,
    DatabaseConfig,
    FeatureFlags,
    UserPreferences,
    create_config_schema,
    load_config,
)


def example_basic_configuration():
    """Example: Basic configuration with dataclasses."""

    @dataclass
    class ServerConfig(BaseConfig):
        host: str = "localhost"
        port: int = 8000
        debug: bool = False
        workers: int = 4
        allowed_hosts: list = field(default_factory=lambda: ["localhost", "127.0.0.1"])

    print("Basic configuration example:")

    # Default configuration
    config = ServerConfig()
    print(f"Default config: {config}")

    # From dictionary
    config = ServerConfig.from_dict(
        {"host": "0.0.0.0", "port": 3000, "debug": True, "allowed_hosts": ["example.com", "api.example.com"]}
    )
    print(f"From dict: {config}")

    # Convert to dict
    config_dict = config.to_dict()
    print(f"As dictionary: {config_dict}")

    return config


def example_environment_variables():
    """Example: Configuration from environment variables."""

    @dataclass
    class ApiConfig(BaseConfig):
        api_key: str = ""
        base_url: str = "https://api.example.com"
        timeout: int = 30
        retry_count: int = 3
        debug_mode: bool = False
        endpoints: list = field(default_factory=list)

    print("\nEnvironment variables example:")

    # Set environment variables
    env_vars = {
        "API_KEY": "secret_api_key_123",
        "BASE_URL": "https://staging.api.example.com",
        "TIMEOUT": "60",
        "DEBUG_MODE": "true",
        "ENDPOINTS": "users,posts,comments",
    }

    # Save original values
    original_env = {}
    for key, value in env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Load from environment
        config = ApiConfig.from_env()

        print(f"API Key: {config.api_key}")
        print(f"Base URL: {config.base_url}")
        print(f"Timeout: {config.timeout}s")
        print(f"Debug: {config.debug_mode}")
        print(f"Endpoints: {config.endpoints}")

        # With prefix
        os.environ["MYAPP_API_KEY"] = "prefixed_key"
        os.environ["MYAPP_TIMEOUT"] = "120"

        prefixed_config = ApiConfig.from_env("MYAPP_")
        print(f"Prefixed API Key: {prefixed_config.api_key}")
        print(f"Prefixed Timeout: {prefixed_config.timeout}s")

    finally:
        # Restore environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

        os.environ.pop("MYAPP_API_KEY", None)
        os.environ.pop("MYAPP_TIMEOUT", None)

    return config


def example_file_configuration():
    """Example: Loading and saving configuration files."""

    @dataclass
    class WebConfig(BaseConfig):
        site_name: str = "My Website"
        theme: str = "default"
        features: dict = field(default_factory=dict)
        plugins: list = field(default_factory=list)

    print("\nFile configuration example:")

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create JSON config
        json_config = {
            "site_name": "Awesome Website",
            "theme": "dark",
            "features": {"comments": True, "analytics": False, "search": True},
            "plugins": ["seo", "cache", "security"],
        }

        json_file = tmpdir / "config.json"
        with open(json_file, "w") as f:
            json.dump(json_config, f, indent=2)

        # Load from JSON
        config = WebConfig.from_file(json_file)
        print(f"Loaded from JSON: {config}")

        # Modify and save as YAML
        config.theme = "light"
        config.features["newsletter"] = True

        yaml_file = tmpdir / "config.yaml"
        config.to_file(yaml_file)

        # Load from YAML
        yaml_config = WebConfig.from_file(yaml_file)
        print(f"Loaded from YAML: {yaml_config}")

        # Show file contents
        print("\nYAML file contents:")
        print(yaml_file.read_text())

    return config


def example_feature_flags():
    """Example: Using feature flags."""

    print("\nFeature flags example:")

    # Create feature flags
    flags = FeatureFlags()

    print(f"New user UI enabled: {flags.is_enabled('new_user_ui')}")

    # Enable features
    flags.enable("new_user_ui")
    flags.enable("beta_features")
    flags.enable("dark_mode")

    print(f"New user UI enabled: {flags.is_enabled('new_user_ui')}")
    print(f"Beta features enabled: {flags.is_enabled('beta_features')}")
    print(f"Analytics enabled: {flags.is_enabled('analytics')}")

    # Toggle features
    flags.toggle("analytics")
    print(f"Analytics after toggle: {flags.is_enabled('analytics')}")

    flags.toggle("analytics")
    print(f"Analytics after second toggle: {flags.is_enabled('analytics')}")

    # From configuration
    flags_config = {"enabled_features": ["feature1", "feature2", "experimental"]}

    loaded_flags = FeatureFlags.from_dict(flags_config)
    print("Loaded flags:")
    for feature in ["feature1", "feature2", "feature3", "experimental"]:
        print(f"  {feature}: {loaded_flags.is_enabled(feature)}")

    return flags


def example_user_preferences():
    """Example: Managing user preferences."""

    print("\nUser preferences example:")

    prefs = UserPreferences()

    # Set various preference types
    prefs.set("theme", "dark")
    prefs.set("language", "en-US")
    prefs.set("notifications", "true")
    prefs.set("max_items_per_page", "50")
    prefs.set("favorite_categories", "tech,science,programming")

    # Get preferences with type conversion
    print(f"Theme: {prefs.get('theme')}")
    print(f"Language: {prefs.get('language', 'en')}")
    print(f"Notifications: {prefs.get_bool('notifications')}")
    print(f"Max items: {prefs.get_int('max_items_per_page')}")
    print(f"Categories: {prefs.get_list('favorite_categories')}")

    # Handle missing preferences
    print(f"Missing pref: {prefs.get('missing_pref', 'default_value')}")
    print(f"Missing bool: {prefs.get_bool('missing_bool', True)}")
    print(f"Missing int: {prefs.get_int('missing_int', 100)}")
    print(f"Missing list: {prefs.get_list('missing_list', ['default'])}")

    # Remove preference
    prefs.remove("language")
    print(f"Language after removal: {prefs.get('language', 'not_set')}")

    return prefs


def example_configuration_validation():
    """Example: Configuration validation."""

    print("\nConfiguration validation example:")

    # Valid configuration
    valid_db = DatabaseConfig(host="production.db.com", port=5432, database="myapp", username="app_user", pool_size=20)

    errors = valid_db.validate()
    print(f"Valid config errors: {errors}")
    print(f"Connection string: {valid_db.connection_string}")

    # Invalid configuration
    invalid_db = DatabaseConfig(
        host="",  # Missing host
        port=99999,  # Invalid port
        database="",  # Missing database
        pool_size=0,  # Invalid pool size
    )

    errors = invalid_db.validate()
    print("\nInvalid config errors:")
    for error in errors:
        print(f"  - {error}")

    # App configuration validation
    invalid_app = AppConfig(
        max_workers=0,  # Too low
        timeout_seconds=-1,  # Negative
        log_level="INVALID",  # Invalid level
    )

    errors = invalid_app.validate()
    print("\nInvalid app config errors:")
    for error in errors:
        print(f"  - {error}")

    return valid_db


def example_configuration_manager():
    """Example: Using configuration manager."""

    print("\nConfiguration manager example:")

    manager = ConfigManager()

    # Register configurations
    app_config = AppConfig(name="MyApp", version="2.1.0", debug=True)

    db_config = DatabaseConfig(host="localhost", database="myapp_dev")

    features = FeatureFlags()
    features.enable("experimental_ui")
    features.enable("advanced_search")

    manager.register("app", app_config)
    manager.register("database", db_config)
    manager.register("features", features)

    # Retrieve configurations
    app = manager.get("app")
    print(f"App name: {app.name}")
    print(f"App version: {app.version}")

    db = manager.get("database")
    print(f"Database: {db.connection_string}")

    # Validate all configurations
    errors = manager.validate_all()
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("All configurations are valid!")

    # Add custom validator
    def app_name_validator(config):
        errors = []
        if len(config.name) < 3:
            errors.append("App name must be at least 3 characters")
        if not config.name.replace("_", "").replace("-", "").isalnum():
            errors.append("App name must be alphanumeric")
        return errors

    manager.add_validator("app", app_name_validator)

    # Test with invalid app name
    invalid_app = AppConfig(name="X!")
    manager.register("app", invalid_app)

    errors = manager.validate_all()
    print(f"\nValidation with custom validator: {errors}")

    return manager


def example_layered_configuration():
    """Example: Layered configuration loading."""

    @dataclass
    class ServiceConfig(BaseConfig):
        service_name: str = "default-service"
        port: int = 8080
        workers: int = 1
        debug: bool = False
        features: list = field(default_factory=list)

    print("\nLayered configuration example:")

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create config file
        config_file = tmpdir / "service.json"
        file_config = {"service_name": "api-service", "port": 3000, "workers": 4, "features": ["logging", "metrics"]}

        with open(config_file, "w") as f:
            json.dump(file_config, f)

        # Set environment variable
        os.environ["DEBUG"] = "true"
        os.environ["WORKERS"] = "8"

        try:
            # Load with layering: defaults -> file -> environment
            config = load_config(
                ServiceConfig, config_file=config_file, defaults={"service_name": "base-service", "features": ["basic"]}
            )

            print("Final config:")
            print(f"  Service name: {config.service_name}")  # From file
            print(f"  Port: {config.port}")  # From file
            print(f"  Workers: {config.workers}")  # From environment (overrides file)
            print(f"  Debug: {config.debug}")  # From environment
            print(f"  Features: {config.features}")  # From file (overrides defaults)

        finally:
            os.environ.pop("DEBUG", None)
            os.environ.pop("WORKERS", None)

    return config


def example_nested_configuration():
    """Example: Nested configuration structures."""

    @dataclass
    class LoggingConfig(BaseConfig):
        level: str = "INFO"
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file: str = ""

    @dataclass
    class SecurityConfig(BaseConfig):
        secret_key: str = ""
        session_timeout: int = 3600
        allowed_hosts: list = field(default_factory=list)

    @dataclass
    class CompleteAppConfig(BaseConfig):
        name: str = "MyApp"
        version: str = "1.0.0"
        logging: LoggingConfig = field(default_factory=LoggingConfig)
        security: SecurityConfig = field(default_factory=SecurityConfig)
        features: FeatureFlags = field(default_factory=FeatureFlags)
        preferences: UserPreferences = field(default_factory=UserPreferences)

    print("\nNested configuration example:")

    # Create configuration with nested structures
    config_data = {
        "name": "Advanced App",
        "version": "2.0.0",
        "logging": {"level": "DEBUG", "file": "/var/log/app.log"},
        "security": {
            "secret_key": "super-secret-key",
            "session_timeout": 7200,
            "allowed_hosts": ["app.example.com", "api.example.com"],
        },
    }

    config = CompleteAppConfig.from_dict(config_data)

    print(f"App: {config.name} v{config.version}")
    print(f"Logging level: {config.logging.level}")
    print(f"Log file: {config.logging.file}")
    print(f"Session timeout: {config.security.session_timeout}s")
    print(f"Allowed hosts: {config.security.allowed_hosts}")

    # Enable some features
    config.features.enable("dark_mode")
    config.features.enable("notifications")

    # Set user preferences
    config.preferences.set("theme", "dark")
    config.preferences.set("language", "en-US")

    print(f"Dark mode enabled: {config.features.is_enabled('dark_mode')}")
    print(f"User theme: {config.preferences.get('theme')}")

    # Convert to dict to see structure
    full_dict = config.to_dict()
    print("\nFull configuration structure:")
    print(json.dumps(full_dict, indent=2))

    return config


def example_schema_generation():
    """Example: Generating JSON schema for configurations."""

    print("\nSchema generation example:")

    # Generate schema for AppConfig
    app_schema = create_config_schema(AppConfig)

    print("AppConfig JSON Schema:")
    print(json.dumps(app_schema, indent=2))

    # Generate schema for DatabaseConfig
    db_schema = create_config_schema(DatabaseConfig)

    print("\nDatabaseConfig JSON Schema:")
    print(json.dumps(db_schema, indent=2))

    return app_schema


if __name__ == "__main__":
    print("=== Configuration Management Examples ===\n")

    print("1. Basic Configuration:")
    example_basic_configuration()

    print("\n2. Environment Variables:")
    example_environment_variables()

    print("\n3. File Configuration:")
    example_file_configuration()

    print("\n4. Feature Flags:")
    example_feature_flags()

    print("\n5. User Preferences:")
    example_user_preferences()

    print("\n6. Configuration Validation:")
    example_configuration_validation()

    print("\n7. Configuration Manager:")
    example_configuration_manager()

    print("\n8. Layered Configuration:")
    example_layered_configuration()

    print("\n9. Nested Configuration:")
    example_nested_configuration()

    print("\n10. Schema Generation:")
    example_schema_generation()
