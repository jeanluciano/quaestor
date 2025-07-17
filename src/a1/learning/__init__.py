"""A1 Learning Framework - Simplified extraction from A1.

Provides essential pattern recognition and adaptation capabilities with:
- File-based JSON storage (vs SQLite)
- Simple pattern recognition (vs complex algorithms)
- Basic adaptation engine (vs complex behavior analysis)
- Minimal orchestration (vs complex async processing)

Target: ~300-400 lines total (90%+ reduction from V2.0's 3,866 lines)
"""

from .adaptation_engine import AdaptationEngine
from .file_store import FileLearningStore
from .learning_manager import LearningManager
from .pattern_recognizer import PatternRecognizer

__all__ = [
    "LearningManager",
    "PatternRecognizer",
    "AdaptationEngine",
    "FileLearningStore",
]
