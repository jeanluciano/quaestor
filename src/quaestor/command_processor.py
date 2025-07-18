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
        # Load base command content
        base_content = self._load_base_command(command_name)

        # Apply configurations and overrides
        processed_content = self.loader.load_command(command_name, base_content)

        # Add configuration marker if modified
        if processed_content != base_content:
            processed_content = self._add_configuration_marker(processed_content, command_name)

        return processed_content

    def _load_base_command(self, command_name: str) -> str:
        """Load the base command content from package resources."""
        try:
            return pkg_resources.read_text("quaestor.commands", f"{command_name}.md")
        except Exception as e:
            raise ValueError(f"Could not load command '{command_name}': {e}") from e

    def _add_configuration_marker(self, content: str, command_name: str) -> str:
        """Add a marker indicating the command has been configured."""
        marker = f"""<!-- CONFIGURED BY QUAESTOR
This command has been customized for your project.
Base command: {command_name}
Configuration: .quaestor/command-config.yaml
Override: .quaestor/commands/{command_name}.md (if exists)
-->

"""
        # Insert marker after YAML frontmatter if present
        if content.startswith("---"):
            # Find end of frontmatter
            end_marker = content.find("---", 3)
            if end_marker != -1:
                # Insert after frontmatter
                return content[: end_marker + 3] + "\n\n" + marker + content[end_marker + 3 :].lstrip()

        # Otherwise insert at beginning
        return marker + content

    def has_configuration(self, command_name: str) -> bool:
        """Check if a command has any configuration or override."""
        config = self.loader.config.get_command_config(command_name)
        override = self.loader.config.has_override(command_name)
        return bool(config) or override

    def get_configured_commands(self) -> list[str]:
        """Get list of commands that have configurations."""
        configured = []

        # Check all known commands
        for cmd_file in pkg_resources.contents("quaestor.commands"):
            if cmd_file.endswith(".md"):
                cmd_name = cmd_file[:-3]  # Remove .md
                if self.has_configuration(cmd_name):
                    configured.append(cmd_name)

        # Also check for pure overrides (commands that only exist locally)
        configured.extend(self.loader.get_available_overrides())

        return list(set(configured))  # Remove duplicates

    def preview_configuration(self, command_name: str) -> dict[str, str]:
        """Preview how configuration affects a command.

        Returns:
            Dict with 'base' and 'configured' versions of the command
        """
        base = self._load_base_command(command_name)
        configured = self.process_command(command_name)

        return {"base": base, "configured": configured, "has_changes": base != configured}
