"""Tests for action logging utilities."""

import time
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from a1.utilities.logging import (
    ActionLogger,
    ActionOutcome,
    ActionRecord,
    ActionSeverity,
    ActionType,
    create_audit_logger,
    create_workflow_logger,
    log_decision,
    log_performance,
    log_workflow_step,
)


class TestActionRecord:
    """Test ActionRecord dataclass."""

    def test_default_values(self):
        """Test default values for ActionRecord."""
        record = ActionRecord()

        assert record.id is None
        assert isinstance(record.timestamp, datetime)
        assert record.action_type == ActionType.INFO
        assert record.outcome == ActionOutcome.SUCCESS
        assert record.severity == ActionSeverity.INFO
        assert record.context == {}
        assert record.tags == set()

    def test_custom_values(self):
        """Test ActionRecord with custom values."""
        record = ActionRecord(
            action_name="test_action",
            action_type=ActionType.COMMAND,
            description="Test description",
            outcome=ActionOutcome.FAILURE,
            severity=ActionSeverity.ERROR,
            duration_ms=123.45,
            user="test_user",
            context={"key": "value"},
            error_message="Test error",
            related_actions=[1, 2, 3],
            tags={"tag1", "tag2"},
        )

        assert record.action_name == "test_action"
        assert record.action_type == ActionType.COMMAND
        assert record.outcome == ActionOutcome.FAILURE
        assert record.tags == {"tag1", "tag2"}


