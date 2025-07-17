"""A1 Utilities Package.

Extracted utilities from A1 with significant complexity reduction.
These utilities provide reusable algorithms and patterns for the core system.
"""

# Statistical and consensus algorithms
# Configuration management
from .config import (
    AppConfig,
    BaseConfig,
    ConfigError,
    ConfigFormat,
    ConfigManager,
    DatabaseConfig,
    FeatureFlags,
    UserPreferences,
    create_config_schema,
    load_config,
    parse_bool,
    parse_list,
)
from .consensus import (
    aggregate_rankings,
    bayesian_aggregation,
    calculate_agreement_matrix,
    calculate_consensus_score,
    median_aggregation,
    weighted_average,
    wisdom_of_crowds,
)

# Action logging and audit trail
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

# Performance monitoring and benchmarking
from .monitoring import (
    AlertSeverity,
    Benchmark,
    BenchmarkResult,
    MetricCollector,
    MetricType,
    PerformanceAlert,
    PerformanceMonitor,
    ResourceMonitor,
    ResourceUsage,
    benchmark_function,
    create_monitor,
    format_benchmark_result,
)

# Advanced pattern recognition
from .patterns_advanced import (
    CognitivePattern,
    ThoughtPatternType,
    analyze_pattern_frequency,
    classify_step_type,
    consolidate_patterns,
    detect_thought_patterns,
    estimate_text_complexity,
    extract_recurring_elements,
    identify_efficiency_patterns,
)

# Task management and workflow coordination
from .tasks import (
    Task,
    TaskManager,
    TaskPriority,
    TaskQueue,
    TaskResult,
    TaskStatus,
    Worker,
    WorkerStatus,
    Workflow,
    WorkflowStep,
    create_simple_task_manager,
    run_tasks,
    task_context,
)

__all__ = [
    # Consensus utilities
    "weighted_average",
    "median_aggregation",
    "wisdom_of_crowds",
    "bayesian_aggregation",
    "calculate_consensus_score",
    "calculate_agreement_matrix",
    "aggregate_rankings",
    # Pattern recognition utilities
    "ThoughtPatternType",
    "CognitivePattern",
    "detect_thought_patterns",
    "estimate_text_complexity",
    "classify_step_type",
    "analyze_pattern_frequency",
    "identify_efficiency_patterns",
    "consolidate_patterns",
    "extract_recurring_elements",
    # Logging utilities
    "ActionLogger",
    "ActionRecord",
    "ActionType",
    "ActionOutcome",
    "ActionSeverity",
    "create_workflow_logger",
    "create_audit_logger",
    "log_decision",
    "log_performance",
    "log_workflow_step",
    # Monitoring utilities
    "MetricCollector",
    "MetricType",
    "ResourceMonitor",
    "ResourceUsage",
    "PerformanceMonitor",
    "PerformanceAlert",
    "AlertSeverity",
    "Benchmark",
    "BenchmarkResult",
    "create_monitor",
    "benchmark_function",
    "format_benchmark_result",
    # Configuration utilities
    "BaseConfig",
    "ConfigError",
    "ConfigFormat",
    "ConfigManager",
    "FeatureFlags",
    "UserPreferences",
    "AppConfig",
    "DatabaseConfig",
    "load_config",
    "create_config_schema",
    "parse_bool",
    "parse_list",
    # Task management utilities
    "Task",
    "Worker",
    "TaskQueue",
    "TaskManager",
    "Workflow",
    "WorkflowStep",
    "TaskStatus",
    "TaskPriority",
    "WorkerStatus",
    "TaskResult",
    "create_simple_task_manager",
    "run_tasks",
    "task_context",
]
