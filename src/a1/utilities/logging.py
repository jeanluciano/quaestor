"""Action logging and audit trail utilities.

Extracted from A1 Action Logger, Decision Logger, and Operations Logging.
Provides comprehensive action tracking with 85% complexity reduction.
"""

import json
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class ActionType(Enum):
    """Types of actions that can be logged."""

    COMMAND = "command"
    FILE_OPERATION = "file_operation"
    DECISION = "decision"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PERFORMANCE = "performance"
    SECURITY = "security"
    WORKFLOW = "workflow"
    LEARNING = "learning"


class ActionOutcome(Enum):
    """Possible outcomes of an action."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ActionSeverity(Enum):
    """Severity levels for actions."""

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


@dataclass
class ActionRecord:
    """Represents a logged action."""

    id: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    action_type: ActionType = ActionType.INFO
    action_name: str = ""
    description: str = ""
    outcome: ActionOutcome = ActionOutcome.SUCCESS
    severity: ActionSeverity = ActionSeverity.INFO
    duration_ms: float | None = None
    user: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    related_actions: list[int] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)


class ActionLogger:
    """Simplified action logging system with persistence."""

    def __init__(self, db_path: str | Path | None = None):
        """Initialize the action logger.

        Args:
            db_path: Path to SQLite database (None for in-memory)
        """
        self.db_path = str(db_path) if db_path else ":memory:"
        self._cache: list[ActionRecord] = []
        self._cache_size = 100
        self._sensitive_patterns = {
            "password",
            "token",
            "secret",
            "key",
            "credential",
            "auth",
            "private",
            "confidential",
        }
        # For in-memory databases, we need to maintain a connection
        self._conn = None
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
        self._init_database()

    def _get_connection(self):
        """Get database connection (persistent for in-memory)."""
        if self._conn:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_database(self):
        """Initialize the database schema."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    description TEXT,
                    outcome TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    duration_ms REAL,
                    user TEXT,
                    context TEXT,
                    error_message TEXT,
                    related_actions TEXT,
                    tags TEXT
                )
            """)

            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON actions(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action_type ON actions(action_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_outcome ON actions(outcome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON actions(severity)")

            if not self._conn:
                conn.commit()
        finally:
            if not self._conn:
                conn.close()

    def log_action(self, action: ActionRecord) -> int:
        """Log an action to the database.

        Args:
            action: Action record to log

        Returns:
            ID of the logged action
        """
        # Mask sensitive data
        action = self._mask_sensitive_data(action)

        # Add to cache
        self._cache.append(action)

        # Flush cache if needed
        if len(self._cache) >= self._cache_size:
            self._flush_cache()

        return action.id or 0

    def log(
        self,
        action_name: str,
        action_type: ActionType = ActionType.INFO,
        description: str = "",
        outcome: ActionOutcome = ActionOutcome.SUCCESS,
        severity: ActionSeverity = ActionSeverity.INFO,
        duration_ms: float | None = None,
        user: str | None = None,
        context: dict[str, Any] | None = None,
        error: Exception | None = None,
        tags: set[str] | None = None,
    ) -> int:
        """Convenience method to log an action.

        Args:
            action_name: Name of the action
            action_type: Type of action
            description: Detailed description
            outcome: Action outcome
            severity: Severity level
            duration_ms: Duration in milliseconds
            user: User who performed the action
            context: Additional context
            error: Exception if any
            tags: Tags for categorization

        Returns:
            ID of the logged action
        """
        record = ActionRecord(
            action_type=action_type,
            action_name=action_name,
            description=description,
            outcome=outcome,
            severity=severity,
            duration_ms=duration_ms,
            user=user,
            context=context or {},
            error_message=str(error) if error else None,
            tags=tags or set(),
        )

        return self.log_action(record)

    @contextmanager
    def timed_action(self, action_name: str, action_type: ActionType = ActionType.INFO, **kwargs):
        """Context manager for timing actions.

        Args:
            action_name: Name of the action
            action_type: Type of action
            **kwargs: Additional arguments for log()

        Yields:
            ActionRecord that will be logged
        """
        start_time = time.time()
        record = ActionRecord(action_name=action_name, action_type=action_type, **kwargs)

        try:
            yield record
            record.outcome = ActionOutcome.SUCCESS
        except Exception as e:
            record.outcome = ActionOutcome.FAILURE
            record.error_message = str(e)
            record.severity = ActionSeverity.ERROR
            raise
        finally:
            record.duration_ms = (time.time() - start_time) * 1000
            self.log_action(record)

    def query_actions(
        self,
        action_type: ActionType | None = None,
        outcome: ActionOutcome | None = None,
        severity: ActionSeverity | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        user: str | None = None,
        tags: set[str] | None = None,
        limit: int = 100,
    ) -> list[ActionRecord]:
        """Query actions from the database.

        Args:
            action_type: Filter by action type
            outcome: Filter by outcome
            severity: Filter by minimum severity
            start_time: Start of time range
            end_time: End of time range
            user: Filter by user
            tags: Filter by tags (any match)
            limit: Maximum results

        Returns:
            List of matching action records
        """
        # Flush cache first
        self._flush_cache()

        query = "SELECT * FROM actions WHERE 1=1"
        params = []

        if action_type:
            query += " AND action_type = ?"
            params.append(action_type.value)

        if outcome:
            query += " AND outcome = ?"
            params.append(outcome.value)

        if severity:
            query += " AND severity >= ?"
            params.append(severity.value)

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        if user:
            query += " AND user = ?"
            params.append(user)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            results = []
            for row in cursor:
                record = self._row_to_record(row)

                # Filter by tags if specified
                if tags and not record.tags.intersection(tags):
                    continue

                results.append(record)

            return results
        finally:
            if not self._conn:
                conn.close()

    def get_statistics(self, start_time: datetime | None = None, end_time: datetime | None = None) -> dict[str, Any]:
        """Get action statistics.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Statistics dictionary
        """
        self._flush_cache()

        query = """
            SELECT
                action_type,
                outcome,
                COUNT(*) as count,
                AVG(duration_ms) as avg_duration,
                MIN(duration_ms) as min_duration,
                MAX(duration_ms) as max_duration
            FROM actions
            WHERE duration_ms IS NOT NULL
        """

        params = []
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        query += " GROUP BY action_type, outcome"

        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params)

            from collections import defaultdict as dd

            stats = {
                "by_type": dd(lambda: dd(dict)),
                "total_actions": 0,
                "total_failures": 0,
                "average_duration_ms": 0.0,
            }

            total_duration = 0.0
            duration_count = 0

            for row in cursor:
                action_type = row[0]
                outcome = row[1]
                count = row[2]
                avg_duration = row[3]

                stats["by_type"][action_type][outcome] = {
                    "count": count,
                    "avg_duration_ms": avg_duration,
                    "min_duration_ms": row[4],
                    "max_duration_ms": row[5],
                }

                stats["total_actions"] += count
                if outcome == ActionOutcome.FAILURE.value:
                    stats["total_failures"] += count

                if avg_duration:
                    total_duration += avg_duration * count
                    duration_count += count

            if duration_count > 0:
                stats["average_duration_ms"] = total_duration / duration_count

            stats["failure_rate"] = (
                stats["total_failures"] / stats["total_actions"] if stats["total_actions"] > 0 else 0.0
            )

            return dict(stats)
        finally:
            if not self._conn:
                conn.close()

    def detect_anomalies(self, window_minutes: int = 60, failure_threshold: float = 0.3) -> list[dict[str, Any]]:
        """Detect anomalous patterns in recent actions.

        Args:
            window_minutes: Time window to analyze
            failure_threshold: Failure rate threshold

        Returns:
            List of detected anomalies
        """
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_actions = self.query_actions(start_time=start_time, limit=1000)

        anomalies = []

        # Group by action type
        from collections import defaultdict

        by_type = defaultdict(list)
        for action in recent_actions:
            by_type[action.action_type].append(action)

        # Check failure rates
        for action_type, actions in by_type.items():
            failures = sum(1 for a in actions if a.outcome == ActionOutcome.FAILURE)
            failure_rate = failures / len(actions) if actions else 0

            if failure_rate > failure_threshold:
                anomalies.append(
                    {
                        "type": "high_failure_rate",
                        "action_type": action_type.value,
                        "failure_rate": failure_rate,
                        "sample_size": len(actions),
                        "recent_errors": [a.error_message for a in actions[-5:] if a.error_message],
                    }
                )

        # Check for unusual patterns
        action_counts = defaultdict(int)
        for action in recent_actions:
            action_counts[action.action_name] += 1

        # Find actions that spike in frequency
        if action_counts:
            avg_count = sum(action_counts.values()) / len(action_counts)
            # Also check absolute threshold
            for action_name, count in action_counts.items():
                if count > max(avg_count * 2, 5):  # 2x average or > 5
                    anomalies.append(
                        {"type": "frequency_spike", "action_name": action_name, "count": count, "average": avg_count}
                    )

        return anomalies

    def _mask_sensitive_data(self, action: ActionRecord) -> ActionRecord:
        """Mask sensitive data in action record.

        Args:
            action: Action record to mask

        Returns:
            Masked action record
        """
        # Check description
        for pattern in self._sensitive_patterns:
            if pattern in action.description.lower():
                action.description = f"[MASKED: Contains {pattern}]"
                break

        # Check context
        masked_context = {}
        for key, value in action.context.items():
            if (
                any(pattern in key.lower() for pattern in self._sensitive_patterns)
                or isinstance(value, str)
                and any(pattern in value.lower() for pattern in self._sensitive_patterns)
            ):
                masked_context[key] = "[MASKED]"
            else:
                masked_context[key] = value

        action.context = masked_context
        return action

    def _flush_cache(self):
        """Flush cached actions to database."""
        if not self._cache:
            return

        conn = self._get_connection()
        try:
            for action in self._cache:
                cursor = conn.execute(
                    """
                    INSERT INTO actions (
                        timestamp, action_type, action_name, description,
                        outcome, severity, duration_ms, user, context,
                        error_message, related_actions, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        action.timestamp.isoformat(),
                        action.action_type.value,
                        action.action_name,
                        action.description,
                        action.outcome.value,
                        action.severity.value,
                        action.duration_ms,
                        action.user,
                        json.dumps(action.context),
                        action.error_message,
                        json.dumps(action.related_actions),
                        json.dumps(list(action.tags)),
                    ),
                )

                if not action.id:
                    action.id = cursor.lastrowid

            if self._conn:
                self._conn.commit()
            else:
                conn.commit()
        finally:
            if not self._conn:
                conn.close()

        self._cache.clear()

    def _row_to_record(self, row: sqlite3.Row) -> ActionRecord:
        """Convert database row to ActionRecord.

        Args:
            row: Database row

        Returns:
            ActionRecord instance
        """
        return ActionRecord(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            action_type=ActionType(row["action_type"]),
            action_name=row["action_name"],
            description=row["description"] or "",
            outcome=ActionOutcome(row["outcome"]),
            severity=ActionSeverity(row["severity"]),
            duration_ms=row["duration_ms"],
            user=row["user"],
            context=json.loads(row["context"]) if row["context"] else {},
            error_message=row["error_message"],
            related_actions=json.loads(row["related_actions"]) if row["related_actions"] else [],
            tags=set(json.loads(row["tags"])) if row["tags"] else set(),
        )

    def close(self):
        """Close the logger and flush remaining cache."""
        self._flush_cache()
        if self._conn:
            self._conn.close()
            self._conn = None


