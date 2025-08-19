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
from quaestor.core.yaml_utils import (
    YAMLConfig,
    convert_json_to_yaml,
    extract_yaml_section,
    load_yaml,
    merge_yaml_configs,
    save_yaml,
    update_yaml_section,
    validate_yaml_schema,
)

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
    # YAML utilities
    "load_yaml",
    "save_yaml",
    "validate_yaml_schema",
    "merge_yaml_configs",
    "extract_yaml_section",
    "update_yaml_section",
    "convert_json_to_yaml",
    "YAMLConfig",
]
