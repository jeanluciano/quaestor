"""Tests for the manifest module."""

from pathlib import Path

from quaestor.manifest import (
    FileType,
    categorize_file,
    extract_version_from_content,
)


class TestFileType:
    """Test FileType enum and categorization."""

    def test_file_type_values(self):
        """Test FileType enum values."""
        assert FileType.SYSTEM.value == "system"
        assert FileType.USER_EDITABLE.value == "user-editable"
        assert FileType.COMMAND.value == "command"
        assert FileType.TEMPLATE.value == "template"


class TestCategorizeFile:
    """Test file categorization logic."""

    def test_categorize_system_files(self):
        """Test categorization of system files."""
        assert categorize_file(Path("CRITICAL_RULES.md"), "CRITICAL_RULES.md") == FileType.SYSTEM
        assert categorize_file(Path("hooks.json"), "hooks.json") == FileType.SYSTEM
        assert categorize_file(Path("CLAUDE.md"), "CLAUDE.md") == FileType.USER_EDITABLE
        assert categorize_file(Path("QUAESTOR_CLAUDE.md"), "QUAESTOR_CLAUDE.md") == FileType.SYSTEM
        assert categorize_file(Path(".quaestor/CRITICAL_RULES.md"), ".quaestor/CRITICAL_RULES.md") == FileType.SYSTEM

    def test_categorize_user_editable_files(self):
        """Test categorization of user-editable files."""
        assert categorize_file(Path("ARCHITECTURE.md"), "ARCHITECTURE.md") == FileType.USER_EDITABLE
        assert categorize_file(Path("MEMORY.md"), "MEMORY.md") == FileType.USER_EDITABLE
        assert categorize_file(Path("MANIFEST.yaml"), "MANIFEST.yaml") == FileType.USER_EDITABLE
        assert categorize_file(Path(".quaestor/ARCHITECTURE.md"), ".quaestor/ARCHITECTURE.md") == FileType.USER_EDITABLE

    def test_categorize_command_files(self):
        """Test categorization of command files."""
        assert categorize_file(Path("commands/task.md"), "commands/task.md") == FileType.COMMAND
        assert categorize_file(Path("commands/help.md"), "commands/help.md") == FileType.COMMAND
        assert categorize_file(Path(".claude/commands/check.md"), ".claude/commands/check.md") == FileType.COMMAND

    def test_categorize_template_files(self):
        """Test categorization of template files (default)."""
        assert categorize_file(Path("random.md"), "random.md") == FileType.TEMPLATE
        assert categorize_file(Path("some/other/file.txt"), "some/other/file.txt") == FileType.TEMPLATE


class TestExtractVersion:
    """Test version extraction from file content."""

    def test_extract_quaestor_version(self):
        """Test extracting QUAESTOR version tag."""
        content = """<!-- QUAESTOR:version:1.0 -->
# Some File
Content here"""
        assert extract_version_from_content(content) == "1.0"

    def test_extract_meta_version(self):
        """Test extracting META version tag."""
        content = """<!-- META:version:2.0 -->
# Another File
More content"""
        assert extract_version_from_content(content) == "2.0"

    def test_extract_simple_version(self):
        """Test extracting simple VERSION tag."""
        content = """<!-- VERSION:3.5 -->
# Yet Another File"""
        assert extract_version_from_content(content) == "3.5"

    def test_extract_version_with_spaces(self):
        """Test extracting version with various spacing."""
        content1 = "<!--  QUAESTOR:version:1.0  -->"
        content2 = "<!-- META:version:2.0   -->"
        content3 = "<!--VERSION:3.0-->"

        assert extract_version_from_content(content1) == "1.0"
        assert extract_version_from_content(content2) == "2.0"
        assert extract_version_from_content(content3) == "3.0"

    def test_extract_version_not_found(self):
        """Test when no version tag is found."""
        content = """# File Without Version
Just regular content here"""
        assert extract_version_from_content(content) is None

    def test_extract_version_multiple_tags(self):
        """Test extraction when multiple version tags exist (first wins)."""
        content = """<!-- QUAESTOR:version:1.0 -->
<!-- META:version:2.0 -->
# File with Multiple Tags"""
        assert extract_version_from_content(content) == "1.0"

    def test_extract_version_complex_version_number(self):
        """Test extraction with complex version numbers."""
        content1 = "<!-- QUAESTOR:version:1.0.0 -->"
        content2 = "<!-- META:version:2.1.3 -->"
        content3 = "<!-- VERSION:0.0.1 -->"

        assert extract_version_from_content(content1) == "1.0.0"
        assert extract_version_from_content(content2) == "2.1.3"
        assert extract_version_from_content(content3) == "0.0.1"
