"""YAML handling utilities with graceful fallbacks."""

import json
from pathlib import Path
from typing import Any

from rich.console import Console

console = Console()


def load_yaml(file_path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load YAML file with graceful error handling.

    Args:
        file_path: Path to YAML file
        default: Default value if file cannot be loaded

    Returns:
        Parsed YAML data or default value
    """
    if default is None:
        default = {}

    if not file_path.exists():
        return default

    try:
        # Try to use PyYAML if available
        import yaml

        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else default

    except ImportError:
        # Fallback to JSON if YAML not available (for simple YAML files)
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Try to parse as JSON (subset of YAML)
                data = json.loads(content)
                return data if data is not None else default
        except Exception:
            console.print(f"[yellow]Warning: Could not parse {file_path} (PyYAML not available)[/yellow]")
            return default

    except Exception as e:
        console.print(f"[yellow]Warning: Could not load {file_path}: {e}[/yellow]")
        return default


def save_yaml(file_path: Path, data: dict[str, Any], create_dirs: bool = True) -> bool:
    """Save data to YAML file with error handling.

    Args:
        file_path: Path to save to
        data: Data to save
        create_dirs: Create parent directories if needed

    Returns:
        True if successful, False otherwise
    """
    try:
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Try to use PyYAML if available
        import yaml

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        return True

    except ImportError:
        # Fallback to JSON if YAML not available
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            console.print(f"[yellow]Note: Saved {file_path} as JSON (PyYAML not available)[/yellow]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to save {file_path}: {e}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]Failed to save {file_path}: {e}[/red]")
        return False


def validate_yaml_schema(data: dict[str, Any], required_keys: list[str]) -> tuple[bool, list[str]]:
    """Validate YAML data against a simple schema.

    Args:
        data: Data to validate
        required_keys: List of required top-level keys

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not isinstance(data, dict):
        errors.append("Data must be a dictionary")
        return False, errors

    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    return len(errors) == 0, errors


def merge_yaml_configs(base_config: dict[str, Any], override_config: dict[str, Any]) -> dict[str, Any]:
    """Merge two YAML configurations with override precedence.

    Args:
        base_config: Base configuration
        override_config: Override configuration (takes precedence)

    Returns:
        Merged configuration
    """

    def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    return deep_merge(base_config, override_config)


def extract_yaml_section(file_path: Path, section_key: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract a specific section from a YAML file.

    Args:
        file_path: Path to YAML file
        section_key: Key of the section to extract
        default: Default value if section not found

    Returns:
        Section data or default value
    """
    if default is None:
        default = {}

    data = load_yaml(file_path, {})
    return data.get(section_key, default)


def update_yaml_section(file_path: Path, section_key: str, section_data: dict[str, Any]) -> bool:
    """Update a specific section in a YAML file.

    Args:
        file_path: Path to YAML file
        section_key: Key of the section to update
        section_data: New data for the section

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load existing data
        existing_data = load_yaml(file_path, {})

        # Update section
        existing_data[section_key] = section_data

        # Save back
        return save_yaml(file_path, existing_data)

    except Exception as e:
        console.print(f"[red]Failed to update section {section_key} in {file_path}: {e}[/red]")
        return False


def convert_json_to_yaml(json_path: Path, yaml_path: Path | None = None) -> bool:
    """Convert JSON file to YAML format.

    Args:
        json_path: Path to JSON file
        yaml_path: Path for output YAML file (defaults to same name with .yaml extension)

    Returns:
        True if successful, False otherwise
    """
    if yaml_path is None:
        yaml_path = json_path.with_suffix(".yaml")

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        return save_yaml(yaml_path, data)

    except Exception as e:
        console.print(f"[red]Failed to convert {json_path} to YAML: {e}[/red]")
        return False


class YAMLConfig:
    """Helper class for managing YAML configuration files."""

    def __init__(self, config_path: Path, default_config: dict[str, Any] | None = None):
        self.config_path = config_path
        self.default_config = default_config or {}
        self._config = None

    def load(self) -> dict[str, Any]:
        """Load configuration from file."""
        if self._config is None:
            self._config = load_yaml(self.config_path, self.default_config.copy())
        return self._config

    def save(self) -> bool:
        """Save configuration to file."""
        if self._config is not None:
            return save_yaml(self.config_path, self._config)
        return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        config = self.load()

        # Support dot notation (e.g., "database.host")
        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        config = self.load()

        # Support dot notation (e.g., "database.host")
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self._config = config

    def update(self, updates: dict[str, Any]) -> None:
        """Update configuration with new values."""
        config = self.load()
        self._config = merge_yaml_configs(config, updates)

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.default_config.copy()
