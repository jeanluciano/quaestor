"""Test execution history tracking.

This module tracks test execution results over time, enabling trend analysis
and test reliability metrics.
"""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from a1.core.event_bus import EventBus

from ..events import SystemEvent


@dataclass
class TestRun:
    """Record of a single test execution."""

    test_name: str
    test_file: str
    timestamp: datetime
    duration_ms: float
    status: str  # 'passed', 'failed', 'skipped', 'error'
    failure_message: str | None = None
    coverage_percentage: float | None = None
    branch_id: str | None = None  # Git branch
    commit_hash: str | None = None


@dataclass
class TestStats:
    """Statistical information about a test."""

    test_name: str
    total_runs: int
    pass_count: int
    fail_count: int
    skip_count: int
    average_duration_ms: float
    failure_rate: float
    flakiness_score: float  # 0.0 = stable, 1.0 = very flaky
    last_run: datetime | None
    last_status: str | None


@dataclass
class TestTrend:
    """Trend information for test metrics."""

    metric_name: str
    time_period: str  # 'day', 'week', 'month'
    values: list[float]
    timestamps: list[datetime]
    trend_direction: str  # 'improving', 'degrading', 'stable'
    change_percentage: float


class HistoryTracker:
    """Tracks test execution history and provides analytics."""

    def __init__(self, storage_path: Path | None = None, event_bus: EventBus | None = None):
        """Initialize the history tracker.

        Args:
            storage_path: Path to store history database (memory if None)
            event_bus: Optional event bus for history events
        """
        self.event_bus = event_bus
        self.storage_path = storage_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the history database."""
        if self.storage_path:
            self.conn = sqlite3.connect(str(self.storage_path))
        else:
            self.conn = sqlite3.connect(":memory:")

        cursor = self.conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_file TEXT NOT NULL,
                timestamp REAL NOT NULL,
                duration_ms REAL NOT NULL,
                status TEXT NOT NULL,
                failure_message TEXT,
                coverage_percentage REAL,
                branch_id TEXT,
                commit_hash TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_stats_cache (
                test_name TEXT PRIMARY KEY,
                stats_json TEXT NOT NULL,
                last_updated REAL NOT NULL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_name ON test_runs(test_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_timestamp ON test_runs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(status)")

        self.conn.commit()

    def record_test_run(self, test_run: TestRun) -> None:
        """Record a test execution result.

        Args:
            test_run: Test execution information
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO test_runs (
                test_name, test_file, timestamp, duration_ms, status,
                failure_message, coverage_percentage, branch_id, commit_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                test_run.test_name,
                test_run.test_file,
                test_run.timestamp.timestamp(),
                test_run.duration_ms,
                test_run.status,
                test_run.failure_message,
                test_run.coverage_percentage,
                test_run.branch_id,
                test_run.commit_hash,
            ),
        )
        self.conn.commit()

        # Invalidate stats cache for this test
        cursor.execute("DELETE FROM test_stats_cache WHERE test_name = ?", (test_run.test_name,))

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="test_run_recorded",
                    data={
                        "test_name": test_run.test_name,
                        "status": test_run.status,
                        "duration_ms": test_run.duration_ms,
                    },
                )
            )

    def record_test_runs_batch(self, test_runs: list[TestRun]) -> None:
        """Record multiple test runs efficiently.

        Args:
            test_runs: List of test execution results
        """
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT INTO test_runs (
                test_name, test_file, timestamp, duration_ms, status,
                failure_message, coverage_percentage, branch_id, commit_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                (
                    run.test_name,
                    run.test_file,
                    run.timestamp.timestamp(),
                    run.duration_ms,
                    run.status,
                    run.failure_message,
                    run.coverage_percentage,
                    run.branch_id,
                    run.commit_hash,
                )
                for run in test_runs
            ],
        )
        self.conn.commit()

        # Clear stats cache
        cursor.execute("DELETE FROM test_stats_cache")

        if self.event_bus:
            self.event_bus.emit(SystemEvent(type="test_runs_batch_recorded", data={"count": len(test_runs)}))

    def get_test_stats(self, test_name: str) -> TestStats | None:
        """Get statistical information for a test.

        Args:
            test_name: Name of the test

        Returns:
            TestStats or None if test not found
        """
        # Check cache first
        cursor = self.conn.cursor()
        cursor.execute("SELECT stats_json FROM test_stats_cache WHERE test_name = ?", (test_name,))
        row = cursor.fetchone()
        if row:
            return TestStats(**json.loads(row[0]))

        # Calculate stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as fail_count,
                SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skip_count,
                AVG(duration_ms) as avg_duration,
                MAX(timestamp) as last_timestamp,
                (SELECT status FROM test_runs
                 WHERE test_name = ?
                 ORDER BY timestamp DESC LIMIT 1) as last_status
            FROM test_runs
            WHERE test_name = ?
        """,
            (test_name, test_name),
        )

        row = cursor.fetchone()
        if not row or row[0] == 0:
            return None

        total_runs, pass_count, fail_count, skip_count, avg_duration, last_timestamp, last_status = row

        # Calculate failure rate and flakiness
        failure_rate = fail_count / total_runs if total_runs > 0 else 0.0
        flakiness_score = self._calculate_flakiness(test_name)

        stats = TestStats(
            test_name=test_name,
            total_runs=total_runs,
            pass_count=pass_count,
            fail_count=fail_count,
            skip_count=skip_count,
            average_duration_ms=avg_duration or 0.0,
            failure_rate=failure_rate,
            flakiness_score=flakiness_score,
            last_run=datetime.fromtimestamp(last_timestamp) if last_timestamp else None,
            last_status=last_status,
        )

        # Cache the stats
        cursor.execute(
            "INSERT OR REPLACE INTO test_stats_cache (test_name, stats_json, last_updated) VALUES (?, ?, ?)",
            (test_name, json.dumps(asdict(stats), default=str), datetime.now().timestamp()),
        )
        self.conn.commit()

        return stats

    def get_all_test_stats(self) -> list[TestStats]:
        """Get statistics for all tests.

        Returns:
            List of TestStats for all recorded tests
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT test_name FROM test_runs")
        test_names = [row[0] for row in cursor.fetchall()]

        stats = []
        for test_name in test_names:
            test_stat = self.get_test_stats(test_name)
            if test_stat:
                stats.append(test_stat)

        return stats

    def get_test_history(self, test_name: str, limit: int = 100) -> list[TestRun]:
        """Get execution history for a test.

        Args:
            test_name: Name of the test
            limit: Maximum number of records to return

        Returns:
            List of TestRun records, newest first
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT test_file, timestamp, duration_ms, status, failure_message,
                   coverage_percentage, branch_id, commit_hash
            FROM test_runs
            WHERE test_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (test_name, limit),
        )

        runs = []
        for row in cursor.fetchall():
            runs.append(
                TestRun(
                    test_name=test_name,
                    test_file=row[0],
                    timestamp=datetime.fromtimestamp(row[1]),
                    duration_ms=row[2],
                    status=row[3],
                    failure_message=row[4],
                    coverage_percentage=row[5],
                    branch_id=row[6],
                    commit_hash=row[7],
                )
            )

        return runs

    def get_failing_tests(self, since: datetime | None = None) -> list[TestStats]:
        """Get tests that are currently failing.

        Args:
            since: Only consider runs since this time

        Returns:
            List of TestStats for failing tests
        """
        cursor = self.conn.cursor()

        if since:
            cursor.execute(
                """
                SELECT DISTINCT test_name
                FROM test_runs
                WHERE status = 'failed' AND timestamp > ?
            """,
                (since.timestamp(),),
            )
        else:
            cursor.execute("""
                SELECT DISTINCT test_name
                FROM test_runs t1
                WHERE status = 'failed'
                AND timestamp = (
                    SELECT MAX(timestamp)
                    FROM test_runs t2
                    WHERE t2.test_name = t1.test_name
                )
            """)

        failing_tests = []
        for (test_name,) in cursor.fetchall():
            stats = self.get_test_stats(test_name)
            if stats and stats.last_status == "failed":
                failing_tests.append(stats)

        return failing_tests

    def get_flaky_tests(self, threshold: float = 0.3) -> list[TestStats]:
        """Get tests with high flakiness scores.

        Args:
            threshold: Minimum flakiness score (0.0-1.0)

        Returns:
            List of TestStats for flaky tests
        """
        all_stats = self.get_all_test_stats()
        return [stats for stats in all_stats if stats.flakiness_score >= threshold]

    def get_coverage_trend(self, time_period: str = "day", limit: int = 30) -> TestTrend:
        """Get coverage percentage trend over time.

        Args:
            time_period: 'day', 'week', or 'month'
            limit: Number of time periods to include

        Returns:
            TestTrend with coverage data
        """
        cursor = self.conn.cursor()

        # Determine time grouping
        if time_period == "day":
            group_by = "DATE(timestamp, 'unixepoch')"
        elif time_period == "week":
            group_by = "strftime('%Y-%W', timestamp, 'unixepoch')"
        else:  # month
            group_by = "strftime('%Y-%m', timestamp, 'unixepoch')"

        cursor.execute(
            f"""
            SELECT {group_by} as period, AVG(coverage_percentage) as avg_coverage
            FROM test_runs
            WHERE coverage_percentage IS NOT NULL
            GROUP BY period
            ORDER BY period DESC
            LIMIT ?
        """,
            (limit,),
        )

        values = []
        timestamps = []
        for period, avg_coverage in cursor.fetchall():
            timestamps.append(datetime.fromisoformat(period))
            values.append(avg_coverage or 0.0)

        # Reverse to get chronological order
        values.reverse()
        timestamps.reverse()

        # Calculate trend
        trend_direction = "stable"
        change_percentage = 0.0
        if len(values) >= 2:
            change = values[-1] - values[0]
            change_percentage = (change / values[0] * 100) if values[0] > 0 else 0.0
            if change_percentage > 5:
                trend_direction = "improving"
            elif change_percentage < -5:
                trend_direction = "degrading"

        return TestTrend(
            metric_name="coverage_percentage",
            time_period=time_period,
            values=values,
            timestamps=timestamps,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
        )

    def get_performance_trend(self, test_name: str, limit: int = 100) -> TestTrend:
        """Get performance trend for a specific test.

        Args:
            test_name: Name of the test
            limit: Number of runs to analyze

        Returns:
            TestTrend with duration data
        """
        history = self.get_test_history(test_name, limit)
        if not history:
            return TestTrend(
                metric_name="duration_ms",
                time_period="run",
                values=[],
                timestamps=[],
                trend_direction="stable",
                change_percentage=0.0,
            )

        values = [run.duration_ms for run in reversed(history)]
        timestamps = [run.timestamp for run in reversed(history)]

        # Calculate trend using linear regression
        if len(values) >= 5:
            # Simple trend detection
            first_quarter = sum(values[: len(values) // 4]) / (len(values) // 4)
            last_quarter = sum(values[-(len(values) // 4) :]) / (len(values) // 4)
            change_percentage = ((last_quarter - first_quarter) / first_quarter * 100) if first_quarter > 0 else 0.0

            if change_percentage > 10:
                trend_direction = "degrading"  # Getting slower
            elif change_percentage < -10:
                trend_direction = "improving"  # Getting faster
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
            change_percentage = 0.0

        return TestTrend(
            metric_name="duration_ms",
            time_period="run",
            values=values,
            timestamps=timestamps,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
        )

    def _calculate_flakiness(self, test_name: str) -> float:
        """Calculate flakiness score for a test.

        Flakiness is based on status changes between consecutive runs.

        Args:
            test_name: Name of the test

        Returns:
            Flakiness score (0.0 = stable, 1.0 = very flaky)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT status, LAG(status) OVER (ORDER BY timestamp) as prev_status
            FROM test_runs
            WHERE test_name = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """,
            (test_name,),
        )

        status_changes = 0
        total_transitions = 0

        for status, prev_status in cursor.fetchall():
            if prev_status is not None:
                total_transitions += 1
                if status != prev_status and status != "skipped" and prev_status != "skipped":
                    status_changes += 1

        if total_transitions == 0:
            return 0.0

        return status_changes / total_transitions

    def cleanup_old_history(self, days_to_keep: int = 90) -> int:
        """Remove old test history records.

        Args:
            days_to_keep: Number of days of history to keep

        Returns:
            Number of records deleted
        """
        cutoff = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM test_runs WHERE timestamp < ?", (cutoff,))
        deleted = cursor.rowcount
        self.conn.commit()

        # Clear stats cache
        cursor.execute("DELETE FROM test_stats_cache")

        if self.event_bus:
            self.event_bus.emit(SystemEvent(type="history_cleanup_completed", data={"deleted_records": deleted}))

        return deleted

    def export_history(self, output_path: Path, test_name: str | None = None) -> None:
        """Export test history to JSON file.

        Args:
            output_path: Path for the output file
            test_name: Optional specific test to export
        """
        cursor = self.conn.cursor()

        if test_name:
            cursor.execute("SELECT * FROM test_runs WHERE test_name = ? ORDER BY timestamp", (test_name,))
        else:
            cursor.execute("SELECT * FROM test_runs ORDER BY test_name, timestamp")

        rows = cursor.fetchall()
        records = []

        for row in rows:
            records.append(
                {
                    "test_name": row[1],
                    "test_file": row[2],
                    "timestamp": row[3],
                    "duration_ms": row[4],
                    "status": row[5],
                    "failure_message": row[6],
                    "coverage_percentage": row[7],
                    "branch_id": row[8],
                    "commit_hash": row[9],
                }
            )

        with open(output_path, "w") as f:
            json.dump(records, f, indent=2)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
