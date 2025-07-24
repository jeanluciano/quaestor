"""CLI demonstration for test coverage mapping functionality."""

import time
from datetime import datetime
from pathlib import Path

from rich.console import Console

from a1.core.event_bus import EventBus

from ..code_index import CodeNavigationIndex
from ..symbol_table import SymbolTable
from .coverage_calculator import CoverageCalculator
from .coverage_mapper import CoverageMapper
from .history_tracker import HistoryTracker, TestRun
from .report_generator import ReportGenerator


def demonstrate_test_coverage():
    """Demonstrate the test coverage mapping functionality."""
    console = Console()
    console.print("[bold cyan]Test Coverage Mapping Demonstration[/bold cyan]\n")

    # Initialize components
    event_bus = EventBus()
    symbol_table = SymbolTable(event_bus)
    code_index = CodeNavigationIndex(event_bus=event_bus)
    coverage_mapper = CoverageMapper(symbol_table, code_index, event_bus)
    coverage_calculator = CoverageCalculator(symbol_table, coverage_mapper, event_bus)
    history_tracker = HistoryTracker(event_bus=event_bus)
    report_generator = ReportGenerator(coverage_calculator, coverage_mapper, history_tracker, event_bus)

    # Get project root (current directory for demo)
    project_root = Path.cwd()

    # Step 1: Index the codebase
    console.print("[yellow]Step 1: Indexing codebase...[/yellow]")
    start_time = time.time()
    code_index.index_directory(project_root / "src")
    index_time = time.time() - start_time
    console.print(f"✓ Indexed codebase in {index_time:.2f}s\n")

    # Step 2: Discover and map tests
    console.print("[yellow]Step 2: Discovering and mapping tests...[/yellow]")
    start_time = time.time()
    mappings = coverage_mapper.map_tests_to_source(project_root)
    map_time = time.time() - start_time
    console.print(f"✓ Created {len(mappings)} test-to-source mappings in {map_time:.2f}s\n")

    # Step 3: Calculate coverage metrics
    console.print("[yellow]Step 3: Calculating coverage metrics...[/yellow]")
    start_time = time.time()
    project_coverage = coverage_calculator.calculate_project_coverage(project_root)
    calc_time = time.time() - start_time
    console.print(f"✓ Calculated coverage metrics in {calc_time:.2f}s\n")

    # Step 4: Generate report
    console.print("[yellow]Step 4: Generating coverage report...[/yellow]")
    report = report_generator.generate_report(project_coverage)
    report_generator.print_summary(report)

    # Save reports
    reports_dir = Path("coverage_reports")
    reports_dir.mkdir(exist_ok=True)

    report_generator.write_text_report(report, reports_dir / "coverage.txt")
    report_generator.write_json_report(report, reports_dir / "coverage.json")
    report_generator.write_markdown_report(report, reports_dir / "coverage.md")
    report_generator.write_html_report(report, reports_dir / "coverage.html")

    console.print(f"\n✓ Reports saved to {reports_dir}/")

    # Demonstrate specific queries
    console.print("\n[bold cyan]Example Queries:[/bold cyan]")

    # Query 1: Find tests for a specific symbol
    console.print("\n[yellow]Query: What tests cover the 'SymbolTable' class?[/yellow]")
    symbol_tests = coverage_mapper.get_tests_for_symbol("symbol_table.SymbolTable")
    if symbol_tests:
        for mapping in symbol_tests[:3]:
            console.print(f"  - {mapping.test_name} (confidence: {mapping.confidence:.2f})")
    else:
        console.print("  No tests found")

    # Query 2: Find uncovered symbols
    console.print("\n[yellow]Query: What symbols have no test coverage?[/yellow]")
    uncovered = coverage_mapper.get_uncovered_symbols()
    for symbol in uncovered[:5]:
        console.print(f"  - {symbol.symbol_name} ({symbol.symbol_type.value})")
    if len(uncovered) > 5:
        console.print(f"  ... and {len(uncovered) - 5} more")

    # Demonstrate history tracking (simulated)
    console.print("\n[bold cyan]Simulating Test Execution History:[/bold cyan]")

    # Simulate some test runs
    test_runs = [
        TestRun(
            test_name="test_symbol_table_add",
            test_file="tests/test_symbol_table.py",
            timestamp=datetime.now(),
            duration_ms=45.2,
            status="passed",
            coverage_percentage=85.3,
        ),
        TestRun(
            test_name="test_coverage_calculation",
            test_file="tests/test_coverage.py",
            timestamp=datetime.now(),
            duration_ms=123.5,
            status="passed",
            coverage_percentage=82.1,
        ),
        TestRun(
            test_name="test_flaky_behavior",
            test_file="tests/test_integration.py",
            timestamp=datetime.now(),
            duration_ms=234.1,
            status="failed",
            failure_message="Timeout waiting for response",
        ),
    ]

    for run in test_runs:
        history_tracker.record_test_run(run)

    # Show test statistics
    console.print("\n[yellow]Test Statistics:[/yellow]")
    for run in test_runs:
        stats = history_tracker.get_test_stats(run.test_name)
        if stats:
            console.print(f"  - {stats.test_name}: {stats.last_status} (avg: {stats.average_duration_ms:.1f}ms)")

    console.print("\n[green]✓ Test coverage mapping demonstration complete![/green]")


def main():
    """CLI entry point."""
    demonstrate_test_coverage()


if __name__ == "__main__":
    main()
