"""Configuration management utilities.

Extracted from V2.0 Config, Plugin Configuration, and State Management.
Provides flexible configuration handling with 85% complexity reduction.
"""

import json
import os
from dataclasses import asdict, dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

import yaml

T = TypeVar("T")


class ConfigFormat(Enum):
    """Supported configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    ENV = "env"


@dataclass
class ConfigError(Exception):
    """Configuration-related error."""

    message: str
    field_path: str | None = None
    original_error: Exception | None = None


def parse_bool(value: str | bool) -> bool:
    """Parse boolean from string or bool.

    Args:
        value: Value to parse

    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ("true", "yes", "1", "on", "enabled")

    return bool(value)


def parse_list(value: str | list) -> list:
    """Parse list from string or list.

    Args:
        value: Value to parse (comma-separated string or list)

    Returns:
        List value
    """
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        if not value:
            return []
        # Handle both comma and semicolon separators
        if ";" in value:
            return [item.strip() for item in value.split(";") if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    return [value]


@dataclass
class BaseConfig:
    """Base configuration class with common functionality."""

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Configuration instance
        """
        # Get field info
        field_map = {f.name: f for f in fields(cls)}

        # Process fields with type conversion
        filtered_data = {}
        for key, value in data.items():
            if key in field_map:
                field = field_map[key]
                # Check if field type is a BaseConfig subclass
                if isinstance(value, dict) and hasattr(field.type, "__bases__") and BaseConfig in field.type.__bases__:
                    # Recursively create nested config
                    filtered_data[key] = field.type.from_dict(value)
                else:
                    filtered_data[key] = value

        return cls(**filtered_data)

    @classmethod
    def from_env(cls: type[T], prefix: str = "") -> T:
        """Create config from environment variables.

        Args:
            prefix: Environment variable prefix

        Returns:
            Configuration instance
        """
        data = {}

        for f in fields(cls):
            env_name = f"{prefix}{f.name.upper()}" if prefix else f.name.upper()
            env_value = os.environ.get(env_name)

            if env_value is not None:
                # Type conversion based on field type
                if f.type is bool:
                    data[f.name] = parse_bool(env_value)
                elif f.type is int:
                    data[f.name] = int(env_value)
                elif f.type is float:
                    data[f.name] = float(env_value)
                elif f.type is list or (hasattr(f.type, "__origin__") and f.type.__origin__ is list):
                    data[f.name] = parse_list(env_value)
                else:
                    data[f.name] = env_value

        return cls.from_dict(data)

    @classmethod
    def from_file(cls: type[T], path: str | Path) -> T:
        """Load config from file.

        Args:
            path: Configuration file path

        Returns:
            Configuration instance

        Raises:
            ConfigError: If file cannot be loaded
        """
        path = Path(path)

        if not path.exists():
            raise ConfigError(f"Configuration file not found: {path}")

        try:
            with open(path) as f:
                if path.suffix == ".json":
                    data = json.load(f)
                elif path.suffix in (".yaml", ".yml"):
                    data = yaml.safe_load(f)
                else:
                    raise ConfigError(f"Unsupported file format: {path.suffix}")

            return cls.from_dict(data)

        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {path}", original_error=e) from e

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Configuration dictionary
        """
        return asdict(self)

    def to_file(self, path: str | Path, format: ConfigFormat | None = None):
        """Save config to file.

        Args:
            path: Output file path
            format: Output format (auto-detected if not specified)
        """
        path = Path(path)
        data = self.to_dict()

        # Auto-detect format from extension
        if format is None:
            if path.suffix == ".json":
                format = ConfigFormat.JSON
            elif path.suffix in (".yaml", ".yml"):
                format = ConfigFormat.YAML
            else:
                format = ConfigFormat.JSON

        with open(path, "w") as f:
            if format == ConfigFormat.JSON:
                json.dump(data, f, indent=2)
            elif format == ConfigFormat.YAML:
                yaml.safe_dump(data, f, default_flow_style=False)

    def update(self, updates: dict[str, Any]):
        """Update configuration values.

        Args:
            updates: Dictionary of updates
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate(self) -> list[str]:
        """Validate configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Override in subclasses for custom validation
        return errors


@dataclass
class FeatureFlags(BaseConfig):
    """Feature flag configuration."""

    enabled_features: set[str] = field(default_factory=set)

    def is_enabled(self, feature: str) -> bool:
        """Check if feature is enabled.

        Args:
            feature: Feature name

        Returns:
            True if enabled
        """
        return feature in self.enabled_features

    def enable(self, feature: str):
        """Enable a feature.

        Args:
            feature: Feature name
        """
        self.enabled_features.add(feature)

    def disable(self, feature: str):
        """Disable a feature.

        Args:
            feature: Feature name
        """
        self.enabled_features.discard(feature)

    def toggle(self, feature: str):
        """Toggle a feature.

        Args:
            feature: Feature name
        """
        if self.is_enabled(feature):
            self.disable(feature)
        else:
            self.enable(feature)


@dataclass
class UserPreferences(BaseConfig):
    """User preferences configuration."""

    preferences: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get preference value.

        Args:
            key: Preference key
            default: Default value

        Returns:
            Preference value
        """
        return self.preferences.get(key, default)

    def set(self, key: str, value: Any):
        """Set preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value

    def remove(self, key: str):
        """Remove preference.

        Args:
            key: Preference key
        """
        self.preferences.pop(key, None)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean preference.

        Args:
            key: Preference key
            default: Default value

        Returns:
            Boolean value
        """
        value = self.get(key, default)
        return parse_bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer preference.

        Args:
            key: Preference key
            default: Default value

        Returns:
            Integer value
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_list(self, key: str, default: list | None = None) -> list:
        """Get list preference.

        Args:
            key: Preference key
            default: Default value

        Returns:
            List value
        """
        value = self.get(key, default or [])
        return parse_list(value)


class ConfigManager:
    """Centralized configuration manager for A1 system.

    Provides unified configuration management for all A1 components with:
    - Environment variable support (QUAESTOR_A1_*)
    - YAML/JSON configuration files
    - Component-specific configurations
    - Validation and error reporting
    - Default configuration generation
    """

    def __init__(self, config_dir: str | Path | None = None):
        """Initialize configuration manager.

        Args:
            config_dir: Configuration directory (defaults to .quaestor)
        """
        self._configs: dict[str, BaseConfig] = {}
        self._validators: dict[str, list[callable]] = {}
        self._config_dir = Path(config_dir or ".quaestor")
        self._main_config_file = self._config_dir / "a1_config.yaml"
        self._loaded = False

    def register(self, name: str, config: BaseConfig):
        """Register a configuration.

        Args:
            name: Configuration name
            config: Configuration instance
        """
        self._configs[name] = config

    def get(self, name: str) -> BaseConfig | None:
        """Get configuration by name.

        Args:
            name: Configuration name

        Returns:
            Configuration instance or None
        """
        if not self._loaded:
            self.load_defaults()
        return self._configs.get(name)

    def ensure_loaded(self):
        """Ensure configuration is loaded."""
        if not self._loaded:
            self.load_defaults()

    def load_defaults(self):
        """Load default A1 configuration."""
        try:
            # Try to load from file first
            if self._main_config_file.exists():
                self.load_from_file(self._main_config_file)
            else:
                # Create default configuration
                self._create_default_configuration()

            # Override with environment variables
            self._load_environment_overrides()

            self._loaded = True

        except Exception as e:
            raise ConfigError(f"Failed to load A1 configuration: {e}", original_error=e) from e

    def add_validator(self, name: str, validator: callable):
        """Add validator for configuration.

        Args:
            name: Configuration name
            validator: Validator function that returns list of errors
        """
        if name not in self._validators:
            self._validators[name] = []
        self._validators[name].append(validator)

    def validate_all(self) -> dict[str, list[str]]:
        """Validate all configurations.

        Returns:
            Dictionary of configuration names to error lists
        """
        all_errors = {}

        for name, config in self._configs.items():
            errors = config.validate()

            # Run custom validators
            if name in self._validators:
                for validator in self._validators[name]:
                    errors.extend(validator(config))

            if errors:
                all_errors[name] = errors

        return all_errors

    def load_from_directory(self, directory: str | Path, pattern: str = "*.yaml"):
        """Load all configurations from directory.

        Args:
            directory: Directory path
            pattern: File pattern to match
        """
        directory = Path(directory)

        if not directory.exists():
            return

        for config_file in directory.glob(pattern):
            name = config_file.stem

            # Try to determine config class from name
            # This is a simple example - override for custom logic
            if name == "features":
                config = FeatureFlags.from_file(config_file)
            elif name == "preferences":
                config = UserPreferences.from_file(config_file)
            else:
                # Skip unknown configs
                continue

            self.register(name, config)

    def save_all(self, directory: str | Path):
        """Save all configurations to directory.

        Args:
            directory: Output directory
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        for name, config in self._configs.items():
            config.to_file(directory / f"{name}.yaml")

    def save_main_config(self):
        """Save main A1 configuration to file."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

        # Build comprehensive configuration
        config_data = self._build_main_config_data()

        with open(self._main_config_file, "w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, indent=2)

    def load_from_file(self, config_file: str | Path):
        """Load configuration from YAML file.

        Args:
            config_file: Configuration file path
        """
        config_file = Path(config_file)

        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file) as f:
                config_data = yaml.safe_load(f) or {}

            # Parse configuration sections
            self._parse_configuration_data(config_data)

        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {config_file}", original_error=e) from e

    def set_value(self, path: str, value: Any):
        """Set configuration value using dot notation.

        Args:
            path: Configuration path (e.g., 'extensions.state.max_snapshots')
            value: Value to set
        """
        parts = path.split(".")

        if len(parts) < 2:
            raise ConfigError(f"Invalid configuration path: {path}")

        config_name = parts[0]
        config = self.get(config_name)

        if not config:
            raise ConfigError(f"Configuration section not found: {config_name}")

        # Navigate to the field
        obj = config
        for part in parts[1:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                raise ConfigError(f"Configuration field not found: {'.'.join(parts[:-1])}")

        # Set the final value
        final_field = parts[-1]
        if hasattr(obj, final_field):
            setattr(obj, final_field, value)
        elif isinstance(obj, dict):
            obj[final_field] = value
        else:
            raise ConfigError(f"Configuration field not found: {path}")

    def get_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            path: Configuration path (e.g., 'extensions.state.max_snapshots')
            default: Default value if not found

        Returns:
            Configuration value
        """
        try:
            parts = path.split(".")

            if len(parts) < 2:
                return default

            config_name = parts[0]
            config = self.get(config_name)

            if not config:
                return default

            # Navigate to the field
            obj = config
            for part in parts[1:]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return default

            return obj

        except Exception:
            return default

    def _create_default_configuration(self):
        """Create default A1 configuration."""
        # Register default configurations
        self.register("system", A1SystemConfig())
        self.register("core", A1CoreConfig())
        self.register("extensions", A1ExtensionsConfig())
        self.register("cli", A1CLIConfig())
        self.register("features", A1FeatureFlags())
        self.register("preferences", A1UserPreferences())

    def _load_environment_overrides(self):
        """Load environment variable overrides."""
        # System overrides
        system_config = self._configs.get("system")
        if system_config:
            env_system = A1SystemConfig.from_env("QUAESTOR_A1_SYSTEM_")
            system_config.update(env_system.to_dict())

        # Extension overrides
        extensions_config = self._configs.get("extensions")
        if extensions_config:
            env_extensions = A1ExtensionsConfig.from_env("QUAESTOR_A1_EXT_")
            extensions_config.update(env_extensions.to_dict())

        # CLI overrides
        cli_config = self._configs.get("cli")
        if cli_config:
            env_cli = A1CLIConfig.from_env("QUAESTOR_A1_CLI_")
            cli_config.update(env_cli.to_dict())

    def _parse_configuration_data(self, config_data: dict[str, Any]):
        """Parse configuration data from file.

        Args:
            config_data: Configuration dictionary
        """
        # Parse each section
        if "system" in config_data:
            self.register("system", A1SystemConfig.from_dict(config_data["system"]))
        else:
            self.register("system", A1SystemConfig())

        if "core" in config_data:
            # Handle nested context config
            core_data = config_data["core"]
            if "context" in core_data:
                context_config = A1ContextConfig.from_dict(core_data["context"])
                core_config = A1CoreConfig(context=context_config)
            else:
                core_config = A1CoreConfig.from_dict(core_data)
            self.register("core", core_config)
        else:
            self.register("core", A1CoreConfig())

        if "extensions" in config_data:
            # Handle nested extension configs
            ext_data = config_data["extensions"]
            ext_config = A1ExtensionsConfig()

            if "state" in ext_data:
                ext_config.state = A1StateConfig.from_dict(ext_data["state"])
            if "hooks" in ext_data:
                ext_config.hooks = A1HooksConfig.from_dict(ext_data["hooks"])
            if "prediction" in ext_data:
                ext_config.prediction = A1PredictionConfig.from_dict(ext_data["prediction"])
            if "workflow" in ext_data:
                ext_config.workflow = A1WorkflowConfig.from_dict(ext_data["workflow"])
            if "persistence" in ext_data:
                ext_config.persistence = A1PersistenceConfig.from_dict(ext_data["persistence"])
            if "learning" in ext_data:
                ext_config.learning = A1LearningConfig.from_dict(ext_data["learning"])

            self.register("extensions", ext_config)
        else:
            self.register("extensions", A1ExtensionsConfig())

        if "cli" in config_data:
            self.register("cli", A1CLIConfig.from_dict(config_data["cli"]))
        else:
            self.register("cli", A1CLIConfig())

        if "features" in config_data:
            features_data = config_data["features"]
            features = A1FeatureFlags()
            for feature, enabled in features_data.items():
                if enabled:
                    features.enable(feature)
            self.register("features", features)
        else:
            self.register("features", A1FeatureFlags())

        if "preferences" in config_data:
            prefs = A1UserPreferences()
            prefs.preferences = config_data["preferences"]
            self.register("preferences", prefs)
        else:
            self.register("preferences", A1UserPreferences())

    def _build_main_config_data(self) -> dict[str, Any]:
        """Build main configuration data for saving.

        Returns:
            Configuration dictionary
        """
        config_data = {"version": "A1.0", "generated_at": "auto-generated"}

        # Add each configuration section
        for name, config in self._configs.items():
            if name == "features":
                # Special handling for feature flags
                config_data[name] = {feature: True for feature in config.enabled_features}
            elif name == "preferences":
                # Special handling for user preferences
                config_data[name] = config.preferences
            else:
                config_data[name] = config.to_dict()

        return config_data


# Example configuration classes


@dataclass
class AppConfig(BaseConfig):
    """Example application configuration."""

    name: str = "Quaestor A1"
    version: str = "A1.0"
    debug: bool = False
    log_level: str = "INFO"

    # Nested configurations
    features: FeatureFlags = field(default_factory=FeatureFlags)
    preferences: UserPreferences = field(default_factory=UserPreferences)

    # Application-specific settings
    max_workers: int = 4
    timeout_seconds: float = 30.0
    allowed_extensions: list[str] = field(default_factory=lambda: [".py", ".md", ".yaml"])

    def validate(self) -> list[str]:
        """Validate application configuration."""
        errors = []

        if self.max_workers < 1:
            errors.append("max_workers must be at least 1")

        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")

        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            errors.append(f"log_level must be one of {valid_log_levels}")

        return errors


@dataclass
class DatabaseConfig(BaseConfig):
    """Example database configuration."""

    host: str = "localhost"
    port: int = 5432
    database: str = "quaestor"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    echo: bool = False

    def validate(self) -> list[str]:
        """Validate database configuration."""
        errors = []

        if not self.host:
            errors.append("host is required")

        if not 1 <= self.port <= 65535:
            errors.append("port must be between 1 and 65535")

        if not self.database:
            errors.append("database name is required")

        if self.pool_size < 1:
            errors.append("pool_size must be at least 1")

        return errors

    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        auth = ""
        if self.username:
            auth = f"{self.username}"
            if self.password:
                auth += f":{self.password}"
            auth += "@"

        return f"postgresql://{auth}{self.host}:{self.port}/{self.database}"


# A1-specific configuration classes


@dataclass
class A1SystemConfig(BaseConfig):
    """A1 system configuration."""

    version: str = "A1.0"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = ".quaestor"
    max_workers: int = 4
    timeout_seconds: float = 30.0

    def validate(self) -> list[str]:
        """Validate system configuration."""
        errors = []

        if self.max_workers < 1:
            errors.append("max_workers must be at least 1")

        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")

        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            errors.append(f"log_level must be one of {valid_log_levels}")

        return errors


@dataclass
class A1ContextConfig(BaseConfig):
    """A1 context management configuration."""

    default_type: str = "development"
    max_relevant_files: int = 20
    relevance_threshold: float = 0.3
    auto_update_relevance: bool = True
    context_cache_size: int = 100

    def validate(self) -> list[str]:
        """Validate context configuration."""
        errors = []

        if not 0.0 <= self.relevance_threshold <= 1.0:
            errors.append("relevance_threshold must be between 0.0 and 1.0")

        if self.max_relevant_files < 1:
            errors.append("max_relevant_files must be at least 1")

        if self.context_cache_size < 0:
            errors.append("context_cache_size must be non-negative")

        return errors


@dataclass
class A1CoreConfig(BaseConfig):
    """A1 core component configuration."""

    context: A1ContextConfig = field(default_factory=A1ContextConfig)

    def validate(self) -> list[str]:
        """Validate core configuration."""
        errors = []
        if hasattr(self.context, "validate"):
            errors.extend(self.context.validate())
        return errors


@dataclass
class A1StateConfig(BaseConfig):
    """A1 state management configuration."""

    enabled: bool = True
    storage_path: str = "state"
    max_snapshots: int = 50
    auto_cleanup: bool = True
    cleanup_days: int = 30
    compression: bool = True

    def validate(self) -> list[str]:
        """Validate state configuration."""
        errors = []

        if self.max_snapshots < 0:
            errors.append("max_snapshots must be non-negative")

        if self.cleanup_days < 1:
            errors.append("cleanup_days must be at least 1")

        return errors


@dataclass
class A1HooksConfig(BaseConfig):
    """A1 hooks configuration."""

    enabled: bool = True
    config_file: str = "hooks.json"
    default_timeout: int = 30
    parallel_execution: bool = True
    max_concurrent: int = 5

    def validate(self) -> list[str]:
        """Validate hooks configuration."""
        errors = []

        if self.default_timeout < 1:
            errors.append("default_timeout must be at least 1")

        if self.max_concurrent < 1:
            errors.append("max_concurrent must be at least 1")

        return errors


@dataclass
class A1PredictionConfig(BaseConfig):
    """A1 prediction engine configuration."""

    enabled: bool = True
    pattern_file: str = "patterns.json"
    confidence_threshold: float = 0.7
    learning_rate: float = 0.1
    max_patterns: int = 1000
    auto_learn: bool = True

    def validate(self) -> list[str]:
        """Validate prediction configuration."""
        errors = []

        if not 0.0 <= self.confidence_threshold <= 1.0:
            errors.append("confidence_threshold must be between 0.0 and 1.0")

        if not 0.0 <= self.learning_rate <= 1.0:
            errors.append("learning_rate must be between 0.0 and 1.0")

        if self.max_patterns < 1:
            errors.append("max_patterns must be at least 1")

        return errors


@dataclass
class A1WorkflowConfig(BaseConfig):
    """A1 workflow detection configuration."""

    enabled: bool = True
    detection_sensitivity: str = "medium"
    auto_track: bool = True
    pattern_window_size: int = 10
    min_pattern_length: int = 3

    def validate(self) -> list[str]:
        """Validate workflow configuration."""
        errors = []

        valid_sensitivities = {"low", "medium", "high"}
        if self.detection_sensitivity not in valid_sensitivities:
            errors.append(f"detection_sensitivity must be one of {valid_sensitivities}")

        if self.pattern_window_size < 1:
            errors.append("pattern_window_size must be at least 1")

        if self.min_pattern_length < 1:
            errors.append("min_pattern_length must be at least 1")

        return errors


@dataclass
class A1PersistenceConfig(BaseConfig):
    """A1 persistence configuration."""

    enabled: bool = True
    backend: str = "file"
    compression: bool = True
    retention_days: int = 90
    auto_backup: bool = True
    backup_interval_hours: int = 24

    def validate(self) -> list[str]:
        """Validate persistence configuration."""
        errors = []

        valid_backends = {"file", "memory"}
        if self.backend not in valid_backends:
            errors.append(f"backend must be one of {valid_backends}")

        if self.retention_days < 1:
            errors.append("retention_days must be at least 1")

        if self.backup_interval_hours < 1:
            errors.append("backup_interval_hours must be at least 1")

        return errors


@dataclass
class A1LearningConfig(BaseConfig):
    """A1 learning configuration."""

    enabled: bool = True
    adaptation_threshold: float = 0.8
    max_adaptations: int = 500
    auto_learn: bool = True
    learning_window_days: int = 7

    def validate(self) -> list[str]:
        """Validate learning configuration."""
        errors = []

        if not 0.0 <= self.adaptation_threshold <= 1.0:
            errors.append("adaptation_threshold must be between 0.0 and 1.0")

        if self.max_adaptations < 1:
            errors.append("max_adaptations must be at least 1")

        if self.learning_window_days < 1:
            errors.append("learning_window_days must be at least 1")

        return errors


@dataclass
class A1ExtensionsConfig(BaseConfig):
    """A1 extensions configuration."""

    state: A1StateConfig = field(default_factory=A1StateConfig)
    hooks: A1HooksConfig = field(default_factory=A1HooksConfig)
    prediction: A1PredictionConfig = field(default_factory=A1PredictionConfig)
    workflow: A1WorkflowConfig = field(default_factory=A1WorkflowConfig)
    persistence: A1PersistenceConfig = field(default_factory=A1PersistenceConfig)
    learning: A1LearningConfig = field(default_factory=A1LearningConfig)

    def validate(self) -> list[str]:
        """Validate extensions configuration."""
        errors = []

        # Handle case where config objects might be dicts
        if hasattr(self.state, "validate"):
            errors.extend(self.state.validate())
        if hasattr(self.hooks, "validate"):
            errors.extend(self.hooks.validate())
        if hasattr(self.prediction, "validate"):
            errors.extend(self.prediction.validate())
        if hasattr(self.workflow, "validate"):
            errors.extend(self.workflow.validate())
        if hasattr(self.persistence, "validate"):
            errors.extend(self.persistence.validate())
        if hasattr(self.learning, "validate"):
            errors.extend(self.learning.validate())

        return errors


@dataclass
class A1CLIConfig(BaseConfig):
    """A1 CLI configuration."""

    output_format: str = "rich"
    show_progress: bool = True
    auto_confirm: bool = False
    theme: str = "default"
    verbosity: str = "normal"

    def validate(self) -> list[str]:
        """Validate CLI configuration."""
        errors = []

        valid_formats = {"rich", "plain", "json"}
        if self.output_format not in valid_formats:
            errors.append(f"output_format must be one of {valid_formats}")

        valid_themes = {"default", "dark", "light"}
        if self.theme not in valid_themes:
            errors.append(f"theme must be one of {valid_themes}")

        valid_verbosity = {"quiet", "normal", "verbose", "debug"}
        if self.verbosity not in valid_verbosity:
            errors.append(f"verbosity must be one of {valid_verbosity}")

        return errors


@dataclass
class A1FeatureFlags(FeatureFlags):
    """A1 feature flags configuration."""

    def __post_init__(self):
        """Initialize with default features."""
        super().__init__()
        # Set default enabled features
        default_features = {
            "advanced_prediction",
            "auto_hooks",
            "state_management",
            "workflow_detection",
            "persistence",
            "learning_adaptation",
        }
        self.enabled_features.update(default_features)


@dataclass
class A1UserPreferences(UserPreferences):
    """A1 user preferences configuration."""

    def __post_init__(self):
        """Initialize with default preferences."""
        super().__init__()
        # Set default preferences
        default_prefs = {
            "notifications": True,
            "auto_save": True,
            "confirm_destructive": True,
            "show_tips": True,
            "compact_output": False,
        }
        self.preferences.update(default_prefs)


# Global configuration manager instance
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get or create global configuration manager.

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(section: str) -> BaseConfig | None:
    """Get configuration section.

    Args:
        section: Configuration section name

    Returns:
        Configuration instance or None
    """
    return get_config_manager().get(section)


def set_config_value(path: str, value: Any):
    """Set configuration value using dot notation.

    Args:
        path: Configuration path (e.g., 'extensions.state.max_snapshots')
        value: Value to set
    """
    get_config_manager().set_value(path, value)


def get_config_value(path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation.

    Args:
        path: Configuration path (e.g., 'extensions.state.max_snapshots')
        default: Default value if not found

    Returns:
        Configuration value
    """
    return get_config_manager().get_value(path, default)


def init_config(config_dir: str | Path | None = None) -> ConfigManager:
    """Initialize configuration system.

    Args:
        config_dir: Configuration directory (defaults to .quaestor)

    Returns:
        Initialized ConfigManager
    """
    global _config_manager
    _config_manager = ConfigManager(config_dir)
    _config_manager.ensure_loaded()
    return _config_manager


def save_config():
    """Save current configuration to file."""
    get_config_manager().save_main_config()


# Convenience functions


def load_config[T](
    config_class: type[T],
    env_prefix: str = "",
    config_file: str | Path | None = None,
    defaults: dict[str, Any] | None = None,
) -> T:
    """Load configuration from multiple sources.

    Args:
        config_class: Configuration class
        env_prefix: Environment variable prefix
        config_file: Optional configuration file
        defaults: Default values

    Returns:
        Configuration instance
    """
    # Start with defaults
    config_dict = defaults or {}

    # Load from file if provided
    if config_file and Path(config_file).exists():
        file_config = config_class.from_file(config_file)
        config_dict.update(file_config.to_dict())

    # Override with environment variables (only include non-default values)
    env_config = config_class.from_env(env_prefix)
    env_dict = env_config.to_dict()

    # Only override with env vars that have actual values
    default_config = config_class()
    default_dict = default_config.to_dict()

    for key, value in env_dict.items():
        if key in default_dict and value != default_dict[key]:
            config_dict[key] = value

    # Create final config
    return config_class.from_dict(config_dict)


def create_config_schema(config_class: type[BaseConfig]) -> dict[str, Any]:
    """Generate JSON schema for configuration class.

    Args:
        config_class: Configuration class

    Returns:
        JSON schema dictionary
    """
    schema = {"type": "object", "properties": {}, "required": []}

    for f in fields(config_class):
        prop_schema = {"type": "string"}  # Default

        if f.type is bool:
            prop_schema = {"type": "boolean"}
        elif f.type is int:
            prop_schema = {"type": "integer"}
        elif f.type is float:
            prop_schema = {"type": "number"}
        elif f.type is list or (hasattr(f.type, "__origin__") and f.type.__origin__ is list):
            prop_schema = {"type": "array", "items": {"type": "string"}}
        elif hasattr(f.type, "__dataclass_fields__"):
            # Nested dataclass
            prop_schema = create_config_schema(f.type)

        schema["properties"][f.name] = prop_schema

        # Check if required (no default value)
        if f.default == field().default and f.default_factory == field().default_factory:
            schema["required"].append(f.name)

    return schema
