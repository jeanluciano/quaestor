"""Unified configuration management for Quaestor."""

from pathlib import Path
from typing import Any

from .utils.project_detection import detect_project_type
from .utils.yaml_utils import YAMLConfig, load_yaml


class QuaestorConfig:
    """Unified configuration manager for Quaestor projects."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.quaestor_dir = self.project_root / ".quaestor"

        # Core configuration files
        self.main_config = YAMLConfig(self.quaestor_dir / "config.yaml", self._get_default_config())

        self.command_config = YAMLConfig(self.quaestor_dir / "command-config.yaml", self._get_default_command_config())

        # Load language-specific configurations
        self._language_configs = None
        self._project_type = None

    def _get_default_config(self) -> dict[str, Any]:
        """Get default Quaestor configuration."""
        return {
            "version": "1.0",
            "mode": "personal",  # personal or team
            "hooks": {
                "enabled": True,
                "enforcement": {"enabled": True, "strict_mode": False},
                "automation": {"enabled": True, "auto_commit": False},
                "intelligence": {"enabled": True, "context_refresh": True},
            },
            "quality": {"run_on_commit": True, "block_on_fail": False, "custom_commands": {}},
            "workflow": {"enforce_research": True, "min_research_files": 3, "research_timeout_hours": 2},
        }

    def _get_default_command_config(self) -> dict[str, Any]:
        """Get default command configuration."""
        return {"version": "1.0", "commands": {}, "overrides": {}}

    def _load_language_configs(self) -> dict[str, Any]:
        """Load language-specific configurations."""
        if self._language_configs is not None:
            return self._language_configs

        # Load from templates/config/languages.yaml
        languages_path = Path(__file__).parent / "templates" / "config" / "languages.yaml"

        self._language_configs = load_yaml(languages_path, {})
        return self._language_configs

    @property
    def project_type(self) -> str:
        """Get detected project type."""
        if self._project_type is None:
            self._project_type = detect_project_type(self.project_root)
        return self._project_type

    def get_language_config(self, language: str | None = None) -> dict[str, Any]:
        """Get language-specific configuration."""
        language = language or self.project_type
        language_configs = self._load_language_configs()
        return language_configs.get(language, {})

    def get_quality_commands(self) -> dict[str, str]:
        """Get quality check commands for the current project."""
        # Get from language config first
        lang_config = self.get_language_config()
        quality_commands = {}

        if "lint_command" in lang_config:
            quality_commands["lint"] = lang_config["lint_command"]
        if "format_command" in lang_config:
            quality_commands["format"] = lang_config["format_command"]
        if "test_command" in lang_config:
            quality_commands["test"] = lang_config["test_command"]

        # Override with custom commands from main config
        custom_commands = self.main_config.get("quality.custom_commands", {})
        quality_commands.update(custom_commands)

        return quality_commands

    def get_hook_config(self, hook_category: str) -> dict[str, Any]:
        """Get configuration for a specific hook category."""
        hooks_config = self.main_config.get("hooks", {})
        return hooks_config.get(hook_category, {})

    def is_hook_enabled(self, hook_name: str, category: str = "enforcement") -> bool:
        """Check if a specific hook is enabled."""
        # Check global hooks enabled first
        if not self.main_config.get("hooks.enabled", True):
            return False

        # Check category enabled
        category_config = self.get_hook_config(category)
        if not category_config.get("enabled", True):
            return False

        # Check specific hook if configured
        hook_config = category_config.get("hooks", {}).get(hook_name, {})
        return hook_config.get("enabled", True)

    def get_command_config(self, command_name: str) -> dict[str, Any]:
        """Get configuration for a specific command."""
        commands_config = self.command_config.get("commands", {})
        return commands_config.get(command_name, {})

    def has_command_override(self, command_name: str) -> bool:
        """Check if a command has a local override file."""
        override_path = self.quaestor_dir / "commands" / f"{command_name}.md"
        return override_path.exists()

    def get_command_override_path(self, command_name: str) -> Path | None:
        """Get path to command override file if it exists."""
        override_path = self.quaestor_dir / "commands" / f"{command_name}.md"
        return override_path if override_path.exists() else None

    def get_workflow_config(self) -> dict[str, Any]:
        """Get workflow-related configuration."""
        return self.main_config.get("workflow", {})

    def should_enforce_research(self) -> bool:
        """Check if research enforcement is enabled."""
        return self.get_workflow_config().get("enforce_research", True)

    def get_min_research_files(self) -> int:
        """Get minimum number of files to examine during research."""
        return self.get_workflow_config().get("min_research_files", 3)

    def get_research_timeout_hours(self) -> int:
        """Get research timeout in hours."""
        return self.get_workflow_config().get("research_timeout_hours", 2)

    def update_config(self, updates: dict[str, Any]) -> bool:
        """Update main configuration with new values."""
        try:
            self.main_config.update(updates)
            return self.main_config.save()
        except Exception:
            return False

    def update_command_config(self, command_name: str, config: dict[str, Any]) -> bool:
        """Update configuration for a specific command."""
        try:
            current_commands = self.command_config.get("commands", {})
            current_commands[command_name] = config
            self.command_config.set("commands", current_commands)
            return self.command_config.save()
        except Exception:
            return False

    def initialize_default_configs(self) -> bool:
        """Initialize default configuration files if they don't exist."""
        try:
            # Ensure .quaestor directory exists
            self.quaestor_dir.mkdir(parents=True, exist_ok=True)

            # Initialize main config
            if not self.main_config.config_path.exists():
                self.main_config.save()

            # Initialize command config
            if not self.command_config.config_path.exists():
                self.command_config.save()

            return True

        except Exception:
            return False

    def get_merged_config(self) -> dict[str, Any]:
        """Get a merged view of all configurations."""
        base_config = self.main_config.load()

        # Add language-specific data
        lang_config = self.get_language_config()
        if lang_config:
            base_config["language"] = lang_config
            base_config["project_type"] = self.project_type

        # Add command configurations
        base_config["commands"] = self.command_config.load()

        return base_config

    def export_config(self, output_path: Path) -> bool:
        """Export merged configuration to a file."""
        try:
            from .utils.yaml_utils import save_yaml

            merged_config = self.get_merged_config()
            return save_yaml(output_path, merged_config)
        except Exception:
            return False

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration files."""
        errors = []

        try:
            # Validate main config
            main_config = self.main_config.load()
            if "version" not in main_config:
                errors.append("Main config missing version field")

            # Validate command config
            cmd_config = self.command_config.load()
            if "version" not in cmd_config:
                errors.append("Command config missing version field")

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Config validation error: {e}")
            return False, errors


def get_project_config(project_root: Path | None = None) -> QuaestorConfig:
    """Get QuaestorConfig instance for a project.

    Args:
        project_root: Project root directory (auto-detected if None)

    Returns:
        QuaestorConfig instance
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

    return QuaestorConfig(project_root)
