"""Essential metrics for A1 Analysis Engine.

Provides basic file and code metrics without complex calculations.
Target: ~80 lines (vs scattered metrics across A1)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CodeMetrics:
    """Basic code metrics."""

    file_count: int = 0
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    import_count: int = 0
    avg_complexity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "files": self.file_count,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": self.function_count,
            "classes": self.class_count,
            "imports": self.import_count,
            "avg_complexity": self.avg_complexity,
        }


@dataclass
class FileMetrics:
    """Metrics for a single file."""

    file_path: str
    lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    complexity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert file metrics to dictionary."""
        return {
            "file": self.file_path,
            "lines": self.lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "complexity": self.complexity,
        }


def calculate_complexity(node_count: int, branch_count: int) -> float:
    """Calculate simple cyclomatic complexity."""
    # Simple approximation: branches + 1
    return float(branch_count + 1)


def combine_metrics(file_metrics: list[FileMetrics]) -> CodeMetrics:
    """Combine file metrics into overall code metrics."""
    if not file_metrics:
        return CodeMetrics()

    total_complexity = sum(fm.complexity for fm in file_metrics)
    avg_complexity = total_complexity / len(file_metrics) if file_metrics else 0.0

    return CodeMetrics(
        file_count=len(file_metrics),
        total_lines=sum(fm.lines for fm in file_metrics),
        code_lines=sum(fm.code_lines for fm in file_metrics),
        comment_lines=sum(fm.comment_lines for fm in file_metrics),
        blank_lines=sum(fm.blank_lines for fm in file_metrics),
        function_count=sum(fm.functions for fm in file_metrics),
        class_count=sum(fm.classes for fm in file_metrics),
        import_count=sum(fm.imports for fm in file_metrics),
        avg_complexity=avg_complexity,
    )
