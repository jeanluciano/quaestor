"""Quaestor A1 - Premium Context Management Addon

This is the main entry point for Quaestor A1, providing premium context management capabilities.

A1 provides a dramatically simplified architecture for intelligent context management:
- 25,000 lines (vs 119,416 in V2.0) - 79% reduction
- 5 core components (vs 20+ complex modules)
- File-based storage (vs complex databases)
- Event-driven architecture (vs complex orchestration)
- Optional extensions (vs monolithic features)

Core Components:
- Event Bus: Simple publish/subscribe system
- Context Management: Basic context switching and relevance scoring
- Quality Guardian: Essential quality checks and rules
- Learning Framework: Pattern recognition and adaptation
- Analysis Engine: Code analysis and metrics

Utilities:
- Configuration management
- Logging and monitoring
- Task management
- Consensus algorithms
- Pattern recognition

Extensions (Optional):
- Prediction engine
- Hook system
- State management
- Workflow detection
- Persistence system
"""

# Core Components
# Analysis Engine
from .analysis import (
    AnalysisEngine,
    CodeAnalyzer,
    CodeMetrics,
    QualityChecker,
)
from .core import (
    ContextConfiguration,
    ContextManager,
    ContextSession,
    ContextState,
    ContextSwitcher,
    # Context management
    ContextType,
    Event,
    # Event system
    EventBus,
    EventStore,
    FileChangeEvent,
    LearningEvent,
    QualityGuardian,
    QualityIssue,
    # Quality system
    QualityLevel,
    QualityMetrics,
    QualityReport,
    QualityRule,
    QualityRuleEngine,
    RelevanceScorer,
    RuleSeverity,
    SystemEvent,
    ToolUseEvent,
    UserActionEvent,
)

# Optional Extensions (can be imported separately)
from .extensions import (
    # Prediction system
    BasicPredictionEngine,
    BasicSnapshot,
    FilePredictor,
    FileStorageBackend,
    HookDefinition,
    HookResult,
    MemoryStorageBackend,
    PredictionPattern,
    PredictionResult,
    SequencePredictor,
    # Hook system
    SimpleHookManager,
    SimplePatternRecognizer,
    # Persistence system
    SimplePersistenceManager,
    # State management
    SimpleStateManager,
    # Workflow detection
    SimpleWorkflowDetector,
    WorkflowInstance,
    WorkflowType,
    create_default_config,
    create_snapshot,
    detect_workflow_anomalies,
    execute_hooks,
    execute_post_tool_hooks,
    execute_pre_tool_hooks,
    get_current_workflows,
    get_hook_manager,
    get_persistence_manager,
    get_prediction_engine,
    get_state_manager,
    get_workflow_detector,
    load_config,
    load_manifest,
    predict_next_file,
    predict_next_tool,
    record_file_change,
    record_tool_use,
    redo_last_action,
    register_hook,
    reload_hooks,
    restore_snapshot,
    save_config,
    save_manifest,
    undo_last_action,
)

# Learning Framework
from .learning import (
    AdaptationEngine,
    FileLearningStore,
    LearningManager,
    PatternRecognizer,
)

# Predictive Engine (Phase 5)
from .predictive import (
    CommandPattern,
    FilePattern,
    Pattern,
    PatternType,
    PredictiveEngine,
    SequenceMiner,
    WorkflowPattern,
)

# Utilities
from .utilities import (
    # Logging and monitoring
    ActionLogger,
    ActionOutcome,
    ActionRecord,
    ActionSeverity,
    ActionType,
    AlertSeverity,
    AppConfig,
    # Configuration management
    BaseConfig,
    Benchmark,
    BenchmarkResult,
    CognitivePattern,
    ConfigError,
    ConfigFormat,
    ConfigManager,
    DatabaseConfig,
    FeatureFlags,
    # Performance monitoring
    MetricCollector,
    MetricType,
    PerformanceAlert,
    PerformanceMonitor,
    ResourceMonitor,
    ResourceUsage,
    # Task management
    Task,
    TaskManager,
    TaskPriority,
    TaskQueue,
    TaskResult,
    TaskStatus,
    # Pattern recognition
    ThoughtPatternType,
    UserPreferences,
    Worker,
    WorkerStatus,
    Workflow,
    WorkflowStep,
    aggregate_rankings,
    analyze_pattern_frequency,
    bayesian_aggregation,
    benchmark_function,
    calculate_agreement_matrix,
    calculate_consensus_score,
    classify_step_type,
    consolidate_patterns,
    create_audit_logger,
    create_config_schema,
    create_monitor,
    create_simple_task_manager,
    create_workflow_logger,
    detect_thought_patterns,
    estimate_text_complexity,
    extract_recurring_elements,
    format_benchmark_result,
    identify_efficiency_patterns,
    log_decision,
    log_performance,
    log_workflow_step,
    median_aggregation,
    parse_bool,
    parse_list,
    run_tasks,
    task_context,
    # Consensus algorithms
    weighted_average,
    wisdom_of_crowds,
)

