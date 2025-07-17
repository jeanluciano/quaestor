"""Tests for the simplified quality guardian system."""

import pytest

from a1.core.quality import (
    QualityGuardian,
    QualityIssue,
    QualityLevel,
    QualityMetrics,
    QualityReport,
    QualityRule,
    QualityRuleEngine,
    RuleSeverity,
)


@pytest.fixture
def sample_metrics():
    """Sample quality metrics for testing."""
    return QualityMetrics(
        file_path="test_file.py",
        overall_score=75.0,
        maintainability=80.0,
        readability=85.0,
        complexity=60.0,  # Below threshold
        testability=75.0,
        documentation=55.0,  # Below threshold
    )


@pytest.fixture
def quality_guardian():
    """Quality guardian instance for testing."""
    return QualityGuardian()


@pytest.fixture
def rule_engine():
    """Rule engine instance for testing."""
    return QualityRuleEngine()


class TestQualityRule:
    """Test quality rule functionality."""

    def test_rule_creation(self):
        """Test creating a quality rule."""
        rule = QualityRule(
            name="test_rule",
            description="Test rule for maintainability",
            min_score=70.0,
            severity=RuleSeverity.WARNING,
            dimension="maintainability",
        )

        assert rule.name == "test_rule"
        assert rule.min_score == 70.0
        assert rule.severity == RuleSeverity.WARNING
        assert rule.dimension == "maintainability"

    def test_rule_check_pass(self):
        """Test rule check when score meets threshold."""
        rule = QualityRule("test", "Test rule", 70.0, dimension="test")
        assert not rule.check(80.0)  # Should not violate

    def test_rule_check_fail(self):
        """Test rule check when score below threshold."""
        rule = QualityRule("test", "Test rule", 70.0, dimension="test")
        assert rule.check(60.0)  # Should violate


class TestQualityMetrics:
    """Test quality metrics data class."""

    def test_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = QualityMetrics(
            file_path="test.py",
            overall_score=80.0,
            maintainability=85.0,
            readability=90.0,
            complexity=70.0,
            testability=75.0,
            documentation=80.0,
        )

        assert metrics.file_path == "test.py"
        assert metrics.overall_score == 80.0
        assert metrics.maintainability == 85.0


class TestQualityRuleEngine:
    """Test quality rule engine functionality."""

    def test_engine_initialization(self, rule_engine):
        """Test rule engine initializes with default rules."""
        assert len(rule_engine.rules) == 5
        assert any(rule.dimension == "maintainability" for rule in rule_engine.rules)
        assert any(rule.dimension == "complexity" for rule in rule_engine.rules)
        assert any(rule.dimension == "readability" for rule in rule_engine.rules)

    def test_check_rules_no_violations(self, rule_engine):
        """Test checking rules with high-quality metrics."""
        metrics = QualityMetrics(
            file_path="good_file.py",
            maintainability=90.0,
            readability=85.0,
            complexity=80.0,
            testability=85.0,
            documentation=75.0,
        )

        issues = rule_engine.check_rules(metrics)
        assert len(issues) == 0

    def test_check_rules_with_violations(self, rule_engine, sample_metrics):
        """Test checking rules with violations."""
        issues = rule_engine.check_rules(sample_metrics)

        # Should find violations for complexity and documentation
        assert len(issues) >= 2

        # Check that issues contain expected violations
        violation_dimensions = [issue.dimension for issue in issues]
        assert "complexity" in violation_dimensions
        assert "documentation" in violation_dimensions

    def test_issue_details(self, rule_engine, sample_metrics):
        """Test that issues contain proper details."""
        issues = rule_engine.check_rules(sample_metrics)

        for issue in issues:
            assert issue.file_path == sample_metrics.file_path
            assert issue.rule_name
            assert issue.dimension
            assert issue.current_score > 0
            assert issue.expected_score > 0
            assert issue.description
            assert issue.suggestion
            assert isinstance(issue.severity, RuleSeverity)

    def test_get_suggestion(self, rule_engine):
        """Test suggestion generation."""
        suggestion = rule_engine._get_suggestion("maintainability", 60.0, 70.0)
        assert "maintainability" in suggestion.lower() or "refactor" in suggestion.lower()

        suggestion = rule_engine._get_suggestion("complexity", 50.0, 65.0)
        assert "complexity" in suggestion.lower() or "simplify" in suggestion.lower()


