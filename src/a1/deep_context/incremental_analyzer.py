"""Incremental analysis for efficient code updates.

This module provides incremental analysis capabilities to efficiently
update the symbol table and index when files change, without re-analyzing
the entire codebase.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from a1.core.event_bus import EventBus
from a1.core.events import SystemEvent

from .code_index import CodeNavigationIndex


@dataclass
class FileMetadata:
    """Metadata for tracking file changes."""

    path: Path
    size: int
    mtime: float
    checksum: str
    dependencies: set[str] = field(default_factory=set)
    dependents: set[str] = field(default_factory=set)


@dataclass
class AnalysisUpdate:
    """Result of an incremental analysis."""

    updated_files: list[Path]
    removed_files: list[Path]
    affected_files: list[Path]
    duration_ms: float


class IncrementalAnalyzer:
    """Handles incremental updates to code analysis."""

    def __init__(self, index: CodeNavigationIndex, event_bus: EventBus | None = None):
        """Initialize the incremental analyzer.

        Args:
            index: The code navigation index to update
            event_bus: Optional event bus for update events
        """
        self.index = index
        self.event_bus = event_bus
        self._file_metadata: dict[Path, FileMetadata] = {}
        self._dependency_graph: dict[str, set[str]] = {}
        self._cache_file: Path | None = None

    def set_cache_file(self, cache_file: Path) -> None:
        """Set the cache file for persistent metadata storage.

        Args:
            cache_file: Path to store metadata cache
        """
        self._cache_file = cache_file
        self._load_cache()

    def analyze_changes(self, root_path: Path) -> AnalysisUpdate:
        """Analyze what files have changed since last analysis.

        Args:
            root_path: Root directory to analyze

        Returns:
            AnalysisUpdate with information about changes
        """
        start_time = time.time()

        # Find all Python files
        current_files = set(root_path.rglob("*.py"))
        known_files = set(self._file_metadata.keys())

        # Categorize changes
        added_files = current_files - known_files
        removed_files = known_files - current_files
        potentially_modified = current_files & known_files

        # Check for actual modifications
        modified_files = []
        for file_path in potentially_modified:
            if self._has_file_changed(file_path):
                modified_files.append(file_path)

        # Find affected files (dependents of modified files)
        affected_files = self._find_affected_files(list(added_files) + modified_files + list(removed_files))

        duration_ms = (time.time() - start_time) * 1000

        return AnalysisUpdate(
            updated_files=list(added_files) + modified_files,
            removed_files=list(removed_files),
            affected_files=affected_files,
            duration_ms=duration_ms,
        )

    def update_incrementally(self, root_path: Path, base_module: str = "") -> AnalysisUpdate:
        """Perform incremental update of the analysis.

        Args:
            root_path: Root directory to analyze
            base_module: Base module name

        Returns:
            AnalysisUpdate with results
        """
        # Analyze changes
        update = self.analyze_changes(root_path)

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="incremental_update_started",
                    data={
                        "updated_files": len(update.updated_files),
                        "removed_files": len(update.removed_files),
                        "affected_files": len(update.affected_files),
                    },
                )
            )

        # Remove symbols from deleted files
        for file_path in update.removed_files:
            self._remove_file_symbols(file_path)

        # Update modified and new files
        for file_path in update.updated_files:
            self._update_file(file_path, root_path, base_module)

        # Re-analyze affected files (to update references)
        for file_path in update.affected_files:
            if file_path not in update.updated_files:
                self._update_file(file_path, root_path, base_module)

        # Update dependency graph
        self._rebuild_dependency_graph()

        # Save cache
        self._save_cache()

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="incremental_update_completed",
                    data={"duration_ms": update.duration_ms, "total_symbols": len(self.index.symbol_table._symbols)},
                )
            )

        return update

    def _has_file_changed(self, file_path: Path) -> bool:
        """Check if a file has changed since last analysis.

        Args:
            file_path: Path to check

        Returns:
            True if file has changed
        """
        if file_path not in self._file_metadata:
            return True

        try:
            stat = file_path.stat()
            metadata = self._file_metadata[file_path]

            # Quick check: size and mtime
            if stat.st_size != metadata.size or stat.st_mtime > metadata.mtime:
                # Verify with checksum
                current_checksum = self._calculate_checksum(file_path)
                return current_checksum != metadata.checksum

            return False

        except OSError:
            # File might have been deleted
            return True

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            Checksum string
        """
        hasher = hashlib.md5()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return ""

    def _find_affected_files(self, changed_files: list[Path]) -> list[Path]:
        """Find files affected by changes.

        Args:
            changed_files: Files that have changed

        Returns:
            List of affected files
        """
        affected = set()

        for file_path in changed_files:
            if file_path in self._file_metadata:
                # Add all files that depend on this file
                metadata = self._file_metadata[file_path]
                affected.update(Path(dep) for dep in metadata.dependents if Path(dep) != file_path)

        return list(affected)

    def _update_file(self, file_path: Path, root_path: Path, base_module: str) -> None:
        """Update analysis for a single file.

        Args:
            file_path: File to update
            root_path: Root directory
            base_module: Base module name
        """
        # Remove old symbols first
        self._remove_file_symbols(file_path)

        # Calculate module name
        relative_path = file_path.relative_to(root_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]

        if base_module:
            module_name = f"{base_module}.{'.'.join(module_parts)}" if module_parts else base_module
        else:
            module_name = ".".join(module_parts) if module_parts else "root"

        try:
            # Parse and add to symbol table
            self.index.builder.process_file(file_path, module_name)

            # Update metadata
            stat = file_path.stat()
            self._file_metadata[file_path] = FileMetadata(
                path=file_path, size=stat.st_size, mtime=stat.st_mtime, checksum=self._calculate_checksum(file_path)
            )

            # Extract dependencies
            module_info = self.index.analyzer.analyze_module(file_path)
            dependencies = self.index.analyzer.parser.extract_dependencies(module_info)
            self._file_metadata[file_path].dependencies = dependencies

        except Exception as e:
            if self.event_bus:
                self.event_bus.emit(
                    SystemEvent(type="incremental_update_error", data={"file": str(file_path), "error": str(e)})
                )

    def _remove_file_symbols(self, file_path: Path) -> None:
        """Remove all symbols from a file.

        Args:
            file_path: File whose symbols to remove
        """
        symbols = self.index.symbol_table.get_symbols_in_file(file_path)

        for symbol in symbols:
            # Remove from symbol table
            if symbol.qualified_name in self.index.symbol_table._symbols:
                del self.index.symbol_table._symbols[symbol.qualified_name]

            # Remove from indexes
            simple_name = symbol.name.split(".")[-1]
            if simple_name in self.index.symbol_table._name_index:
                self.index.symbol_table._name_index[simple_name].discard(symbol.qualified_name)

        # Remove from file index
        if file_path in self.index.symbol_table._file_symbols:
            del self.index.symbol_table._file_symbols[file_path]

        # Remove metadata
        if file_path in self._file_metadata:
            del self._file_metadata[file_path]

    def _rebuild_dependency_graph(self) -> None:
        """Rebuild the dependency graph from metadata."""
        self._dependency_graph.clear()

        # Build forward dependencies
        for file_path, metadata in self._file_metadata.items():
            file_str = str(file_path)
            self._dependency_graph[file_str] = set(metadata.dependencies)

        # Build reverse dependencies (dependents)
        for file_path, metadata in self._file_metadata.items():
            file_str = str(file_path)
            for dep in metadata.dependencies:
                # Find files that provide this dependency
                for other_path, other_metadata in self._file_metadata.items():
                    if other_path == file_path:
                        continue

                    # Simple check: does the file's module name match the dependency?
                    # This is a simplification - real implementation would use symbol table
                    other_module = self._path_to_module_name(other_path)
                    if other_module and dep.startswith(other_module):
                        other_metadata.dependents.add(file_str)

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to module name (simplified)."""
        parts = file_path.stem.split("/")
        return ".".join(parts)

    def _load_cache(self) -> None:
        """Load metadata cache from disk."""
        if not self._cache_file or not self._cache_file.exists():
            return

        try:
            with open(self._cache_file) as f:
                data = json.load(f)

            for file_str, metadata_dict in data.get("file_metadata", {}).items():
                file_path = Path(file_str)
                self._file_metadata[file_path] = FileMetadata(
                    path=file_path,
                    size=metadata_dict["size"],
                    mtime=metadata_dict["mtime"],
                    checksum=metadata_dict["checksum"],
                    dependencies=set(metadata_dict.get("dependencies", [])),
                    dependents=set(metadata_dict.get("dependents", [])),
                )

        except Exception as e:
            # Log error but continue - cache is not critical
            if self.event_bus:
                self.event_bus.emit(SystemEvent(type="cache_load_error", data={"error": str(e)}))

    def _save_cache(self) -> None:
        """Save metadata cache to disk."""
        if not self._cache_file:
            return

        try:
            data = {
                "file_metadata": {
                    str(path): {
                        "size": metadata.size,
                        "mtime": metadata.mtime,
                        "checksum": metadata.checksum,
                        "dependencies": list(metadata.dependencies),
                        "dependents": list(metadata.dependents),
                    }
                    for path, metadata in self._file_metadata.items()
                }
            }

            self._cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self._cache_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            # Log error but continue
            if self.event_bus:
                self.event_bus.emit(SystemEvent(type="cache_save_error", data={"error": str(e)}))

    def watch_for_changes(self, root_path: Path, callback=None, interval: float = 1.0) -> None:
        """Watch for file changes and trigger updates.

        Args:
            root_path: Root directory to watch
            callback: Optional callback for updates
            interval: Check interval in seconds
        """
        # This would integrate with file system watchers
        # For now, it's a placeholder for the interface
        raise NotImplementedError("File watching not yet implemented")
