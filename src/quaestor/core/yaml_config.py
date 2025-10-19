"""Simple YAML utilities for configuration files only (not specifications)."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(file_path: Path, default: Any = None) -> Any:
    """Load a YAML file.

    Args:
        file_path: Path to YAML file
        default: Default value if file doesn't exist or is empty

    Returns:
        Parsed YAML data or default
    """
    if not file_path.exists():
        return default

    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
            return data if data is not None else default
    except Exception:
        return default


def save_yaml(file_path: Path, data: Any) -> bool:
    """Save data to a YAML file.

    Args:
        file_path: Path to save to
        data: Data to save

    Returns:
        True if successful
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False


def merge_yaml_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge two YAML configurations.

    Args:
        base: Base configuration
        override: Configuration to override with

    Returns:
        Merged configuration
    """
    import copy

    result = copy.deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_yaml_configs(result[key], value)
        else:
            result[key] = value

    return result
