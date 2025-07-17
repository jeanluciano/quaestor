"""Simplified Pattern Recognizer for A1 - Essential pattern detection only.

Focuses on the most valuable patterns from A1 with minimal complexity.
Target: ~80 lines (vs 574 lines in A1)
"""

import time
from collections import deque
from typing import Any
from uuid import uuid4

from .file_store import FileLearningStore, Pattern


class PatternRecognizer:
    """Simple pattern recognition for common user workflows."""

    def __init__(self, store: FileLearningStore):
        self.store = store
        self.recent_actions = deque(maxlen=10)  # Keep last 10 actions

    def analyze_event(self, event: dict[str, Any]) -> list[Pattern]:
        """Analyze an event and detect patterns."""
        self.recent_actions.append(event)

        patterns = []

        # Tool sequence patterns
        if event.get("type") == "tool_use":
            patterns.extend(self._detect_tool_sequence_patterns())

        # File patterns
        elif event.get("type") == "file_change":
            patterns.extend(self._detect_file_patterns())

        return patterns

    def _detect_tool_sequence_patterns(self) -> list[Pattern]:
        """Detect simple tool usage sequences."""
        patterns = []

        # Look for sequences of 3+ tools
        if len(self.recent_actions) >= 3:
            # Get last 3 tool uses
            tool_sequence = []
            for action in list(self.recent_actions)[-3:]:
                if action.get("type") == "tool_use":
                    tool_sequence.append(action.get("tool_name", ""))

            if len(tool_sequence) >= 3:
                sequence_str = " -> ".join(tool_sequence)

                # Check if this sequence already exists
                existing_patterns = self.store.get_patterns("tool_sequence")
                for existing in existing_patterns:
                    if existing.data.get("sequence") == sequence_str:
                        # Update existing pattern
                        self.store.update_pattern_frequency(existing.id)
                        patterns.append(existing)
                        return patterns

                # Create new pattern
                pattern = Pattern(
                    id=str(uuid4()),
                    pattern_type="tool_sequence",
                    data={"sequence": sequence_str, "tools": tool_sequence},
                    confidence=0.6,  # Starting confidence
                    frequency=1,
                    first_seen=time.time(),
                    last_seen=time.time(),
                )
                self.store.store_pattern(pattern)
                patterns.append(pattern)

        return patterns

    def _detect_file_patterns(self) -> list[Pattern]:
        """Detect simple file modification patterns."""
        patterns = []

        # Look for file type patterns
        recent_files = []
        for action in self.recent_actions:
            if action.get("type") == "file_change":
                file_path = action.get("file_path", "")
                file_ext = file_path.split(".")[-1] if "." in file_path else "none"
                recent_files.append(file_ext)

        if len(recent_files) >= 2:
            # Create pattern for file type sequence
            file_sequence = " -> ".join(recent_files[-2:])

            # Check if this pattern exists
            existing_patterns = self.store.get_patterns("file_pattern")
            for existing in existing_patterns:
                if existing.data.get("file_sequence") == file_sequence:
                    self.store.update_pattern_frequency(existing.id)
                    patterns.append(existing)
                    return patterns

            # Create new file pattern
            pattern = Pattern(
                id=str(uuid4()),
                pattern_type="file_pattern",
                data={"file_sequence": file_sequence, "file_types": recent_files[-2:]},
                confidence=0.5,
                frequency=1,
                first_seen=time.time(),
                last_seen=time.time(),
            )
            self.store.store_pattern(pattern)
            patterns.append(pattern)

        return patterns

    def get_suggestions(self, current_context: dict[str, Any]) -> list[str]:
        """Get pattern-based suggestions for current context."""
        suggestions = []

        # Get tool sequence suggestions
        if current_context.get("recent_tools"):
            recent_tools = current_context["recent_tools"]
            tool_patterns = self.store.get_patterns("tool_sequence")

            for pattern in tool_patterns:
                pattern_tools = pattern.data.get("tools", [])
                if len(pattern_tools) > len(recent_tools) and pattern_tools[: len(recent_tools)] == recent_tools:
                    next_tool = pattern_tools[len(recent_tools)]
                    suggestions.append(f"Consider using {next_tool} next")

        return suggestions[:3]  # Return top 3 suggestions
