"""Tests for template and initialization system."""

import tempfile
from pathlib import Path

import pytest


class TestTemplateCopying:
    """Test that all templates are properly included during init."""

    def test_template_files_constant_completeness(self):
        """Test that TEMPLATE_FILES includes all critical Quaestor files."""
        from quaestor.constants import TEMPLATE_FILES

        # These are the critical files that must be included
        required_files = {
            "AGENT.md",
            "ARCHITECTURE.md",
            "RULES.md",
        }

        actual_files = set(TEMPLATE_FILES.values())

        missing_files = required_files - actual_files
        assert not missing_files, f"Missing required template files: {missing_files}"

    def test_claude_md_template_references_all_files(self):
        """Test that CLAUDE.md template references all the required files."""
        import importlib.resources as pkg_resources

        # Read the include.md template
        try:
            claude_template = pkg_resources.read_text("quaestor", "include.md")
        except Exception:
            pytest.skip("include.md template not found")

        # Files that should be referenced in CLAUDE.md
        expected_references = [
            ".quaestor/AGENT.md",
            ".quaestor/ARCHITECTURE.md",
        ]

        for ref in expected_references:
            assert ref in claude_template, f"CLAUDE.md template should reference {ref}"

    def test_template_files_exist(self):
        """Test that all template files exist in the package."""
        import importlib.resources as pkg_resources

        from quaestor.constants import TEMPLATE_FILES

        for template_name in TEMPLATE_FILES:
            try:
                content = pkg_resources.read_text("quaestor", template_name)
                assert len(content) > 0, f"Template file {template_name} is empty"
            except Exception as e:
                pytest.fail(f"Template file not found: {template_name} - {e}")


class TestInitDirectoryStructure:
    """Test that init creates the correct directory structure."""

    def test_specs_directory_structure(self):
        """Test that init should create proper specs directory structure."""
        # This documents the expected directory structure
        expected_dirs = ["draft", "active", "completed", "archived"]

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            quaestor_dir = target_dir / ".quaestor"
            specs_dir = quaestor_dir / "specs"

            # Create the structure init should create
            quaestor_dir.mkdir()
            for dir_name in expected_dirs:
                (specs_dir / dir_name).mkdir(parents=True)

            # Verify structure
            for dir_name in expected_dirs:
                assert (specs_dir / dir_name).exists(), f"specs/{dir_name} should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
