"""Tests for the Quaestor update functionality."""

from unittest.mock import patch

from quaestor.manifest import FileManifest, FileType
from quaestor.updater import QuaestorUpdater, UpdateResult


class TestFileManifest:
    """Test the FileManifest class."""

    def test_create_empty_manifest(self, temp_dir):
        """Test creating an empty manifest."""
        manifest_path = temp_dir / "manifest.json"
        manifest = FileManifest(manifest_path)

        assert manifest.manifest["version"] == "1.0"
        assert manifest.manifest["files"] == {}
        assert manifest.get_quaestor_version() is None

    def test_track_file(self, temp_dir):
        """Test tracking a file in the manifest."""
        manifest_path = temp_dir / "manifest.json"
        manifest = FileManifest(manifest_path)

        # Create a test file
        test_file = temp_dir / "test.md"
        test_file.write_text("<!-- QUAESTOR:version:1.0 -->\nTest content")

        # Track the file
        manifest.track_file(test_file, FileType.USER_EDITABLE, "1.0", temp_dir)

        # Check it was tracked
        file_info = manifest.get_file_info("test.md")
        assert file_info is not None
        assert file_info["type"] == FileType.USER_EDITABLE.value
        assert file_info["version"] == "1.0"
        assert file_info["user_modified"] is False

    def test_detect_file_modification(self, temp_dir):
        """Test detecting when a file has been modified."""
        manifest_path = temp_dir / "manifest.json"
        manifest = FileManifest(manifest_path)

        # Create and track a file
        test_file = temp_dir / "test.md"
        test_file.write_text("Original content")
        manifest.track_file(test_file, FileType.USER_EDITABLE, "1.0", temp_dir)

        # Modify the file
        test_file.write_text("Modified content")
        manifest.update_file_status("test.md", test_file)

        # Check modification was detected
        assert manifest.is_file_modified("test.md") is True

    def test_save_and_load_manifest(self, temp_dir):
        """Test saving and loading a manifest."""
        manifest_path = temp_dir / "manifest.json"
        manifest1 = FileManifest(manifest_path)

        # Set some data
        manifest1.set_quaestor_version("0.2.4")
        test_file = temp_dir / "test.md"
        test_file.write_text("Test content")
        manifest1.track_file(test_file, FileType.SYSTEM, "1.0", temp_dir)

        # Save
        manifest1.save()

        # Load in a new instance
        manifest2 = FileManifest(manifest_path)
        assert manifest2.get_quaestor_version() == "0.2.4"
        assert "test.md" in manifest2.get_all_files()


class TestQuaestorUpdater:
    """Test the QuaestorUpdater class."""

    def test_check_for_updates_no_updates(self, temp_dir):
        """Test checking for updates when everything is up to date."""
        # Setup
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        manifest = FileManifest(quaestor_dir / "manifest.json")
        manifest.set_quaestor_version("0.2.4")

        # Create files that match current version
        claude_md = temp_dir / "CLAUDE.md"
        claude_md.write_text("<!-- QUAESTOR:version:1.0 -->\nTest content")
        manifest.track_file(claude_md, FileType.SYSTEM, "1.0", temp_dir)

        updater = QuaestorUpdater(temp_dir, manifest)

        # Mock the version check
        with patch("quaestor.updater.__version__", "0.2.4"):
            updates = updater.check_for_updates(show_diff=False)

        assert updates["needs_update"] is False
        assert updates["current_version"] == "0.2.4"
        assert updates["new_version"] == "0.2.4"

    def test_check_for_updates_version_change(self, temp_dir):
        """Test checking for updates when version has changed."""
        # Setup
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        manifest = FileManifest(quaestor_dir / "manifest.json")
        manifest.set_quaestor_version("0.2.3")

        updater = QuaestorUpdater(temp_dir, manifest)

        # Mock the version check
        with patch("quaestor.updater.__version__", "0.2.4"):
            updates = updater.check_for_updates(show_diff=False)

        assert updates["needs_update"] is True
        assert updates["current_version"] == "0.2.3"
        assert updates["new_version"] == "0.2.4"

    def test_update_skip_user_modified_files(self, temp_dir):
        """Test that user-modified files are skipped during update."""
        # Setup
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        manifest = FileManifest(quaestor_dir / "manifest.json")

        # Create a user-editable file and track it
        arch_file = quaestor_dir / "ARCHITECTURE.md"
        arch_file.write_text("User customized content")
        manifest.track_file(arch_file, FileType.USER_EDITABLE, "1.0", temp_dir)

        # Mark as modified
        arch_file.write_text("User customized content - modified")
        manifest.update_file_status(".quaestor/ARCHITECTURE.md", arch_file)

        updater = QuaestorUpdater(temp_dir, manifest)

        # Mock package resources
        with patch("quaestor.updater.pkg_resources.read_text") as mock_read:
            mock_read.return_value = "<!-- QUAESTOR:version:1.1 -->\nNew content"
            result = updater.update()

        # User-modified file should be skipped
        assert ".quaestor/ARCHITECTURE.md" in result.skipped

    def test_update_system_files_always(self, temp_dir):
        """Test that system files are always updated."""
        # Setup
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        manifest = FileManifest(quaestor_dir / "manifest.json")

        # Create a system file
        critical_file = quaestor_dir / "CRITICAL_RULES.md"
        critical_file.write_text("Old content")
        manifest.track_file(critical_file, FileType.SYSTEM, "1.0", temp_dir)

        updater = QuaestorUpdater(temp_dir, manifest)

        # Mock package resources with new content
        with patch("quaestor.updater.pkg_resources.read_text") as mock_read:
            mock_read.return_value = "<!-- QUAESTOR:version:1.1 -->\nNew critical rules"
            updater.update()

        # System file should be updated
        assert critical_file.read_text() == "<!-- QUAESTOR:version:1.1 -->\nNew critical rules"

    def test_update_with_backup(self, temp_dir):
        """Test creating a backup during update."""
        # Setup
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()
        manifest = FileManifest(quaestor_dir / "manifest.json")

        # Create some files
        (temp_dir / "CLAUDE.md").write_text("Original CLAUDE content")
        (quaestor_dir / "MEMORY.md").write_text("Original MEMORY content")

        updater = QuaestorUpdater(temp_dir, manifest)

        # Mock the backup creation
        with patch.object(updater, "_create_backup") as mock_backup:
            backup_dir = quaestor_dir / ".backup" / "20240110_120000"
            mock_backup.return_value = backup_dir
            updater.update(backup=True)

        mock_backup.assert_called_once()

    def test_update_result_summary(self):
        """Test UpdateResult summary generation."""
        result = UpdateResult()
        result.updated = ["file1.md", "file2.md"]
        result.added = ["new_file.md"]
        result.skipped = ["user_file.md"]
        result.failed = [("bad_file.md", "Permission denied")]

        summary = result.summary()
        assert "2 updated" in summary
        assert "1 added" in summary
        assert "1 skipped" in summary
        assert "1 failed" in summary


