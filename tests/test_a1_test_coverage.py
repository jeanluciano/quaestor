"""Tests for the test coverage mapping functionality."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from a1.deep_context.symbol_table import Symbol, SymbolLocation, SymbolTable, SymbolType
from a1.deep_context.test_coverage import (
    CoverageCalculator,
    CoverageMapper,
    CoverageMetrics,
    HistoryTracker,
    ReportGenerator,
    TestAnalyzer,
    TestDiscovery,
    TestRun,
)


@pytest.fixture
def event_bus():
    """Create a mock event bus for testing."""
    mock_bus = MagicMock()
    mock_bus.emit = MagicMock()
    return mock_bus


@pytest.fixture
def symbol_table(event_bus):
    """Create a symbol table with test data."""
    table = SymbolTable(event_bus)

    # Add some test symbols
    symbols = [
        Symbol(
            name="calculate_total",
            qualified_name="shopping.cart.calculate_total",
            symbol_type=SymbolType.FUNCTION,
            location=SymbolLocation(file_path=Path("src/shopping/cart.py"), line_start=10, line_end=20),
        ),
        Symbol(
            name="User",
            qualified_name="models.user.User",
            symbol_type=SymbolType.CLASS,
            location=SymbolLocation(file_path=Path("src/models/user.py"), line_start=5, line_end=50),
        ),
        Symbol(
            name="__init__",
            qualified_name="models.user.User.__init__",
            symbol_type=SymbolType.METHOD,
            location=SymbolLocation(file_path=Path("src/models/user.py"), line_start=10, line_end=15),
            parent="models.user.User",
        ),
        Symbol(
            name="validate_email",
            qualified_name="utils.validators.validate_email",
            symbol_type=SymbolType.FUNCTION,
            location=SymbolLocation(file_path=Path("src/utils/validators.py"), line_start=5, line_end=10),
        ),
    ]

    for symbol in symbols:
        table.add_symbol(symbol)

    return table


@pytest.fixture
def test_project(tmp_path):
    """Create a test project structure."""
    # Source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "calculator.py").write_text('''
"""Calculator module."""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

class Calculator:
    """Calculator class."""

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
''')

    # Test files
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    (tests_dir / "test_calculator.py").write_text('''
"""Tests for calculator module."""

import pytest
from src.calculator import add, subtract, Calculator

def test_add():
    """Test addition."""
    assert add(2, 3) == 5

def test_subtract():
    """Test subtraction."""
    assert subtract(5, 3) == 2

class TestCalculator:
    """Test Calculator class."""

    def test_multiply(self):
        """Test multiplication."""
        calc = Calculator()
        assert calc.multiply(3, 4) == 12
''')

    return tmp_path


class TestTestDiscovery:
    """Tests for test file discovery."""

    def test_discover_tests(self, test_project):
        """Test discovering test files in a project."""
        discovery = TestDiscovery()
        test_files = discovery.discover_tests(test_project)

        assert len(test_files) == 1
        assert test_files[0].path.name == "test_calculator.py"
        assert test_files[0].test_type == "unit"
        assert test_files[0].framework == "pytest"

    def test_is_test_file(self, test_project):
        """Test identifying test files."""
        discovery = TestDiscovery()

        test_file = test_project / "tests" / "test_calculator.py"
        result = discovery.is_test_file(test_file)
        assert result is not None
        assert result.test_type == "unit"

        src_file = test_project / "src" / "calculator.py"
        result = discovery.is_test_file(src_file)
        assert result is None

    def test_custom_patterns(self, tmp_path):
        """Test custom test patterns."""
        from a1.deep_context.test_coverage.test_discovery import TestPattern

        # Create file with custom pattern
        (tmp_path / "spec_calculator.py").write_text("# spec file")

        custom_patterns = [TestPattern("spec", "spec_*.py", test_type="spec", framework="custom")]

        discovery = TestDiscovery(patterns=custom_patterns)
        test_files = discovery.discover_tests(tmp_path)

        assert len(test_files) == 1
        assert test_files[0].test_type == "spec"
        assert test_files[0].framework == "custom"


class TestTestAnalyzer:
    """Tests for test code analysis."""

    def test_analyze_test_file(self, test_project, symbol_table):
        """Test analyzing a test file."""
        analyzer = TestAnalyzer(symbol_table)
        test_file = test_project / "tests" / "test_calculator.py"

        test_module = analyzer.analyze_test_file(test_file)

        assert len(test_module.test_functions) == 2
        assert len(test_module.test_classes) == 1
        assert test_module.test_classes[0].test_methods[0].name == "test_multiply"

    def test_extract_test_info(self, test_project, symbol_table):
        """Test extracting test information."""
        analyzer = TestAnalyzer(symbol_table)
        test_file = test_project / "tests" / "test_calculator.py"

        test_module = analyzer.analyze_test_file(test_file)

        # Check test function info
        test_add = next(t for t in test_module.test_functions if t.name == "test_add")
        assert test_add.docstring == "Test addition."
        assert "add" in test_add.calls

    def test_extract_test_targets(self, test_project, symbol_table):
        """Test extracting what a test targets."""
        analyzer = TestAnalyzer(symbol_table)
        test_file = test_project / "tests" / "test_calculator.py"

        test_module = analyzer.analyze_test_file(test_file)
        targets = analyzer.extract_test_targets(test_module)

        assert "src.calculator" in targets


class TestCoverageMapper:
    """Tests for coverage mapping."""

    def test_map_tests_to_source(self, test_project, symbol_table, event_bus):
        """Test mapping tests to source code."""
        # Index the test project
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mappings = mapper.map_tests_to_source(test_project)

        assert len(mappings) > 0
        # Should map test_add to add function
        add_mappings = [m for m in mappings if "add" in m.source_symbol and "test_add" in m.test_name]
        assert len(add_mappings) > 0

    def test_get_tests_for_symbol(self, test_project, symbol_table, event_bus):
        """Test getting tests for a specific symbol."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        # Find the add function symbol
        add_symbol = None
        for sym in code_index.symbol_table._symbols.values():
            if sym.name == "add":
                add_symbol = sym
                break

        if add_symbol:
            tests = mapper.get_tests_for_symbol(add_symbol.qualified_name)
            assert len(tests) > 0
            assert any("test_add" in t.test_name for t in tests)

    def test_get_uncovered_symbols(self, test_project, symbol_table, event_bus):
        """Test finding uncovered symbols."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        uncovered = mapper.get_uncovered_symbols()
        # Some symbols might not be covered
        assert isinstance(uncovered, list)


class TestCoverageCalculator:
    """Tests for coverage calculation."""

    def test_calculate_project_coverage(self, test_project, symbol_table, event_bus):
        """Test calculating project-wide coverage."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        assert project_coverage.overall_metrics.total_items > 0
        assert project_coverage.overall_metrics.coverage_percentage >= 0
        assert len(project_coverage.module_coverage) > 0

    def test_coverage_metrics(self):
        """Test coverage metrics calculation."""
        metrics = CoverageMetrics(entity_name="test_module", entity_type="module", total_items=10, covered_items=7)

        # Coverage percentage should be calculated
        from a1.deep_context.test_coverage.coverage_calculator import CoverageCalculator

        calc = CoverageCalculator(None, None)  # Don't need real instances for this test
        calc._finalize_metrics(metrics)

        assert metrics.coverage_percentage == 70.0

    def test_get_coverage_summary(self, test_project, symbol_table, event_bus):
        """Test getting coverage summary."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        summary = calculator.get_coverage_summary(project_coverage)

        assert "overall_coverage" in summary
        assert "total_symbols" in summary
        assert "module_count" in summary
        assert summary["total_symbols"] > 0


class TestHistoryTracker:
    """Tests for test execution history tracking."""

    def test_record_test_run(self, event_bus):
        """Test recording a test run."""
        tracker = HistoryTracker(event_bus=event_bus)

        test_run = TestRun(
            test_name="test_example",
            test_file="test_example.py",
            timestamp=datetime.now(),
            duration_ms=100.5,
            status="passed",
            coverage_percentage=85.0,
        )

        tracker.record_test_run(test_run)

        # Verify it was recorded
        stats = tracker.get_test_stats("test_example")
        assert stats is not None
        assert stats.total_runs == 1
        assert stats.pass_count == 1
        assert stats.average_duration_ms == 100.5

    def test_test_statistics(self, event_bus):
        """Test calculating test statistics."""
        tracker = HistoryTracker(event_bus=event_bus)

        # Record multiple runs
        for i in range(5):
            test_run = TestRun(
                test_name="test_flaky",
                test_file="test_flaky.py",
                timestamp=datetime.now(),
                duration_ms=100 + i * 10,
                status="passed" if i % 2 == 0 else "failed",
            )
            tracker.record_test_run(test_run)

        stats = tracker.get_test_stats("test_flaky")
        assert stats.total_runs == 5
        assert stats.pass_count == 3
        assert stats.fail_count == 2
        assert stats.failure_rate == 0.4

    def test_flaky_test_detection(self, event_bus):
        """Test detecting flaky tests."""
        tracker = HistoryTracker(event_bus=event_bus)

        # Create a flaky test pattern
        statuses = ["passed", "failed", "passed", "failed", "passed"]
        for _i, status in enumerate(statuses):
            test_run = TestRun(
                test_name="test_flaky",
                test_file="test_flaky.py",
                timestamp=datetime.now(),
                duration_ms=100,
                status=status,
            )
            tracker.record_test_run(test_run)

        flaky_tests = tracker.get_flaky_tests(threshold=0.3)
        assert len(flaky_tests) > 0
        assert flaky_tests[0].test_name == "test_flaky"

    def test_performance_trend(self, event_bus):
        """Test tracking performance trends."""
        tracker = HistoryTracker(event_bus=event_bus)

        # Record runs with increasing duration
        for i in range(10):
            test_run = TestRun(
                test_name="test_slow",
                test_file="test_slow.py",
                timestamp=datetime.now(),
                duration_ms=100 + i * 20,  # Getting slower
                status="passed",
            )
            tracker.record_test_run(test_run)

        trend = tracker.get_performance_trend("test_slow")
        assert len(trend.values) == 10
        assert trend.trend_direction == "degrading"  # Getting slower


class TestReportGenerator:
    """Tests for report generation."""

    def test_generate_report(self, test_project, symbol_table, event_bus):
        """Test generating a coverage report."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        history_tracker = HistoryTracker(event_bus=event_bus)
        generator = ReportGenerator(calculator, mapper, history_tracker, event_bus)

        report = generator.generate_report(project_coverage)

        assert report.project_root == test_project
        assert report.total_symbols > 0
        assert isinstance(report.overall_coverage, float)
        assert len(report.module_coverage) > 0

    def test_text_report_generation(self, test_project, symbol_table, event_bus, tmp_path):
        """Test generating text report."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        generator = ReportGenerator(calculator, mapper, None, event_bus)
        report = generator.generate_report(project_coverage)

        # Generate text report
        output_path = tmp_path / "coverage.txt"
        text_content = generator.write_text_report(report, output_path)

        assert output_path.exists()
        assert "OVERALL COVERAGE" in text_content
        assert "MODULE COVERAGE" in text_content

    def test_json_report_generation(self, test_project, symbol_table, event_bus, tmp_path):
        """Test generating JSON report."""
        from a1.deep_context.code_index import CodeNavigationIndex

        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mapper.map_tests_to_source(test_project)

        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        generator = ReportGenerator(calculator, mapper, None, event_bus)
        report = generator.generate_report(project_coverage)

        # Generate JSON report
        output_path = tmp_path / "coverage.json"
        generator.write_json_report(report, output_path)

        assert output_path.exists()

        # Verify JSON is valid
        import json

        with open(output_path) as f:
            data = json.load(f)
            assert "overall_coverage" in data
            assert "module_coverage" in data


class TestIntegration:
    """Integration tests for the complete coverage system."""

    def test_full_coverage_workflow(self, test_project, event_bus):
        """Test the complete coverage workflow."""
        from a1.deep_context.code_index import CodeNavigationIndex

        # Step 1: Index the codebase
        code_index = CodeNavigationIndex(event_bus=event_bus)
        code_index.index_directory(test_project / "src")

        # Step 2: Map tests to source
        mapper = CoverageMapper(code_index.symbol_table, code_index, event_bus)
        mappings = mapper.map_tests_to_source(test_project)

        # Step 3: Calculate coverage
        calculator = CoverageCalculator(code_index.symbol_table, mapper, event_bus)
        project_coverage = calculator.calculate_project_coverage(test_project)

        # Step 4: Track history
        history_tracker = HistoryTracker(event_bus=event_bus)
        test_run = TestRun(
            test_name="test_add",
            test_file="tests/test_calculator.py",
            timestamp=datetime.now(),
            duration_ms=50.0,
            status="passed",
            coverage_percentage=project_coverage.overall_metrics.coverage_percentage,
        )
        history_tracker.record_test_run(test_run)

        # Step 5: Generate report
        generator = ReportGenerator(calculator, mapper, history_tracker, event_bus)
        report = generator.generate_report(project_coverage)

        # Verify complete workflow
        assert len(mappings) > 0
        assert project_coverage.overall_metrics.total_items > 0
        assert report.overall_coverage >= 0
        assert report.test_statistics  # Should have stats from history
