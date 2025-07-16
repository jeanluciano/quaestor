"""Command configuration system for project-specific overrides.

This module provides backward compatibility while delegating to the unified config system.
"""

import json
from pathlib import Path
from typing import Any

import yaml


class CommandConfig:
    """Manage project-specific command configurations.

    This class now serves as a compatibility layer over the unified QuaestorConfig system.
    """

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.config_path = project_dir / ".quaestor" / "command-config.yaml"
        self.override_dir = project_dir / ".quaestor" / "commands"
        self._config: dict[str, Any] | None = None

        # Use unified config system internally
        try:
            from .config_manager import QuaestorConfig

            self._unified_config = QuaestorConfig(project_dir)
        except ImportError:
            # Fallback to legacy behavior if unified config not available
            self._unified_config = None

    def load_config(self) -> dict[str, Any]:
        """Load command configuration from file."""
        if self._config is not None:
            return self._config

        # Use unified config if available
        if self._unified_config:
            try:
                config_data = self._unified_config.command_config.load()
                self._config = config_data
                return self._config
            except Exception:
                pass

        # Fallback to direct file loading
        self._config = {}
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                # Fall back to empty config on error
                self._config = {}

        return self._config

    def get_command_config(self, command_name: str) -> dict[str, Any]:
        """Get configuration for a specific command."""
        # Use unified config if available
        if self._unified_config:
            try:
                return self._unified_config.get_command_config(command_name)
            except Exception:
                pass

        # Fallback to legacy behavior
        config = self.load_config()
        commands = config.get("commands", {})
        return commands.get(command_name, {})

    def has_override(self, command_name: str) -> bool:
        """Check if a command has a local override file."""
        # Use unified config if available
        if self._unified_config:
            try:
                return self._unified_config.has_command_override(command_name)
            except Exception:
                pass

        # Fallback to direct check
        override_path = self.override_dir / f"{command_name}.md"
        return override_path.exists()

    def get_override_path(self, command_name: str) -> Path | None:
        """Get path to command override file if it exists."""
        # Use unified config if available
        if self._unified_config:
            try:
                return self._unified_config.get_command_override_path(command_name)
            except Exception:
                pass

        # Fallback to direct check
        override_path = self.override_dir / f"{command_name}.md"
        return override_path if override_path.exists() else None

    def merge_command_content(self, command_name: str, base_content: str) -> str:
        """Merge base command content with local overrides."""
        config = self.get_command_config(command_name)
        override_path = self.get_override_path(command_name)

        # If there's a full override file, use it
        if override_path:
            return override_path.read_text()

        # Otherwise, apply configuration modifications
        modified_content = base_content

        # Apply enforcement level
        enforcement = config.get("enforcement", "default")
        if enforcement == "strict":
            modified_content = self._apply_strict_enforcement(modified_content, command_name)
        elif enforcement == "relaxed":
            modified_content = self._apply_relaxed_enforcement(modified_content, command_name)

        # Apply custom parameters
        if "parameters" in config:
            modified_content = self._apply_custom_parameters(modified_content, config["parameters"])

        # Apply custom rules
        if "custom_rules" in config:
            modified_content = self._apply_custom_rules(modified_content, config["custom_rules"])

        return modified_content

    def _apply_strict_enforcement(self, content: str, command_name: str) -> str:
        """Apply stricter enforcement to command content."""
        # Add strict enforcement header
        strict_header = """
<!-- PROJECT-SPECIFIC: STRICT ENFORCEMENT ENABLED -->
## ⚠️ STRICT MODE ACTIVE

This project has enabled strict enforcement for this command.
ALL rules are MANDATORY with ZERO tolerance for deviations.

"""
        # Insert after the command description
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# ") and i > 0:  # Found main heading
                lines.insert(i + 1, strict_header)
                break

        return "\n".join(lines)

    def _apply_relaxed_enforcement(self, content: str, command_name: str) -> str:
        """Apply more relaxed enforcement to command content."""
        # Add relaxed enforcement note
        relaxed_note = """
<!-- PROJECT-SPECIFIC: RELAXED ENFORCEMENT -->
Note: This project uses relaxed enforcement. Focus on practicality over strict compliance.

"""
        # Insert after the command description
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# ") and i > 0:  # Found main heading
                lines.insert(i + 1, relaxed_note)
                break

        return "\n".join(lines)

    def _apply_custom_parameters(self, content: str, parameters: dict[str, Any]) -> str:
        """Apply custom parameter values to command content."""
        # Replace parameter placeholders
        for param, value in parameters.items():
            # Look for YAML blocks and update values
            placeholder = f"{param}:"
            if placeholder in content:
                # Simple replacement for now - could be enhanced
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith(placeholder):
                        # Preserve indentation
                        indent = len(line) - len(line.lstrip())
                        lines[i] = f"{' ' * indent}{param}: {json.dumps(value)}"
                content = "\n".join(lines)

        return content

    def _apply_custom_rules(self, content: str, rules: list[str]) -> str:
        """Add project-specific custom rules to command."""
        if not rules:
            return content

        custom_section = "\n## 📋 PROJECT-SPECIFIC RULES\n\n"
        for rule in rules:
            custom_section += f"- {rule}\n"
        custom_section += "\n"

        # Insert before completion criteria if exists, otherwise at end
        if "## COMPLETION CRITERIA" in content:
            parts = content.split("## COMPLETION CRITERIA")
            return parts[0] + custom_section + "## COMPLETION CRITERIA" + parts[1]
        else:
            return content + custom_section

    def get_available_overrides(self) -> list[str]:
        """Get list of commands that have local overrides."""
        if not self.override_dir.exists():
            return []

        return [f.stem for f in self.override_dir.glob("*.md")]

    def create_default_config(self) -> None:
        """Create a default command configuration file."""
        default_config = {
            "# Command Configuration": "Customize command behavior for this project",
            "commands": {
                "task": {
                    "enforcement": "default",  # Options: strict, default, relaxed
                    "require_planning": True,
                    "agent_threshold": 3,
                    "parameters": {
                        "minimum_test_coverage": 80,
                        "max_function_lines": 50,
                    },
                    "custom_rules": [
                        "Always use type hints in Python code",
                        "Include integration tests for API changes",
                    ],
                },
                "check": {
                    "auto_fix": True,
                    "strict_mode": False,
                    "include_checks": ["lint", "test", "type"],
                },
                "milestone": {
                    "auto_commit": True,
                    "require_tests": True,
                },
            },
        }

        # Create directory if needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default config
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)


class CommandLoader:
    """Load commands with project-specific overrides."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.config = CommandConfig(project_dir)

    def load_command(self, command_name: str, base_content: str) -> str:
        """Load a command with any project-specific overrides applied."""
        # Check if project has command customizations
        if not self.config.config_path.exists() and not self.config.override_dir.exists():
            return base_content

        # Apply overrides and customizations
        return self.config.merge_command_content(command_name, base_content)

    def get_available_overrides(self) -> list[str]:
        """Get list of commands that have local overrides."""
        if not self.config.override_dir.exists():
            return []

        return [f.stem for f in self.config.override_dir.glob("*.md")]
