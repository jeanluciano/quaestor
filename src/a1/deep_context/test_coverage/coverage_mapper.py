"""Maps tests to source code for coverage analysis.

This module creates mappings between test code and the source code it tests,
enabling accurate coverage tracking.
"""

from dataclasses import dataclass, field
from pathlib import Path

from a1.core.event_bus import EventBus

from ..code_index import CodeNavigationIndex
from ..events import SystemEvent
from ..symbol_table import Symbol, SymbolTable, SymbolType
from .test_analyzer import TestAnalyzer, TestInfo, TestModule
from .test_discovery import TestDiscovery, TestFile


@dataclass
class TestMapping:
    """Mapping between a test and what it tests."""

    test_name: str  # Qualified test name
    test_file: Path
    test_line: int
    source_symbol: str  # Qualified name of source symbol
    source_file: Path
    source_line: int
    confidence: float  # 0.0 to 1.0
    mapping_type: str  # 'direct', 'indirect', 'inferred'


@dataclass
class SourceCoverage:
    """Coverage information for a source symbol."""

    symbol_name: str
    symbol_type: SymbolType
    file_path: Path
    line_start: int
    line_end: int
    covering_tests: list[str] = field(default_factory=list)
    coverage_confidence: float = 0.0
    is_covered: bool = False