class TestActionLogger:
    """Test ActionLogger functionality."""

    def test_initialization(self):
        """Test logger initialization."""
        # In-memory logger
        logger = ActionLogger()
        assert logger.db_path == ":memory:"

        # File-based logger
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            logger = ActionLogger(db_path)
            assert logger.db_path == str(db_path)

    def test_log_action(self):
        """Test logging a single action."""
        logger = ActionLogger()

        record = ActionRecord(action_name="test_action", description="Test description", action_type=ActionType.COMMAND)

        action_id = logger.log_action(record)
        assert action_id >= 0

        # Flush cache to ensure it's in database
        logger._flush_cache()

        # Query the action
        results = logger.query_actions(limit=1)
        assert len(results) == 1
        assert results[0].action_name == "test_action"

    def test_log_convenience_method(self):
        """Test the convenience log method."""
        logger = ActionLogger()

        action_id = logger.log(
            action_name="convenience_test",
            action_type=ActionType.FILE_OPERATION,
            description="Testing convenience method",
            outcome=ActionOutcome.SUCCESS,
            severity=ActionSeverity.INFO,
            duration_ms=50.0,
            context={"file": "test.txt"},
            tags={"test", "convenience"},
        )

        assert action_id >= 0

        results = logger.query_actions(action_type=ActionType.FILE_OPERATION)
        assert len(results) == 1
        assert results[0].action_name == "convenience_test"
        assert results[0].duration_ms == 50.0
        assert "test" in results[0].tags

    def test_timed_action_success(self):
        """Test timing an action that succeeds."""
        logger = ActionLogger()

        with logger.timed_action("timed_test", ActionType.PERFORMANCE) as record:
            time.sleep(0.01)  # 10ms
            record.context["test"] = "value"

        results = logger.query_actions(action_type=ActionType.PERFORMANCE)
        assert len(results) == 1
        assert results[0].action_name == "timed_test"
        assert results[0].outcome == ActionOutcome.SUCCESS
        assert results[0].duration_ms >= 10.0
        assert results[0].context["test"] == "value"

    def test_timed_action_failure(self):
        """Test timing an action that fails."""
        logger = ActionLogger()

        with pytest.raises(ValueError):
            with logger.timed_action("failed_test", ActionType.ERROR) as record:
                raise ValueError("Test error")

        results = logger.query_actions(action_type=ActionType.ERROR)
        assert len(results) == 1
        assert results[0].outcome == ActionOutcome.FAILURE
        assert results[0].error_message == "Test error"
        assert results[0].severity == ActionSeverity.ERROR

    def test_query_actions_filters(self):
        """Test querying actions with various filters."""
        logger = ActionLogger()

        # Log various actions
        logger.log("action1", ActionType.COMMAND, outcome=ActionOutcome.SUCCESS)
        logger.log("action2", ActionType.FILE_OPERATION, outcome=ActionOutcome.FAILURE)
        logger.log("action3", ActionType.COMMAND, outcome=ActionOutcome.SUCCESS, user="user1")
        logger.log("action4", ActionType.ERROR, severity=ActionSeverity.ERROR)
        logger.log("action5", ActionType.INFO, tags={"important", "test"})

        # Test type filter
        results = logger.query_actions(action_type=ActionType.COMMAND)
        assert len(results) == 2

        # Test outcome filter
        results = logger.query_actions(outcome=ActionOutcome.FAILURE)
        assert len(results) == 1
        assert results[0].action_name == "action2"

        # Test user filter
        results = logger.query_actions(user="user1")
        assert len(results) == 1
        assert results[0].action_name == "action3"

        # Test severity filter
        results = logger.query_actions(severity=ActionSeverity.ERROR)
        assert len(results) == 1
        assert results[0].action_name == "action4"

        # Test tag filter
        results = logger.query_actions(tags={"important"})
        assert len(results) == 1
        assert results[0].action_name == "action5"

    def test_query_time_range(self):
        """Test querying actions within a time range."""
        logger = ActionLogger()

        # Log actions with different timestamps
        now = datetime.now()

        record1 = ActionRecord(action_name="past_action", timestamp=now - timedelta(hours=2))
        record2 = ActionRecord(action_name="recent_action", timestamp=now - timedelta(minutes=30))
        record3 = ActionRecord(action_name="current_action", timestamp=now)

        logger.log_action(record1)
        logger.log_action(record2)
        logger.log_action(record3)

        # Query last hour
        results = logger.query_actions(start_time=now - timedelta(hours=1), end_time=now)
        assert len(results) == 2
        assert all(r.action_name in ["recent_action", "current_action"] for r in results)

    def test_get_statistics(self):
        """Test getting action statistics."""
        logger = ActionLogger()

        # Log various actions with durations
        logger.log("cmd1", ActionType.COMMAND, duration_ms=100, outcome=ActionOutcome.SUCCESS)
        logger.log("cmd2", ActionType.COMMAND, duration_ms=200, outcome=ActionOutcome.SUCCESS)
        logger.log("cmd3", ActionType.COMMAND, duration_ms=150, outcome=ActionOutcome.FAILURE)
        logger.log("file1", ActionType.FILE_OPERATION, duration_ms=50, outcome=ActionOutcome.SUCCESS)
        logger.log("file2", ActionType.FILE_OPERATION, duration_ms=75, outcome=ActionOutcome.SUCCESS)

        stats = logger.get_statistics()

        assert stats["total_actions"] == 5
        assert stats["total_failures"] == 1
        assert stats["failure_rate"] == 0.2

        # Check command statistics
        cmd_stats = stats["by_type"]["command"]
        assert cmd_stats["success"]["count"] == 2
        assert cmd_stats["success"]["avg_duration_ms"] == 150.0
        assert cmd_stats["failure"]["count"] == 1

        # Check file operation statistics
        file_stats = stats["by_type"]["file_operation"]
        assert file_stats["success"]["count"] == 2
        assert file_stats["success"]["avg_duration_ms"] == 62.5

    def test_detect_anomalies(self):
        """Test anomaly detection."""
        logger = ActionLogger()

        # Create a pattern with high failure rate
        for _ in range(7):
            logger.log("failing_action", ActionType.ERROR, outcome=ActionOutcome.FAILURE)
        for _ in range(3):
            logger.log("failing_action", ActionType.ERROR, outcome=ActionOutcome.SUCCESS)

        # Create a frequency spike
        for _ in range(20):
            logger.log("frequent_action", ActionType.INFO)

        # Normal actions
        logger.log("normal_action1", ActionType.INFO)
        logger.log("normal_action2", ActionType.INFO)

        anomalies = logger.detect_anomalies(window_minutes=60, failure_threshold=0.5)

        # Should detect high failure rate
        failure_anomalies = [a for a in anomalies if a["type"] == "high_failure_rate"]
        assert len(failure_anomalies) == 1
        assert failure_anomalies[0]["failure_rate"] == 0.7

        # Should detect frequency spike
        spike_anomalies = [a for a in anomalies if a["type"] == "frequency_spike"]
        assert len(spike_anomalies) >= 1
        assert any(a["action_name"] == "frequent_action" for a in spike_anomalies)

    def test_sensitive_data_masking(self):
        """Test masking of sensitive data."""
        logger = ActionLogger()

        # Log with sensitive data
        logger.log(
            action_name="auth_action",
            description="User password is secret123",
            context={"token": "abcd1234", "api_key": "xyz789", "normal_field": "visible"},
        )

        results = logger.query_actions()
        assert len(results) == 1

        # Check description is masked
        assert "secret123" not in results[0].description
        assert "MASKED" in results[0].description

        # Check context is masked
        assert results[0].context["token"] == "[MASKED]"
        assert results[0].context["api_key"] == "[MASKED]"
        assert results[0].context["normal_field"] == "visible"

    def test_cache_flushing(self):
        """Test cache flushing behavior."""
        logger = ActionLogger()
        logger._cache_size = 5  # Small cache for testing

        # Log actions to fill cache
        for i in range(4):
            logger.log(f"action{i}", ActionType.INFO)

        # Cache should not be flushed yet
        assert len(logger._cache) == 4

        # This should trigger flush
        logger.log("action4", ActionType.INFO)
        assert len(logger._cache) == 0

        # Verify all actions are in database
        results = logger.query_actions(limit=10)
        assert len(results) == 5


