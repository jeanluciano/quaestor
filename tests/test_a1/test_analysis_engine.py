"""Tests for V2.1 Analysis Engine - Simplified code analysis system."""

import shutil
import tempfile
from pathlib import Path

from a1.analysis import AnalysisEngine, CodeAnalyzer, CodeMetrics, QualityChecker
from a1.analysis.metrics import FileMetrics


class TestCodeMetrics:
    """Tests for code metrics."""

    def test_code_metrics_creation(self):
        """Test creating code metrics."""
        metrics = CodeMetrics(file_count=5, total_lines=100, function_count=10, class_count=2)

        assert metrics.file_count == 5
        assert metrics.total_lines == 100
        assert metrics.function_count == 10
        assert metrics.class_count == 2

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = CodeMetrics(file_count=1, total_lines=50)
        result = metrics.to_dict()

        assert result["files"] == 1
        assert result["total_lines"] == 50
        assert "functions" in result
        assert "classes" in result

    def test_file_metrics_creation(self):
        """Test creating file metrics."""
        metrics = FileMetrics(file_path="/test/file.py", lines=100, functions=5, classes=2)

        assert metrics.file_path == "/test/file.py"
        assert metrics.lines == 100
        assert metrics.functions == 5
        assert metrics.classes == 2


class TestCodeAnalyzer:
    """Tests for code analyzer."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analyzer = CodeAnalyzer()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file."""
        # Create test file
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""
def hello():
    '''A simple function.'''
    return "Hello, World!"

class TestClass:
    '''A simple class.'''
    pass
""")

        metrics = self.analyzer.analyze_file(test_file)

        assert metrics is not None
        assert metrics.functions == 1
        assert metrics.classes == 1
        assert metrics.lines > 0

    def test_analyze_file_with_imports(self):
        """Test analyzing file with imports."""
        test_file = self.temp_dir / "imports.py"
        test_file.write_text("""
import os
from pathlib import Path
import sys

def main():
    pass