class CoverageMapper:
    """Maps tests to source code for coverage analysis."""

    def __init__(
        self,
        symbol_table: SymbolTable,
        code_index: CodeNavigationIndex | None = None,
        event_bus: EventBus | None = None,
    ):
        """Initialize the coverage mapper.

        Args:
            symbol_table: Symbol table with source code information
            code_index: Optional code navigation index for enhanced mapping
            event_bus: Optional event bus for mapping events
        """
        self.symbol_table = symbol_table
        self.code_index = code_index
        self.event_bus = event_bus
        self.test_discovery = TestDiscovery(event_bus=event_bus)
        self.test_analyzer = TestAnalyzer(symbol_table=symbol_table, event_bus=event_bus)
        self._mappings: list[TestMapping] = []
        self._source_coverage: dict[str, SourceCoverage] = {}

    def map_tests_to_source(self, project_root: Path) -> list[TestMapping]:
        """Create mappings between tests and source code.

        Args:
            project_root: Root directory of the project

        Returns:
            List of test-to-source mappings
        """
        # Clear existing mappings
        self._mappings.clear()
        self._source_coverage.clear()

        # Emit start event
        if self.event_bus:
            self.event_bus.emit(SystemEvent(type="coverage_mapping_started", data={"root": str(project_root)}))

        # Discover test files
        test_files = self.test_discovery.discover_tests(project_root)

        # Analyze each test file
        for test_file in test_files:
            self._process_test_file(test_file, project_root)

        # Calculate coverage for all source symbols
        self._calculate_source_coverage()

        # Emit completion event
        if self.event_bus:
            stats = self.get_coverage_statistics()
            self.event_bus.emit(
                SystemEvent(type="coverage_mapping_completed", data={"mappings": len(self._mappings), "stats": stats})
            )

        return self._mappings

    def get_tests_for_symbol(self, symbol_name: str) -> list[TestMapping]:
        """Get all tests that cover a specific symbol.

        Args:
            symbol_name: Qualified name of the symbol

        Returns:
            List of test mappings for the symbol
        """
        return [mapping for mapping in self._mappings if mapping.source_symbol == symbol_name]

    def get_coverage_for_file(self, file_path: Path) -> list[SourceCoverage]:
        """Get coverage information for all symbols in a file.

        Args:
            file_path: Path to the source file

        Returns:
            List of coverage information for symbols in the file
        """
        coverages = []
        for coverage in self._source_coverage.values():
            if coverage.file_path == file_path:
                coverages.append(coverage)
        return coverages

    def get_uncovered_symbols(self) -> list[SourceCoverage]:
        """Get all symbols that have no test coverage.

        Returns:
            List of uncovered symbols
        """
        return [coverage for coverage in self._source_coverage.values() if not coverage.is_covered]

    def get_coverage_statistics(self) -> dict[str, any]:
        """Get overall coverage statistics.

        Returns:
            Dictionary with coverage metrics
        """
        total_symbols = len(self._source_coverage)
        covered_symbols = sum(1 for cov in self._source_coverage.values() if cov.is_covered)

        # Count by symbol type
        type_stats = {}
        for coverage in self._source_coverage.values():
            symbol_type = coverage.symbol_type.value
            if symbol_type not in type_stats:
                type_stats[symbol_type] = {"total": 0, "covered": 0}
            type_stats[symbol_type]["total"] += 1
            if coverage.is_covered:
                type_stats[symbol_type]["covered"] += 1

        # Calculate percentages
        for stats in type_stats.values():
            stats["percentage"] = (stats["covered"] / stats["total"] * 100) if stats["total"] > 0 else 0

        return {
            "total_symbols": total_symbols,
            "covered_symbols": covered_symbols,
            "coverage_percentage": (covered_symbols / total_symbols * 100) if total_symbols > 0 else 0,
            "total_tests": len(set(m.test_name for m in self._mappings)),
            "total_mappings": len(self._mappings),
            "by_type": type_stats,
        }

    def _process_test_file(self, test_file: TestFile, project_root: Path) -> None:
        """Process a single test file to create mappings."""
        try:
            # Analyze the test file
            test_module = self.test_analyzer.analyze_test_file(test_file.path)

            # Process test functions
            for test_func in test_module.test_functions:
                self._map_test_function(test_func, test_file, test_module, project_root)

            # Process test classes
            for test_class in test_module.test_classes:
                for test_method in test_class.test_methods:
                    self._map_test_function(test_method, test_file, test_module, project_root)

        except Exception as e:
            if self.event_bus:
                self.event_bus.emit(
                    SystemEvent(type="coverage_mapping_error", data={"file": str(test_file.path), "error": str(e)})
                )

    def _map_test_function(
        self, test_info: TestInfo, test_file: TestFile, test_module: TestModule, project_root: Path
    ) -> None:
        """Map a single test function to source code."""
        # Strategy 1: Direct name matching
        self._map_by_name_matching(test_info, test_file, project_root)

        # Strategy 2: Import analysis
        self._map_by_imports(test_info, test_file, test_module, project_root)

        # Strategy 3: Call analysis
        self._map_by_calls(test_info, test_file, project_root)

        # Strategy 4: Inferred from test file targets
        if test_file.targets:
            self._map_by_inference(test_info, test_file, project_root)

    def _map_by_name_matching(self, test_info: TestInfo, test_file: TestFile, project_root: Path) -> None:
        """Map tests to source by matching names."""
        test_name = test_info.name

        # Extract source function name from test name
        source_name = None
        if test_name.startswith("test_"):
            source_name = test_name[5:]
        elif test_name.startswith("test"):
            source_name = test_name[4:].lower()

        if source_name:
            # Look for matching symbols
            symbols = self.symbol_table.find_symbols_by_name(source_name)
            for symbol in symbols:
                if symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD]:
                    confidence = self._calculate_name_match_confidence(test_name, symbol.name)
                    self._add_mapping(
                        test_info=test_info,
                        test_file=test_file,
                        source_symbol=symbol,
                        confidence=confidence,
                        mapping_type="direct",
                    )

    def _map_by_imports(
        self, test_info: TestInfo, test_file: TestFile, test_module: TestModule, project_root: Path
    ) -> None:
        """Map tests to source by analyzing imports."""
        for import_name in test_module.imports:
            # Find symbols from imported modules
            module_symbols = self._get_symbols_from_module(import_name)
            for symbol in module_symbols:
                # Check if test might be testing this symbol
                if self._test_likely_tests_symbol(test_info, symbol):
                    self._add_mapping(
                        test_info=test_info,
                        test_file=test_file,
                        source_symbol=symbol,
                        confidence=0.6,
                        mapping_type="indirect",
                    )

    def _map_by_calls(self, test_info: TestInfo, test_file: TestFile, project_root: Path) -> None:
        """Map tests to source by analyzing function calls."""
        for call in test_info.calls:
            # Try to resolve the call to a symbol
            if "." in call:
                # Method call
                parts = call.split(".", 1)
                symbols = self.symbol_table.find_symbols_by_name(parts[1])
                for symbol in symbols:
                    if symbol.symbol_type == SymbolType.METHOD:
                        self._add_mapping(
                            test_info=test_info,
                            test_file=test_file,
                            source_symbol=symbol,
                            confidence=0.8,
                            mapping_type="direct",
                        )
            else:
                # Function call
                symbols = self.symbol_table.find_symbols_by_name(call)
                for symbol in symbols:
                    if symbol.symbol_type == SymbolType.FUNCTION:
                        self._add_mapping(
                            test_info=test_info,
                            test_file=test_file,
                            source_symbol=symbol,
                            confidence=0.8,
                            mapping_type="direct",
                        )

    def _map_by_inference(self, test_info: TestInfo, test_file: TestFile, project_root: Path) -> None:
        """Map tests to source by inference from test file targets."""
        for target_module in test_file.targets:
            # Get all symbols from the target module
            symbols = self._get_symbols_from_module(target_module)
            for symbol in symbols:
                if symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD, SymbolType.CLASS]:
                    # Lower confidence for inferred mappings
                    self._add_mapping(
                        test_info=test_info,
                        test_file=test_file,
                        source_symbol=symbol,
                        confidence=0.4,
                        mapping_type="inferred",
                    )

    def _add_mapping(
        self, test_info: TestInfo, test_file: TestFile, source_symbol: Symbol, confidence: float, mapping_type: str
    ) -> None:
        """Add a test-to-source mapping."""
        mapping = TestMapping(
            test_name=test_info.qualified_name,
            test_file=test_file.path,
            test_line=test_info.line_start,
            source_symbol=source_symbol.qualified_name,
            source_file=source_symbol.location.file_path,
            source_line=source_symbol.location.line_start,
            confidence=confidence,
            mapping_type=mapping_type,
        )
        self._mappings.append(mapping)

    def _calculate_source_coverage(self) -> None:
        """Calculate coverage for all source symbols."""
        # Initialize coverage for all symbols
        for qualified_name, symbol in self.symbol_table._symbols.items():
            if symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD, SymbolType.CLASS]:
                self._source_coverage[qualified_name] = SourceCoverage(
                    symbol_name=qualified_name,
                    symbol_type=symbol.symbol_type,
                    file_path=symbol.location.file_path,
                    line_start=symbol.location.line_start,
                    line_end=symbol.location.line_end,
                )

        # Update coverage based on mappings
        for mapping in self._mappings:
            if mapping.source_symbol in self._source_coverage:
                coverage = self._source_coverage[mapping.source_symbol]
                coverage.covering_tests.append(mapping.test_name)
                coverage.is_covered = True
                # Update confidence (max of all mappings)
                coverage.coverage_confidence = max(coverage.coverage_confidence, mapping.confidence)

    def _get_symbols_from_module(self, module_name: str) -> list[Symbol]:
        """Get all symbols from a module."""
        symbols = []
        for qualified_name, symbol in self.symbol_table._symbols.items():
            if qualified_name.startswith(module_name + "."):
                symbols.append(symbol)
        return symbols

    def _test_likely_tests_symbol(self, test_info: TestInfo, symbol: Symbol) -> bool:
        """Check if a test likely tests a symbol."""
        # Simple heuristic: check if symbol name appears in test name
        return symbol.name.lower() in test_info.name.lower()

    def _calculate_name_match_confidence(self, test_name: str, source_name: str) -> float:
        """Calculate confidence score for name matching."""
        test_name_lower = test_name.lower()
        source_name_lower = source_name.lower()

        # Exact match after removing test prefix
        if test_name_lower.replace("test_", "") == source_name_lower:
            return 0.9
        # Source name contained in test name
        elif source_name_lower in test_name_lower:
            return 0.7
        # Partial match
        else:
            return 0.5
