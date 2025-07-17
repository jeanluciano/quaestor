"""Basic File-Based Persistence - Simplified storage for A1

Provides essential file-based storage functionality extracted from V2.0's complex system:
- JSON/YAML file operations with atomic writes
- Simple data models for common storage needs
- Centralized storage management
- Error handling and recovery
- In-memory backend for testing

Replaces V2.0's 5,583+ line database system with ~600 focused lines.
"""

import contextlib
import json
import os
import shutil
import tempfile
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import yaml

from ..core.event_bus import EventBus
from ..core.events import SystemEvent

# Type variable for generic storage operations
T = TypeVar("T")


# Exceptions
class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class FileNotFoundError(StorageError):
    """Raised when a requested file doesn't exist."""

    pass


class CorruptedDataError(StorageError):
    """Raised when stored data is corrupted or invalid."""

    pass


class LockError(StorageError):
    """Raised when file locking fails."""

    pass


# Data Models
@dataclass
class ProjectManifest:
    """Simple project manifest data model."""

    project_path: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    file_checksums: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = time.time()


@dataclass
class PatternData:
    """Storage model for learned patterns."""

    pattern_id: str
    pattern_type: str
    frequency: int = 1
    confidence: float = 0.0
    last_seen: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)

    def increment_frequency(self) -> None:
        """Increment pattern frequency and update timestamp."""
        self.frequency += 1
        self.last_seen = time.time()


@dataclass
class ConfigurationData:
    """Storage model for configuration settings."""

    version: str = "1.0"
    settings: dict[str, Any] = field(default_factory=dict)
    feature_flags: dict[str, bool] = field(default_factory=dict)
    overrides: dict[str, Any] = field(default_factory=dict)
    updated_at: float = field(default_factory=time.time)


@dataclass
class AdaptationData:
    """Storage model for AI adaptations."""

    adaptation_id: str
    adaptation_type: str
    trigger: str
    response: str
    success_count: int = 0
    failure_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


# Storage Interface
class StorageBackend(ABC):
    """Abstract interface for storage operations."""

    @abstractmethod
    def read(self, path: str) -> dict[str, Any]:
        """Read data from storage."""
        pass

    @abstractmethod
    def write(self, path: str, data: dict[str, Any]) -> None:
        """Write data to storage."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists in storage."""
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """Delete data at path."""
        pass

    @abstractmethod
    def list_files(self, directory: str) -> list[str]:
        """List files in directory."""
        pass