""")

        metrics = self.analyzer.analyze_file(test_file)

        assert metrics is not None
        assert metrics.imports == 3
        assert metrics.functions == 1

    def test_analyze_file_with_complexity(self):
        """Test analyzing file with complexity."""
        test_file = self.temp_dir / "complex.py"
        test_file.write_text("""
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    return x
""")

        metrics = self.analyzer.analyze_file(test_file)

        assert metrics is not None
        assert metrics.complexity > 1  # Should have some complexity

    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        # Create multiple test files
        file1 = self.temp_dir / "file1.py"
        file1.write_text("def func1(): pass")

        file2 = self.temp_dir / "file2.py"
        file2.write_text("class Class2: pass")

        files = [file1, file2]
        metrics = self.analyzer.analyze_files(files)

        assert isinstance(metrics, CodeMetrics)
        assert metrics.file_count == 2
        assert metrics.function_count == 1
        assert metrics.class_count == 1

    def test_is_test_file(self):
        """Test test file detection."""
        assert self.analyzer.is_test_file(Path("test_something.py"))
        assert self.analyzer.is_test_file(Path("something_test.py"))
        assert self.analyzer.is_test_file(Path("tests/test_file.py"))
        assert not self.analyzer.is_test_file(Path("normal_file.py"))

    def test_maintainability_index(self):
        """Test maintainability index calculation."""
        metrics = FileMetrics(file_path="test.py", code_lines=100, complexity=5.0)

        index = self.analyzer.calculate_maintainability_index(metrics)

        assert 0.0 <= index <= 100.0

    def test_analyze_syntax_error_file(self):
        """Test analyzing file with syntax error."""
        test_file = self.temp_dir / "syntax_error.py"
        test_file.write_text("def broken_function(\n    invalid syntax")

        metrics = self.analyzer.analyze_file(test_file)

        # Should still return metrics for line counts
        assert metrics is not None
        assert metrics.lines > 0
        assert metrics.functions == 0  # AST parsing failed


class TestQualityChecker:
    """Tests for quality checker."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checker = QualityChecker()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_check_line_length(self):
        """Test line length checking."""
        test_file = self.temp_dir / "long_lines.py"
        long_line = "x = " + "a" * 200  # Very long line
        test_file.write_text(f"short_line = 1\n{long_line}\n")

        issues = self.checker.check_file(test_file)

        line_length_issues = [i for i in issues if i["type"] == "line_length"]
        assert len(line_length_issues) == 1
        assert line_length_issues[0]["line"] == 2

    def test_check_long_function(self):
        """Test long function detection."""
        test_file = self.temp_dir / "long_function.py"

        # Create a function with many lines
        lines = ["def long_function():"] + [f"    line_{i} = {i}" for i in range(60)]
        test_file.write_text("\n".join(lines))

        issues = self.checker.check_file(test_file)

        long_func_issues = [i for i in issues if i["type"] == "long_function"]
        assert len(long_func_issues) == 1
        assert "too long" in long_func_issues[0]["message"]

    def test_check_high_complexity(self):
        """Test high complexity detection."""
        test_file = self.temp_dir / "complex.py"
        test_file.write_text("""
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                while i > 0:
                    if i % 3 == 0:
                        if i % 5 == 0:
                            if i % 7 == 0:
                                return i
                    i -= 1
    return 0
""")

        issues = self.checker.check_file(test_file)

        complexity_issues = [i for i in issues if i["type"] == "high_complexity"]
        assert len(complexity_issues) == 1
        assert "too complex" in complexity_issues[0]["message"]

    def test_check_no_docstring(self):
        """Test no docstring detection."""
        test_file = self.temp_dir / "no_docstring.py"
        test_file.write_text("""
def function_without_docstring():
    return "no docs"

class ClassWithoutDocstring:
    pass
""")

        issues = self.checker.check_file(test_file)

        docstring_issues = [i for i in issues if i["type"] == "no_docstring"]
        assert len(docstring_issues) == 2  # Function and class

    def test_check_syntax_error(self):
        """Test syntax error detection."""
        test_file = self.temp_dir / "syntax_error.py"
        test_file.write_text("def broken_function(\n    invalid syntax")

        issues = self.checker.check_file(test_file)

        syntax_issues = [i for i in issues if i["type"] == "syntax_error"]
        assert len(syntax_issues) == 1
        assert "syntax error" in syntax_issues[0]["message"].lower()

    def test_quality_score(self):
        """Test quality score calculation."""
        issues = [
            {"type": "line_length", "message": "Line too long"},
            {"type": "no_docstring", "message": "No docstring"},
            {"type": "high_complexity", "message": "Too complex"},
        ]

        score = self.checker.get_quality_score(issues, 100)

        assert 0.0 <= score <= 100.0
        assert score < 100.0  # Should be penalized for issues

    def test_check_multiple_files(self):
        """Test checking multiple files."""
        # Create files with different issues
        file1 = self.temp_dir / "file1.py"
        file1.write_text("def func(): pass")  # No docstring

        file2 = self.temp_dir / "file2.py"
        file2.write_text("x = " + "a" * 200)  # Long line

        issues = self.checker.check_files([file1, file2])

        assert len(issues) >= 2
        assert any(i["type"] == "no_docstring" for i in issues)
        assert any(i["type"] == "line_length" for i in issues)


class TestAnalysisEngine:
    """Tests for analysis engine."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = AnalysisEngine()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_analyze_single_file(self):
        """Test analyzing a single file."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""
def hello():
    '''Say hello.'''
    return "Hello, World!"
""")

        result = self.engine.analyze([str(test_file)])

        assert result.code_metrics is not None
        assert result.code_metrics.file_count == 1
        assert result.code_metrics.function_count == 1
        assert result.analysis_time > 0
        assert len(result.errors) == 0

    def test_analyze_directory(self):
        """Test analyzing a directory."""
        # Create test directory with multiple files
        test_dir = self.temp_dir / "project"
        test_dir.mkdir()

        (test_dir / "main.py").write_text("def main(): pass")
        (test_dir / "utils.py").write_text("class Utils: pass")
        (test_dir / "readme.txt").write_text("Not Python")  # Should be ignored

        result = self.engine.analyze([str(test_dir)])

        assert result.code_metrics is not None
        assert result.code_metrics.file_count == 2  # Only .py files
        assert result.code_metrics.function_count == 1
        assert result.code_metrics.class_count == 1

    def test_analyze_with_quality_issues(self):
        """Test analysis with quality issues."""
        test_file = self.temp_dir / "issues.py"
        test_file.write_text(
            """
def function_without_docstring():
    x = """
            + "a" * 200
            + """
    return x
