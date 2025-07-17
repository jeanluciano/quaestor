"""Simplified prediction engine for A1 - extracted from V2.0 complexity.

Provides next-tool and next-file prediction with 65% code reduction from A1.
Focuses on practical functionality with simplified dependencies.
"""

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..core.events import ToolUseEvent


@dataclass
class PredictionPattern:
    """Simplified pattern for predictions."""

    sequence: list[str]
    frequency: int = 1
    last_seen: float = field(default_factory=time.time)

    @property
    def score(self) -> float:
        """Calculate pattern score based on frequency and recency."""
        recency = max(0, 1 - (time.time() - self.last_seen) / 86400)  # 24h decay
        return (self.frequency * 0.7) + (recency * 0.3)


@dataclass
class PredictionResult:
    """Simplified prediction result."""

    prediction_type: str
    value: str
    confidence: float
    explanation: str


class SimplePatternRecognizer:
    """Simplified pattern recognition for A1."""

    def __init__(self, storage_file: str = ".quaestor/patterns.json"):
        self.storage_file = Path(storage_file)
        self.patterns: dict[str, list[PredictionPattern]] = {}
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load patterns from JSON file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file) as f:
                    data = json.load(f)
                    for pattern_type, patterns_data in data.items():
                        self.patterns[pattern_type] = [
                            PredictionPattern(
                                sequence=p["sequence"], frequency=p["frequency"], last_seen=p["last_seen"]
                            )
                            for p in patterns_data
                        ]
            except (json.JSONDecodeError, KeyError):
                self.patterns = {}

    def _save_patterns(self) -> None:
        """Save patterns to JSON file."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for pattern_type, patterns in self.patterns.items():
            data[pattern_type] = [
                {"sequence": p.sequence, "frequency": p.frequency, "last_seen": p.last_seen} for p in patterns
            ]

        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def record_sequence(self, pattern_type: str, sequence: list[str]) -> None:
        """Record a new sequence pattern."""
        if pattern_type not in self.patterns:
            self.patterns[pattern_type] = []

        # Find existing pattern or create new one
        for pattern in self.patterns[pattern_type]:
            if pattern.sequence == sequence:
                pattern.frequency += 1
                pattern.last_seen = time.time()
                break
        else:
            self.patterns[pattern_type].append(PredictionPattern(sequence=sequence))

        self._save_patterns()

    def get_patterns(self, pattern_type: str) -> list[PredictionPattern]:
        """Get patterns for a specific type."""
        return self.patterns.get(pattern_type, [])


class SequencePredictor:
    """Predicts next tool based on sequence patterns."""

    def __init__(self, pattern_recognizer: SimplePatternRecognizer):
        self.pattern_recognizer = pattern_recognizer

    def predict(self, recent_actions: list[str], max_predictions: int = 3) -> list[PredictionResult]:
        """Predict next tools based on recent action sequence."""
        if not recent_actions:
            return []

        # Get tool sequence patterns
        patterns = self.pattern_recognizer.get_patterns("tool_sequences")

        # Find matching patterns
        next_tool_scores = defaultdict(float)
        next_tool_evidence = defaultdict(list)

        for pattern in patterns:
            if self._sequence_matches(recent_actions, pattern.sequence):
                next_index = len(recent_actions)
                if next_index < len(pattern.sequence):
                    next_tool = pattern.sequence[next_index]
                    score = pattern.score

                    next_tool_scores[next_tool] += score
                    next_tool_evidence[next_tool].append(f"Pattern (freq: {pattern.frequency})")

        # Sort by score and create predictions
        sorted_tools = sorted(next_tool_scores.items(), key=lambda x: x[1], reverse=True)
        results = []

        for tool, score in sorted_tools[:max_predictions]:
            # More generous confidence calculation
            confidence = min(score / 3.0, 1.0)  # Normalize to 0-1 with lower denominator
            if confidence >= 0.2:  # Lower minimum confidence threshold
                results.append(
                    PredictionResult(
                        prediction_type="next_tool",
                        value=tool,
                        confidence=confidence,
                        explanation=f"Based on {len(next_tool_evidence[tool])} patterns",
                    )
                )

        return results

    def _sequence_matches(self, recent_actions: list[str], pattern_sequence: list[str]) -> bool:
        """Check if recent actions match the beginning of a pattern."""
        if len(recent_actions) >= len(pattern_sequence):
            return False

        for i, action in enumerate(recent_actions):
            if i >= len(pattern_sequence) or action != pattern_sequence[i]:
                return False

        return True


class FilePredictor:
    """Predicts next file based on workflow patterns."""

    def __init__(self, pattern_recognizer: SimplePatternRecognizer):
        self.pattern_recognizer = pattern_recognizer

    def predict(self, current_file: str, max_predictions: int = 3) -> list[PredictionResult]:
        """Predict next files based on current file."""
        if not current_file:
            return []

        # Get file workflow patterns
        patterns = self.pattern_recognizer.get_patterns("file_workflows")

        # Find patterns containing current file
        next_file_scores = defaultdict(float)
        next_file_evidence = defaultdict(list)

        for pattern in patterns:
            if current_file in pattern.sequence:
                current_index = pattern.sequence.index(current_file)

                # Predict next files in workflow
                for i in range(current_index + 1, min(current_index + 4, len(pattern.sequence))):
                    next_file = pattern.sequence[i]
                    # Decrease score for files further away
                    distance_penalty = 0.8 ** (i - current_index - 1)
                    score = pattern.score * distance_penalty

                    next_file_scores[next_file] += score
                    next_file_evidence[next_file].append(f"Workflow step {i - current_index}")

        # Sort by score and create predictions
        sorted_files = sorted(next_file_scores.items(), key=lambda x: x[1], reverse=True)
        results = []

        for file_path, score in sorted_files[:max_predictions]:
            # More generous confidence calculation
            confidence = min(score / 3.0, 1.0)  # Normalize to 0-1 with lower denominator
            if confidence >= 0.2:  # Lower minimum confidence threshold
                results.append(
                    PredictionResult(
                        prediction_type="next_file",
                        value=file_path,
                        confidence=confidence,
                        explanation=f"Based on {len(next_file_evidence[file_path])} patterns",
                    )
                )

        return results


class BasicPredictionEngine:
    """Simplified prediction engine for A1."""

    def __init__(self, storage_dir: str = ".quaestor"):
        self.pattern_recognizer = SimplePatternRecognizer(f"{storage_dir}/patterns.json")
        self.sequence_predictor = SequencePredictor(self.pattern_recognizer)
        self.file_predictor = FilePredictor(self.pattern_recognizer)

        # Track recent actions for learning
        self.recent_tools: list[str] = []
        self.recent_files: list[str] = []
        self.max_history = 20

    def predict_next_tool(self, max_predictions: int = 3) -> list[PredictionResult]:
        """Predict next tool based on recent actions."""
        return self.sequence_predictor.predict(self.recent_tools, max_predictions)

    def predict_next_file(self, current_file: str, max_predictions: int = 3) -> list[PredictionResult]:
        """Predict next file based on current file."""
        return self.file_predictor.predict(current_file, max_predictions)

    def handle_tool_use_event(self, event: ToolUseEvent) -> None:
        """Handle tool use event for learning."""
        if event.tool_name and event.success:
            # Record tool usage
            self.recent_tools.append(event.tool_name)
            if len(self.recent_tools) > self.max_history:
                self.recent_tools.pop(0)

            # Learn sequence patterns (minimum 2 tools)
            if len(self.recent_tools) >= 2:
                for length in range(2, min(6, len(self.recent_tools) + 1)):
                    sequence = self.recent_tools[-length:]
                    self.pattern_recognizer.record_sequence("tool_sequences", sequence)

    def handle_file_change(self, file_path: str) -> None:
        """Handle file change for learning workflows."""
        if file_path:
            # Record file usage
            self.recent_files.append(file_path)
            if len(self.recent_files) > self.max_history:
                self.recent_files.pop(0)

            # Learn workflow patterns (minimum 2 files)
            if len(self.recent_files) >= 2:
                for length in range(2, min(6, len(self.recent_files) + 1)):
                    sequence = self.recent_files[-length:]
                    self.pattern_recognizer.record_sequence("file_workflows", sequence)

    def get_summary(self) -> dict[str, Any]:
        """Get prediction engine summary."""
        tool_patterns = len(self.pattern_recognizer.get_patterns("tool_sequences"))
        file_patterns = len(self.pattern_recognizer.get_patterns("file_workflows"))

        return {
            "tool_patterns": tool_patterns,
            "file_patterns": file_patterns,
            "recent_tools": len(self.recent_tools),
            "recent_files": len(self.recent_files),
            "status": "active",
        }


# Global instance for easy access
_prediction_engine: BasicPredictionEngine | None = None


def get_prediction_engine() -> BasicPredictionEngine:
    """Get global prediction engine instance."""
    global _prediction_engine
    if _prediction_engine is None:
        _prediction_engine = BasicPredictionEngine()
    return _prediction_engine


# Convenience functions
def predict_next_tool(max_predictions: int = 3) -> list[PredictionResult]:
    """Predict next tool to be used."""
    return get_prediction_engine().predict_next_tool(max_predictions)


def predict_next_file(current_file: str, max_predictions: int = 3) -> list[PredictionResult]:
    """Predict next file to be worked on."""
    return get_prediction_engine().predict_next_file(current_file, max_predictions)


def record_tool_use(tool_name: str, success: bool = True) -> None:
    """Record tool usage for learning."""
    event = ToolUseEvent(tool_name=tool_name, success=success)
    get_prediction_engine().handle_tool_use_event(event)


def record_file_change(file_path: str) -> None:
    """Record file change for learning."""
    get_prediction_engine().handle_file_change(file_path)
