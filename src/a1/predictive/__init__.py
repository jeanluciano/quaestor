"""A1 Predictive Engine - Phase 5.

This module implements pattern recognition, next action prediction,
workflow detection, and intelligent suggestions based on user behavior.
"""

from .patterns import (
    BasePattern,
    CommandPattern,
    FilePattern,
    Pattern,
    PatternType,
    WorkflowPattern,
)
from .predictive_engine import PredictiveEngine
from .sequence_miner import SequenceMiner

__all__ = [
    "BasePattern",
    "CommandPattern",
    "FilePattern",
    "Pattern",
    "PatternType",
    "PredictiveEngine",
    "SequenceMiner",
    "WorkflowPattern",
]
