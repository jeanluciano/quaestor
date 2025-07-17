"""Simplified quality guardian for Quaestor A1."""

import time
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class QualityLevel(Enum):
    """Quality level classifications."""

    EXCELLENT = "excellent"  # >= 90
    GOOD = "good"  # >= 80
    ACCEPTABLE = "acceptable"  # >= 70
    POOR = "poor"  # < 70


class RuleSeverity(Enum):
    """Rule violation severities."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class QualityRule:
    """Simple quality rule."""

    name: str
    description: str
    min_score: float
    severity: RuleSeverity = RuleSeverity.WARNING
    dimension: str = ""

    def check(self, score: float) -> bool:
        """Check if rule is violated."""
        return score < self.min_score


@dataclass
class QualityIssue:
    """A quality issue."""

    id: str = field(default_factory=lambda: str(uuid4()))
    file_path: str = ""
    rule_name: str = ""
    dimension: str = ""
    current_score: float = 0.0
    expected_score: float = 0.0
    severity: RuleSeverity = RuleSeverity.WARNING
    description: str = ""
    suggestion: str = ""
    detected_at: float = field(default_factory=time.time)


@dataclass
class QualityReport:
    """Quality assessment report."""

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.ACCEPTABLE
    dimension_scores: dict[str, float] = field(default_factory=dict)
    issues: list[QualityIssue] = field(default_factory=list)
    files_analyzed: int = 0
    analysis_duration: float = 0.0


@dataclass
class QualityMetrics:
    """Basic quality metrics for a file."""

    file_path: str = ""
    overall_score: float = 0.0
    maintainability: float = 0.0
    readability: float = 0.0
    complexity: float = 0.0
    testability: float = 0.0
    documentation: float = 0.0


class QualityRuleEngine:
    """Simple rule engine for quality checks."""

    def __init__(self):
        self.rules: list[QualityRule] = []
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize basic quality rules."""
        self.rules = [
            QualityRule(
                name="maintainability_threshold",
                description="Maintainability score must be at least 70",
                min_score=70.0,
                severity=RuleSeverity.WARNING,
                dimension="maintainability",
            ),
            QualityRule(
                name="complexity_threshold",
                description="Complexity score must be at least 65",
                min_score=65.0,
                severity=RuleSeverity.ERROR,
                dimension="complexity",
            ),
            QualityRule(
                name="readability_threshold",
                description="Readability score must be at least 75",
                min_score=75.0,
                severity=RuleSeverity.WARNING,
                dimension="readability",
            ),
            QualityRule(
                name="testability_threshold",
                description="Testability score must be at least 70",
                min_score=70.0,
                severity=RuleSeverity.WARNING,
                dimension="testability",
            ),
            QualityRule(
                name="documentation_threshold",
                description="Documentation score must be at least 60",
                min_score=60.0,
                severity=RuleSeverity.INFO,
                dimension="documentation",
            ),
        ]

    def check_rules(self, metrics: QualityMetrics) -> list[QualityIssue]:
        """Check quality rules against metrics."""
        issues = []

        for rule in self.rules:
            if not rule.dimension:
                continue

            score = getattr(metrics, rule.dimension, 0.0)

            if rule.check(score):
                suggestion = self._get_suggestion(rule.dimension, score, rule.min_score)

                issue = QualityIssue(
                    file_path=metrics.file_path,
                    rule_name=rule.name,
                    dimension=rule.dimension,
                    current_score=score,
                    expected_score=rule.min_score,
                    severity=rule.severity,
                    description=rule.description,
                    suggestion=suggestion,
                )
                issues.append(issue)

        return issues

    def _get_suggestion(self, dimension: str, current: float, target: float) -> str:
        """Get improvement suggestion for a dimension."""
        suggestions = {
            "maintainability": "Refactor complex functions and improve naming",
            "complexity": "Simplify complex logic and reduce nesting",
            "readability": "Add comments and improve code structure",
            "testability": "Add unit tests and reduce coupling",
            "documentation": "Add docstrings and documentation",
        }
        return suggestions.get(dimension, "Improve code quality")


