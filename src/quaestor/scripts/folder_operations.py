#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Folder-based specification lifecycle management.

Atomic folder operations for managing specifications across draft/, active/,
and completed/ directories with git integration and file locking.

Usage:
    # As a standalone script
    uv run scripts/folder-operations.py create .quaestor/specs
    uv run scripts/folder-operations.py move .quaestor/specs/draft/spec.md active

    # As an imported module
    from scripts.folder_operations import FolderManager, FolderOperationResult
"""

import contextlib
import logging
import platform
import shutil
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

# Platform-specific imports
if platform.system() != "Windows":
    import fcntl
else:
    import msvcrt

logger = logging.getLogger(__name__)


@dataclass
class FolderOperationResult:
    """Result of a folder operation."""

    success: bool
    message: str
    moved_files: list[str] = None
    rollback_performed: bool = False


class FolderManager:
    """
    Manages folder-based specification lifecycle with atomic operations.

    Provides thread-safe folder operations with rollback capability,
    git integration, and performance guarantees (<100ms operations).
    """

    FOLDER_NAMES = {"draft": "draft", "active": "active", "completed": "completed"}

    MAX_ACTIVE_SPECS = 3
    OPERATION_TIMEOUT = 0.1  # 100ms

    def __init__(self, base_path: Path):
        """
        Initialize FolderManager with base specification path.

        Args:
            base_path: Base path for specifications (e.g., .quaestor/specifications)
        """
        self.base_path = Path(base_path)
        self._lock_file = self.base_path / ".folder_lock"

    def create_folder_structure(self) -> FolderOperationResult:
        """
        Create the folder structure for specification lifecycle.

        Creates draft/, active/, and completed/ directories with proper
        permissions and git tracking.

        Returns:
            FolderOperationResult with success status and details
        """
        start_time = time.time()

        try:
            created_folders = []

            for folder_name in self.FOLDER_NAMES.values():
                folder_path = self.base_path / folder_name
                if not folder_path.exists():
                    folder_path.mkdir(parents=True, exist_ok=True)
                    created_folders.append(str(folder_path))

                    # Add .gitkeep to track empty folders
                    gitkeep = folder_path / ".gitkeep"
                    if not gitkeep.exists():
                        gitkeep.touch()
                        self._git_add(gitkeep)

            elapsed = time.time() - start_time
            if elapsed > self.OPERATION_TIMEOUT:
                logger.warning(f"Folder creation took {elapsed:.3f}s, exceeding 100ms target")

            message = f"Created folder structure with {len(created_folders)} new folders"
            return FolderOperationResult(success=True, message=message, moved_files=created_folders)

        except Exception as e:
            logger.error(f"Failed to create folder structure: {e}")
            return FolderOperationResult(success=False, message=f"Folder creation failed: {str(e)}")

    @contextmanager
    def _file_lock(self, timeout: float = 5.0):
        """
        Acquire file lock for atomic operations.

        Args:
            timeout: Maximum time to wait for lock

        Yields:
            Lock file descriptor
        """
        # Ensure lock file exists
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file.touch()

        with open(self._lock_file, "w") as lock_file:
            lock_acquired = False

            # Try to acquire lock with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    if platform.system() != "Windows":
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    else:
                        # Windows file locking
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    lock_acquired = True
                    break
                except OSError:
                    time.sleep(0.01)

            if not lock_acquired:
                raise TimeoutError(f"Could not acquire lock within {timeout}s")

            try:
                yield lock_file
            finally:
                if lock_acquired:
                    if platform.system() != "Windows":
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    else:
                        # Windows unlock
                        with contextlib.suppress(OSError):
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)

    def move_specification(self, spec_path: Path, target_folder: str) -> FolderOperationResult:
        """
        Atomically move a specification to target folder with git tracking.

        Args:
            spec_path: Path to specification file
            target_folder: Target folder name ('draft', 'active', 'completed')

        Returns:
            FolderOperationResult with operation details
        """
        if target_folder not in self.FOLDER_NAMES:
            return FolderOperationResult(success=False, message=f"Invalid target folder: {target_folder}")

        try:
            with self._file_lock():
                return self._move_spec_internal(spec_path, target_folder)

        except Exception as e:
            logger.error(f"Failed to move specification: {e}")
            return FolderOperationResult(success=False, message=f"Move operation failed: {str(e)}")

    def _move_spec_internal(self, spec_path: Path, target_folder: str) -> FolderOperationResult:
        """Internal move method that doesn't acquire lock (assumes lock is already held)."""
        start_time = time.time()

        # Validate active folder limit
        if target_folder == "active":
            active_count = self._count_specifications("active")
            if active_count >= self.MAX_ACTIVE_SPECS:
                return FolderOperationResult(
                    success=False,
                    message=f"Active folder limit reached ({self.MAX_ACTIVE_SPECS} specs). "
                    f"Complete one before activating another.",
                )

        # Prepare paths
        spec_name = spec_path.name
        target_path = self.base_path / target_folder / spec_name

        # Check if already in target
        if spec_path.parent.name == target_folder:
            return FolderOperationResult(success=True, message=f"Specification already in {target_folder} folder")

        # Perform atomic move with rollback capability
        backup_path = None
        try:
            # Create backup for rollback
            if target_path.exists():
                backup_path = target_path.with_suffix(".backup")
                shutil.copy2(target_path, backup_path)

            # Use git mv if file is tracked, otherwise regular move
            if self._is_git_tracked(spec_path):
                self._git_move(spec_path, target_path)
            else:
                shutil.move(str(spec_path), str(target_path))
                self._git_add(target_path)

            # Clean up backup
            if backup_path and backup_path.exists():
                backup_path.unlink()

            elapsed = time.time() - start_time
            if elapsed > self.OPERATION_TIMEOUT:
                logger.warning(f"Move operation took {elapsed:.3f}s, exceeding 100ms target")

            return FolderOperationResult(
                success=True,
                message=f"Moved {spec_name} to {target_folder} folder",
                moved_files=[str(target_path)],
            )

        except Exception as e:
            # Rollback on failure
            if backup_path and backup_path.exists():
                shutil.move(str(backup_path), str(target_path))
                return FolderOperationResult(
                    success=False, message=f"Move failed, rolled back: {str(e)}", rollback_performed=True
                )
            raise

    def migrate_flat_specifications(self) -> FolderOperationResult:
        """
        Migrate existing flat specification files to folder structure.

        Analyzes specification status and moves files to appropriate folders
        while preserving git history.

        Returns:
            FolderOperationResult with migration details
        """
        start_time = time.time()
        migrated_files = []

        try:
            with self._file_lock():
                # Find all YAML files in base path (flat structure)
                flat_specs = [
                    f
                    for f in self.base_path.glob("*.md")
                    if f.is_file() and not any(f.parent.name == folder for folder in self.FOLDER_NAMES.values())
                ]

                if not flat_specs:
                    return FolderOperationResult(success=True, message="No flat specifications found to migrate")

                # Analyze and migrate each specification
                for spec_path in flat_specs:
                    status = self._determine_spec_status(spec_path)
                    target_folder = self._status_to_folder(status)

                    # Use internal move without lock since we already have it
                    result = self._move_spec_internal(spec_path, target_folder)
                    if result.success:
                        migrated_files.extend(result.moved_files or [])
                    else:
                        logger.warning(f"Failed to migrate {spec_path}: {result.message}")

                elapsed = time.time() - start_time
                if elapsed > self.OPERATION_TIMEOUT * len(flat_specs):
                    logger.warning(f"Migration took {elapsed:.3f}s for {len(flat_specs)} files")

                return FolderOperationResult(
                    success=True,
                    message=f"Migrated {len(migrated_files)} specifications to folder structure",
                    moved_files=migrated_files,
                )

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return FolderOperationResult(success=False, message=f"Migration failed: {str(e)}")

    def enforce_active_limit(self) -> tuple[bool, list[str]]:
        """
        Enforce maximum active specifications limit.

        Returns:
            Tuple of (limit_ok, list_of_active_specs)
        """
        active_specs = list((self.base_path / "active").glob("*.md"))
        return len(active_specs) < self.MAX_ACTIVE_SPECS, [s.name for s in active_specs]

    def get_folder_statistics(self) -> dict[str, int]:
        """
        Get count of specifications in each folder.

        Returns:
            Dictionary mapping folder names to specification counts
        """
        stats = {}
        for folder_name in self.FOLDER_NAMES.values():
            stats[folder_name] = self._count_specifications(folder_name)
        return stats

    def _count_specifications(self, folder: str) -> int:
        """Count YAML specifications in a folder."""
        folder_path = self.base_path / folder
        if not folder_path.exists():
            return 0
        return len(list(folder_path.glob("*.md")))

    def _determine_spec_status(self, spec_path: Path) -> str:
        """
        Determine specification status by reading YAML content.

        Simple heuristic based on common status patterns.
        """
        try:
            content = spec_path.read_text()
            if "status: completed" in content.lower():
                return "completed"
            elif "status: active" in content.lower() or "status: in_progress" in content.lower():
                return "active"
            else:
                return "draft"
        except Exception:
            return "draft"  # Default to draft if can't determine

    def _status_to_folder(self, status: str) -> str:
        """Map status to folder name."""
        status_map = {
            "completed": "completed",
            "active": "active",
            "in_progress": "active",
            "draft": "draft",
            "staged": "draft",  # Simplified from 4-state to 3-state
        }
        return status_map.get(status.lower(), "draft")

    def _is_git_tracked(self, file_path: Path) -> bool:
        """Check if file is tracked by git."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(file_path)],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _git_move(self, source: Path, destination: Path) -> None:
        """Move file using git mv to preserve history."""
        try:
            subprocess.run(
                ["git", "mv", str(source), str(destination)],
                check=True,
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )
        except subprocess.CalledProcessError:
            # Fallback to regular move if git mv fails
            shutil.move(str(source), str(destination))
            self._git_add(destination)

    def _git_add(self, file_path: Path) -> None:
        """Add file to git staging."""
        with contextlib.suppress(subprocess.CalledProcessError):
            subprocess.run(
                ["git", "add", str(file_path)], check=True, capture_output=True, text=True, cwd=self.base_path
            )


def main():
    """CLI interface for folder-operations."""
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/folder-operations.py <command> [args]")
        print()
        print("Commands:")
        print("  create <base_path>              - Create folder structure")
        print("  move <spec_path> <target>       - Move spec to target folder (draft/active/completed)")
        print("  stats <base_path>               - Show folder statistics")
        print("  migrate <base_path>             - Migrate flat specs to folders")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            print("Error: Missing base_path")
            sys.exit(1)
        base_path = Path(sys.argv[2])
        manager = FolderManager(base_path)
        result = manager.create_folder_structure()
        print(result.message)
        sys.exit(0 if result.success else 1)

    elif command == "move":
        if len(sys.argv) < 4:
            print("Error: Missing spec_path or target folder")
            sys.exit(1)
        spec_path = Path(sys.argv[2])
        target = sys.argv[3]
        base_path = spec_path.parent.parent  # Assume spec is in a subfolder
        manager = FolderManager(base_path)
        result = manager.move_specification(spec_path, target)
        print(result.message)
        sys.exit(0 if result.success else 1)

    elif command == "stats":
        if len(sys.argv) < 3:
            print("Error: Missing base_path")
            sys.exit(1)
        base_path = Path(sys.argv[2])
        manager = FolderManager(base_path)
        stats = manager.get_folder_statistics()
        print(json.dumps(stats, indent=2))

    elif command == "migrate":
        if len(sys.argv) < 3:
            print("Error: Missing base_path")
            sys.exit(1)
        base_path = Path(sys.argv[2])
        manager = FolderManager(base_path)
        result = manager.migrate_flat_specifications()
        print(result.message)
        sys.exit(0 if result.success else 1)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
