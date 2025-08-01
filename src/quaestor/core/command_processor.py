"""Command processor that applies project-specific configurations to commands."""

import importlib.resources as pkg_resources
from pathlib import Path

from .command_config import CommandLoader


class CommandProcessor:
    """Process commands with project-specific configurations."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.loader = CommandLoader(project_dir)

    def process_command(self, command_name: str) -> str:
        """Process a command with configurations and overrides.

        Args:
            command_name: Name of the command (without .md extension)

        Returns:
            Processed command content with configurations applied
        """
        # Load base command
        base_content = self._load_base_command(command_name)

        # Check for override
        override_content = self.loader.get_override(command_name)
        if override_content:
            return override_content

        # Apply configurations
        config = self.loader.get_configuration(command_name)
        if config:
            processed_content = self._apply_configuration(base_content, config)
        else:
            processed_content = base_content

        return processed_content

    def _load_base_command(self, command_name: str) -> str:
        """Load the base command from the package.

        Args:
            command_name: Name of the command (without .md extension)

        Returns:
            Base command content
        """
        try:
            return pkg_resources.read_text("quaestor.claude.commands", f"{command_name}.md")
        except FileNotFoundError:
            raise ValueError(f"Command not found: {command_name}")

    def _apply_configuration(self, content: str, config: dict) -> str:
        """Apply configuration to command content.

        Args:
            content: Base command content
            config: Configuration dictionary

        Returns:
            Configured command content
        """
        # Apply configuration header
        if config.get("enabled", True):
            header = self._create_configuration_header(config)
            content = self._inject_header(content, header)

        # Apply custom rules
        if config.get("rules"):
            rules_section = self._create_rules_section(config["rules"])
            content = self._inject_rules(content, rules_section)

        return content

    def _create_configuration_header(self, config: dict) -> str:
        """Create configuration header for command."""
        header = "<!-- PROJECT-SPECIFIC: "
        if config.get("enforcement") == "strict":
            header += "STRICT ENFORCEMENT ENABLED"
        else:
            header += "RELAXED CONFIGURATION"
        header += " -->\n"

        if config.get("enforcement") == "strict":
            header += "## ⚠️ STRICT MODE ACTIVE\n\n"
            header += "This project has enabled strict enforcement for this command.\n"
            header += "ALL rules are MANDATORY with ZERO tolerance for deviations.\n"

        return header

    def _create_rules_section(self, rules: list[str]) -> str:
        """Create rules section from configuration."""
        section = "\n## 📋 PROJECT-SPECIFIC RULES\n\n"
        for rule in rules:
            section += f"- {rule}\n"
        return section

    def _inject_header(self, content: str, header: str) -> str:
        """Inject header after command title."""
        lines = content.split("\n")

        # Find first heading
        for i, line in enumerate(lines):
            if line.startswith("#") and not line.startswith("##"):
                # Insert after title and empty line
                insert_index = i + 1
                while insert_index < len(lines) and not lines[insert_index].strip():
                    insert_index += 1
                lines.insert(insert_index, header)
                break

        return "\n".join(lines)

    def get_configured_commands(self) -> list[str]:
        """Get list of commands that have configurations."""
        # Load the config file directly
        config_path = self.project_dir / ".quaestor" / "command-config.yaml"
        if not config_path.exists():
            return []

        try:
            import yaml

            with open(config_path) as f:
                config_data = yaml.safe_load(f) or {}
            return list(config_data.get("commands", {}).keys())
        except Exception:
            return []

    def _inject_rules(self, content: str, rules_section: str) -> str:
        """Inject rules section at end of content."""
        return content.rstrip() + "\n" + rules_section

    def has_configuration(self, command_name: str) -> bool:
        """Check if a command has configuration.

        Args:
            command_name: Name of the command

        Returns:
            True if command has configuration
        """
        return self.loader.has_configuration(command_name)

    def get_command_info(self, command_name: str) -> dict:
        """Get information about command configuration.

        Args:
            command_name: Name of the command

        Returns:
            Dict with 'base' and 'configured' versions of the command
        """
        base = self._load_base_command(command_name)
        configured = self.process_command(command_name)

        return {"base": base, "configured": configured, "has_changes": base != configured}

    def preview_configuration(self, command_name: str) -> dict:
        """Preview configuration changes for a command.

        Args:
            command_name: Name of the command

        Returns:
            Dict with 'base' and 'configured' versions and 'has_changes' flag
        """
        return self.get_command_info(command_name)