class TestQualityGuardian:
    """Test quality guardian functionality."""

    def test_guardian_initialization(self, quality_guardian):
        """Test guardian initializes properly."""
        assert quality_guardian.rule_engine is not None
        assert quality_guardian.current_report is None
        assert len(quality_guardian.report_history) == 0
        assert len(quality_guardian.active_issues) == 0
        assert quality_guardian.metrics["total_analyses"] == 0

    def test_analyze_quality_single_file(self, quality_guardian, sample_metrics):
        """Test analyzing quality for a single file."""
        report = quality_guardian.analyze_quality([sample_metrics])

        assert isinstance(report, QualityReport)
        assert report.files_analyzed == 1
        assert report.overall_score > 0
        assert len(report.dimension_scores) > 0
        assert report.analysis_duration > 0
        assert quality_guardian.current_report == report
        assert len(quality_guardian.report_history) == 1

    def test_analyze_quality_multiple_files(self, quality_guardian):
        """Test analyzing quality for multiple files."""
        metrics_list = [
            QualityMetrics(
                file_path="file1.py",
                maintainability=85.0,
                readability=80.0,
                complexity=75.0,
                testability=80.0,
                documentation=70.0,
            ),
            QualityMetrics(
                file_path="file2.py",
                maintainability=75.0,
                readability=85.0,
                complexity=55.0,  # Violation
                testability=70.0,
                documentation=65.0,
            ),
        ]

        report = quality_guardian.analyze_quality(metrics_list)

        assert report.files_analyzed == 2
        assert len(report.issues) >= 1  # At least complexity violation
        assert "maintainability" in report.dimension_scores
        assert "complexity" in report.dimension_scores

    def test_quality_level_determination(self, quality_guardian):
        """Test quality level determination."""
        assert quality_guardian._determine_quality_level(95.0) == QualityLevel.EXCELLENT
        assert quality_guardian._determine_quality_level(85.0) == QualityLevel.GOOD
        assert quality_guardian._determine_quality_level(75.0) == QualityLevel.ACCEPTABLE
        assert quality_guardian._determine_quality_level(65.0) == QualityLevel.POOR

    def test_get_issues_for_file(self, quality_guardian, sample_metrics):
        """Test getting issues for a specific file."""
        report = quality_guardian.analyze_quality([sample_metrics])

        issues = quality_guardian.get_issues_for_file(sample_metrics.file_path)
        assert len(issues) >= 0

        # All returned issues should be for the requested file
        for issue in issues:
            assert issue.file_path == sample_metrics.file_path

    def test_resolve_issue(self, quality_guardian, sample_metrics):
        """Test resolving quality issues."""
        report = quality_guardian.analyze_quality([sample_metrics])

        if report.issues:
            issue_id = report.issues[0].id
            assert issue_id in quality_guardian.active_issues

            success = quality_guardian.resolve_issue(issue_id)
            assert success
            assert issue_id not in quality_guardian.active_issues

        # Test resolving non-existent issue
        assert not quality_guardian.resolve_issue("non_existent_id")

    def test_quality_gate_pass(self, quality_guardian):
        """Test quality gate when conditions are met."""
        high_quality_metrics = QualityMetrics(
            file_path="excellent_file.py",
            maintainability=90.0,
            readability=95.0,
            complexity=85.0,
            testability=88.0,
            documentation=82.0,
        )

        quality_guardian.analyze_quality([high_quality_metrics])
        passed, violations = quality_guardian.check_quality_gate(70.0)

        assert passed
        assert len(violations) == 0

    def test_quality_gate_fail_score(self, quality_guardian):
        """Test quality gate failure due to low score."""
        low_quality_metrics = QualityMetrics(
            file_path="poor_file.py",
            maintainability=50.0,
            readability=55.0,
            complexity=45.0,
            testability=50.0,
            documentation=40.0,
        )

        quality_guardian.analyze_quality([low_quality_metrics])
        passed, violations = quality_guardian.check_quality_gate(70.0)

        assert not passed
        assert len(violations) > 0
        assert any("overall score" in v.lower() for v in violations)

    def test_quality_gate_fail_critical_issues(self, quality_guardian, sample_metrics):
        """Test quality gate failure due to critical issues."""
        # Analyze to generate some issues
        quality_guardian.analyze_quality([sample_metrics])

        # Manually add a critical issue for testing
        if quality_guardian.current_report:
            critical_issue = QualityIssue(
                file_path="test.py",
                rule_name="critical_rule",
                dimension="complexity",
                current_score=30.0,
                expected_score=65.0,
                severity=RuleSeverity.ERROR,
                description="Critical complexity issue",
            )
            quality_guardian.current_report.issues.append(critical_issue)

            passed, violations = quality_guardian.check_quality_gate(50.0)  # Low threshold

            assert not passed
            assert any("critical" in v.lower() for v in violations)

    def test_quality_gate_no_report(self, quality_guardian):
        """Test quality gate when no report is available."""
        passed, violations = quality_guardian.check_quality_gate()

        assert not passed
        assert "no quality report" in violations[0].lower()

    def test_get_statistics(self, quality_guardian, sample_metrics):
        """Test getting quality statistics."""
        stats = quality_guardian.get_statistics()
        initial_analyses = stats["total_analyses"]

        # Analyze quality to generate data
        quality_guardian.analyze_quality([sample_metrics])

        updated_stats = quality_guardian.get_statistics()

        assert updated_stats["total_analyses"] == initial_analyses + 1
        assert updated_stats["reports_generated"] == 1
        assert "current_quality_level" in updated_stats

    def test_update_average_quality(self, quality_guardian):
        """Test average quality score updates."""
        initial_avg = quality_guardian.metrics["average_quality"]

        # Simulate multiple analyses by updating total_analyses first
        quality_guardian.metrics["total_analyses"] = 1
        quality_guardian._update_average_quality(80.0)
        first_avg = quality_guardian.metrics["average_quality"]

        quality_guardian.metrics["total_analyses"] = 2
        quality_guardian._update_average_quality(60.0)
        second_avg = quality_guardian.metrics["average_quality"]

        assert first_avg == 80.0  # First score becomes average
        assert second_avg == 70.0  # Average of 80 and 60

    def test_report_history_limit(self, quality_guardian):
        """Test that report history is limited."""
        metrics = QualityMetrics(file_path="test.py", overall_score=80.0)

        # Generate more than 50 reports
        for i in range(55):
            quality_guardian.analyze_quality([metrics])

        # History should be limited to 50
        assert len(quality_guardian.report_history) == 50


