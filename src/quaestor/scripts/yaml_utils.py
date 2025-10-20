#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
YAML utilities for configuration files.

Simple self-contained utilities for loading, saving, and merging YAML files.
Can be used as a standalone script or imported as a module.

Usage:
    # As a standalone script
    uv run scripts/yaml-utils.py

    # As an imported module
    from scripts.yaml_utils import load_yaml, save_yaml, merge_yaml_configs
"""

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


def main():
    """CLI interface for yaml-utils."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/yaml-utils.py <command> [args]")
        print()
        print("Commands:")
        print("  load <file>              - Load and print YAML file")
        print("  validate <file>          - Validate YAML syntax")
        print("  merge <base> <override>  - Merge two YAML files")
        sys.exit(1)

    command = sys.argv[1]

    if command == "load":
        if len(sys.argv) < 3:
            print("Error: Missing file path")
            sys.exit(1)
        data = load_yaml(Path(sys.argv[2]))
        print(yaml.safe_dump(data, default_flow_style=False))

    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Missing file path")
            sys.exit(1)
        data = load_yaml(Path(sys.argv[2]))
        if data is not None:
            print("✓ Valid YAML")
        else:
            print("✗ Invalid YAML")
            sys.exit(1)

    elif command == "merge":
        if len(sys.argv) < 4:
            print("Error: Missing base or override file")
            sys.exit(1)
        base = load_yaml(Path(sys.argv[2]), {})
        override = load_yaml(Path(sys.argv[3]), {})
        merged = merge_yaml_configs(base, override)
        print(yaml.safe_dump(merged, default_flow_style=False))

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
