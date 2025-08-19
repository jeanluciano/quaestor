"""Modern configuration management system with layered loading."""

import copy
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from rich.console import Console

from quaestor.core.project_detection import detect_project_type
from quaestor.core.yaml_utils import load_yaml, merge_yaml_configs, save_yaml

from .config_schemas import (
    ConfigurationLayer,
    ConfigValidationResult,
    LanguageConfig,
    LanguagesConfig,
    QuaestorMainConfig,
)

console = Console()


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""

    pass


class ConfigManager:
    """Modern configuration manager with layered loading and validation."""

    def __init__(self, project_root: Path, language_override: str | None = None):
        """Initialize configuration manager.

        Args:
            project_root: Root directory of the project
            language_override: Optional language override
        """
        self.project_root = Path(project_root)
        self.quaestor_dir = self.project_root / ".quaestor"
        self.language_override = language_override

        # Configuration layers (priority order: 1=highest, 5=lowest)
        self._layers: list[ConfigurationLayer] = []
        self._main_config: QuaestorMainConfig | None = None
        self._languages_config: LanguagesConfig | None = None
        self._project_type: str | None = None

        self._initialize_layers()

    def _initialize_layers(self) -> None:
        """Initialize the configuration layers in priority order."""
        self._layers = [
            # Priority 1: Runtime API parameters (handled in merge methods)
            ConfigurationLayer(
                priority=1,
                source="Runtime API parameters",
                description="Highest priority, programmatic overrides",
                config_data={},
            ),
            # Priority 2: Project-specific language overrides
            ConfigurationLayer(
                priority=2,
                source=".quaestor/languages.yaml",
                description="Project-specific language overrides",
                file_path=self.quaestor_dir / "languages.yaml",
            ),
            # Priority 3: General project configuration
            ConfigurationLayer(
                priority=3,
                source=".quaestor/config.yaml",
                description="General project configuration",
                file_path=self.quaestor_dir / "config.yaml",
            ),
            # Priority 4: Base language configurations
            ConfigurationLayer(
                priority=4,
                source="src/quaestor/core/languages.yaml",
                description="Base language configurations",
                file_path=Path(__file__).parent / "languages.yaml",
            ),
            # Priority 5: Built-in defaults
            ConfigurationLayer(
                priority=5,
                source="Built-in defaults",
                description="Fallback for missing values",
                config_data=self._get_builtin_defaults(),
            ),
        ]

        # Load data for file-based layers
        for layer in self._layers:
            if layer.file_path:
                layer.exists = layer.file_path.exists()
                if layer.exists:
                    loaded_data = load_yaml(layer.file_path, {})
                    # Special handling for core languages.yaml - wrap in languages section
                    if "core/languages.yaml" in str(layer.file_path):
                        layer.config_data = {"languages": loaded_data}
                    else:
                        layer.config_data = loaded_data

    def _get_builtin_defaults(self) -> dict[str, Any]:
        """Get built-in default configuration."""
        return {
            "main": {
                "version": "1.0",
                "hooks": {
                    "enabled": True,
                    "strict_mode": False,
                },
            },
            "languages": {
                "unknown": {
                    "primary_language": "unknown",
                    "lint_command": "# Configure your linter",
                    "format_command": "# Configure your formatter",
                    "test_command": "# Configure your test runner",
                    "coverage_command": "# Configure coverage tool",
                    "type_check_command": None,
                    "security_scan_command": None,
                    "profile_command": None,
                    "coverage_threshold": None,
                    "type_checking": False,
                    "performance_target_ms": 200,
                    "commit_prefix": "chore",
                    "quick_check_command": "make check",
                    "full_check_command": "make validate",
                    "precommit_install_command": "pre-commit install",
                    "doc_style_example": None,
                }
            },
        }

    @property
    def project_type(self) -> str:
        """Get detected project type."""
        if self._project_type is None:
            self._project_type = self.language_override or detect_project_type(self.project_root)
        return self._project_type

    @project_type.setter
    def project_type(self, value: str) -> None:
        """Set project type (mainly for testing)."""
        self._project_type = value

    @project_type.deleter
    def project_type(self) -> None:
        """Delete cached project type (mainly for testing)."""
        self._project_type = None

    def get_main_config(self, runtime_overrides: dict[str, Any] | None = None) -> QuaestorMainConfig:
        """Get validated main configuration with layered loading.

        Args:
            runtime_overrides: Optional runtime configuration overrides

        Returns:
            Validated main configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self._main_config is None or runtime_overrides:
            merged_config = self._merge_layered_config("main", runtime_overrides)

            try:
                self._main_config = QuaestorMainConfig(**merged_config)
            except ValidationError as e:
                raise ConfigurationError(f"Invalid main configuration: {e}") from e

        return self._main_config

    def get_languages_config(self, runtime_overrides: dict[str, Any] | None = None) -> LanguagesConfig:
        """Get validated languages configuration with layered loading.

        Args:
            runtime_overrides: Optional runtime language configuration overrides

        Returns:
            Validated languages configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self._languages_config is None or runtime_overrides:
            merged_config = self._merge_layered_config("languages", runtime_overrides)

            # Convert language dictionaries to LanguageConfig objects
            languages = {}
            for lang_name, lang_data in merged_config.items():
                try:
                    languages[lang_name] = LanguageConfig(**lang_data)
                except ValidationError as e:
                    console.print(f"[yellow]Warning: Invalid configuration for language '{lang_name}': {e}[/yellow]")
                    # Skip invalid language configs rather than fail entirely
                    continue

            self._languages_config = LanguagesConfig(languages=languages)

        return self._languages_config

    def get_language_config(
        self, language: str | None = None, runtime_overrides: dict[str, Any] | None = None
    ) -> LanguageConfig | None:
        """Get configuration for a specific language.

        Args:
            language: Language name (defaults to detected project type)
            runtime_overrides: Optional runtime overrides for this language

        Returns:
            Language configuration or None if not found
        """
        target_language = language or self.project_type
        languages_config = self.get_languages_config()

        base_config = languages_config.get_language_config(target_language)

        if base_config is None:
            # Try to get unknown language config as fallback
            base_config = languages_config.get_language_config("unknown")

        if runtime_overrides and base_config:
            # Apply runtime overrides to the base config
            merged_data = merge_yaml_configs(base_config.model_dump(), runtime_overrides)
            try:
                return LanguageConfig(**merged_data)
            except ValidationError as e:
                console.print(
                    f"[yellow]Warning: Invalid runtime overrides for language '{target_language}': {e}[/yellow]"
                )
                return base_config

        return base_config

    def _merge_layered_config(
        self, config_section: str, runtime_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Merge configuration from all layers for a specific section.

        Args:
            config_section: Configuration section to merge ("main", "languages", "commands")
            runtime_overrides: Optional runtime overrides (highest priority)

        Returns:
            Merged configuration dictionary
        """
        # Start with empty config
        merged_config = {}

        # Apply layers from lowest priority to highest priority (5->4->3->2->1)
        sorted_layers = sorted(self._layers, key=lambda x: x.priority, reverse=True)

        for layer in sorted_layers:
            if layer.priority == 1:
                # Handle runtime overrides
                if runtime_overrides:
                    # Runtime overrides are the section data directly
                    merged_config = self._deep_merge_configs(merged_config, runtime_overrides)
                continue

            # Get section data from this layer
            section_data = layer.config_data.get(config_section, {})
            if section_data:
                merged_config = self._deep_merge_configs(merged_config, section_data)

        return merged_config

    def _deep_merge_configs(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configuration dictionaries with conflict resolution.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        result = copy.deepcopy(base)

        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    # Deep merge nested dictionaries
                    result[key] = self._deep_merge_configs(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    # Array replacement (not concatenation) as per spec
                    result[key] = copy.deepcopy(value)
                else:
                    # Direct replacement for other types
                    result[key] = copy.deepcopy(value)
            else:
                # New key from override
                result[key] = copy.deepcopy(value)

        return result

    def _invalidate_cache(self) -> None:
        """Invalidate cached configuration objects."""
        self._main_config = None
        self._languages_config = None

    def _reload_layers(self) -> None:
        """Reload configuration layers from files."""
        for layer in self._layers:
            if layer.file_path:
                layer.exists = layer.file_path.exists()
                if layer.exists:
                    loaded_data = load_yaml(layer.file_path, {})
                    # Special handling for core languages.yaml - wrap in languages section
                    if "core/languages.yaml" in str(layer.file_path):
                        layer.config_data = {"languages": loaded_data}
                    else:
                        layer.config_data = loaded_data
                else:
                    layer.config_data = {}

    def validate_configuration(self) -> ConfigValidationResult:
        """Validate all configuration files and return detailed results.

        Returns:
            Validation result with warnings and errors
        """
        result = ConfigValidationResult(valid=True)

        # Validate main configuration
        try:
            self.get_main_config()
            # Main config validation passed if we get here

        except ConfigurationError as e:
            result.add_error(f"Main configuration error: {e}")

        # Validate language configurations
        try:
            languages_config = self.get_languages_config()

            for lang_name, lang_config in languages_config.languages.items():
                # Check for warnings
                if lang_config.coverage_threshold and lang_config.coverage_threshold > 95:
                    result.add_warning(
                        f"coverage_threshold ({lang_config.coverage_threshold}) unusually high for {lang_name}"
                    )

                if lang_config.performance_target_ms and lang_config.performance_target_ms < 10:
                    result.add_warning(
                        f"performance_target_ms ({lang_config.performance_target_ms}) unusually low for {lang_name}"
                    )

        except ConfigurationError as e:
            result.add_error(f"Language configuration error: {e}")

        # Validate file layer existence and readability
        for layer in self._layers:
            if layer.file_path and not layer.exists and layer.priority <= 4:
                # Only warn about missing files that should exist (not project overrides)
                if layer.priority == 4:  # Base languages.yaml should exist
                    result.add_error(f"Required configuration file missing: {layer.file_path}")

        return result

    def get_effective_config(self, runtime_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get the complete effective configuration after all merging.

        Args:
            runtime_overrides: Optional runtime configuration overrides

        Returns:
            Complete merged configuration dictionary
        """
        try:
            main_config = self.get_main_config(runtime_overrides.get("main") if runtime_overrides else None)
            languages_config = self.get_languages_config(
                runtime_overrides.get("languages") if runtime_overrides else None
            )

            # Add current language config
            current_language_config = self.get_language_config(
                runtime_overrides=runtime_overrides.get("current_language") if runtime_overrides else None
            )

            return {
                "main": main_config.model_dump(mode="json"),
                "languages": {
                    name: config.model_dump(mode="json") for name, config in languages_config.languages.items()
                },
                "current_language": current_language_config.model_dump(mode="json")
                if current_language_config
                else None,
                "project_type": self.project_type,
                "layers": [
                    {
                        "priority": layer.priority,
                        "source": layer.source,
                        "description": layer.description,
                        "exists": layer.exists,
                    }
                    for layer in self._layers
                ],
            }

        except ConfigurationError as e:
            raise ConfigurationError(f"Failed to get effective configuration: {e}") from e

    def save_project_config(self, config_updates: dict[str, Any], config_type: str = "main") -> bool:
        """Save configuration updates to project files.

        Args:
            config_updates: Configuration updates to save
            config_type: Type of config to save ("main", "languages")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .quaestor directory exists
            self.quaestor_dir.mkdir(parents=True, exist_ok=True)

            if config_type == "main":
                config_path = self.quaestor_dir / "config.yaml"
                # Load existing config and merge updates
                existing_config = load_yaml(config_path, {})
                # Ensure updates are in the "main" section
                sectioned_updates = {"main": config_updates}
                merged_config = self._deep_merge_configs(existing_config, sectioned_updates)
                success = save_yaml(config_path, merged_config)
                if success:
                    self._invalidate_cache()
                    self._reload_layers()
                return success

            elif config_type == "languages":
                config_path = self.quaestor_dir / "languages.yaml"
                # Load existing config and merge updates
                existing_config = load_yaml(config_path, {})
                # Ensure updates are in the "languages" section
                sectioned_updates = {"languages": config_updates}
                merged_config = self._deep_merge_configs(existing_config, sectioned_updates)
                success = save_yaml(config_path, merged_config)
                if success:
                    self._invalidate_cache()
                    self._reload_layers()
                return success

            else:
                raise ValueError(f"Unknown config type: {config_type}")

        except Exception as e:
            console.print(f"[red]Failed to save {config_type} configuration: {e}[/red]")
            return False

    def initialize_default_configs(self) -> bool:
        """Initialize default configuration files if they don't exist.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .quaestor directory exists
            self.quaestor_dir.mkdir(parents=True, exist_ok=True)

            success = True

            # Initialize main config if it doesn't exist
            main_config_path = self.quaestor_dir / "config.yaml"
            if not main_config_path.exists():
                # Save with the main wrapper for consistency
                default_main = {"main": self._get_builtin_defaults()["main"]}
                success &= save_yaml(main_config_path, default_main)

            # Note: We don't create languages.yaml by default as it's for overrides only

            return success

        except Exception as e:
            console.print(f"[red]Failed to initialize default configurations: {e}[/red]")
            return False


def get_config_manager(project_root: Path | None = None, language_override: str | None = None) -> ConfigManager:
    """Get ConfigManager instance for a project.

    Args:
        project_root: Project root directory (auto-detected if None)
        language_override: Optional language type override

    Returns:
        ConfigManager instance
    """
    if project_root is None:
        # Auto-detect project root by looking for .quaestor directory
        current = Path.cwd()
        while current != current.parent:
            if (current / ".quaestor").exists():
                project_root = current
                break
            current = current.parent
        else:
            project_root = Path.cwd()

    return ConfigManager(project_root, language_override)
