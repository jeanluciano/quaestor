"""Basic Adaptation Engine for A1 - Simple suggestion generation.

Provides basic adaptation suggestions based on detected patterns.
Target: ~60 lines (vs 567 lines in A1)
"""

import time
from typing import Any
from uuid import uuid4

from .file_store import Adaptation, FileLearningStore


class AdaptationEngine:
    """Simple adaptation engine for generating suggestions."""

    def __init__(self, store: FileLearningStore):
        self.store = store

    def generate_suggestions(self, patterns: list[Any], context: dict[str, Any]) -> list[str]:
        """Generate adaptation suggestions based on patterns."""
        suggestions = []

        for pattern in patterns:
            if pattern.pattern_type == "tool_sequence":
                suggestion = self._suggest_from_tool_sequence(pattern, context)
                if suggestion:
                    suggestions.append(suggestion)
                    self._store_adaptation(pattern.id, suggestion, 0.7)

            elif pattern.pattern_type == "file_pattern":
                suggestion = self._suggest_from_file_pattern(pattern, context)
                if suggestion:
                    suggestions.append(suggestion)
                    self._store_adaptation(pattern.id, suggestion, 0.6)

        return suggestions[:5]  # Return top 5 suggestions

    def _suggest_from_tool_sequence(self, pattern: Any, context: dict[str, Any]) -> str:
        """Generate suggestion from tool sequence pattern."""
        sequence = pattern.data.get("sequence", "")
        tools = pattern.data.get("tools", [])

        if len(tools) > 2:
            last_tool = tools[-1]
            return f"Based on your workflow pattern '{sequence}', consider using {last_tool} for similar tasks"

        return ""

    def _suggest_from_file_pattern(self, pattern: Any, context: dict[str, Any]) -> str:
        """Generate suggestion from file pattern."""
        file_types = pattern.data.get("file_types", [])

        if len(file_types) == 2:
            return f"You often work with {file_types[0]} files after {file_types[1]} files"

        return ""

    def _store_adaptation(self, pattern_id: str, suggestion: str, confidence: float) -> None:
        """Store an adaptation for tracking."""
        adaptation = Adaptation(
            id=str(uuid4()), pattern_id=pattern_id, suggestion=suggestion, confidence=confidence, timestamp=time.time()
        )
        self.store.store_adaptation(adaptation)

    def get_recent_adaptations(self, limit: int = 10) -> list[Adaptation]:
        """Get recent adaptations for display."""
        return self.store.get_adaptations()[:limit]
