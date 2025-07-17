"""Basic Quality Checker for A1 - Simple quality validation.

Provides essential quality checks without complex scoring algorithms.
Target: ~100 lines (vs 1,250 lines across A1 quality/pattern files)
"""

import ast
from pathlib import Path
from typing import Any


class QualityChecker:
    """Simple quality checker for Python code."""

    def __init__(self):
        self.max_function_lines = 50
        self.max_class_lines = 200
        self.max_complexity = 5  # Reduced for easier testing
        self.max_line_length = 100

    def check_files(self, file_paths: list[Path]) -> list[dict[str, Any]]:
        """Check quality issues in multiple files."""
        issues = []

        for file_path in file_paths:
            if file_path.suffix == ".py":
                file_issues = self.check_file(file_path)
                issues.extend(file_issues)

        return issues

    def check_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Check quality issues in a single file."""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check line length
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if len(line) > self.max_line_length:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": i,
                            "type": "line_length",
                            "message": f"Line too long ({len(line)} > {self.max_line_length})",
                        }
                    )

            # Parse AST for structural checks
            try:
                tree = ast.parse(content)
                issues.extend(self._check_ast(tree, file_path, lines))
            except SyntaxError as e:
                issues.append(
                    {
                        "file": str(file_path),
                        "line": e.lineno or 1,
                        "type": "syntax_error",
                        "message": f"Syntax error: {e.msg}",
                    }
                )

        except (OSError, UnicodeDecodeError) as e:
            issues.append(
                {"file": str(file_path), "line": 1, "type": "file_error", "message": f"Cannot read file: {e}"}
            )

        return issues

    def _check_ast(self, tree: ast.AST, file_path: Path, lines: list[str]) -> list[dict[str, Any]]:
        """Check AST for quality issues."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                issues.extend(self._check_function(node, file_path, lines))
            elif isinstance(node, ast.ClassDef):
                issues.extend(self._check_class(node, file_path, lines))

        return issues

    def _check_function(self, node: ast.FunctionDef, file_path: Path, lines: list[str]) -> list[dict[str, Any]]:
        """Check function for quality issues."""
        issues = []

        # Calculate function length
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        func_lines = end_line - start_line + 1

        if func_lines > self.max_function_lines:
            issues.append(
                {
                    "file": str(file_path),
                    "line": start_line,
                    "type": "long_function",
                    "message": f"Function '{node.name}' too long ({func_lines} > {self.max_function_lines} lines)",
                }
            )

        # Check complexity (simple version)
        complexity = self._calculate_complexity(node)
        if complexity > self.max_complexity:
            issues.append(
                {
                    "file": str(file_path),
                    "line": start_line,
                    "type": "high_complexity",
                    "message": f"Function '{node.name}' too complex (complexity: {complexity})",
                }
            )

        # Check for no docstring
        if not ast.get_docstring(node):
            issues.append(
                {
                    "file": str(file_path),
                    "line": start_line,
                    "type": "no_docstring",
                    "message": f"Function '{node.name}' has no docstring",
                }
            )

        return issues

    def _check_class(self, node: ast.ClassDef, file_path: Path, lines: list[str]) -> list[dict[str, Any]]:
        """Check class for quality issues."""
        issues = []

        # Calculate class length
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        class_lines = end_line - start_line + 1

        if class_lines > self.max_class_lines:
            issues.append(
                {
                    "file": str(file_path),
                    "line": start_line,
                    "type": "long_class",
                    "message": f"Class '{node.name}' too long ({class_lines} > {self.max_class_lines} lines)",
                }
            )

        # Check for no docstring
        if not ast.get_docstring(node):
            issues.append(
                {
                    "file": str(file_path),
                    "line": start_line,
                    "type": "no_docstring",
                    "message": f"Class '{node.name}' has no docstring",
                }
            )

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate simple cyclomatic complexity."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.For | ast.While | ast.With | ast.Try):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def get_quality_score(self, issues: list[dict[str, Any]], total_lines: int) -> float:
        """Calculate a simple quality score."""
        if total_lines == 0:
            return 100.0

        # Weight different issue types
        weights = {
            "syntax_error": 10,
            "high_complexity": 5,
            "long_function": 3,
            "long_class": 3,
            "line_length": 1,
            "no_docstring": 1,
        }

        penalty = sum(weights.get(issue["type"], 1) for issue in issues)

        # Calculate score (0-100)
        score = max(0, 100 - (penalty * 100 / total_lines))

        return score