class TestSpecializedLoggers:
    """Test specialized logger factories."""

    def test_workflow_logger(self):
        """Test workflow-optimized logger."""
        logger = create_workflow_logger()
        assert logger._cache_size == 50

    def test_audit_logger(self):
        """Test audit-optimized logger."""
        logger = create_audit_logger()
        assert logger._cache_size == 1  # Immediate writes


class TestConvenienceFunctions:
    """Test convenience logging functions."""

    def test_log_decision(self):
        """Test decision logging."""
        logger = ActionLogger()

        action_id = log_decision(
            logger,
            decision_name="choose_algorithm",
            reasoning="Based on data size and complexity",
            confidence=0.85,
            alternatives=["algorithm_a", "algorithm_b"],
        )

        results = logger.query_actions(action_type=ActionType.DECISION)
        assert len(results) == 1
        assert results[0].action_name == "decision:choose_algorithm"
        assert results[0].context["confidence"] == 0.85
        assert "algorithm_a" in results[0].context["alternatives"]
        assert "decision" in results[0].tags
        assert "confidence:85" in results[0].tags

    def test_log_performance(self):
        """Test performance logging."""
        logger = ActionLogger()

        # Fast operation
        log_performance(logger, operation_name="fast_op", duration_ms=100.0, metrics={"cpu": 0.5, "memory": 100})

        # Slow operation
        log_performance(logger, operation_name="slow_op", duration_ms=6000.0)

        # Very slow operation
        log_performance(logger, operation_name="very_slow_op", duration_ms=11000.0)

        results = logger.query_actions(action_type=ActionType.PERFORMANCE)
        assert len(results) == 3

        # Check outcomes based on duration
        fast = next(r for r in results if r.action_name == "performance:fast_op")
        assert fast.outcome == ActionOutcome.SUCCESS
        assert fast.severity == ActionSeverity.INFO

        slow = next(r for r in results if r.action_name == "performance:slow_op")
        assert slow.outcome == ActionOutcome.PARTIAL
        assert slow.severity == ActionSeverity.WARNING

        very_slow = next(r for r in results if r.action_name == "performance:very_slow_op")
        assert very_slow.outcome == ActionOutcome.TIMEOUT
        assert very_slow.severity == ActionSeverity.ERROR

    def test_log_workflow_step(self):
        """Test workflow step logging."""
        logger = ActionLogger()

        # Log workflow steps
        for i in range(1, 4):
            log_workflow_step(
                logger,
                workflow_name="data_processing",
                step_name=f"step_{i}",
                step_number=i,
                total_steps=3,
                outcome=ActionOutcome.SUCCESS,
                context={"data_size": i * 100},
            )

        results = logger.query_actions(action_type=ActionType.WORKFLOW)
        assert len(results) == 3

        # Check workflow tags and progress
        for i, result in enumerate(reversed(results)):  # Results are in reverse order
            assert f"step:{i+1}" in result.tags
            assert result.context["progress"] == (i + 1) / 3
            assert result.context["workflow"] == "data_processing"
            assert "workflow" in result.tags
            assert "data_processing" in result.tags
