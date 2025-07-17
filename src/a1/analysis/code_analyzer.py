"""Basic Code Analyzer for A1 - Python-only analysis.

Provides essential Python code analysis without multi-language complexity.
Target: ~120 lines (vs 529 lines in A1)
"""

import ast
from pathlib import Path

from .metrics import CodeMetrics, FileMetrics, combine_metrics


class CodeAnalyzer:
    """Simple Python code analyzer."""

    def __init__(self):
        self.supported_extensions = {".py"}

    def analyze_files(self, file_paths: list[Path]) -> CodeMetrics:
        """Analyze multiple Python files."""
        file_metrics = []

        for file_path in file_paths:
            if file_path.suffix in self.supported_extensions:
                metrics = self.analyze_file(file_path)
                if metrics:
                    file_metrics.append(metrics)

        return combine_metrics(file_metrics)

    def analyze_file(self, file_path: Path) -> FileMetrics | None:
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Count lines
            lines = content.split("\n")
            metrics = FileMetrics(file_path=str(file_path), lines=len(lines))

            # Classify lines
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    metrics.blank_lines += 1
                elif stripped.startswith("#"):
                    metrics.comment_lines += 1
                else:
                    metrics.code_lines += 1

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, metrics)
            except SyntaxError:
                # If we can't parse, still return basic line metrics
                pass

            return metrics

        except (OSError, UnicodeDecodeError):
            return None

    def _analyze_ast(self, tree: ast.AST, metrics: FileMetrics) -> None:
        """Analyze AST for structural metrics."""
        class_count = 0
        function_count = 0
        import_count = 0
        branches = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_count += 1
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                function_count += 1
            elif isinstance(node, ast.Import | ast.ImportFrom):
                import_count += 1
            elif isinstance(node, ast.If | ast.For | ast.While | ast.With | ast.Try):
                branches += 1

        metrics.classes = class_count
        metrics.functions = function_count
        metrics.imports = import_count
        metrics.complexity = float(branches + 1)  # Simple cyclomatic complexity

    def get_file_info(self, file_path: Path) -> dict:
        """Get basic file information."""
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "size": stat.st_size,
                "extension": file_path.suffix,
                "is_python": file_path.suffix in self.supported_extensions,
            }
        except OSError:
            return {"path": str(file_path), "error": "Cannot access file"}

    def is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name = file_path.name.lower()
        return name.startswith("test_") or name.endswith("_test.py") or "test" in file_path.parts

    def calculate_maintainability_index(self, metrics: FileMetrics) -> float:
        """Calculate a simple maintainability index."""
        if metrics.code_lines == 0:
            return 100.0

        # Simple formula based on complexity and size
        complexity_factor = min(metrics.complexity / 10.0, 1.0)  # Normalize complexity
        size_factor = min(metrics.code_lines / 500.0, 1.0)  # Normalize size

        # Higher complexity and size reduce maintainability
        maintainability = 100.0 - (complexity_factor * 40.0) - (size_factor * 30.0)

        return max(0.0, min(100.0, maintainability))
