"""Context factor analysis for rule adaptation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ContextWeight:
    """Weight configuration for a context factor."""

    name: str
    weight: float
    min_value: float = 0.0
    max_value: float = 1.0

    def normalize(self, value: float) -> float:
        """Normalize value to 0-1 range."""
        if value <= self.min_value:
            return 0.0
        elif value >= self.max_value:
            return 1.0
        else:
            return (value - self.min_value) / (self.max_value - self.min_value)


class ContextFactorAnalyzer:
    """Analyze various context factors for rule adaptation."""

    def __init__(self):
        self.intent_patterns = self._init_intent_patterns()
        self.urgency_indicators = self._init_urgency_indicators()
        self.file_criticality_patterns = self._init_criticality_patterns()

    def _init_intent_patterns(self) -> dict[str, list[str]]:
        """Initialize patterns for intent detection."""
        return {
            "research": ["explore", "understand", "investigate", "analyze", "search", "find"],
            "testing": ["test", "spec", "verify", "validate", "check", "assert"],
            "implementation": ["implement", "add", "create", "build", "develop", "code"],
            "documentation": ["document", "explain", "describe", "readme", "docs", "comment"],
            "refactoring": ["refactor", "clean", "optimize", "improve", "reorganize", "simplify"],
            "debugging": ["debug", "fix", "solve", "troubleshoot", "diagnose", "repair"],
            "hotfix": ["hotfix", "urgent", "critical", "emergency", "patch", "quick fix"],
            "experimentation": ["experiment", "try", "prototype", "poc", "proof of concept", "explore"],
        }

    def _init_urgency_indicators(self) -> list[tuple[str, float]]:
        """Initialize urgency indicators with weights."""
        return [
            ("asap", 0.9),
            ("urgent", 0.9),
            ("critical", 0.9),
            ("emergency", 1.0),
            ("hotfix", 0.8),
            ("quick", 0.7),
            ("fast", 0.7),
            ("hurry", 0.8),
            ("deadline", 0.8),
            ("immediately", 0.9),
            ("now", 0.8),
            ("today", 0.6),
            ("production", 0.8),
            ("blocking", 0.9),
        ]

    def _init_criticality_patterns(self) -> dict[str, float]:
        """Initialize file criticality patterns."""
        return {
            "config": 0.8,
            "auth": 0.9,
            "security": 0.9,
            "payment": 0.9,
            "core": 0.8,
            "critical": 0.9,
            "database": 0.8,
            "migration": 0.8,
            "api": 0.7,
            "main": 0.7,
            "index": 0.7,
            "setup": 0.8,
            "install": 0.8,
        }

    def analyze_intent_clarity(self, user_intent: str, metadata: dict[str, Any]) -> float:
        """Analyze how clear the user's intent is (0-1)."""
        if not user_intent or user_intent == "unknown":
            return 0.0

        intent_lower = user_intent.lower()
        clarity_score = 0.0

        # Check for explicit intent patterns
        for _intent_type, patterns in self.intent_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in intent_lower)
            if matches > 0:
                clarity_score = max(clarity_score, min(1.0, matches * 0.3))

        # Bonus for specific tool mentions
        if metadata.get("tool_name"):
            clarity_score = min(1.0, clarity_score + 0.2)

        # Bonus for clear file paths
        if metadata.get("file_path"):
            clarity_score = min(1.0, clarity_score + 0.1)

        return clarity_score

    def analyze_time_pressure(self, context_data: dict[str, Any]) -> float:
        """Analyze time pressure from multiple signals (0-1)."""
        pressure_score = 0.0

        # Check for urgency keywords
        text_to_check = " ".join(
            [
                str(context_data.get("user_intent", "")),
                str(context_data.get("args", [])),
                str(context_data.get("message", "")),
            ]
        ).lower()

        for indicator, weight in self.urgency_indicators:
            if indicator in text_to_check:
                pressure_score = max(pressure_score, weight)

        # Check workflow velocity
        if "workflow_velocity" in context_data:
            velocity = context_data["workflow_velocity"]
            if velocity > 10:  # More than 10 actions per hour
                pressure_score = max(pressure_score, 0.7)

        # Check time of day (late night = higher pressure)
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 4:
            pressure_score = max(pressure_score, 0.6)

        # Check if weekend (might indicate urgent fix)
        if datetime.now().weekday() >= 5:
            pressure_score = max(pressure_score, 0.5)

        return min(1.0, pressure_score)

    def analyze_file_criticality(self, file_path: str) -> float:
        """Analyze how critical a file is (0-1)."""
        if not file_path:
            return 0.5  # Default medium criticality

        file_lower = file_path.lower()
        criticality = 0.5  # Base criticality

        # Check against criticality patterns
        for pattern, score in self.criticality_patterns.items():
            if pattern in file_lower:
                criticality = max(criticality, score)

        # Check file location
        if "/test" in file_lower or "/tests" in file_lower:
            criticality *= 0.6  # Tests are less critical
        elif "/docs" in file_lower or "/documentation" in file_lower:
            criticality *= 0.4  # Docs are least critical
        elif "/examples" in file_lower:
            criticality *= 0.5  # Examples are medium critical

        # Check file extension
        if file_lower.endswith((".md", ".txt", ".rst")):
            criticality *= 0.5  # Documentation files
        elif file_lower.endswith((".test.py", ".spec.js", "_test.go")):
            criticality *= 0.6  # Test files

        return min(1.0, criticality)

    def analyze_developer_confidence(self, context_data: dict[str, Any]) -> float:
        """Analyze developer confidence from behavior patterns (0-1)."""
        confidence = 0.5  # Default medium confidence

        # Multiple research files = higher confidence
        files_examined = context_data.get("files_examined", 0)
        if files_examined > 5:
            confidence += 0.2
        elif files_examined < 2:
            confidence -= 0.2

        # Clear commit messages = higher confidence
        if context_data.get("has_clear_commit_message", False):
            confidence += 0.1

        # Previous successful completions = higher confidence
        if context_data.get("recent_success_rate", 0) > 0.8:
            confidence += 0.2

        # Too many recent violations = lower confidence
        if context_data.get("previous_violations", 0) > 5:
            confidence -= 0.3

        return max(0.0, min(1.0, confidence))

    def calculate_risk_score(self, context_data: dict[str, Any]) -> float:
        """Calculate overall risk score for the action (0-1)."""
        risk_factors = []

        # File criticality contributes to risk
        file_risk = self.analyze_file_criticality(context_data.get("file_path", ""))
        risk_factors.append(file_risk * 0.3)

        # Low developer experience increases risk
        experience = context_data.get("developer_experience", 0.5)
        risk_factors.append((1.0 - experience) * 0.2)

        # High time pressure increases risk
        pressure = self.analyze_time_pressure(context_data)
        risk_factors.append(pressure * 0.2)

        # Complex changes increase risk
        if context_data.get("change_size", "small") == "large":
            risk_factors.append(0.3)

        # Production environment increases risk
        if context_data.get("environment", "").lower() == "production":
            risk_factors.append(0.4)

        return min(1.0, sum(risk_factors))

    def get_context_summary(self, context_data: dict[str, Any]) -> dict[str, float]:
        """Get comprehensive context analysis summary."""
        return {
            "intent_clarity": self.analyze_intent_clarity(context_data.get("user_intent", ""), context_data),
            "time_pressure": self.analyze_time_pressure(context_data),
            "file_criticality": self.analyze_file_criticality(context_data.get("file_path", "")),
            "developer_confidence": self.analyze_developer_confidence(context_data),
            "risk_score": self.calculate_risk_score(context_data),
        }