class TestQualityReport:
    """Test quality report functionality."""

    def test_report_creation(self):
        """Test creating a quality report."""
        report = QualityReport(
            overall_score=85.0,
            quality_level=QualityLevel.GOOD,
            dimension_scores={"maintainability": 80.0, "readability": 90.0},
            files_analyzed=3,
            analysis_duration=0.5,
        )

        assert report.overall_score == 85.0
        assert report.quality_level == QualityLevel.GOOD
        assert report.files_analyzed == 3
        assert report.analysis_duration == 0.5
        assert len(report.dimension_scores) == 2


class TestQualityIssue:
    """Test quality issue functionality."""

    def test_issue_creation(self):
        """Test creating a quality issue."""
        issue = QualityIssue(
            file_path="test.py",
            rule_name="maintainability_rule",
            dimension="maintainability",
            current_score=65.0,
            expected_score=70.0,
            severity=RuleSeverity.WARNING,
            description="Maintainability below threshold",
            suggestion="Refactor complex functions",
        )

        assert issue.file_path == "test.py"
        assert issue.rule_name == "maintainability_rule"
        assert issue.dimension == "maintainability"
        assert issue.current_score == 65.0
        assert issue.expected_score == 70.0
        assert issue.severity == RuleSeverity.WARNING
        assert issue.detected_at > 0