# Version information
__version__ = "A1.0"
__author__ = "Quaestor Team"
__description__ = "Simplified AI context management system"

# Main exports - grouped by category for easy discovery
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core Event System
    "EventBus",
    "EventStore",
    "Event",
    "FileChangeEvent",
    "LearningEvent",
    "SystemEvent",
    "ToolUseEvent",
    "UserActionEvent",
    # Core Context Management
    "ContextType",
    "ContextState",
    "ContextConfiguration",
    "ContextSession",
    "RelevanceScorer",
    "ContextSwitcher",
    "ContextManager",
    # Core Quality System
    "QualityLevel",
    "RuleSeverity",
    "QualityRule",
    "QualityIssue",
    "QualityReport",
    "QualityMetrics",
    "QualityRuleEngine",
    "QualityGuardian",
    # Learning Framework
    "LearningManager",
    "PatternRecognizer",
    "AdaptationEngine",
    "FileLearningStore",
    # Predictive Engine (Phase 5)
    "PredictiveEngine",
    "SequenceMiner",
    "Pattern",
    "PatternType",
    "CommandPattern",
    "WorkflowPattern",
    "FilePattern",
    # Analysis Engine
    "AnalysisEngine",
    "CodeAnalyzer",
    "QualityChecker",
    "CodeMetrics",
    # Configuration Utilities
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
    # Logging Utilities
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
    # Monitoring Utilities
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
    # Task Management Utilities
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
    # Consensus Utilities
    "weighted_average",
    "median_aggregation",
    "wisdom_of_crowds",
    "bayesian_aggregation",
    "calculate_consensus_score",
    "calculate_agreement_matrix",
    "aggregate_rankings",
    # Pattern Recognition Utilities
    "ThoughtPatternType",
    "CognitivePattern",
    "detect_thought_patterns",
    "estimate_text_complexity",
    "classify_step_type",
    "analyze_pattern_frequency",
    "identify_efficiency_patterns",
    "consolidate_patterns",
    "extract_recurring_elements",
    # Extensions - Prediction System
    "BasicPredictionEngine",
    "SimplePatternRecognizer",
    "SequencePredictor",
    "FilePredictor",
    "PredictionPattern",
    "PredictionResult",
    "get_prediction_engine",
    "predict_next_tool",
    "predict_next_file",
    "record_tool_use",
    "record_file_change",
    # Extensions - Hook System
    "SimpleHookManager",
    "HookDefinition",
    "HookResult",
    "get_hook_manager",
    "execute_hooks",
    "execute_pre_tool_hooks",
    "execute_post_tool_hooks",
    "register_hook",
    "reload_hooks",
    "create_default_config",
    # Extensions - State Management
    "SimpleStateManager",
    "BasicSnapshot",
    "get_state_manager",
    "create_snapshot",
    "restore_snapshot",
    "undo_last_action",
    "redo_last_action",
    # Extensions - Workflow Detection
    "SimpleWorkflowDetector",
    "WorkflowType",
    "WorkflowInstance",
    "get_workflow_detector",
    "get_current_workflows",
    "detect_workflow_anomalies",
    # Extensions - Persistence System
    "SimplePersistenceManager",
    "MemoryStorageBackend",
    "FileStorageBackend",
    "get_persistence_manager",
    "load_config",
    "save_config",
    "load_manifest",
    "save_manifest",
]


# Convenience functions for common use cases
def create_basic_system(config_path: str = None, enable_extensions: bool = True):
    """Create a basic A1 system with default components.

    Args:
        config_path: Optional path to configuration file
        enable_extensions: Whether to enable optional extensions

    Returns:
        Dictionary containing initialized core components
    """
    # Initialize core event bus
    event_bus = EventBus()

    # Initialize core components with event bus
    context_manager = ContextManager()
    quality_guardian = QualityGuardian()
    learning_manager = LearningManager()
    analysis_engine = AnalysisEngine()

    system = {
        "event_bus": event_bus,
        "context_manager": context_manager,
        "quality_guardian": quality_guardian,
        "learning_manager": learning_manager,
        "analysis_engine": analysis_engine,
    }

    # Optionally add extensions
    if enable_extensions:
        try:
            system["prediction_engine"] = get_prediction_engine()
            system["hook_manager"] = get_hook_manager()
            system["state_manager"] = get_state_manager()
            system["workflow_detector"] = get_workflow_detector()
            system["persistence_manager"] = get_persistence_manager()
        except Exception as e:
            # Extensions are optional - log but don't fail
            print(f"Warning: Could not initialize some extensions: {e}")

    return system


def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "core": 5,  # event_bus, context, quality, learning, analysis
            "utilities": 10,  # config, logging, monitoring, tasks, consensus, patterns
            "extensions": 5,  # prediction, hooks, state, workflow, persistence
        },
        "lines_of_code": "~25,000",
        "reduction_from_v2": "79%",
    }
