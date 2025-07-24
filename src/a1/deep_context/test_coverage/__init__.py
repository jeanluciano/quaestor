"""Test Coverage Mapping Module.

This module provides comprehensive test coverage analysis including:
- Test file discovery and pattern matching
- Test-to-source code mapping
- Coverage metrics calculation
- Test execution history tracking
- Coverage report generation
"""

from .coverage_calculator import CoverageCalculator, CoverageMetrics
from .coverage_mapper import CoverageMapper, TestMapping
from .history_tracker import HistoryTracker, TestRun
from .report_generator import CoverageReport, ReportGenerator
from .test_analyzer import TestAnalyzer, TestInfo
from .test_discovery import TestDiscovery, TestFile

__all__ = [
    "TestDiscovery",
    "TestFile",
    "TestAnalyzer",
    "TestInfo",
    "CoverageMapper",
    "TestMapping",
    "CoverageCalculator",
    "CoverageMetrics",
    "HistoryTracker",
    "TestRun",
    "ReportGenerator",
    "CoverageReport",
]
