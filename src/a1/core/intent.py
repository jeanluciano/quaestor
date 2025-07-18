"""Intent detection system for analyzing Claude event patterns."""

import logging
from collections import deque
from datetime import datetime, timedelta

from a1.core.events import ClaudeEvent

logger = logging.getLogger(__name__)


class Intent:
    """Represents a detected intent with metadata."""

    def __init__(self, intent_type: str, confidence: float, evidence: dict[str, any]):
        """Initialize intent.

        Args:
            intent_type: Type of intent (exploring, implementing, etc.)
            confidence: Confidence score (0.0-1.0)
            evidence: Evidence supporting this intent
        """
        self.type = intent_type
        self.confidence = confidence
        self.evidence = evidence
        self.detected_at = datetime.now()

    def to_dict(self) -> dict[str, any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "detected_at": self.detected_at.isoformat(),
        }


class IntentDetector:
    """Advanced intent detection from Claude event patterns."""

    # Intent types
    EXPLORING = "exploring"
    IMPLEMENTING = "implementing"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTING = "documenting"
    IDLE = "idle"

    def __init__(self, history_size: int = 50, time_window: int = 300):
        """Initialize intent detector.

        Args:
            history_size: Number of events to keep in history
            time_window: Time window in seconds for pattern analysis
        """
        self.history_size = history_size
        self.time_window = timedelta(seconds=time_window)
        self.event_history = deque(maxlen=history_size)
        self.current_intent: Intent | None = None
        self.intent_history: list[Intent] = []

        # Pattern definitions
        self._init_patterns()

    def _init_patterns(self):
        """Initialize pattern definitions for intent detection."""
        self.patterns = {
            self.EXPLORING: {
                "tools": ["Read", "Grep", "Glob", "LS"],
                "min_tool_ratio": 0.7,
                "max_edits": 0,
                "indicators": ["multiple_reads", "search_patterns"],
            },
            self.IMPLEMENTING: {
                "tools": ["Edit", "Write", "MultiEdit"],
                "min_tool_ratio": 0.3,
                "required_sequence": ["Read", "Edit"],
                "indicators": ["new_files", "sequential_edits"],
            },
            self.DEBUGGING: {
                "tools": ["Bash", "Read", "Edit"],
                "indicators": ["test_failures", "error_investigation", "log_reading"],
                "sequences": [["test_run", "Read"], ["Bash", "Edit", "Bash"]],
            },
            self.REFACTORING: {
                "tools": ["MultiEdit", "Edit"],
                "min_edits": 3,
                "indicators": ["multi_file_edits", "rename_operations"],
                "time_constraint": 120,  # Multiple edits within 2 minutes
            },
            self.TESTING: {
                "tools": ["Bash"],
                "indicators": ["test_commands", "pytest", "npm_test"],
                "required_patterns": ["test", "spec", "pytest", "jest"],
            },
            self.DOCUMENTING: {
                "tools": ["Edit", "Write"],
                "file_patterns": ["*.md", "README", "docs/"],
                "indicators": ["markdown_edits", "docstring_updates"],
            },
        }

    async def update(self, event: ClaudeEvent) -> Intent:
        """Update intent detection with new event.

        Args:
            event: Claude event to process

        Returns:
            Detected intent with confidence
        """
        # Add to history
        self.event_history.append(event)

        # Get recent events within time window
        recent_events = self._get_recent_events()

        # Detect intent from patterns
        intent = self._detect_intent(recent_events)

        # Update current intent if changed significantly
        if self._should_update_intent(intent):
            self.current_intent = intent
            self.intent_history.append(intent)
            logger.info(f"Intent changed to: {intent.type} (confidence: {intent.confidence})")

        return self.current_intent or Intent(self.IDLE, 0.0, {})

    def _get_recent_events(self) -> list[ClaudeEvent]:
        """Get events within the time window."""
        if not self.event_history:
            return []

        cutoff_time = datetime.now() - self.time_window
        return [e for e in self.event_history if e.timestamp > cutoff_time]

    def _detect_intent(self, events: list[ClaudeEvent]) -> Intent:
        """Detect intent from event patterns."""
        if not events:
            return Intent(self.IDLE, 0.0, {"reason": "no_recent_events"})

        # Calculate scores for each intent type
        intent_scores = {}

        for intent_type, pattern in self.patterns.items():
            score, evidence = self._calculate_intent_score(events, pattern)
            intent_scores[intent_type] = (score, evidence)

        # Find highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1][0])
        intent_type, (confidence, evidence) = best_intent

        # Threshold for minimum confidence
        if confidence < 0.3:
            return Intent(self.IDLE, confidence, evidence)

        return Intent(intent_type, confidence, evidence)

    def _calculate_intent_score(self, events: list[ClaudeEvent], pattern: dict) -> tuple[float, dict]:
        """Calculate score for a specific intent pattern.

        Args:
            events: Recent events
            pattern: Pattern definition

        Returns:
            Tuple of (confidence_score, evidence)
        """
        score = 0.0
        evidence = {}

        # Extract tool usage
        tool_events = [e for e in events if e.type == "post_tool_use"]
        tools_used = [e.data.get("tool", "") for e in tool_events]

        # Check tool usage patterns
        if "tools" in pattern:
            pattern_tools = pattern["tools"]
            matching_tools = [t for t in tools_used if t in pattern_tools]

            if tools_used:
                tool_ratio = len(matching_tools) / len(tools_used)
                evidence["tool_ratio"] = tool_ratio

                if "min_tool_ratio" in pattern:
                    if tool_ratio >= pattern["min_tool_ratio"]:
                        score += 0.4
                else:
                    score += 0.4 * tool_ratio

        # Check required sequences
        if "required_sequence" in pattern:
            if self._has_sequence(tools_used, pattern["required_sequence"]):
                score += 0.3
                evidence["has_required_sequence"] = True

        # Check edit counts
        edit_count = tools_used.count("Edit") + tools_used.count("MultiEdit")
        evidence["edit_count"] = edit_count

        if (
            "min_edits" in pattern
            and edit_count >= pattern["min_edits"]
            or "max_edits" in pattern
            and edit_count <= pattern["max_edits"]
        ):
            score += 0.2

        # Check indicators
        if "indicators" in pattern:
            indicator_score = self._check_indicators(events, pattern["indicators"])
            score += 0.3 * indicator_score
            evidence["indicators_matched"] = indicator_score

        # Time constraint check
        if "time_constraint" in pattern:
            if self._events_within_timeframe(events, pattern["time_constraint"]):
                score += 0.1
                evidence["within_time_constraint"] = True

        return min(score, 1.0), evidence

    def _has_sequence(self, tools: list[str], sequence: list[str]) -> bool:
        """Check if tools contain required sequence."""
        if len(tools) < len(sequence):
            return False

        for i in range(len(tools) - len(sequence) + 1):
            if tools[i : i + len(sequence)] == sequence:
                return True
        return False

    def _check_indicators(self, events: list[ClaudeEvent], indicators: list[str]) -> float:
        """Check how many indicators are present."""
        matches = 0

        for indicator in indicators:
            if indicator == "multiple_reads":
                read_count = sum(1 for e in events if e.data.get("tool") == "Read")
                if read_count >= 3:
                    matches += 1

            elif indicator == "search_patterns":
                search_tools = ["Grep", "Glob", "WebSearch"]
                if any(e.data.get("tool") in search_tools for e in events):
                    matches += 1

            elif indicator == "test_failures":
                if any("fail" in str(e.data).lower() for e in events):
                    matches += 1

            elif indicator == "error_investigation":
                if any("error" in str(e.data).lower() or "exception" in str(e.data).lower() for e in events):
                    matches += 1

            elif indicator == "multi_file_edits":
                edit_events = [e for e in events if e.data.get("tool") in ["Edit", "MultiEdit"]]
                files_edited = set(e.data.get("file_path", "") for e in edit_events)
                if len(files_edited) >= 3:
                    matches += 1

        return matches / len(indicators) if indicators else 0

    def _events_within_timeframe(self, events: list[ClaudeEvent], seconds: int) -> bool:
        """Check if all events occurred within timeframe."""
        if not events:
            return False

        time_span = events[-1].timestamp - events[0].timestamp
        return time_span.total_seconds() <= seconds

    def _should_update_intent(self, new_intent: Intent) -> bool:
        """Determine if intent should be updated."""
        if not self.current_intent:
            return True

        # Update if type changed
        if new_intent.type != self.current_intent.type:
            return new_intent.confidence > 0.5

        # Update if confidence changed significantly
        confidence_delta = abs(new_intent.confidence - self.current_intent.confidence)
        return confidence_delta > 0.2

    def get_intent_history(self, limit: int = 10) -> list[Intent]:
        """Get recent intent history.

        Args:
            limit: Maximum number of intents to return

        Returns:
            List of recent intents
        """
        return self.intent_history[-limit:]