def create_workflow_logger(db_path: str | Path | None = None) -> ActionLogger:
    """Create a logger optimized for workflow tracking.

    Args:
        db_path: Database path

    Returns:
        Configured ActionLogger
    """
    logger = ActionLogger(db_path)
    logger._cache_size = 50  # Smaller cache for more frequent writes
    return logger


def create_audit_logger(db_path: str | Path | None = None) -> ActionLogger:
    """Create a logger optimized for audit trails.

    Args:
        db_path: Database path

    Returns:
        Configured ActionLogger
    """
    logger = ActionLogger(db_path)
    logger._cache_size = 1  # Write immediately for audit trail
    return logger


# Convenience functions for common logging patterns


def log_decision(
    logger: ActionLogger,
    decision_name: str,
    reasoning: str,
    confidence: float,
    outcome: ActionOutcome = ActionOutcome.SUCCESS,
    alternatives: list[str] | None = None,
) -> int:
    """Log a decision with context.

    Args:
        logger: ActionLogger instance
        decision_name: Name of the decision
        reasoning: Reasoning behind the decision
        confidence: Confidence level (0-1)
        outcome: Decision outcome
        alternatives: Alternative options considered

    Returns:
        Action ID
    """
    return logger.log(
        action_name=f"decision:{decision_name}",
        action_type=ActionType.DECISION,
        description=reasoning,
        outcome=outcome,
        context={"confidence": confidence, "alternatives": alternatives or []},
        tags={"decision", f"confidence:{int(confidence * 100)}"},
    )


