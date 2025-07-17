"""Usage examples for action logging utilities.

These examples demonstrate how to use the logging system
for audit trails, performance monitoring, and workflow tracking.
"""

import time
from datetime import datetime, timedelta

from .logging import (
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


def example_basic_logging():
    """Example: Basic action logging."""
    logger = ActionLogger()

    # Log a simple action
    logger.log(
        action_name="user_login",
        action_type=ActionType.SECURITY,
        description="User authenticated successfully",
        user="john.doe@example.com",
        context={"ip_address": "192.168.1.100", "method": "oauth2"},
    )

    # Log an error
    logger.log(
        action_name="database_connection",
        action_type=ActionType.ERROR,
        description="Failed to connect to database",
        outcome=ActionOutcome.FAILURE,
        severity=ActionSeverity.ERROR,
        error_message="Connection timeout after 30s",
        context={"host": "db.example.com", "port": 5432},
    )

    # Query recent actions
    recent_actions = logger.query_actions(limit=10)

    print("Recent Actions:")
    for action in recent_actions:
        print(f"  [{action.timestamp}] {action.action_name}: {action.outcome.value}")

    return logger


def example_timed_operations():
    """Example: Timing operations with context manager."""
    logger = ActionLogger()

    # Time a successful operation
    with logger.timed_action("data_processing", ActionType.PERFORMANCE) as action:
        # Simulate processing
        time.sleep(0.1)

        # Add context during execution
        action.context["records_processed"] = 1000
        action.context["algorithm"] = "quicksort"

    # Time an operation that fails
    try:
        with logger.timed_action("file_upload", ActionType.FILE_OPERATION) as action:
            action.context["file_size"] = 1024 * 1024 * 50  # 50MB

            # Simulate failure
            raise OSError("Disk full")
    except OSError:
        pass  # Error is logged automatically

    # Check performance statistics
    stats = logger.get_statistics()
    print("\nPerformance Statistics:")
    print(f"  Total actions: {stats['total_actions']}")
    print(f"  Failure rate: {stats['failure_rate']:.1%}")
    print(f"  Average duration: {stats['average_duration_ms']:.2f}ms")

    return logger


def example_workflow_tracking():
    """Example: Tracking multi-step workflows."""
    logger = create_workflow_logger()

    workflow_name = "data_pipeline"
    steps = ["validate_input", "transform_data", "apply_business_rules", "generate_output", "send_notifications"]

    print(f"\nExecuting workflow: {workflow_name}")

    for i, step in enumerate(steps, 1):
        # Simulate step execution
        time.sleep(0.05)

        # Determine outcome (simulate occasional failures)
        outcome = ActionOutcome.SUCCESS
        if step == "apply_business_rules" and i % 2 == 0:
            outcome = ActionOutcome.PARTIAL

        # Log the step
        log_workflow_step(
            logger,
            workflow_name=workflow_name,
            step_name=step,
            step_number=i,
            total_steps=len(steps),
            outcome=outcome,
            context={"duration_ms": 50 + (i * 10), "records_affected": i * 100},
        )

        print(f"  Step {i}/{len(steps)}: {step} - {outcome.value}")

    # Query workflow actions
    workflow_actions = logger.query_actions(action_type=ActionType.WORKFLOW, tags={workflow_name})

    print(f"\nWorkflow summary: {len(workflow_actions)} steps completed")

    return logger


def example_decision_logging():
    """Example: Logging decisions with reasoning."""
    logger = ActionLogger()

    # Log algorithm selection decision
    log_decision(
        logger,
        decision_name="select_sorting_algorithm",
        reasoning="Dataset size is 10,000 items with mostly sorted data",
        confidence=0.9,
        alternatives=["quicksort", "mergesort", "heapsort", "timsort"],
        outcome=ActionOutcome.SUCCESS,
    )

    # Log resource allocation decision
    log_decision(
        logger,
        decision_name="allocate_compute_resources",
        reasoning="High priority job requires fast completion",
        confidence=0.75,
        alternatives=["2_cores", "4_cores", "8_cores"],
        outcome=ActionOutcome.SUCCESS,
    )

    # Log failed decision
    log_decision(
        logger,
        decision_name="choose_cache_strategy",
        reasoning="Unable to determine access patterns",
        confidence=0.3,
        outcome=ActionOutcome.FAILURE,
        alternatives=["lru", "lfu", "fifo"],
    )

    # Query decisions
    decisions = logger.query_actions(action_type=ActionType.DECISION)

    print("\nDecision Log:")
    for decision in decisions:
        confidence = decision.context.get("confidence", 0)
        print(f"  {decision.action_name}: confidence={confidence:.0%} - {decision.outcome.value}")

    return logger


def example_performance_monitoring():
    """Example: Monitoring performance metrics."""
    logger = ActionLogger()

    operations = [
        ("api_call", 250),
        ("database_query", 1500),
        ("cache_lookup", 5),
        ("file_write", 3000),
        ("network_request", 8000),
        ("cpu_intensive_task", 12000),
    ]

    print("\nLogging performance metrics:")

    for op_name, duration in operations:
        log_performance(
            logger,
            operation_name=op_name,
            duration_ms=duration,
            metrics={"cpu_percent": min(duration / 100, 100), "memory_mb": duration / 10},
        )

        # Determine status based on duration
        if duration < 1000:
            status = "✓ Fast"
        elif duration < 5000:
            status = "⚡ Normal"
        elif duration < 10000:
            status = "⚠️  Slow"
        else:
            status = "❌ Timeout"

        print(f"  {op_name}: {duration}ms {status}")

    # Get performance statistics
    stats = logger.get_statistics()
    perf_stats = stats["by_type"].get("performance", {})

    print("\nPerformance Summary:")
    for outcome, data in perf_stats.items():
        print(f"  {outcome}: {data['count']} operations, avg {data['avg_duration_ms']:.0f}ms")

    return logger


def example_audit_trail():
    """Example: Creating an audit trail for compliance."""
    logger = create_audit_logger()  # Immediate writes, no caching

    # Log security-sensitive actions
    actions = [
        ("access_granted", "User accessed financial records", ActionOutcome.SUCCESS),
        ("permission_change", "Admin privileges granted to user", ActionOutcome.SUCCESS),
        ("data_export", "Exported customer data to CSV", ActionOutcome.SUCCESS),
        ("access_denied", "Unauthorized access attempt", ActionOutcome.FAILURE),
        ("config_change", "Modified security settings", ActionOutcome.SUCCESS),
    ]

    print("\nCreating audit trail:")

    for action_name, description, outcome in actions:
        logger.log(
            action_name=action_name,
            action_type=ActionType.SECURITY,
            description=description,
            outcome=outcome,
            severity=ActionSeverity.WARNING if outcome == ActionOutcome.FAILURE else ActionSeverity.INFO,
            user="admin@example.com",
            context={"session_id": "abc123", "ip_address": "10.0.0.1", "timestamp": datetime.now().isoformat()},
            tags={"audit", "compliance", "security"},
        )

        symbol = "✓" if outcome == ActionOutcome.SUCCESS else "✗"
        print(f"  {symbol} {action_name}: {description}")

    # Query audit trail for failures
    failures = logger.query_actions(action_type=ActionType.SECURITY, outcome=ActionOutcome.FAILURE)

    print(f"\nSecurity failures: {len(failures)}")
    for failure in failures:
        print(f"  - {failure.action_name}: {failure.description}")

    return logger


def example_anomaly_detection():
    """Example: Detecting anomalous patterns."""
    logger = ActionLogger()

    # Simulate normal activity
    for i in range(20):
        logger.log(f"normal_operation_{i}", ActionType.INFO, outcome=ActionOutcome.SUCCESS)

    # Simulate anomaly: high failure rate
    for i in range(15):
        outcome = ActionOutcome.FAILURE if i < 12 else ActionOutcome.SUCCESS
        logger.log(
            "problematic_operation",
            ActionType.ERROR,
            outcome=outcome,
            error_message="Connection refused" if outcome == ActionOutcome.FAILURE else None,
        )

    # Simulate anomaly: frequency spike
    for _i in range(50):
        logger.log("suspicious_activity", ActionType.WARNING, description="Unusual pattern detected")

    # Detect anomalies
    anomalies = logger.detect_anomalies(window_minutes=60, failure_threshold=0.5)

    print("\nAnomaly Detection Results:")
    for anomaly in anomalies:
        if anomaly["type"] == "high_failure_rate":
            print(f"  ⚠️  High failure rate: {anomaly['action_type']} - {anomaly['failure_rate']:.1%}")
            print(f"     Recent errors: {anomaly['recent_errors'][:3]}")
        elif anomaly["type"] == "frequency_spike":
            print(f"  📈 Frequency spike: {anomaly['action_name']} - {anomaly['count']} occurrences")
            print(f"     Average: {anomaly['average']:.1f}")

    return logger


def example_complex_query():
    """Example: Complex querying and analysis."""
    logger = ActionLogger()

    # Generate varied test data
    base_time = datetime.now() - timedelta(hours=2)

    for hour in range(3):
        current_time = base_time + timedelta(hours=hour)

        for i in range(10):
            logger.log_action(
                ActionRecord(
                    timestamp=current_time + timedelta(minutes=i * 5),
                    action_name=f"task_{hour}_{i}",
                    action_type=ActionType.WORKFLOW if i % 2 == 0 else ActionType.COMMAND,
                    outcome=ActionOutcome.SUCCESS if i < 8 else ActionOutcome.FAILURE,
                    duration_ms=100 + (i * 50),
                    user=f"user{i % 3}",
                    tags={f"hour_{hour}", "automated"} if i % 3 == 0 else set(),
                )
            )

    # Complex queries
    print("\nComplex Query Examples:")

    # 1. Recent failures by specific user
    recent_failures = logger.query_actions(
        outcome=ActionOutcome.FAILURE, user="user1", start_time=datetime.now() - timedelta(hours=1)
    )
    print(f"  Recent failures by user1: {len(recent_failures)}")

    # 2. Workflow actions in last hour with tags
    workflow_tagged = logger.query_actions(
        action_type=ActionType.WORKFLOW, tags={"automated"}, start_time=datetime.now() - timedelta(hours=1)
    )
    print(f"  Tagged workflow actions (last hour): {len(workflow_tagged)}")

    # 3. Time-based statistics
    stats_recent = logger.get_statistics(start_time=datetime.now() - timedelta(minutes=30))
    stats_all = logger.get_statistics()

    print(f"  Actions last 30 min: {stats_recent['total_actions']}")
    print(f"  Actions all time: {stats_all['total_actions']}")
    print(f"  Recent failure rate: {stats_recent['failure_rate']:.1%}")

    return logger


if __name__ == "__main__":
    print("=== Action Logging Examples ===\n")

    print("1. Basic Logging:")
    example_basic_logging()

    print("\n2. Timed Operations:")
    example_timed_operations()

    print("\n3. Workflow Tracking:")
    example_workflow_tracking()

    print("\n4. Decision Logging:")
    example_decision_logging()

    print("\n5. Performance Monitoring:")
    example_performance_monitoring()

    print("\n6. Audit Trail:")
    example_audit_trail()

    print("\n7. Anomaly Detection:")
    example_anomaly_detection()

    print("\n8. Complex Queries:")
    example_complex_query()
