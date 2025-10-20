"""UV scripts for Quaestor utilities.

These are self-contained UV scripts that can be run standalone or imported as modules.

Hook Scripts (executable via python3 -m):
- hook_session_context_loader: Loads active specifications at session start
- hook_spec_validator: Validates specifications when written

Utility Scripts:
- file_operations: File utilities
- project_detector: Project type detection
- yaml_utils: YAML operations
- folder_operations: Folder lifecycle management
"""

# Re-export all functions from scripts for easy importing
from .file_operations import (
    clean_empty_directories,
    copy_file_with_processing,
    create_directory,
    find_project_root,
    get_file_size_summary,
    safe_read_text,
    safe_write_text,
    update_gitignore,
)
from .project_detector import (
    detect_project_type,
    get_project_complexity_indicators,
    get_project_files_by_type,
    is_test_file,
)
from .yaml_utils import load_yaml, merge_yaml_configs, save_yaml

__all__ = [
    # File operations
    "clean_empty_directories",
    "copy_file_with_processing",
    "create_directory",
    "find_project_root",
    "get_file_size_summary",
    "safe_read_text",
    "safe_write_text",
    "update_gitignore",
    # Project detection
    "detect_project_type",
    "get_project_complexity_indicators",
    "get_project_files_by_type",
    "is_test_file",
    # YAML utilities
    "load_yaml",
    "merge_yaml_configs",
    "save_yaml",
]
