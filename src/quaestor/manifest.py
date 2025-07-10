"""File manifest management for intelligent updates.

This module tracks installed files, their versions, and modification status
to enable smart updates that preserve user customizations.
"""

import hashlib
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .constants import SYSTEM_FILES, USER_EDITABLE_FILES, VERSION_PATTERNS


class FileType(Enum):
    """Categories of files for update logic."""

    SYSTEM = "system"  # Always update (e.g., CRITICAL_RULES.md)
    USER_EDITABLE = "user-editable"  # Never overwrite if exists (e.g., ARCHITECTURE.md)
    COMMAND = "command"  # Only add new ones
    TEMPLATE = "template"  # Can update tagged sections


class FileManifest:
    """Manages the manifest of installed files."""

    def __init__(self, manifest_path: Path):
        """Initialize manifest manager.

        Args:
            manifest_path: Path to manifest.json file
        """
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        """Load manifest from disk or create new one."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                # Corrupted manifest, start fresh
                return self._create_empty_manifest()
        return self._create_empty_manifest()

    def _create_empty_manifest(self) -> dict[str, Any]:
        """Create an empty manifest structure."""
        return {
            "version": "1.0",
            "quaestor_version": None,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "files": {},
        }

    def save(self):
        """Save manifest to disk."""
        self.manifest["last_updated"] = datetime.now().isoformat()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex string of checksum
        """
        if not file_path.exists():
            return ""

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def track_file(
        self,
        file_path: Path,
        file_type: FileType,
        version: str,
        relative_to: Path | None = None,
    ):
        """Track a file in the manifest.

        Args:
            file_path: Path to the file
            file_type: Type of file for update logic
            version: Version of the file
            relative_to: Base path to make file_path relative to
        """
        key = str(file_path.relative_to(relative_to)) if relative_to else str(file_path)

        checksum = self.calculate_checksum(file_path)

        self.manifest["files"][key] = {
            "type": file_type.value,
            "version": version,
            "installed_at": datetime.now().isoformat(),
            "original_checksum": checksum,
            "current_checksum": checksum,
            "user_modified": False,
        }

    def update_file_status(self, file_key: str, file_path: Path):
        """Update the status of a tracked file.

        Args:
            file_key: Key in manifest (relative path)
            file_path: Actual path to file
        """
        if file_key not in self.manifest["files"]:
            return

        file_info = self.manifest["files"][file_key]
        current_checksum = self.calculate_checksum(file_path)

        file_info["current_checksum"] = current_checksum
        file_info["user_modified"] = current_checksum != file_info["original_checksum"]

    def is_file_modified(self, file_key: str) -> bool:
        """Check if a file has been modified by the user.

        Args:
            file_key: Key in manifest

        Returns:
            True if file has been modified
        """
        if file_key not in self.manifest["files"]:
            return False
        return self.manifest["files"][file_key].get("user_modified", False)

    def get_file_info(self, file_key: str) -> dict[str, Any] | None:
        """Get information about a tracked file.

        Args:
            file_key: Key in manifest

        Returns:
            File info dict or None if not tracked
        """
        return self.manifest["files"].get(file_key)

    def get_file_type(self, file_key: str) -> FileType | None:
        """Get the type of a tracked file.

        Args:
            file_key: Key in manifest

        Returns:
            FileType or None if not tracked
        """
        info = self.get_file_info(file_key)
        if info:
            return FileType(info["type"])
        return None

    def set_quaestor_version(self, version: str):
        """Set the quaestor version in manifest.

        Args:
            version: Quaestor version string
        """
        self.manifest["quaestor_version"] = version

    def get_quaestor_version(self) -> str | None:
        """Get the quaestor version from manifest.

        Returns:
            Version string or None
        """
        return self.manifest.get("quaestor_version")

    def get_all_files(self) -> dict[str, dict[str, Any]]:
        """Get all tracked files.

        Returns:
            Dict of file_key -> file_info
        """
        return self.manifest.get("files", {})

    def remove_file(self, file_key: str):
        """Remove a file from tracking.

        Args:
            file_key: Key in manifest
        """
        self.manifest["files"].pop(file_key, None)

    def update_file_version(self, file_key: str, new_version: str, new_checksum: str):
        """Update a file's version and checksum after an update.

        Args:
            file_key: Key in manifest
            new_version: New version string
            new_checksum: New checksum after update
        """
        if file_key in self.manifest["files"]:
            file_info = self.manifest["files"][file_key]
            file_info["version"] = new_version
            file_info["original_checksum"] = new_checksum
            file_info["current_checksum"] = new_checksum
            file_info["user_modified"] = False
            file_info["last_updated"] = datetime.now().isoformat()


def extract_version_from_content(content: str) -> str | None:
    """Extract version from file content.

    Looks for patterns like:
    - <!-- QUAESTOR:version:1.0 -->
    - <!-- META:version:1.0 -->

    Args:
        content: File content

    Returns:
        Version string or None
    """
    import re

    patterns = VERSION_PATTERNS

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)

    return None


def categorize_file(file_path: Path, relative_path: str) -> FileType:
    """Categorize a file based on its path and name.

    Args:
        file_path: Full path to file
        relative_path: Relative path from project root

    Returns:
        FileType category
    """
    # Command files
    if "commands/" in relative_path or relative_path.endswith((".md",)) and "task" in relative_path:
        return FileType.COMMAND

    # System files (always update)
    if any(relative_path.endswith(f) for f in SYSTEM_FILES):
        return FileType.SYSTEM

    # User-editable files (never auto-overwrite)
    if any(relative_path.endswith(f) for f in USER_EDITABLE_FILES):
        return FileType.USER_EDITABLE

    # Default to template
    return FileType.TEMPLATE
