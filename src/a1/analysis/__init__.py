"""A1 Analysis Engine - Simplified extraction from A1.

Provides essential code analysis capabilities with:
- Python-only analysis (vs multi-language support)
- Synchronous processing (vs async complexity)
- Simple quality checks (vs comprehensive assessment)
- Basic metrics (vs advanced performance analysis)

Target: ~400 lines total (90%+ reduction from V2.0's 4,267 lines)
"""

from .code_analyzer import CodeAnalyzer
from .engine import AnalysisEngine
from .metrics import CodeMetrics
from .quality_checker import QualityChecker

__all__ = [
    "AnalysisEngine",
    "CodeAnalyzer",
    "QualityChecker",
    "CodeMetrics",
]
