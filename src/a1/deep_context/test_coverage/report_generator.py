"""Coverage report generation in various formats.

This module generates human-readable coverage reports in multiple formats
including text, HTML, JSON, and Markdown.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from a1.core.event_bus import EventBus

from ..events import SystemEvent
from .coverage_calculator import CoverageCalculator, ProjectCoverage
from .coverage_mapper import CoverageMapper
from .history_tracker import HistoryTracker


@dataclass
class CoverageReport:
    """Complete coverage report data."""

    project_root: Path
    generated_at: datetime
    overall_coverage: float
    total_symbols: int
    covered_symbols: int
    total_tests: int
    module_coverage: dict[str, dict]
    coverage_gaps: list[str]
    test_statistics: dict[str, any]
    recommendations: list[str]


class ReportGenerator:
    """Generates coverage reports in various formats."""

    def __init__(
        self,
        coverage_calculator: CoverageCalculator,
        coverage_mapper: CoverageMapper,
        history_tracker: HistoryTracker | None = None,
        event_bus: EventBus | None = None,
    ):
        """Initialize the report generator.

        Args:
            coverage_calculator: Calculator for coverage metrics
            coverage_mapper: Mapper with test-to-source mappings
            history_tracker: Optional history tracker for trends
            event_bus: Optional event bus for report events
        """
        self.coverage_calculator = coverage_calculator
        self.coverage_mapper = coverage_mapper
        self.history_tracker = history_tracker
        self.event_bus = event_bus
        self.console = Console()

    def generate_report(self, project_coverage: ProjectCoverage) -> CoverageReport:
        """Generate a complete coverage report.

        Args:
            project_coverage: Project coverage data

        Returns:
            CoverageReport with all report data
        """
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(type="report_generation_started", data={"root": str(project_coverage.project_root)})
            )

        # Get test statistics if history is available
        test_stats = {}
        if self.history_tracker:
            test_stats = self._generate_test_statistics()

        # Generate recommendations
        recommendations = self._generate_recommendations(project_coverage, test_stats)

        # Build module coverage data
        module_data = {}
        for module_name, module_cov in project_coverage.module_coverage.items():
            module_data[module_name] = {
                "coverage_percentage": module_cov.metrics.coverage_percentage,
                "total_symbols": module_cov.metrics.total_items,
                "covered_symbols": module_cov.metrics.covered_items,
                "test_count": module_cov.metrics.test_count,
                "uncovered": module_cov.uncovered_symbols,
            }

        report = CoverageReport(
            project_root=project_coverage.project_root,
            generated_at=datetime.now(),
            overall_coverage=project_coverage.overall_metrics.coverage_percentage,
            total_symbols=project_coverage.overall_metrics.total_items,
            covered_symbols=project_coverage.overall_metrics.covered_items,
            total_tests=project_coverage.overall_metrics.test_count,
            module_coverage=module_data,
            coverage_gaps=project_coverage.coverage_gaps,
            test_statistics=test_stats,
            recommendations=recommendations,
        )

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(type="report_generation_completed", data={"coverage": report.overall_coverage})
            )

        return report

    def write_text_report(self, report: CoverageReport, output_path: Path | None = None) -> str:
        """Generate a text coverage report.

        Args:
            report: Coverage report data
            output_path: Optional path to write report

        Returns:
            Text report content
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"Coverage Report for {report.project_root}")
        lines.append(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # Overall summary
        lines.append("OVERALL COVERAGE")
        lines.append("-" * 40)
        lines.append(f"Coverage: {report.overall_coverage:.1f}%")
        lines.append(f"Total Symbols: {report.total_symbols}")
        lines.append(f"Covered Symbols: {report.covered_symbols}")
        lines.append(f"Total Tests: {report.total_tests}")
        lines.append("")

        # Module breakdown
        lines.append("MODULE COVERAGE")
        lines.append("-" * 40)
        lines.append(f"{'Module':<40} {'Coverage':>10} {'Symbols':>10} {'Tests':>10}")
        lines.append("-" * 70)

        sorted_modules = sorted(report.module_coverage.items(), key=lambda x: x[1]["coverage_percentage"], reverse=True)

        for module_name, data in sorted_modules:
            coverage_str = f"{data['coverage_percentage']:.1f}%"
            symbols_str = f"{data['covered_symbols']}/{data['total_symbols']}"
            tests_str = str(data["test_count"])
            lines.append(f"{module_name:<40} {coverage_str:>10} {symbols_str:>10} {tests_str:>10}")

        lines.append("")

        # Coverage gaps
        if report.coverage_gaps:
            lines.append("COVERAGE GAPS")
            lines.append("-" * 40)
            for i, gap in enumerate(report.coverage_gaps[:10], 1):
                lines.append(f"{i}. {gap}")
            lines.append("")

        # Test statistics
        if report.test_statistics:
            lines.append("TEST STATISTICS")
            lines.append("-" * 40)
            if "flaky_tests" in report.test_statistics:
                lines.append(f"Flaky Tests: {len(report.test_statistics['flaky_tests'])}")
            if "slow_tests" in report.test_statistics:
                lines.append(f"Slow Tests: {len(report.test_statistics['slow_tests'])}")
            if "failing_tests" in report.test_statistics:
                lines.append(f"Failing Tests: {len(report.test_statistics['failing_tests'])}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        content = "\n".join(lines)

        if output_path:
            output_path.write_text(content)

        return content

    def write_json_report(self, report: CoverageReport, output_path: Path) -> None:
        """Write coverage report as JSON.

        Args:
            report: Coverage report data
            output_path: Path to write JSON report
        """
        report_dict = asdict(report)
        # Convert datetime to string
        report_dict["generated_at"] = report.generated_at.isoformat()
        # Convert Path to string
        report_dict["project_root"] = str(report.project_root)

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)

    def write_markdown_report(self, report: CoverageReport, output_path: Path) -> None:
        """Write coverage report as Markdown.

        Args:
            report: Coverage report data
            output_path: Path to write Markdown report
        """
        lines = []
        lines.append(f"# Coverage Report: {report.project_root.name}")
        lines.append(f"*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        # Summary badges
        coverage_color = (
            "green" if report.overall_coverage >= 80 else "yellow" if report.overall_coverage >= 60 else "red"
        )
        lines.append(
            f"![Coverage](https://img.shields.io/badge/coverage-{report.overall_coverage:.1f}%25-{coverage_color})"
        )
        lines.append(f"![Tests](https://img.shields.io/badge/tests-{report.total_tests}-blue)")
        lines.append("")

        # Overall metrics
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Overall Coverage | **{report.overall_coverage:.1f}%** |")
        lines.append(f"| Total Symbols | {report.total_symbols} |")
        lines.append(f"| Covered Symbols | {report.covered_symbols} |")
        lines.append(f"| Total Tests | {report.total_tests} |")
        lines.append("")

        # Module coverage table
        lines.append("## Module Coverage")
        lines.append("")
        lines.append("| Module | Coverage | Symbols | Tests |")
        lines.append("|--------|----------|---------|-------|")

        sorted_modules = sorted(report.module_coverage.items(), key=lambda x: x[1]["coverage_percentage"], reverse=True)

        for module_name, data in sorted_modules[:20]:  # Top 20 modules
            coverage_str = f"{data['coverage_percentage']:.1f}%"
            symbols_str = f"{data['covered_symbols']}/{data['total_symbols']}"
            lines.append(f"| `{module_name}` | {coverage_str} | {symbols_str} | {data['test_count']} |")

        if len(sorted_modules) > 20:
            lines.append("| ... | ... | ... | ... |")
            lines.append(f"| *{len(sorted_modules) - 20} more modules* | | | |")

        lines.append("")

        # Coverage gaps
        if report.coverage_gaps:
            lines.append("## Coverage Gaps")
            lines.append("")
            lines.append("Critical areas lacking test coverage:")
            lines.append("")
            for gap in report.coverage_gaps[:10]:
                lines.append(f"- {gap}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Test health (if available)
        if report.test_statistics:
            lines.append("## Test Health")
            lines.append("")
            if "flaky_tests" in report.test_statistics and report.test_statistics["flaky_tests"]:
                lines.append("### ⚠️ Flaky Tests")
                for test in report.test_statistics["flaky_tests"][:5]:
                    lines.append(f"- `{test['name']}` (flakiness: {test['score']:.2f})")
                lines.append("")

            if "slow_tests" in report.test_statistics and report.test_statistics["slow_tests"]:
                lines.append("### 🐌 Slow Tests")
                for test in report.test_statistics["slow_tests"][:5]:
                    lines.append(f"- `{test['name']}` ({test['duration']:.0f}ms)")
                lines.append("")

        output_path.write_text("\n".join(lines))

    def write_html_report(self, report: CoverageReport, output_path: Path) -> None:
        """Write coverage report as HTML.

        Args:
            report: Coverage report data
            output_path: Path to write HTML report
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report - {report.project_root.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .coverage-high {{ color: #28a745; }}
        .coverage-medium {{ color: #ffc107; }}
        .coverage-low {{ color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .progress-bar {{ width: 100px; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #28a745; }}
        .gap {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .recommendation {{ background: #d1ecf1; padding: 10px; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Coverage Report: {report.project_root.name}</h1>
        <p>Generated: {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="metrics">
        <div class="metric">
            <div class="metric-label">Overall Coverage</div>
            <div class="metric-value {self._get_coverage_class(report.overall_coverage)}">
                {report.overall_coverage:.1f}%
            </div>
        </div>
        <div class="metric">
            <div class="metric-label">Total Symbols</div>
            <div class="metric-value">{report.total_symbols}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Covered Symbols</div>
            <div class="metric-value">{report.covered_symbols}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Total Tests</div>
            <div class="metric-value">{report.total_tests}</div>
        </div>
    </div>

    <h2>Module Coverage</h2>
    <table>
        <tr>
            <th>Module</th>
            <th>Coverage</th>
            <th>Progress</th>
            <th>Symbols</th>
            <th>Tests</th>
        </tr>
"""

        sorted_modules = sorted(report.module_coverage.items(), key=lambda x: x[1]["coverage_percentage"], reverse=True)

        for module_name, data in sorted_modules:
            coverage = data["coverage_percentage"]
            html += f"""
        <tr>
            <td><code>{module_name}</code></td>
            <td class="{self._get_coverage_class(coverage)}">{coverage:.1f}%</td>
            <td>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {coverage}%"></div>
                </div>
            </td>
            <td>{data["covered_symbols"]}/{data["total_symbols"]}</td>
            <td>{data["test_count"]}</td>
        </tr>
"""

        html += """
    </table>
"""

        if report.coverage_gaps:
            html += """
    <h2>Coverage Gaps</h2>
"""
            for gap in report.coverage_gaps[:10]:
                html += f'    <div class="gap">{gap}</div>\n'

        if report.recommendations:
            html += """
    <h2>Recommendations</h2>
"""
            for rec in report.recommendations:
                html += f'    <div class="recommendation">{rec}</div>\n'

        html += """
</body>
</html>
"""

        output_path.write_text(html)

    def print_summary(self, report: CoverageReport) -> None:
        """Print a summary of the coverage report to console.

        Args:
            report: Coverage report data
        """
        # Create coverage summary table
        table = Table(title=f"Coverage Report for {report.project_root.name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        coverage_style = (
            "green" if report.overall_coverage >= 80 else "yellow" if report.overall_coverage >= 60 else "red"
        )
        table.add_row("Overall Coverage", f"[{coverage_style}]{report.overall_coverage:.1f}%[/{coverage_style}]")
        table.add_row("Total Symbols", str(report.total_symbols))
        table.add_row("Covered Symbols", str(report.covered_symbols))
        table.add_row("Total Tests", str(report.total_tests))

        self.console.print(table)

        # Show top coverage gaps
        if report.coverage_gaps:
            self.console.print("\n[bold red]Top Coverage Gaps:[/bold red]")
            for i, gap in enumerate(report.coverage_gaps[:5], 1):
                self.console.print(f"  {i}. {gap}")

        # Show recommendations
        if report.recommendations:
            self.console.print("\n[bold blue]Recommendations:[/bold blue]")
            for i, rec in enumerate(report.recommendations[:3], 1):
                self.console.print(f"  {i}. {rec}")

    def _generate_test_statistics(self) -> dict[str, any]:
        """Generate test statistics from history."""
        if not self.history_tracker:
            return {}

        stats = {}

        # Get flaky tests
        flaky_tests = self.history_tracker.get_flaky_tests(threshold=0.2)
        stats["flaky_tests"] = [{"name": test.test_name, "score": test.flakiness_score} for test in flaky_tests[:10]]

        # Get slow tests
        all_stats = self.history_tracker.get_all_test_stats()
        slow_tests = sorted(all_stats, key=lambda x: x.average_duration_ms, reverse=True)[:10]
        stats["slow_tests"] = [{"name": test.test_name, "duration": test.average_duration_ms} for test in slow_tests]

        # Get failing tests
        failing_tests = self.history_tracker.get_failing_tests()
        stats["failing_tests"] = [
            {"name": test.test_name, "failure_rate": test.failure_rate} for test in failing_tests[:10]
        ]

        # Get coverage trend
        coverage_trend = self.history_tracker.get_coverage_trend()
        stats["coverage_trend"] = {
            "direction": coverage_trend.trend_direction,
            "change_percentage": coverage_trend.change_percentage,
        }

        return stats

    def _generate_recommendations(self, project_coverage: ProjectCoverage, test_stats: dict) -> list[str]:
        """Generate actionable recommendations based on coverage data."""
        recommendations = []

        # Low overall coverage
        if project_coverage.overall_metrics.coverage_percentage < 60:
            recommendations.append(
                f"Overall coverage is low ({project_coverage.overall_metrics.coverage_percentage:.1f}%). "
                "Consider adding tests for critical functionality."
            )

        # Modules with zero coverage
        zero_coverage_modules = [
            name
            for name, cov in project_coverage.module_coverage.items()
            if cov.metrics.coverage_percentage == 0 and cov.metrics.total_items > 0
        ]
        if zero_coverage_modules:
            recommendations.append(f"Add tests for completely untested modules: {', '.join(zero_coverage_modules[:3])}")

        # Large coverage gaps
        if len(project_coverage.coverage_gaps) > 10:
            recommendations.append("Focus on testing critical functions identified in coverage gaps")

        # Flaky tests
        if test_stats.get("flaky_tests"):
            recommendations.append(f"Fix {len(test_stats['flaky_tests'])} flaky tests to improve test reliability")

        # Slow tests
        if test_stats.get("slow_tests") and test_stats["slow_tests"][0]["duration"] > 1000:
            recommendations.append(
                "Optimize slow tests - longest test takes {:.1f}s".format(
                    test_stats["slow_tests"][0]["duration"] / 1000
                )
            )

        # Coverage trend
        if test_stats.get("coverage_trend", {}).get("direction") == "degrading":
            recommendations.append("Coverage is declining - ensure new code includes tests")

        return recommendations

    def _get_coverage_class(self, coverage: float) -> str:
        """Get CSS class for coverage percentage."""
        if coverage >= 80:
            return "coverage-high"
        elif coverage >= 60:
            return "coverage-medium"
        else:
            return "coverage-low"