def log_performance(
    logger: ActionLogger, operation_name: str, duration_ms: float, metrics: dict[str, float] | None = None
) -> int:
    """Log a performance measurement.

    Args:
        logger: ActionLogger instance
        operation_name: Name of the operation
        duration_ms: Duration in milliseconds
        metrics: Additional performance metrics

    Returns:
        Action ID
    """
    context = {"metrics": metrics or {}}

    # Determine outcome based on duration thresholds
    outcome = ActionOutcome.SUCCESS
    severity = ActionSeverity.INFO

    if duration_ms > 10000:  # > 10 seconds
        outcome = ActionOutcome.TIMEOUT
        severity = ActionSeverity.ERROR
    elif duration_ms > 5000:  # > 5 seconds
        outcome = ActionOutcome.PARTIAL
        severity = ActionSeverity.WARNING

    return logger.log(
        action_name=f"performance:{operation_name}",
        action_type=ActionType.PERFORMANCE,
        description=f"Operation completed in {duration_ms:.2f}ms",
        outcome=outcome,
        severity=severity,
        duration_ms=duration_ms,
        context=context,
        tags={"performance", f"duration:{int(duration_ms)}"},
    )


def log_workflow_step(
    logger: ActionLogger,
    workflow_name: str,
    step_name: str,
    step_number: int,
    total_steps: int,
    outcome: ActionOutcome = ActionOutcome.SUCCESS,
    context: dict[str, Any] | None = None,
) -> int:
    """Log a workflow step execution.

    Args:
        logger: ActionLogger instance
        workflow_name: Name of the workflow
        step_name: Name of the step
        step_number: Current step number
        total_steps: Total number of steps
        outcome: Step outcome
        context: Additional context

    Returns:
        Action ID
    """
    return logger.log(
        action_name=f"{workflow_name}:{step_name}",
        action_type=ActionType.WORKFLOW,
        description=f"Step {step_number}/{total_steps}: {step_name}",
        outcome=outcome,
        context={
            "workflow": workflow_name,
            "step": step_name,
            "progress": step_number / total_steps,
            **(context or {}),
        },
        tags={"workflow", workflow_name.lower().replace(" ", "_"), f"step:{step_number}"},
    )
