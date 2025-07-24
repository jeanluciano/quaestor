"""Test file discovery and pattern matching.

This module handles finding test files in a codebase using configurable
patterns and heuristics.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from a1.core.event_bus import EventBus

from ..events import SystemEvent


@dataclass
class TestFile:
    """Represents a discovered test file."""

    path: Path
    test_type: str  # 'unit', 'integration', 'e2e', 'performance'
    framework: str  # 'pytest', 'unittest', 'nose', 'custom'
    module_path: str  # Dotted module path
    targets: list[str] = field(default_factory=list)  # Source modules it tests


@dataclass
class TestPattern:
    """Pattern for identifying test files."""

    name: str
    file_pattern: str  # Glob pattern
    path_pattern: str | None = None  # Regex for path matching
    test_type: str = "unit"
    framework: str = "pytest"


class TestDiscovery:
    """Discovers test files in a codebase."""

    # Default test patterns for Python projects
    DEFAULT_PATTERNS = [
        TestPattern("pytest_test", "test_*.py", test_type="unit", framework="pytest"),
        TestPattern("pytest_tests", "*_test.py", test_type="unit", framework="pytest"),
        TestPattern("unittest", "test*.py", test_type="unit", framework="unittest"),
        TestPattern("integration", "test_*_integration.py", test_type="integration"),
        TestPattern("e2e", "test_*_e2e.py", test_type="e2e"),
        TestPattern("performance", "test_*_performance.py", test_type="performance"),
        TestPattern("benchmark", "bench_*.py", test_type="performance", framework="custom"),
    ]

    def __init__(self, patterns: list[TestPattern] | None = None, event_bus: EventBus | None = None):
        """Initialize test discovery.

        Args:
            patterns: Custom test patterns (uses defaults if None)
            event_bus: Optional event bus for discovery events
        """
        self.patterns = patterns or self.DEFAULT_PATTERNS
        self.event_bus = event_bus
        self._test_dirs = ["tests", "test", "testing", "spec", "specs"]
        self._exclude_dirs = ["__pycache__", ".pytest_cache", "node_modules", ".git", ".venv", "venv"]

    def discover_tests(self, root_path: Path) -> list[TestFile]:
        """Discover all test files in a directory tree.

        Args:
            root_path: Root directory to search

        Returns:
            List of discovered test files
        """
        test_files = []

        # Emit start event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="test_discovery_started", data={"root": str(root_path), "patterns": len(self.patterns)}
                )
            )

        # Search for test files
        for pattern in self.patterns:
            matches = self._find_files_matching_pattern(root_path, pattern)
            test_files.extend(matches)

        # Deduplicate by path
        unique_files = {}
        for test_file in test_files:
            if test_file.path not in unique_files:
                unique_files[test_file.path] = test_file

        results = list(unique_files.values())

        # Analyze test targets
        for test_file in results:
            test_file.targets = self._infer_test_targets(test_file, root_path)

        # Emit completion event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="test_discovery_completed",
                    data={
                        "root": str(root_path),
                        "discovered": len(results),
                        "test_types": self._count_by_type(results),
                    },
                )
            )

        return results

    def find_test_directories(self, root_path: Path) -> list[Path]:
        """Find directories likely to contain tests.

        Args:
            root_path: Root directory to search

        Returns:
            List of test directories
        """
        test_dirs = []

        for dir_name in self._test_dirs:
            # Check root level
            test_dir = root_path / dir_name
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(test_dir)

            # Check subdirectories
            for subdir in root_path.rglob(dir_name):
                if subdir.is_dir() and not any(exclude in str(subdir) for exclude in self._exclude_dirs):
                    test_dirs.append(subdir)

        return list(set(test_dirs))

    def is_test_file(self, file_path: Path) -> TestFile | None:
        """Check if a file is a test file.

        Args:
            file_path: Path to check

        Returns:
            TestFile if it's a test, None otherwise
        """
        if file_path.suffix != ".py":
            return None

        # Check against patterns
        for pattern in self.patterns:
            if self._matches_pattern(file_path, pattern):
                return TestFile(
                    path=file_path,
                    test_type=pattern.test_type,
                    framework=pattern.framework,
                    module_path=self._path_to_module(file_path),
                )

        return None

    def _find_files_matching_pattern(self, root_path: Path, pattern: TestPattern) -> list[TestFile]:
        """Find all files matching a test pattern.

        Args:
            root_path: Root directory to search
            pattern: Test pattern to match

        Returns:
            List of matching test files
        """
        matches = []

        # Search in test directories first
        test_dirs = self.find_test_directories(root_path)
        all_dirs = [root_path] + test_dirs

        for search_dir in all_dirs:
            for file_path in search_dir.rglob(pattern.file_pattern):
                if self._should_include_file(file_path) and self._matches_pattern(file_path, pattern):
                    test_file = TestFile(
                        path=file_path,
                        test_type=pattern.test_type,
                        framework=pattern.framework,
                        module_path=self._path_to_module(file_path, root_path),
                    )
                    matches.append(test_file)

        return matches

    def _matches_pattern(self, file_path: Path, pattern: TestPattern) -> bool:
        """Check if a file matches a test pattern.

        Args:
            file_path: File to check
            pattern: Pattern to match against

        Returns:
            True if matches
        """
        # Check file name pattern
        if not file_path.match(pattern.file_pattern):
            return False

        # Check path pattern if specified
        if pattern.path_pattern:
            if not re.search(pattern.path_pattern, str(file_path)):
                return False

        return True

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included in results.

        Args:
            file_path: File to check

        Returns:
            True if should include
        """
        path_str = str(file_path)

        # Exclude certain directories
        for exclude in self._exclude_dirs:
            if exclude in path_str:
                return False

        # Only Python files
        if file_path.suffix != ".py":
            return False

        # Must exist and be a file
        if not file_path.exists() or not file_path.is_file():
            return False

        return True

    def _infer_test_targets(self, test_file: TestFile, root_path: Path) -> list[str]:
        """Infer what source modules a test file targets.

        Args:
            test_file: Test file to analyze
            root_path: Project root path

        Returns:
            List of target module paths
        """
        targets = []
        test_name = test_file.path.stem

        # Common patterns:
        # test_module.py -> module.py
        # test_package_module.py -> package/module.py
        # module_test.py -> module.py

        # Remove test prefix/suffix
        if test_name.startswith("test_"):
            target_name = test_name[5:]
        elif test_name.endswith("_test"):
            target_name = test_name[:-5]
        elif test_name.startswith("test") and len(test_name) > 4:
            target_name = test_name[4:].lower()
        else:
            return targets

        # Try to find matching source files
        # Look for direct match
        source_file = root_path / f"{target_name}.py"
        if source_file.exists():
            targets.append(self._path_to_module(source_file, root_path))

        # Look for package/module pattern
        if "_" in target_name:
            parts = target_name.split("_", 1)
            package_path = root_path / parts[0]
            if package_path.is_dir():
                module_file = package_path / f"{parts[1]}.py"
                if module_file.exists():
                    targets.append(self._path_to_module(module_file, root_path))

        # Look in src/ directory if exists
        src_dir = root_path / "src"
        if src_dir.exists():
            source_file = src_dir / f"{target_name}.py"
            if source_file.exists():
                targets.append(self._path_to_module(source_file, root_path))

        return targets

    def _path_to_module(self, file_path: Path, root_path: Path | None = None) -> str:
        """Convert file path to module path.

        Args:
            file_path: File path to convert
            root_path: Optional root path for relative conversion

        Returns:
            Dotted module path
        """
        if root_path:
            try:
                relative_path = file_path.relative_to(root_path)
            except ValueError:
                relative_path = file_path
        else:
            relative_path = file_path

        # Remove .py extension and convert separators
        parts = list(relative_path.parts[:-1]) + [relative_path.stem]

        # Remove src/ prefix if present
        if parts and parts[0] == "src":
            parts = parts[1:]

        # Remove __init__ from path
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    def _count_by_type(self, test_files: list[TestFile]) -> dict[str, int]:
        """Count test files by type.

        Args:
            test_files: List of test files

        Returns:
            Dictionary of type -> count
        """
        counts = {}
        for test_file in test_files:
            counts[test_file.test_type] = counts.get(test_file.test_type, 0) + 1
        return counts
