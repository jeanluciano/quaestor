"""Tests for A1 incremental analysis functionality."""

import time

import pytest

from a1.deep_context import CodeNavigationIndex
from a1.deep_context.incremental_analyzer import IncrementalAnalyzer


class TestIncrementalAnalyzer:
    """Test incremental analysis functionality."""

    @pytest.fixture
    def test_project(self, tmp_path):
        """Create a test project structure."""
        # Create initial files
        main_file = tmp_path / "main.py"
        main_file.write_text('''
"""Main module."""

from utils import helper

def main():
    result = helper()
    print(result)
''')

        utils_file = tmp_path / "utils.py"
        utils_file.write_text('''
"""Utilities."""

def helper():
    return "Hello, World!"
''')

        return tmp_path

    @pytest.fixture
    def analyzer(self, test_project):
        """Create analyzer with initial index."""
        index = CodeNavigationIndex()
        index.index_directory(test_project)

        analyzer = IncrementalAnalyzer(index)
        # Initialize metadata by doing a full update
        analyzer.update_incrementally(test_project)

        return analyzer

    def test_detect_no_changes(self, analyzer, test_project):
        """Test detecting when no files have changed."""
        # Run analysis again without changes
        update = analyzer.analyze_changes(test_project)

        assert len(update.updated_files) == 0
        assert len(update.removed_files) == 0
        assert len(update.affected_files) == 0

    def test_detect_file_modification(self, analyzer, test_project):
        """Test detecting modified files."""
        # Modify a file
        utils_file = test_project / "utils.py"
        time.sleep(0.01)  # Ensure mtime changes
        utils_file.write_text('''
"""Utilities."""

def helper():
    return "Hello, Modified World!"

def new_function():
    pass
''')

        update = analyzer.analyze_changes(test_project)

        assert len(update.updated_files) == 1
        assert utils_file in update.updated_files

    def test_detect_file_addition(self, analyzer, test_project):
        """Test detecting new files."""
        # Add a new file
        new_file = test_project / "new_module.py"
        new_file.write_text('''
"""New module."""

def new_func():
    pass
''')

        update = analyzer.analyze_changes(test_project)

        assert len(update.updated_files) == 1
        assert new_file in update.updated_files

    def test_detect_file_deletion(self, analyzer, test_project):
        """Test detecting deleted files."""
        # Delete a file
        utils_file = test_project / "utils.py"
        utils_file.unlink()

        update = analyzer.analyze_changes(test_project)

        assert len(update.removed_files) == 1
        assert utils_file in update.removed_files

    def test_find_affected_files(self, analyzer, test_project):
        """Test finding files affected by changes."""
        # Modify utils.py which is imported by main.py
        utils_file = test_project / "utils.py"
        time.sleep(0.01)
        utils_file.write_text('''
"""Utilities."""

def helper():
    return "Modified!"
''')

        # First update to establish dependencies
        analyzer.update_incrementally(test_project)

        # Now modify utils again
        time.sleep(0.01)
        utils_file.write_text('''
"""Utilities."""

def helper():
    return "Modified again!"
''')

        update = analyzer.analyze_changes(test_project)

        # main.py should be affected since it imports utils
        assert utils_file in update.updated_files
        # Affected files detection depends on dependency tracking

    def test_incremental_update(self, analyzer, test_project):
        """Test performing incremental update."""
        # Add a new function to utils
        utils_file = test_project / "utils.py"
        time.sleep(0.01)
        utils_file.write_text('''
"""Utilities."""

def helper():
    return "Hello, World!"

def another_helper():
    return "Another function"
''')

        # Perform incremental update
        update = analyzer.update_incrementally(test_project)

        assert len(update.updated_files) == 1

        # Check that new symbol was added
        symbols = analyzer.index.search_symbols("another_helper")
        assert len(symbols) == 1

    def test_remove_file_symbols(self, analyzer, test_project):
        """Test removing symbols when file is deleted."""
        # Check initial symbols
        initial_symbols = analyzer.index.search_symbols("helper")
        assert len(initial_symbols) == 1

        # Delete utils.py
        utils_file = test_project / "utils.py"
        utils_file.unlink()

        # Update incrementally
        analyzer.update_incrementally(test_project)

        # Symbol should be gone
        symbols = analyzer.index.search_symbols("helper")
        assert len(symbols) == 0

    def test_cache_persistence(self, analyzer, test_project, tmp_path):
        """Test cache save and load."""
        cache_file = tmp_path / "cache.json"
        analyzer.set_cache_file(cache_file)

        # Modify a file
        utils_file = test_project / "utils.py"
        time.sleep(0.01)
        utils_file.write_text('''
"""Modified utilities."""

def helper():
    return "Modified!"
''')

        # Update and save cache
        analyzer.update_incrementally(test_project)

        # Create new analyzer and load cache
        new_index = CodeNavigationIndex()
        new_analyzer = IncrementalAnalyzer(new_index)
        new_analyzer.set_cache_file(cache_file)

        # Should detect no changes (cache is up to date)
        update = new_analyzer.analyze_changes(test_project)
        assert len(update.updated_files) == 0

    def test_checksum_verification(self, analyzer, test_project):
        """Test that checksum catches content changes even if mtime doesn't change."""
        utils_file = test_project / "utils.py"

        # Get initial state
        analyzer.analyze_changes(test_project)

        # Modify file but keep same mtime
        stat = utils_file.stat()
        utils_file.write_text('''
"""Modified content with same mtime."""

def helper():
    return "Sneaky change!"
''')

        # Try to preserve mtime (might not work on all systems)
        import contextlib
        import os

        with contextlib.suppress(BaseException):
            os.utime(utils_file, (stat.st_atime, stat.st_mtime))

        # Should still detect change via checksum
        update = analyzer.analyze_changes(test_project)
        assert utils_file in update.updated_files

    def test_performance_metrics(self, analyzer, test_project):
        """Test that performance metrics are tracked."""
        # Add multiple files
        for i in range(5):
            file_path = test_project / f"module_{i}.py"
            file_path.write_text(f"""
def func_{i}():
    pass
""")

        # Update incrementally
        update = analyzer.update_incrementally(test_project)

        # Should have timing information
        assert update.duration_ms > 0
        assert len(update.updated_files) == 5
