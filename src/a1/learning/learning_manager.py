"""Simplified Learning Manager for A1 - Basic orchestration only.

Provides simple synchronous coordination of learning components.
Target: ~80 lines (vs 358 lines in A1)
"""

import time
from typing import Any

from .adaptation_engine import AdaptationEngine
from .file_store import FileLearningStore
from .pattern_recognizer import PatternRecognizer


class LearningManager:
    """Simple learning manager for basic pattern recognition and adaptation."""

    def __init__(self, data_dir: str = ".quaestor/learning"):
        # Initialize storage
        self.store = FileLearningStore(data_dir)

        # Initialize components
        self.pattern_recognizer = PatternRecognizer(self.store)
        self.adaptation_engine = AdaptationEngine(self.store)

        # Simple stats tracking
        self.stats = {
            "events_processed": 0,
            "patterns_detected": 0,
            "suggestions_generated": 0,
            "session_start": time.time(),
        }

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process a single event through the learning pipeline."""
        self.stats["events_processed"] += 1

        # Detect patterns
        patterns = self.pattern_recognizer.analyze_event(event)
        self.stats["patterns_detected"] += len(patterns)

        # Generate suggestions
        suggestions = []
        if patterns:
            context = self._build_context(event)
            suggestions = self.adaptation_engine.generate_suggestions(patterns, context)
            self.stats["suggestions_generated"] += len(suggestions)

        return {"patterns_found": len(patterns), "suggestions": suggestions, "event_processed": True}

    def _build_context(self, event: dict[str, Any]) -> dict[str, Any]:
        """Build context for adaptation suggestions."""
        context = {"event_type": event.get("type"), "timestamp": event.get("timestamp", time.time())}

        # Add recent tools if available
        recent_tools = []
        for action in self.pattern_recognizer.recent_actions:
            if action.get("type") == "tool_use":
                recent_tools.append(action.get("tool_name", ""))

        if recent_tools:
            context["recent_tools"] = recent_tools[-3:]  # Last 3 tools

        return context

    def get_suggestions(self, context: dict[str, Any] | None = None) -> list[str]:
        """Get current suggestions based on context."""
        if context is None:
            context = {"recent_tools": []}

        return self.pattern_recognizer.get_suggestions(context)

    def get_stats(self) -> dict[str, Any]:
        """Get learning statistics."""
        session_duration = time.time() - self.stats["session_start"]

        return {
            **self.stats,
            "session_duration": session_duration,
            "stored_patterns": len(self.store.get_patterns()),
            "stored_adaptations": len(self.store.get_adaptations()),
        }

    def get_learning_insights(self) -> dict[str, Any]:
        """Get insights about learned patterns."""
        patterns = self.store.get_patterns()
        adaptations = self.store.get_adaptations()

        # Basic insights
        tool_patterns = [p for p in patterns if p.pattern_type == "tool_sequence"]
        file_patterns = [p for p in patterns if p.pattern_type == "file_pattern"]

        return {
            "total_patterns": len(patterns),
            "tool_sequence_patterns": len(tool_patterns),
            "file_patterns": len(file_patterns),
            "total_adaptations": len(adaptations),
            "top_patterns": [
                {"type": p.pattern_type, "data": p.data, "confidence": p.confidence, "frequency": p.frequency}
                for p in patterns[:5]  # Top 5 by relevance
            ],
        }
