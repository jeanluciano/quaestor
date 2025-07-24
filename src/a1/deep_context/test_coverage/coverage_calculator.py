"""Coverage metrics calculator.

This module calculates various coverage metrics at different granularities
(function, class, module, project).
"""

from dataclasses import dataclass, field
from pathlib import Path

from a1.core.event_bus import EventBus

from ..events import SystemEvent
from ..symbol_table import SymbolTable, SymbolType
from .coverage_mapper import CoverageMapper


@dataclass
class CoverageMetrics:
    """Coverage metrics for a code entity."""

    entity_name: str
    entity_type: str  # 'function', 'class', 'module', 'package', 'project'
    total_items: int = 0
    covered_items: int = 0
    coverage_percentage: float = 0.0
    line_coverage: float = 0.0  # If available from external tools
    branch_coverage: float = 0.0  # If available from external tools
    complexity_weighted_coverage: float = 0.0
    test_count: int = 0
    direct_test_count: int = 0
    indirect_test_count: int = 0
    confidence_score: float = 0.0  # Average confidence of mappings


@dataclass
class ModuleCoverage:
    """Coverage metrics for a module."""

    module_path: Path
    module_name: str
    metrics: CoverageMetrics
    function_coverage: dict[str, CoverageMetrics] = field(default_factory=dict)
    class_coverage: dict[str, CoverageMetrics] = field(default_factory=dict)
    uncovered_symbols: list[str] = field(default_factory=list)


@dataclass
class ProjectCoverage:
    """Coverage metrics for the entire project."""

    project_root: Path
    overall_metrics: CoverageMetrics
    module_coverage: dict[str, ModuleCoverage] = field(default_factory=dict)
    package_coverage: dict[str, CoverageMetrics] = field(default_factory=dict)
    coverage_gaps: list[str] = field(default_factory=list)  # High-priority uncovered items


