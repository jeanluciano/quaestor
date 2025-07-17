"""File-based learning storage for A1 - Simplified replacement for A1 SQLite KnowledgeStore.

Provides JSON-based persistence for patterns and adaptations.
Target: ~80 lines (vs 611 lines in A1)
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Pattern:
    """Simplified pattern data structure."""

    id: str
    pattern_type: str
    data: dict[str, Any]
    confidence: float
    frequency: int
    first_seen: float
    last_seen: float


@dataclass
class Adaptation:
    """Simplified adaptation data structure."""

    id: str
    pattern_id: str
    suggestion: str
    confidence: float
    timestamp: float


class FileLearningStore:
    """File-based learning storage using JSON."""

    def __init__(self, data_dir: str = ".quaestor/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.data_dir / "patterns.json"
        self.adaptations_file = self.data_dir / "adaptations.json"

        # Initialize files if they don't exist
        if not self.patterns_file.exists():
            self._save_json(self.patterns_file, {})
        if not self.adaptations_file.exists():
            self._save_json(self.adaptations_file, {})

    def _load_json(self, file_path: Path) -> dict:
        """Load JSON data from file."""
        try:
            with open(file_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, file_path: Path, data: dict) -> None:
        """Save JSON data to file."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def store_pattern(self, pattern: Pattern) -> None:
        """Store a pattern."""
        patterns = self._load_json(self.patterns_file)
        patterns[pattern.id] = asdict(pattern)
        self._save_json(self.patterns_file, patterns)

    def get_patterns(self, pattern_type: str | None = None) -> list[Pattern]:
        """Get patterns, optionally filtered by type."""
        patterns = self._load_json(self.patterns_file)

        results = []
        for pattern_data in patterns.values():
            if pattern_type and pattern_data.get("pattern_type") != pattern_type:
                continue
            results.append(Pattern(**pattern_data))

        # Sort by confidence * frequency for relevance
        results.sort(key=lambda p: p.confidence * p.frequency, reverse=True)
        return results

    def update_pattern_frequency(self, pattern_id: str) -> None:
        """Update pattern frequency and last seen time."""
        patterns = self._load_json(self.patterns_file)
        if pattern_id in patterns:
            patterns[pattern_id]["frequency"] += 1
            patterns[pattern_id]["last_seen"] = time.time()
            self._save_json(self.patterns_file, patterns)

    def store_adaptation(self, adaptation: Adaptation) -> None:
        """Store an adaptation."""
        adaptations = self._load_json(self.adaptations_file)
        adaptations[adaptation.id] = asdict(adaptation)
        self._save_json(self.adaptations_file, adaptations)

    def get_adaptations(self, pattern_id: str | None = None) -> list[Adaptation]:
        """Get adaptations, optionally filtered by pattern_id."""
        adaptations = self._load_json(self.adaptations_file)

        results = []
        for adaptation_data in adaptations.values():
            if pattern_id and adaptation_data.get("pattern_id") != pattern_id:
                continue
            results.append(Adaptation(**adaptation_data))

        # Sort by confidence and recency
        results.sort(key=lambda a: (a.confidence, a.timestamp), reverse=True)
        return results