class QualityGuardian:
    """Simplified quality monitoring for A1."""

    def __init__(self):
        self.rule_engine = QualityRuleEngine()
        self.current_report: QualityReport | None = None
        self.report_history: list[QualityReport] = []
        self.active_issues: dict[str, QualityIssue] = {}

        # Simple metrics tracking
        self.metrics = {"total_analyses": 0, "issues_detected": 0, "average_quality": 0.0}

    def analyze_quality(self, file_metrics: list[QualityMetrics]) -> QualityReport:
        """Analyze quality for given file metrics."""
        start_time = time.time()

        all_issues = []
        dimension_totals = {}
        dimension_counts = {}

        # Process each file
        for metrics in file_metrics:
            # Check rules for issues
            issues = self.rule_engine.check_rules(metrics)
            all_issues.extend(issues)

            # Store active issues
            for issue in issues:
                self.active_issues[issue.id] = issue

            # Aggregate dimension scores
            for dim in ["maintainability", "readability", "complexity", "testability", "documentation"]:
                score = getattr(metrics, dim, 0.0)
                if score > 0:
                    dimension_totals[dim] = dimension_totals.get(dim, 0) + score
                    dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

        # Calculate dimension averages
        dimension_scores = {}
        for dim, total in dimension_totals.items():
            if dimension_counts[dim] > 0:
                dimension_scores[dim] = total / dimension_counts[dim]

        # Calculate overall score
        overall_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0.0

        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)

        # Create report
        report = QualityReport(
            overall_score=overall_score,
            quality_level=quality_level,
            dimension_scores=dimension_scores,
            issues=all_issues,
            files_analyzed=len(file_metrics),
            analysis_duration=time.time() - start_time,
        )

        # Update state
        self.current_report = report
        self.report_history.append(report)

        # Limit history
        if len(self.report_history) > 50:
            self.report_history = self.report_history[-50:]

        # Update metrics
        self.metrics["total_analyses"] += 1
        self.metrics["issues_detected"] += len(all_issues)
        self._update_average_quality(overall_score)

        return report

    def get_issues_for_file(self, file_path: str) -> list[QualityIssue]:
        """Get issues for a specific file."""
        return [issue for issue in self.active_issues.values() if issue.file_path == file_path]

    def resolve_issue(self, issue_id: str) -> bool:
        """Mark an issue as resolved."""
        if issue_id in self.active_issues:
            del self.active_issues[issue_id]
            return True
        return False

    def check_quality_gate(self, min_score: float = 70.0) -> tuple[bool, list[str]]:
        """Check if quality gate passes."""
        if not self.current_report:
            return False, ["No quality report available"]

        violations = []

        if self.current_report.overall_score < min_score:
            violations.append(f"Overall score {self.current_report.overall_score:.1f} below threshold {min_score}")

        # Check for critical issues
        critical_issues = [i for i in self.current_report.issues if i.severity == RuleSeverity.ERROR]
        if critical_issues:
            violations.append(f"{len(critical_issues)} critical issues must be resolved")

        return len(violations) == 0, violations

    def get_statistics(self) -> dict:
        """Get quality guardian statistics."""
        stats = self.metrics.copy()
        stats.update(
            {
                "active_issues": len(self.active_issues),
                "reports_generated": len(self.report_history),
                "current_quality_level": self.current_report.quality_level.value if self.current_report else "unknown",
            }
        )
        return stats

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 70:
            return QualityLevel.ACCEPTABLE
        else:
            return QualityLevel.POOR

    def _update_average_quality(self, new_score: float):
        """Update running average quality score."""
        current_avg = self.metrics["average_quality"]
        total_analyses = self.metrics["total_analyses"]

        if total_analyses <= 1:
            self.metrics["average_quality"] = new_score
        else:
            self.metrics["average_quality"] = (current_avg * (total_analyses - 1) + new_score) / total_analyses
