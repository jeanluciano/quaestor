"""A1 Learning Framework - Simplified extraction from A1.

Provides essential pattern recognition and adaptation capabilities with:
- File-based JSON storage (vs SQLite)
- Simple pattern recognition (vs complex algorithms)
- Basic adaptation engine (vs complex behavior analysis)
- Minimal orchestration (vs complex async processing)

Target: ~300-400 lines total (90%+ reduction from V2.0's 3,866 lines)
"""

from .adaptation_engine import AdaptationEngine
from .confidence_scorer import ConfidenceFactors, ConfidenceScorer
from .exception_clustering import ExceptionCluster, ExceptionClusterer
from .file_store import FileLearningStore
from .learned_patterns_store import LearnedPattern, LearnedPatternsStore
from .learning_manager import LearningManager
from .pattern_recognizer import ExceptionPattern, PatternRecognizer

__all__ = [
    # Original components
    "LearningManager",
    "PatternRecognizer",
    "AdaptationEngine",
    "FileLearningStore",
    # Pattern recognition
    "ExceptionPattern",
    # Clustering
    "ExceptionClusterer",
    "ExceptionCluster",
    # Learned patterns
    "LearnedPatternsStore",
    "LearnedPattern",
    # Confidence scoring
    "ConfidenceScorer",
    "ConfidenceFactors",
]