"""
        )

        result = self.engine.analyze([str(test_file)])

        assert len(result.quality_issues) > 0
        assert any(issue["type"] == "no_docstring" for issue in result.quality_issues)
        assert any(issue["type"] == "line_length" for issue in result.quality_issues)

    def test_analyze_nonexistent_path(self):
        """Test analyzing non-existent path."""
        result = self.engine.analyze(["/nonexistent/path"])

        # Should handle gracefully
        assert result.code_metrics is not None
        assert result.code_metrics.file_count == 0

    def test_discover_python_files(self):
        """Test Python file discovery."""
        # Create mixed file types
        test_dir = self.temp_dir / "mixed"
        test_dir.mkdir()

        (test_dir / "script.py").write_text("# Python file")
        (test_dir / "config.json").write_text("{}")
        (test_dir / "readme.md").write_text("# README")

        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "module.py").write_text("# Another Python file")

        files = self.engine._discover_python_files([test_dir], max_depth=2)

        python_files = [f for f in files if f.suffix == ".py"]
        assert len(python_files) == 2
        assert any(f.name == "script.py" for f in python_files)
        assert any(f.name == "module.py" for f in python_files)

    def test_get_summary(self):
        """Test getting analysis summary."""
        test_file = self.temp_dir / "summary_test.py"
        test_file.write_text("""
def func1():
    pass

def func2():
    pass

class TestClass:
    pass
""")

        result = self.engine.analyze([str(test_file)])
        summary = self.engine.get_summary(result)

        assert "analysis_time" in summary
        assert "files_analyzed" in summary
        assert "total_lines" in summary
        assert "functions" in summary
        assert "classes" in summary
        assert "quality_issues" in summary

        assert summary["files_analyzed"] == 1
        assert summary["functions"] == 2
        assert summary["classes"] == 1

    def test_max_depth_limiting(self):
        """Test max depth limiting for directory scanning."""
        # Create deep directory structure
        current_dir = self.temp_dir / "level1"
        current_dir.mkdir()

        for level in range(2, 6):  # Create levels 2-5
            current_dir = current_dir / f"level{level}"
            current_dir.mkdir()
            (current_dir / f"file{level}.py").write_text(f"# Level {level}")

        # Test with max_depth=2
        result = self.engine.analyze([str(self.temp_dir)], max_depth=2)

        # Should only find files up to level 2
        assert result.code_metrics.file_count <= 2


class TestAnalysisEngineIntegration:
    """Integration tests for the complete analysis engine."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = AnalysisEngine()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow."""
        # Create a realistic project structure
        project_dir = self.temp_dir / "project"
        project_dir.mkdir()

        # Main module
        (project_dir / "main.py").write_text("""
import os
from pathlib import Path

def main():
    '''Main entry point.'''
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")

        # Utility module with issues
        (project_dir / "utils.py").write_text("""
def utility_function_with_very_long_name_that_exceeds_normal_length():
    x = "this is a very long line that exceeds the normal length limit and should trigger a line length warning"
    return x

class UtilityClass:
    def method_without_docstring(self):
        if True:
            for i in range(10):
                if i % 2 == 0:
                    while i > 0:
                        if i % 3 == 0:
                            return i
                        i -= 1
        return 0
""")

        # Test module
        (project_dir / "test_main.py").write_text("""
def test_main():
    '''Test the main function.'''
    assert True
""")

        # Analyze the project
        result = self.engine.analyze([str(project_dir)])

        # Verify code metrics
        assert result.code_metrics is not None
        assert result.code_metrics.file_count == 3
        assert result.code_metrics.function_count >= 3
        assert result.code_metrics.class_count >= 1
        assert result.code_metrics.import_count >= 2

        # Verify quality issues
        assert len(result.quality_issues) > 0

        # Check for specific issue types
        issue_types = {issue["type"] for issue in result.quality_issues}
        assert "line_length" in issue_types
        assert "no_docstring" in issue_types
        assert "high_complexity" in issue_types

        # Verify analysis completed successfully
        assert result.analysis_time > 0
        assert len(result.errors) == 0

        # Verify summary
        summary = self.engine.get_summary(result)
        assert summary["files_analyzed"] == 3
        assert summary["quality_issues"] > 0
        assert summary["total_lines"] > 0

    def test_performance_target_validation(self):
        """Test that analysis meets performance targets."""
        # Create moderate-sized project
        project_dir = self.temp_dir / "performance_test"
        project_dir.mkdir()

        # Create 10 files with reasonable content
        for i in range(10):
            file_path = project_dir / f"module_{i}.py"
            content = f"""
def function_{i}():
    '''Function number {i}.'''
    result = 0
    for j in range(100):
        result += j
    return result

class Class_{i}:
    '''Class number {i}.'''
    def method(self):
        return {i}
"""
            file_path.write_text(content)

        # Analyze and check performance
        result = self.engine.analyze([str(project_dir)])

        # Should complete within reasonable time (< 1 second for this size)
        assert result.analysis_time < 1.0

        # Should analyze all files
        assert result.code_metrics.file_count == 10
        assert result.code_metrics.function_count == 20  # 2 per file
        assert result.code_metrics.class_count == 10  # 1 per file
