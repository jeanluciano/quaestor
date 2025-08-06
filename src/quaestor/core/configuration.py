# This file has been removed as part of the backward compatibility cleanup.
# Use ConfigManager directly instead of the legacy QuaestorConfig class.
# See config_manager.py for the modern configuration system.

# For migration guidance:
# - Replace QuaestorConfig with ConfigManager
# - Replace get_project_config() with get_config_manager()
# - Use ConfigManager methods directly instead of compatibility wrappers

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config_manager import ConfigManager


def QuaestorConfig(*args, **kwargs):
    """Deprecated: QuaestorConfig has been removed.

    Use ConfigManager from .config_manager instead.

    Migration guide:
    - QuaestorConfig(project_root) → ConfigManager(project_root)
    - get_project_config() → get_config_manager()
    """
    raise ImportError(
        "QuaestorConfig has been removed. Use ConfigManager from .config_manager instead.\n"
        "Migration: QuaestorConfig(project_root) → ConfigManager(project_root)"
    )


def get_project_config(project_root: Path | None = None) -> "ConfigManager":
    """Deprecated: get_project_config has been removed.

    Use get_config_manager() from .config_manager instead.
    """
    raise ImportError(
        "get_project_config has been removed. Use get_config_manager from .config_manager instead.\n"
        "Migration: get_project_config() → get_config_manager()"
    )
