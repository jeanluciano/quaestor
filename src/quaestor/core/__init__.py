"""Shared utilities for Quaestor."""

from quaestor.core.file_utils import (
    clean_empty_directories,
    copy_file_with_processing,
    create_directory,
    find_project_root,
    get_file_size_summary,
    safe_read_text,
    safe_write_text,
    update_gitignore,
)
from quaestor.core.project_detection import (
    detect_project_type,
    get_project_complexity_indicators,
    get_project_files_by_type,
    is_test_file,
)

# YAML utils removed - using Markdown specs now

__all__ = [
    # Project detection
    "detect_project_type",
    "get_project_complexity_indicators",
    "get_project_files_by_type",
    "is_test_file",
    # File utilities
    "create_directory",
    "safe_write_text",
    "safe_read_text",
    "update_gitignore",
    "copy_file_with_processing",
    "find_project_root",
    "clean_empty_directories",
    "get_file_size_summary",
]
