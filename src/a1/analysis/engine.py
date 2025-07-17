"""Core Analysis Engine for A1 - Simplified orchestration.

Provides basic analysis coordination without complex async processing or caching.
Target: ~80 lines (vs 262 lines in A1)
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .code_analyzer import CodeAnalyzer
from .metrics import CodeMetrics
from .quality_checker import QualityChecker


@dataclass
class AnalysisRequest:
    """Simple analysis request."""

    target_paths: list[Path]
    include_tests: bool = True
    max_depth: int = 5


@dataclass
class AnalysisResult:
    """Simple analysis result."""

    request: AnalysisRequest
    code_metrics: CodeMetrics | None = None
    quality_issues: list[dict[str, Any]] = None
    analysis_time: float = 0.0
    errors: list[str] = None


class AnalysisEngine:
    """Simple analysis engine for basic Python code analysis."""

    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.quality_checker = QualityChecker()

    def analyze(self, target_paths: list[str], **kwargs) -> AnalysisResult:
        """Analyze Python code in target paths."""
        start_time = time.time()

        # Create request
        request = AnalysisRequest(
            target_paths=[Path(p) for p in target_paths],
            include_tests=kwargs.get("include_tests", True),
            max_depth=kwargs.get("max_depth", 5),
        )

        # Initialize result
        result = AnalysisResult(request=request, quality_issues=[], errors=[])

        try:
            # Discover Python files
            python_files = self._discover_python_files(request.target_paths, request.max_depth)

            # Analyze code structure and metrics
            result.code_metrics = self.code_analyzer.analyze_files(python_files)

            # Check quality issues
            result.quality_issues = self.quality_checker.check_files(python_files)

        except Exception as e:
            result.errors.append(str(e))

        # Record analysis time
        result.analysis_time = time.time() - start_time

        return result

    def _discover_python_files(self, paths: list[Path], max_depth: int) -> list[Path]:
        """Discover Python files in given paths."""
        python_files = []

        for path in paths:
            if path.is_file() and path.suffix == ".py":
                python_files.append(path)
            elif path.is_dir():
                python_files.extend(self._scan_directory(path, max_depth))

        return python_files

    def _scan_directory(self, directory: Path, max_depth: int) -> list[Path]:
        """Scan directory for Python files up to max depth."""
        python_files = []

        if max_depth <= 0:
            return python_files

        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix == ".py":
                    python_files.append(item)
                elif item.is_dir() and not item.name.startswith("."):
                    python_files.extend(self._scan_directory(item, max_depth - 1))
        except (PermissionError, OSError):
            pass  # Skip directories we can't read

        return python_files

    def get_summary(self, result: AnalysisResult) -> dict[str, Any]:
        """Get a summary of analysis results."""
        summary = {
            "analysis_time": result.analysis_time,
            "errors": len(result.errors),
            "files_analyzed": 0,
            "total_lines": 0,
            "quality_issues": len(result.quality_issues),
        }

        if result.code_metrics:
            summary["files_analyzed"] = result.code_metrics.file_count
            summary["total_lines"] = result.code_metrics.total_lines
            summary["functions"] = result.code_metrics.function_count
            summary["classes"] = result.code_metrics.class_count

        return summary
