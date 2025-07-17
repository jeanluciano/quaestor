"""Tests for V2.1 Basic Persistence System

Tests the simplified file-based persistence including:
- JSON/YAML file operations with atomic writes
- Data model serialization/deserialization
- Storage manager functionality
- Backup and restore operations
- Error handling and recovery
- In-memory backend for testing
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from a1.extensions.persistence import (
    AdaptationData,
    ConfigurationData,
    CorruptedDataError,
    FileNotFoundError,
    FileStorageBackend,
    MemoryStorageBackend,
    PatternData,
    ProjectManifest,
    SimplePersistenceManager,
    StorageError,
    atomic_write,
    ensure_directory,
    get_persistence_manager,
    initialize_persistence,
    safe_json_load,
    safe_yaml_load,
)


class TestDataModels:
    """Tests for data model classes."""

    def test_project_manifest_creation(self):
        """Test creating a project manifest."""
        manifest = ProjectManifest(project_path="/test/project", metadata={"name": "Test Project"})

        assert manifest.project_path == "/test/project"
        assert manifest.metadata["name"] == "Test Project"
        assert manifest.created_at > 0
        assert manifest.updated_at > 0
        assert len(manifest.file_checksums) == 0

    def test_project_manifest_update_timestamp(self):
        """Test updating manifest timestamp."""
        manifest = ProjectManifest(project_path="/test")
        original_time = manifest.updated_at

        time.sleep(0.01)  # Ensure time difference
        manifest.update_timestamp()

        assert manifest.updated_at > original_time

    def test_pattern_data_creation(self):
        """Test creating pattern data."""
        pattern = PatternData(pattern_id="test_pattern", pattern_type="workflow", confidence=0.85)

        assert pattern.pattern_id == "test_pattern"
        assert pattern.pattern_type == "workflow"
        assert pattern.frequency == 1
        assert pattern.confidence == 0.85
        assert pattern.last_seen > 0

    def test_pattern_data_increment(self):
        """Test incrementing pattern frequency."""
        pattern = PatternData(pattern_id="test", pattern_type="tool_sequence")

        original_freq = pattern.frequency
        original_time = pattern.last_seen

        time.sleep(0.01)
        pattern.increment_frequency()

        assert pattern.frequency == original_freq + 1
        assert pattern.last_seen > original_time

    def test_configuration_data(self):
        """Test configuration data model."""
        config = ConfigurationData(settings={"theme": "dark"}, feature_flags={"experimental": True})

        assert config.version == "1.0"
        assert config.settings["theme"] == "dark"
        assert config.feature_flags["experimental"] is True
        assert config.updated_at > 0

    def test_adaptation_data(self):
        """Test adaptation data model."""
        adaptation = AdaptationData(
            adaptation_id="test_adapt", adaptation_type="behavior", trigger="test trigger", response="test response"
        )

        assert adaptation.adaptation_id == "test_adapt"
        assert adaptation.success_count == 0
        assert adaptation.failure_count == 0
        assert adaptation.success_rate == 0.0

        # Test success rate calculation
        adaptation.success_count = 8
        adaptation.failure_count = 2
        assert adaptation.success_rate == 0.8


class TestFileStorageBackend:
    """Tests for file-based storage backend."""

    def test_read_write_json(self):
        """Test reading and writing JSON files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            # Write data
            data = {"key": "value", "number": 42}
            backend.write("test.json", data)

            # Read data
            loaded = backend.read("test.json")
            assert loaded == data

    def test_read_write_yaml(self):
        """Test reading and writing YAML files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            # Write data
            data = {"settings": {"enabled": True}, "items": ["a", "b", "c"]}
            backend.write("config.yaml", data)

            # Read data
            loaded = backend.read("config.yaml")
            assert loaded == data

    def test_atomic_write(self):
        """Test atomic write operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            # Simulate interrupted write
            with patch("shutil.move", side_effect=Exception("Simulated error")):
                with pytest.raises(StorageError):
                    backend.write("test.json", {"data": "value"})

            # Ensure no partial file exists
            assert not backend.exists("test.json")

    def test_file_not_found(self):
        """Test handling missing files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            with pytest.raises(FileNotFoundError):
                backend.read("nonexistent.json")

    def test_corrupted_file(self):
        """Test handling corrupted files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            # Write invalid JSON
            file_path = Path(tmp_dir) / "corrupted.json"
            file_path.write_text("{invalid json")

            with pytest.raises(CorruptedDataError):
                backend.read("corrupted.json")

    def test_exists(self):
        """Test file existence check."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            assert not backend.exists("test.json")

            backend.write("test.json", {"data": "value"})
            assert backend.exists("test.json")

    def test_delete(self):
        """Test file deletion."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            backend.write("test.json", {"data": "value"})
            assert backend.exists("test.json")

            backend.delete("test.json")
            assert not backend.exists("test.json")

    def test_list_files(self):
        """Test listing files in directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            backend = FileStorageBackend(Path(tmp_dir))

            # Create directory structure
            backend.write("patterns/p1.json", {"id": "p1"})
            backend.write("patterns/p2.json", {"id": "p2"})
            backend.write("config.json", {"version": "1"})

            # List patterns directory
            pattern_files = backend.list_files("patterns")
            assert len(pattern_files) == 2
            assert "patterns/p1.json" in pattern_files
            assert "patterns/p2.json" in pattern_files

            # List non-existent directory
            empty_files = backend.list_files("nonexistent")
            assert len(empty_files) == 0


class TestMemoryStorageBackend:
    """Tests for in-memory storage backend."""

    def test_memory_operations(self):
        """Test basic memory storage operations."""
        backend = MemoryStorageBackend()

        # Write and read
        data = {"test": "data"}
        backend.write("test.json", data)
        loaded = backend.read("test.json")
        assert loaded == data

        # Exists
        assert backend.exists("test.json")
        assert not backend.exists("other.json")

        # Delete
        backend.delete("test.json")
        assert not backend.exists("test.json")

    def test_memory_isolation(self):
        """Test that data is properly isolated."""
        backend = MemoryStorageBackend()

        # Write data
        original = {"mutable": ["list"]}
        backend.write("test.json", original)

        # Modify original
        original["mutable"].append("modified")

        # Read should return unmodified copy
        loaded = backend.read("test.json")
        assert loaded["mutable"] == ["list"]

    def test_memory_list_files(self):
        """Test listing files in memory backend."""
        backend = MemoryStorageBackend()

        backend.write("dir/file1.json", {})
        backend.write("dir/file2.json", {})
        backend.write("dir/sub/file3.json", {})
        backend.write("other.json", {})

        files = backend.list_files("dir")
        assert len(files) == 2
        assert "dir/file1.json" in files
        assert "dir/file2.json" in files


class TestSimplePersistenceManager:
    """Tests for the main persistence manager."""

    def test_manager_initialization(self):
        """Test persistence manager initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            assert manager.root_path == Path(tmp_dir)
            assert isinstance(manager.backend, FileStorageBackend)
            assert len(manager._cache) == 0

    def test_load_save_model(self):
        """Test loading and saving model instances."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Save manifest
            manifest = ProjectManifest(project_path="/test", metadata={"version": "1.0"})
            manager.save("manifest.json", manifest)

            # Load manifest
            loaded = manager.load("manifest.json", ProjectManifest)
            assert loaded.project_path == manifest.project_path
            assert loaded.metadata == manifest.metadata

    def test_caching(self):
        """Test caching functionality."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Save data
            pattern = PatternData(pattern_id="cached_pattern", pattern_type="test")
            manager.save("pattern.json", pattern)

            # First load - from disk
            loaded1 = manager.load("pattern.json", PatternData)

            # Second load - should be from cache
            loaded2 = manager.load("pattern.json", PatternData)

            # Should be the same object (cached)
            assert loaded1 is loaded2

            # Clear cache
            manager.clear_cache()

            # Third load - from disk again
            loaded3 = manager.load("pattern.json", PatternData)
            assert loaded3 is not loaded2

    def test_manifest_operations(self):
        """Test manifest-specific operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Initially no manifest
            assert manager.load_manifest() is None

            # Save manifest
            manifest = ProjectManifest(project_path="/test")
            manifest.file_checksums["file.py"] = "checksum123"
            manager.save_manifest(manifest)

            # Load manifest
            loaded = manager.load_manifest()
            assert loaded is not None
            assert loaded.project_path == "/test"
            assert loaded.file_checksums["file.py"] == "checksum123"

    def test_pattern_operations(self):
        """Test pattern storage operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Initially no patterns
            patterns = manager.load_patterns()
            assert len(patterns) == 0

            # Save patterns
            pattern1 = PatternData(pattern_id="p1", pattern_type="type1")
            pattern2 = PatternData(pattern_id="p2", pattern_type="type2")

            manager.save_pattern(pattern1)
            manager.save_pattern(pattern2)

            # Load patterns
            patterns = manager.load_patterns()
            assert len(patterns) == 2
            pattern_ids = [p.pattern_id for p in patterns]
            assert "p1" in pattern_ids
            assert "p2" in pattern_ids

    def test_config_operations(self):
        """Test configuration operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Initially no config
            assert manager.load_config() is None

            # Save config
            config = ConfigurationData(settings={"theme": "dark"}, feature_flags={"beta": True})
            manager.save_config(config)

            # Load config
            loaded = manager.load_config()
            assert loaded is not None
            assert loaded.settings["theme"] == "dark"
            assert loaded.feature_flags["beta"] is True

    def test_adaptation_operations(self):
        """Test adaptation storage operations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Save adaptation
            adaptation = AdaptationData(
                adaptation_id="adapt1", adaptation_type="test_type", trigger="trigger", response="response"
            )
            manager.save_adaptation(adaptation)

            # Load adaptations
            adaptations = manager.load_adaptations()
            assert len(adaptations) == 1
            assert adaptations[0].adaptation_id == "adapt1"

    def test_backup_restore(self):
        """Test backup and restore functionality."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            # Create some data
            manifest = ProjectManifest(project_path="/original")
            manager.save_manifest(manifest)

            pattern = PatternData(pattern_id="p1", pattern_type="test")
            manager.save_pattern(pattern)

            # Create backup
            backup_path = manager.create_backup("test_backup")
            assert Path(backup_path).exists()

            # Modify data
            manifest.project_path = "/modified"
            manager.save_manifest(manifest)

            # Restore backup
            manager.restore_backup("test_backup")

            # Verify restoration
            restored_manifest = manager.load_manifest()
            assert restored_manifest.project_path == "/original"

    def test_backup_not_found(self):
        """Test restoring non-existent backup."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = SimplePersistenceManager(Path(tmp_dir))

            with pytest.raises(FileNotFoundError):
                manager.restore_backup("nonexistent_backup")


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_atomic_write_context(self):
        """Test atomic write context manager."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "test.txt"

            # Successful write
            with atomic_write(file_path) as temp_path:
                temp_path.write_text("test content")

            assert file_path.exists()
            assert file_path.read_text() == "test content"

            # Failed write
            try:
                with atomic_write(file_path) as temp_path:
                    temp_path.write_text("new content")
                    raise Exception("Simulated error")
            except Exception:
                pass

            # Original content should remain
            assert file_path.read_text() == "test content"

    def test_ensure_directory(self):
        """Test directory creation utility."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            deep_path = Path(tmp_dir) / "a" / "b" / "c"

            assert not deep_path.exists()
            ensure_directory(deep_path)
            assert deep_path.exists()
            assert deep_path.is_dir()

    def test_safe_json_load(self):
        """Test safe JSON loading."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Valid JSON
            valid_path = Path(tmp_dir) / "valid.json"
            valid_path.write_text('{"key": "value"}')
            data = safe_json_load(valid_path)
            assert data == {"key": "value"}

            # Invalid JSON
            invalid_path = Path(tmp_dir) / "invalid.json"
            invalid_path.write_text("{invalid")
            data = safe_json_load(invalid_path, default={"default": True})
            assert data == {"default": True}

            # Non-existent file
            data = safe_json_load(Path(tmp_dir) / "missing.json", default={})
            assert data == {}

    def test_safe_yaml_load(self):
        """Test safe YAML loading."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Valid YAML
            valid_path = Path(tmp_dir) / "valid.yaml"
            valid_path.write_text("key: value\nlist:\n  - item1\n  - item2")
            data = safe_yaml_load(valid_path)
            assert data == {"key": "value", "list": ["item1", "item2"]}

            # Empty YAML
            empty_path = Path(tmp_dir) / "empty.yaml"
            empty_path.write_text("")
            data = safe_yaml_load(empty_path, default={"default": True})
            assert data == {"default": True}


class TestGlobalFunctions:
    """Tests for global instance management."""

    def test_initialize_persistence(self):
        """Test global persistence initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Initialize
            manager = initialize_persistence(Path(tmp_dir))
            assert manager is not None

            # Get global instance
            global_manager = get_persistence_manager()
            assert global_manager is manager

    def test_global_convenience_functions(self):
        """Test global convenience functions."""
        import src.quaestor.v2_1.extensions.persistence as persistence_module

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Initialize global manager
            initialize_persistence(Path(tmp_dir))

            # Test manifest operations
            manifest = ProjectManifest(project_path="/global/test")
            persistence_module.save_manifest(manifest)

            loaded = persistence_module.load_manifest()
            assert loaded is not None
            assert loaded.project_path == "/global/test"

            # Test config operations
            config = ConfigurationData(settings={"global": True})
            persistence_module.save_config(config)

            loaded_config = persistence_module.load_config()
            assert loaded_config is not None
            assert loaded_config.settings["global"] is True


if __name__ == "__main__":
    pytest.main([__file__])