class TestUpdateIntegration:
    """Integration tests for the update functionality."""

    def test_full_update_workflow(self, temp_dir):
        """Test a complete update workflow."""
        # Initial setup - simulate first installation
        quaestor_dir = temp_dir / ".quaestor"
        quaestor_dir.mkdir()

        # Create initial files
        quaestor_claude_md = quaestor_dir / "QUAESTOR_CLAUDE.md"
        quaestor_claude_md.write_text("<!-- QUAESTOR:version:1.0 -->\nOriginal content")

        arch_md = quaestor_dir / "ARCHITECTURE.md"
        arch_md.write_text("<!-- QUAESTOR:version:1.0 -->\nOriginal architecture")

        # Create and populate manifest
        manifest = FileManifest(quaestor_dir / "manifest.json")
        manifest.set_quaestor_version("0.2.3")
        manifest.track_file(quaestor_claude_md, FileType.SYSTEM, "1.0", temp_dir)
        manifest.track_file(arch_md, FileType.USER_EDITABLE, "1.0", temp_dir)
        manifest.save()

        # User modifies architecture file
        arch_md.write_text("<!-- QUAESTOR:version:1.0 -->\nUser customized architecture")
        manifest.update_file_status(".quaestor/ARCHITECTURE.md", arch_md)
        manifest.save()

        # Now simulate an update
        manifest2 = FileManifest(quaestor_dir / "manifest.json")
        updater = QuaestorUpdater(temp_dir, manifest2)

        # Mock new versions of files
        with patch("quaestor.updater.pkg_resources.read_text") as mock_read:
            # Need to handle multiple calls to read_text for different files
            def read_text_side_effect(package, resource):
                if resource == "QUAESTOR_CLAUDE.md":
                    return "<!-- QUAESTOR:version:1.1 -->\nUpdated QUAESTOR_CLAUDE content"
                elif resource == "CRITICAL_RULES.md":
                    return "<!-- QUAESTOR:version:1.1 -->\nUpdated CRITICAL_RULES content"
                elif resource == "ARCHITECTURE.template.md":
                    return "<!-- QUAESTOR:version:1.1 -->\nUpdated architecture"
                elif resource == "MEMORY.template.md":
                    return "<!-- QUAESTOR:version:1.1 -->\nUpdated memory"
                else:
                    raise FileNotFoundError(f"Resource {resource} not found")

            mock_read.side_effect = read_text_side_effect

            with patch("quaestor.updater.__version__", "0.2.4"):
                result = updater.update()

        # Verify results
        assert ".quaestor/QUAESTOR_CLAUDE.md" in result.updated  # System file updated
        assert ".quaestor/ARCHITECTURE.md" in result.skipped  # User file skipped
        assert quaestor_claude_md.read_text() == "<!-- QUAESTOR:version:1.1 -->\nUpdated QUAESTOR_CLAUDE content"
        assert "User customized" in arch_md.read_text()  # User changes preserved
