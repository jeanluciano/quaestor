"""Core business logic for Quaestor.

This module contains the fundamental business logic components:
- Project analysis and metadata management
- Template processing and generation
- Configuration management
"""

from quaestor.core.configuration import QuaestorConfig, get_project_config
from quaestor.core.project_analysis import ProjectAnalyzer
from quaestor.core.project_metadata import (
    FileManifest,
    FileType,
    categorize_file,
    extract_version_from_content,
)
from quaestor.core.template_engine import get_project_data, process_template
from quaestor.core.validation_engine import RuleEngine

__all__ = [
    "QuaestorConfig",
    "get_project_config",
    "ProjectAnalyzer",
    "FileManifest",
    "FileType",
    "categorize_file",
    "extract_version_from_content",
    "get_project_data",
    "process_template",
    "RuleEngine",
]