# File-based Backend
class FileStorageBackend(StorageBackend):
    """File-based storage backend with atomic operations."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

    def read(self, path: str) -> dict[str, Any]:
        """Read JSON or YAML file."""
        file_path = self.root_path / path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            content = file_path.read_text()

            if path.endswith(".yaml") or path.endswith(".yml"):
                return yaml.safe_load(content) or {}
            else:  # Default to JSON
                return json.loads(content)

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise CorruptedDataError(f"Failed to parse {path}: {e}") from e
        except Exception as e:
            raise StorageError(f"Failed to read {path}: {e}") from e

    def write(self, path: str, data: dict[str, Any]) -> None:
        """Write data atomically to JSON or YAML file."""
        file_path = self.root_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file, then rename
        with tempfile.NamedTemporaryFile(mode="w", dir=file_path.parent, delete=False, suffix=".tmp") as tmp_file:
            try:
                if path.endswith(".yaml") or path.endswith(".yml"):
                    yaml.dump(data, tmp_file, default_flow_style=False)
                else:  # Default to JSON
                    json.dump(data, tmp_file, indent=2)

                tmp_file.flush()
                os.fsync(tmp_file.fileno())

                # Atomic rename
                shutil.move(tmp_file.name, str(file_path))

            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                raise StorageError(f"Failed to write {path}: {e}") from e

    def exists(self, path: str) -> bool:
        """Check if file exists."""
        return (self.root_path / path).exists()

    def delete(self, path: str) -> None:
        """Delete file."""
        file_path = self.root_path / path
        if file_path.exists():
            file_path.unlink()

    def list_files(self, directory: str) -> list[str]:
        """List files in directory."""
        dir_path = self.root_path / directory
        if not dir_path.exists():
            return []

        return [str(p.relative_to(self.root_path)) for p in dir_path.iterdir() if p.is_file()]


# In-Memory Backend for Testing
class MemoryStorageBackend(StorageBackend):
    """In-memory storage backend for testing."""

    def __init__(self):
        self.data: dict[str, dict[str, Any]] = {}

    def read(self, path: str) -> dict[str, Any]:
        """Read from memory."""
        if path not in self.data:
            raise FileNotFoundError(f"File not found: {path}")
        # Deep copy to ensure proper isolation
        import copy

        return copy.deepcopy(self.data[path])

    def write(self, path: str, data: dict[str, Any]) -> None:
        """Write to memory."""
        # Deep copy to ensure proper isolation
        import copy

        self.data[path] = copy.deepcopy(data)

    def exists(self, path: str) -> bool:
        """Check if exists in memory."""
        return path in self.data

    def delete(self, path: str) -> None:
        """Delete from memory."""
        self.data.pop(path, None)

    def list_files(self, directory: str) -> list[str]:
        """List files in directory."""
        prefix = directory.rstrip("/") + "/"
        return [path for path in self.data if path.startswith(prefix) and "/" not in path[len(prefix) :]]


# Main Persistence Manager
class SimplePersistenceManager:
    """Centralized persistence management for A1."""

    def __init__(self, root_path: Path, backend: StorageBackend | None = None, event_bus: EventBus | None = None):
        self.root_path = root_path
        self.backend = backend or FileStorageBackend(root_path)
        self.event_bus = event_bus

        # Cache for frequently accessed data
        self._cache: dict[str, tuple[Any, float]] = {}
        self._cache_ttl = 300  # 5 minutes

    # Generic load/save methods
    def load(self, path: str, model_class: type[T]) -> T:
        """Load data and deserialize to model class."""
        # Check cache first
        cached = self._get_cached(path)
        if cached:
            return cached

        try:
            data = self.backend.read(path)
            instance = model_class(**data)

            # Cache the result
            self._set_cache(path, instance)

            # Emit event
            self._emit_event("storage_load", {"path": path, "type": model_class.__name__})

            return instance

        except Exception as e:
            self._emit_event("storage_error", {"path": path, "error": str(e)})
            raise

    def save(self, path: str, instance: Any) -> None:
        """Serialize model instance and save."""
        try:
            # Convert to dict
            if hasattr(instance, "__dict__"):
                data = asdict(instance) if hasattr(instance, "__dataclass_fields__") else instance.__dict__
            else:
                data = instance

            # Save to backend
            self.backend.write(path, data)

            # Update cache
            self._set_cache(path, instance)

            # Emit event
            self._emit_event("storage_save", {"path": path, "type": type(instance).__name__})

        except Exception as e:
            self._emit_event("storage_error", {"path": path, "error": str(e)})
            raise

    # Convenience methods for common operations
    def load_manifest(self) -> ProjectManifest | None:
        """Load project manifest."""
        try:
            return self.load("manifest.json", ProjectManifest)
        except FileNotFoundError:
            return None

    def save_manifest(self, manifest: ProjectManifest) -> None:
        """Save project manifest."""
        manifest.update_timestamp()
        self.save("manifest.json", manifest)

    def load_patterns(self) -> list[PatternData]:
        """Load all patterns."""
        pattern_files = self.backend.list_files("patterns")
        patterns = []

        for file_path in pattern_files:
            if file_path.endswith(".json"):
                try:
                    pattern = self.load(file_path, PatternData)
                    patterns.append(pattern)
                except Exception:
                    # Skip corrupted patterns
                    continue

        return patterns

    def save_pattern(self, pattern: PatternData) -> None:
        """Save a pattern."""
        path = f"patterns/{pattern.pattern_id}.json"
        self.save(path, pattern)

    def load_config(self) -> ConfigurationData | None:
        """Load configuration."""
        try:
            return self.load("config.json", ConfigurationData)
        except FileNotFoundError:
            return None

    def save_config(self, config: ConfigurationData) -> None:
        """Save configuration."""
        config.updated_at = time.time()
        self.save("config.json", config)

    def load_adaptations(self) -> list[AdaptationData]:
        """Load all adaptations."""
        adaptation_files = self.backend.list_files("adaptations")
        adaptations = []

        for file_path in adaptation_files:
            if file_path.endswith(".json"):
                try:
                    adaptation = self.load(file_path, AdaptationData)
                    adaptations.append(adaptation)
                except Exception:
                    # Skip corrupted adaptations
                    continue

        return adaptations

    def save_adaptation(self, adaptation: AdaptationData) -> None:
        """Save an adaptation."""
        path = f"adaptations/{adaptation.adaptation_id}.json"
        self.save(path, adaptation)

    # Backup and restore
    def create_backup(self, backup_name: str) -> str:
        """Create a backup of all data."""
        backup_dir = self.root_path / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for item in self.root_path.iterdir():
            if item.name != "backups" and item.is_file():
                shutil.copy2(item, backup_dir / item.name)
            elif item.is_dir() and item.name != "backups":
                shutil.copytree(item, backup_dir / item.name, dirs_exist_ok=True)

        self._emit_event("storage_backup", {"backup_name": backup_name})
        return str(backup_dir)

    def restore_backup(self, backup_name: str) -> None:
        """Restore from a backup."""
        backup_dir = self.root_path / "backups" / backup_name

        if not backup_dir.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        # Clear current data (except backups)
        for item in self.root_path.iterdir():
            if item.name != "backups":
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

        # Restore from backup
        for item in backup_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, self.root_path / item.name)
            elif item.is_dir():
                shutil.copytree(item, self.root_path / item.name)

        # Clear cache
        self._cache.clear()

        self._emit_event("storage_restore", {"backup_name": backup_name})

    # Cache management
    def _get_cached(self, path: str) -> Any | None:
        """Get from cache if still valid."""
        if path in self._cache:
            value, timestamp = self._cache[path]
            if time.time() - timestamp < self._cache_ttl:
                return value
            else:
                del self._cache[path]
        return None

    def _set_cache(self, path: str, value: Any) -> None:
        """Set cache entry."""
        self._cache[path] = (value, time.time())

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    # Event emission
    def _emit_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Emit storage event if event bus available."""
        if self.event_bus:
            with contextlib.suppress(Exception):
                SystemEvent(event_name=f"persistence_{event_name}", component="persistence_manager", severity="info")
                # Add event data to the event somehow
                # Note: SystemEvent doesn't have a data field, so we'd need to handle this differently
                # For now, we'll skip the event emission