class CoverageCalculator:
    """Calculates coverage metrics from test mappings."""

    def __init__(self, symbol_table: SymbolTable, coverage_mapper: CoverageMapper, event_bus: EventBus | None = None):
        """Initialize the coverage calculator.

        Args:
            symbol_table: Symbol table with source code information
            coverage_mapper: Mapper with test-to-source mappings
            event_bus: Optional event bus for calculation events
        """
        self.symbol_table = symbol_table
        self.coverage_mapper = coverage_mapper
        self.event_bus = event_bus

    def calculate_project_coverage(self, project_root: Path) -> ProjectCoverage:
        """Calculate coverage metrics for the entire project.

        Args:
            project_root: Root directory of the project

        Returns:
            ProjectCoverage with comprehensive metrics
        """
        if self.event_bus:
            self.event_bus.emit(SystemEvent(type="coverage_calculation_started", data={"root": str(project_root)}))

        # Initialize project coverage
        project_coverage = ProjectCoverage(
            project_root=project_root,
            overall_metrics=CoverageMetrics(entity_name=str(project_root), entity_type="project"),
        )

        # Get all modules
        modules = self._get_all_modules()

        # Calculate coverage for each module
        for module_path, module_symbols in modules.items():
            module_coverage = self._calculate_module_coverage(module_path, module_symbols)
            project_coverage.module_coverage[module_coverage.module_name] = module_coverage

            # Update project totals
            project_coverage.overall_metrics.total_items += module_coverage.metrics.total_items
            project_coverage.overall_metrics.covered_items += module_coverage.metrics.covered_items
            project_coverage.overall_metrics.test_count += module_coverage.metrics.test_count

        # Calculate project-level metrics
        self._finalize_metrics(project_coverage.overall_metrics)

        # Calculate package-level coverage
        project_coverage.package_coverage = self._calculate_package_coverage(project_coverage.module_coverage)

        # Identify coverage gaps
        project_coverage.coverage_gaps = self._identify_coverage_gaps(project_coverage)

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="coverage_calculation_completed",
                    data={
                        "root": str(project_root),
                        "coverage_percentage": project_coverage.overall_metrics.coverage_percentage,
                        "total_modules": len(project_coverage.module_coverage),
                    },
                )
            )

        return project_coverage

    def calculate_file_coverage(self, file_path: Path) -> ModuleCoverage:
        """Calculate coverage metrics for a single file.

        Args:
            file_path: Path to the source file

        Returns:
            ModuleCoverage for the file
        """
        # Get symbols in the file
        symbols = self.symbol_table.get_symbols_in_file(file_path)
        module_symbols = {"functions": [], "classes": [], "methods": []}

        for symbol in symbols:
            if symbol.symbol_type == SymbolType.FUNCTION:
                module_symbols["functions"].append(symbol)
            elif symbol.symbol_type == SymbolType.CLASS:
                module_symbols["classes"].append(symbol)
            elif symbol.symbol_type == SymbolType.METHOD:
                module_symbols["methods"].append(symbol)

        return self._calculate_module_coverage(file_path, module_symbols)

    def get_coverage_summary(self, project_coverage: ProjectCoverage) -> dict[str, any]:
        """Get a summary of coverage metrics.

        Args:
            project_coverage: Complete project coverage data

        Returns:
            Dictionary with summary statistics
        """
        # Find best and worst covered modules
        sorted_modules = sorted(
            project_coverage.module_coverage.values(),
            key=lambda m: m.metrics.coverage_percentage,
            reverse=True,
        )

        best_modules = [(m.module_name, m.metrics.coverage_percentage) for m in sorted_modules[:5]]
        worst_modules = [
            (m.module_name, m.metrics.coverage_percentage) for m in sorted_modules[-5:] if m.metrics.total_items > 0
        ]

        # Coverage by type
        type_coverage = self._calculate_type_coverage(project_coverage)

        return {
            "overall_coverage": project_coverage.overall_metrics.coverage_percentage,
            "total_symbols": project_coverage.overall_metrics.total_items,
            "covered_symbols": project_coverage.overall_metrics.covered_items,
            "total_tests": project_coverage.overall_metrics.test_count,
            "module_count": len(project_coverage.module_coverage),
            "best_covered_modules": best_modules,
            "worst_covered_modules": worst_modules,
            "coverage_by_type": type_coverage,
            "coverage_gaps": len(project_coverage.coverage_gaps),
            "average_confidence": project_coverage.overall_metrics.confidence_score,
        }

    def _calculate_module_coverage(self, module_path: Path, module_symbols: dict) -> ModuleCoverage:
        """Calculate coverage for a module."""
        module_name = self._path_to_module_name(module_path)

        module_coverage = ModuleCoverage(
            module_path=module_path,
            module_name=module_name,
            metrics=CoverageMetrics(entity_name=module_name, entity_type="module"),
        )

        # Calculate function coverage
        for func_symbol in module_symbols.get("functions", []):
            func_metrics = self._calculate_symbol_coverage(func_symbol, "function")
            module_coverage.function_coverage[func_symbol.name] = func_metrics
            module_coverage.metrics.total_items += 1
            if func_metrics.covered_items > 0:
                module_coverage.metrics.covered_items += 1
                module_coverage.metrics.test_count += func_metrics.test_count

        # Calculate class coverage
        for class_symbol in module_symbols.get("classes", []):
            class_metrics = self._calculate_class_coverage(class_symbol)
            module_coverage.class_coverage[class_symbol.name] = class_metrics
            module_coverage.metrics.total_items += class_metrics.total_items
            module_coverage.metrics.covered_items += class_metrics.covered_items
            module_coverage.metrics.test_count += class_metrics.test_count

        # Find uncovered symbols
        all_symbols = module_symbols.get("functions", []) + module_symbols.get("classes", [])
        for symbol in all_symbols:
            coverage_info = self.coverage_mapper._source_coverage.get(symbol.qualified_name)
            if coverage_info and not coverage_info.is_covered:
                module_coverage.uncovered_symbols.append(symbol.qualified_name)

        # Finalize module metrics
        self._finalize_metrics(module_coverage.metrics)

        return module_coverage

    def _calculate_symbol_coverage(self, symbol, entity_type: str) -> CoverageMetrics:
        """Calculate coverage for a single symbol."""
        metrics = CoverageMetrics(entity_name=symbol.name, entity_type=entity_type)

        # Get coverage info from mapper
        coverage_info = self.coverage_mapper._source_coverage.get(symbol.qualified_name)
        if coverage_info:
            metrics.total_items = 1
            metrics.covered_items = 1 if coverage_info.is_covered else 0
            metrics.test_count = len(coverage_info.covering_tests)
            metrics.confidence_score = coverage_info.coverage_confidence

            # Count direct vs indirect tests
            mappings = self.coverage_mapper.get_tests_for_symbol(symbol.qualified_name)
            metrics.direct_test_count = sum(1 for m in mappings if m.mapping_type == "direct")
            metrics.indirect_test_count = metrics.test_count - metrics.direct_test_count

        # Add complexity weighting if available
        if hasattr(symbol, "metadata") and "complexity" in symbol.metadata:
            complexity = symbol.metadata["complexity"]
            metrics.complexity_weighted_coverage = metrics.coverage_percentage * (1 + complexity / 10)

        self._finalize_metrics(metrics)
        return metrics

    def _calculate_class_coverage(self, class_symbol) -> CoverageMetrics:
        """Calculate coverage for a class including its methods."""
        class_metrics = CoverageMetrics(entity_name=class_symbol.name, entity_type="class")

        # Get all methods of the class
        class_methods = self.symbol_table.get_children(class_symbol.qualified_name)

        # Calculate coverage for each method
        for method in class_methods:
            if method.symbol_type == SymbolType.METHOD:
                method_coverage = self._calculate_symbol_coverage(method, "method")
                class_metrics.total_items += 1
                if method_coverage.covered_items > 0:
                    class_metrics.covered_items += 1
                    class_metrics.test_count += method_coverage.test_count

        # Check if class itself is tested (e.g., instantiation tests)
        class_coverage_info = self.coverage_mapper._source_coverage.get(class_symbol.qualified_name)
        if class_coverage_info and class_coverage_info.is_covered:
            class_metrics.test_count += len(class_coverage_info.covering_tests)
            class_metrics.confidence_score = class_coverage_info.coverage_confidence

        self._finalize_metrics(class_metrics)
        return class_metrics

    def _calculate_package_coverage(self, module_coverage: dict[str, ModuleCoverage]) -> dict[str, CoverageMetrics]:
        """Calculate coverage metrics for packages."""
        package_coverage = {}

        for module_name, coverage in module_coverage.items():
            # Extract package name
            parts = module_name.split(".")
            package_name = parts[0] if len(parts) > 1 else "__root__"

            if package_name not in package_coverage:
                package_coverage[package_name] = CoverageMetrics(entity_name=package_name, entity_type="package")

            # Aggregate metrics
            pkg_metrics = package_coverage[package_name]
            pkg_metrics.total_items += coverage.metrics.total_items
            pkg_metrics.covered_items += coverage.metrics.covered_items
            pkg_metrics.test_count += coverage.metrics.test_count

        # Finalize package metrics
        for metrics in package_coverage.values():
            self._finalize_metrics(metrics)

        return package_coverage

    def _identify_coverage_gaps(self, project_coverage: ProjectCoverage) -> list[str]:
        """Identify high-priority coverage gaps."""
        gaps = []

        # Find completely uncovered modules
        for module_coverage in project_coverage.module_coverage.values():
            if module_coverage.metrics.coverage_percentage == 0 and module_coverage.metrics.total_items > 0:
                gaps.append(f"Module '{module_coverage.module_name}' has no test coverage")

        # Find uncovered critical functions (main, __init__, etc.)
        critical_patterns = ["__init__", "main", "setup", "connect", "execute", "process"]
        for module_coverage in project_coverage.module_coverage.values():
            for func_name in module_coverage.uncovered_symbols:
                if any(pattern in func_name.lower() for pattern in critical_patterns):
                    gaps.append(f"Critical function '{func_name}' is not tested")

        # Find low-coverage packages
        for package_name, metrics in project_coverage.package_coverage.items():
            if metrics.coverage_percentage < 20 and metrics.total_items > 5:
                gaps.append(f"Package '{package_name}' has very low coverage ({metrics.coverage_percentage:.1f}%)")

        return gaps[:10]  # Return top 10 gaps

    def _calculate_type_coverage(self, project_coverage: ProjectCoverage) -> dict[str, float]:
        """Calculate coverage by symbol type."""
        type_totals = {"function": 0, "method": 0, "class": 0}
        type_covered = {"function": 0, "method": 0, "class": 0}

        for module_coverage in project_coverage.module_coverage.values():
            # Functions
            type_totals["function"] += len(module_coverage.function_coverage)
            type_covered["function"] += sum(
                1 for m in module_coverage.function_coverage.values() if m.covered_items > 0
            )

            # Classes and methods
            for class_metrics in module_coverage.class_coverage.values():
                type_totals["class"] += 1
                if class_metrics.covered_items > 0:
                    type_covered["class"] += 1
                type_totals["method"] += class_metrics.total_items
                type_covered["method"] += class_metrics.covered_items

        # Calculate percentages
        type_coverage = {}
        for symbol_type in type_totals:
            if type_totals[symbol_type] > 0:
                type_coverage[symbol_type] = (type_covered[symbol_type] / type_totals[symbol_type]) * 100
            else:
                type_coverage[symbol_type] = 0.0

        return type_coverage

    def _finalize_metrics(self, metrics: CoverageMetrics) -> None:
        """Calculate final metric values."""
        if metrics.total_items > 0:
            metrics.coverage_percentage = (metrics.covered_items / metrics.total_items) * 100
        else:
            metrics.coverage_percentage = 100.0  # Empty modules are "fully covered"

    def _get_all_modules(self) -> dict[Path, dict]:
        """Get all modules and their symbols."""
        modules = {}

        for _qualified_name, symbol in self.symbol_table._symbols.items():
            if symbol.symbol_type == SymbolType.MODULE:
                continue

            file_path = symbol.location.file_path
            if file_path not in modules:
                modules[file_path] = {"functions": [], "classes": [], "methods": []}

            if symbol.symbol_type == SymbolType.FUNCTION:
                modules[file_path]["functions"].append(symbol)
            elif symbol.symbol_type == SymbolType.CLASS:
                modules[file_path]["classes"].append(symbol)
            elif symbol.symbol_type == SymbolType.METHOD:
                modules[file_path]["methods"].append(symbol)

        return modules

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        parts = list(file_path.parts)
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)
