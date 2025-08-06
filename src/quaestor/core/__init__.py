"""Core business logic for Quaestor.

This module contains the fundamental business logic components:
- Project analysis and metadata management
- Template processing and generation
- Configuration management
"""

from quaestor.core.config_manager import ConfigManager, get_config_manager
from quaestor.core.project_analysis import ProjectAnalyzer
from quaestor.core.project_metadata import (
    FileManifest,
    FileType,
    categorize_file,
    extract_version_from_content,
)
from quaestor.core.template_engine import get_project_data, process_template

__all__ = [
    "ConfigManager",
    "get_config_manager",
    "ProjectAnalyzer",
    "FileManifest",
    "FileType",
    "categorize_file",
    "extract_version_from_content",
    "get_project_data",
    "process_template",
]