# Utility Functions
@contextmanager
def atomic_write(file_path: Path):
    """Context manager for atomic file writes."""
    temp_path = file_path.with_suffix(".tmp")
    try:
        yield temp_path
        shutil.move(str(temp_path), str(file_path))
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def ensure_directory(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def safe_json_load(file_path: Path, default: Any = None) -> Any:
    """Safely load JSON with default on error."""
    try:
        if file_path.exists():
            return json.loads(file_path.read_text())
    except Exception:
        pass
    return default


def safe_yaml_load(file_path: Path, default: Any = None) -> Any:
    """Safely load YAML with default on error."""
    try:
        if file_path.exists():
            return yaml.safe_load(file_path.read_text()) or default
    except Exception:
        pass
    return default


# Global instance management
_persistence_manager: SimplePersistenceManager | None = None


def initialize_persistence(root_path: Path, event_bus: EventBus | None = None) -> SimplePersistenceManager:
    """Initialize global persistence manager."""
    global _persistence_manager
    _persistence_manager = SimplePersistenceManager(root_path, event_bus=event_bus)
    return _persistence_manager


def get_persistence_manager() -> SimplePersistenceManager | None:
    """Get global persistence manager instance."""
    return _persistence_manager


# Convenience functions
def load_manifest() -> ProjectManifest | None:
    """Load project manifest using global manager."""
    if _persistence_manager:
        return _persistence_manager.load_manifest()
    return None


def save_manifest(manifest: ProjectManifest) -> None:
    """Save project manifest using global manager."""
    if _persistence_manager:
        _persistence_manager.save_manifest(manifest)


def load_config() -> ConfigurationData | None:
    """Load configuration using global manager."""
    if _persistence_manager:
        return _persistence_manager.load_config()
    return None


def save_config(config: ConfigurationData) -> None:
    """Save configuration using global manager."""
    if _persistence_manager:
        _persistence_manager.save_config(config)
