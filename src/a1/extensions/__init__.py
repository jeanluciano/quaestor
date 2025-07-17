"""A1 Extensions - Optional extensions for enhanced functionality.

These extensions provide additional capabilities while maintaining the core A1
simplicity. Each extension is self-contained and can be used independently.
"""

from .hooks import (
    HookDefinition,
    HookResult,
    SimpleHookManager,
    create_default_config,
    execute_hooks,
    execute_post_tool_hooks,
    execute_pre_tool_hooks,
    get_hook_manager,
    register_hook,
    reload_hooks,
)
from .persistence import (
    FileStorageBackend,
    MemoryStorageBackend,
    SimplePersistenceManager,
    get_persistence_manager,
    load_config,
    load_manifest,
    save_config,
    save_manifest,
)
from .prediction import (
    BasicPredictionEngine,
    FilePredictor,
    PredictionPattern,
    PredictionResult,
    SequencePredictor,
    SimplePatternRecognizer,
    get_prediction_engine,
    predict_next_file,
    predict_next_tool,
    record_file_change,
    record_tool_use,
)
from .state import (
    BasicSnapshot,
    SimpleStateManager,
    create_snapshot,
    get_state_manager,
    redo_last_action,
    restore_snapshot,
    undo_last_action,
)
from .workflow import (
    SimpleWorkflowDetector,
    WorkflowInstance,
    WorkflowType,
    detect_workflow_anomalies,
    get_current_workflows,
    get_workflow_detector,
)

__all__ = [
    # Prediction system
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
    # Hook system
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
    # State management
    "SimpleStateManager",
    "BasicSnapshot",
    "get_state_manager",
    "create_snapshot",
    "restore_snapshot",
    "undo_last_action",
    "redo_last_action",
    # Workflow detection
    "SimpleWorkflowDetector",
    "WorkflowType",
    "WorkflowInstance",
    "get_workflow_detector",
    "get_current_workflows",
    "detect_workflow_anomalies",
    # Persistence system
    "SimplePersistenceManager",
    "MemoryStorageBackend",
    "FileStorageBackend",
    "get_persistence_manager",
    "load_config",
    "save_config",
    "load_manifest",
    "save_manifest",
]
