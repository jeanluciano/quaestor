# Quaestor A1 API Reference

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Events API](#events-api)
4. [Extensions API](#extensions-api)
5. [Utilities API](#utilities-api)
6. [System Functions](#system-functions)
7. [Type Definitions](#type-definitions)
8. [Examples](#examples)

## Overview

The A1 API provides a clean, modular interface for integrating with Quaestor's AI context management system. All components are accessible through the main module:

```python
from quaestor.a1 import (
    EventBus,
    ContextManager,
    QualityGuardian,
    LearningManager,
    AnalysisEngine,
    create_basic_system,
)
```

## Core Components

### EventBus

Central event coordination system.

```python
class EventBus:
    """Simplified event bus for A1."""
    
    def __init__(self, max_queue_size: int = 10000):
        """Initialize event bus with optional queue size limit."""
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
    
    def subscribe(
        self, 
        event_type: type[Event], 
        handler: EventHandler,
        priority: int = 0
    ) -> str:
        """Subscribe to events of a specific type."""
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
    
    async def wait_for(
        self, 
        event_type: type[Event], 
        timeout: float = None
    ) -> Event | None:
        """Wait for a specific event type."""
```

**Example:**
```python
# Create event bus
event_bus = EventBus()

# Subscribe to tool events
async def handle_tool_use(event: ToolUseEvent):
    print(f"Tool used: {event.tool_name}")

subscription_id = event_bus.subscribe(ToolUseEvent, handle_tool_use)

# Publish event
event = ToolUseEvent(tool_name="pytest", success=True)
await event_bus.publish(event)
```

### ContextManager

Manages development context and file relevance.

```python
class ContextManager:
    """Main context management orchestrator."""
    
    def __init__(self, config: ContextConfiguration = None):
        """Initialize with optional configuration."""
    
    def create_session(
        self, 
        initial_context_type: ContextType = ContextType.DEVELOPMENT
    ) -> ContextSession:
        """Create a new context session."""
    
    def switch_context_type(
        self,
        session_id: str,
        new_type: ContextType,
        reason: str = ""
    ) -> ContextState | None:
        """Switch context type for a session."""
    
    def add_file(self, session_id: str, file_path: str) -> bool:
        """Add a file to the current context."""
    
    def remove_file(self, session_id: str, file_path: str) -> bool:
        """Remove a file from the context."""
    
    def optimize_context(self, session_id: str) -> bool:
        """Optimize the current context."""
    
    def get_context_info(self, session_id: str) -> dict | None:
        """Get context information for a session."""
```

**Example:**
```python
# Create context manager
context_mgr = ContextManager()

# Create session
session = context_mgr.create_session(ContextType.DEVELOPMENT)

# Switch context
context_mgr.switch_context_type(
    session.id, 
    ContextType.DEBUGGING,
    "Investigating bug"
)

# Add files
context_mgr.add_file(session.id, "src/main.py")
context_mgr.add_file(session.id, "src/utils.py")

# Get context info
info = context_mgr.get_context_info(session.id)
print(f"Files in context: {info['file_count']}")
```

### QualityGuardian

Monitors and enforces code quality standards.

```python
class QualityGuardian:
    """Simplified quality monitoring for a1."""
    
    def __init__(self):
        """Initialize quality guardian with default rules."""
    
    def analyze_quality(
        self, 
        file_metrics: list[QualityMetrics]
    ) -> QualityReport:
        """Analyze quality for given file metrics."""
    
    def get_issues_for_file(self, file_path: str) -> list[QualityIssue]:
        """Get issues for a specific file."""
    
    def resolve_issue(self, issue_id: str) -> bool:
        """Mark an issue as resolved."""
    
    def check_quality_gate(
        self, 
        min_score: float = 70.0
    ) -> tuple[bool, list[str]]:
        """Check if quality gate passes."""
    
    def get_statistics(self) -> dict:
        """Get quality guardian statistics."""
```

**Example:**
```python
# Create quality guardian
quality = QualityGuardian()

# Create metrics for analysis
metrics = [
    QualityMetrics(
        file_path="src/main.py",
        overall_score=85.0,
        maintainability=80.0,
        readability=90.0,
        complexity=75.0,
        testability=85.0,
        documentation=95.0
    )
]

# Analyze quality
report = quality.analyze_quality(metrics)
print(f"Quality level: {report.quality_level.value}")
print(f"Issues found: {len(report.issues)}")

# Check quality gate
passed, violations = quality.check_quality_gate(min_score=80.0)
if not passed:
    print(f"Quality gate failed: {violations}")
```

### LearningManager

Learns from development patterns and provides insights.

```python
class LearningManager:
    """Simplified learning system for Quaestor a1."""
    
    def __init__(self, config: LearningConfiguration = None):
        """Initialize with optional configuration."""
    
    async def learn_from_event(self, event: Event) -> None:
        """Process an event for learning."""
    
    def get_suggestions(
        self, 
        context: dict[str, Any]
    ) -> list[Suggestion]:
        """Get suggestions based on context."""
    
    def get_insights(self) -> list[Insight]:
        """Get learning insights."""
    
    def get_patterns(self) -> list[Pattern]:
        """Get detected patterns."""
    
    def get_stats(self) -> dict[str, Any]:
        """Get learning statistics."""
```

**Example:**
```python
# Create learning manager
learning = LearningManager()

# Learn from events
event = ToolUseEvent(tool_name="pytest", success=True)
await learning.learn_from_event(event)

# Get suggestions
suggestions = learning.get_suggestions({
    "current_tool": "pytest",
    "context_type": "testing"
})

# Get insights
insights = learning.get_insights()
for insight in insights:
    print(f"{insight.type}: {insight.description}")
```

### AnalysisEngine

Analyzes code structure and metrics.

```python
class AnalysisEngine:
    """Simplified code analysis engine for a1."""
    
    def __init__(self, config: AnalysisConfiguration = None):
        """Initialize with optional configuration."""
    
    def analyze(
        self, 
        paths: list[str],
        recursive: bool = True
    ) -> AnalysisResult:
        """Analyze code at given paths."""
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single file."""
    
    def get_project_structure(
        self, 
        root_path: str
    ) -> ProjectStructure:
        """Get project structure analysis."""
    
    def calculate_metrics(
        self, 
        file_path: str
    ) -> CodeMetrics:
        """Calculate metrics for a file."""
```

**Example:**
```python
# Create analysis engine
analysis = AnalysisEngine()

# Analyze project
result = analysis.analyze(["src/"])
print(f"Files analyzed: {result.code_metrics.file_count}")
print(f"Total lines: {result.code_metrics.total_lines}")
print(f"Functions: {result.code_metrics.function_count}")

# Analyze single file
file_analysis = analysis.analyze_file("src/main.py")
print(f"Complexity: {file_analysis.complexity}")
print(f"Issues: {len(file_analysis.issues)}")
```

## Events API

### Event Types

```python
@dataclass
class Event(ABC):
    """Base event class."""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = "quaestor.a1"

@dataclass
class ToolUseEvent(Event):
    """Event fired when a tool is used."""
    tool_name: str = ""
    success: bool = True
    duration_ms: float | None = None

@dataclass
class FileChangeEvent(Event):
    """Event fired when a file is modified."""
    file_path: str = ""
    change_type: str = "modified"  # "created", "modified", "deleted"

@dataclass
class UserActionEvent(Event):
    """Event fired when user performs an action."""
    action_type: str = "command"
    action_details: dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemEvent(Event):
    """Event fired for system-level events."""
    event_name: str = ""
    severity: str = "info"  # "info", "warning", "error"
    component: str = ""

@dataclass
class LearningEvent(Event):
    """Event fired when the system learns something new."""
    learning_type: str = "pattern_detected"
    confidence: float = 0.0  # 0.0 to 1.0
```

### Event Publishing

```python
# Publish tool use event
event = ToolUseEvent(
    tool_name="black",
    success=True,
    duration_ms=125.5
)
await event_bus.publish(event)

# Publish file change event
event = FileChangeEvent(
    file_path="src/main.py",
    change_type="modified"
)
await event_bus.publish(event)

# Publish system event
event = SystemEvent(
    event_name="quality_check_failed",
    severity="warning",
    component="quality_guardian"
)
await event_bus.publish(event)
```

## Extensions API

### Prediction Engine

```python
class BasicPredictionEngine:
    """Simple prediction engine for A1."""
    
    def predict_next_tool(
        self,
        limit: int = 5
    ) -> list[tuple[str, float]]:
        """Predict next tool usage."""
    
    def predict_next_file(
        self,
        current_file: str,
        limit: int = 5
    ) -> list[tuple[str, float]]:
        """Predict next file to work on."""
    
    def get_summary(self) -> dict[str, Any]:
        """Get prediction engine summary."""

# Usage
prediction = get_prediction_engine()
tools = prediction.predict_next_tool(limit=3)
# Returns: [("pytest", 0.8), ("black", 0.6), ("mypy", 0.4)]
```

### State Management

```python
class SimpleStateManager:
    """Simple state management for file tracking."""
    
    def track_files(self, file_patterns: list[str]) -> None:
        """Add file patterns to track."""
    
    def create_snapshot(
        self,
        description: str,
        metadata: dict[str, Any] = None
    ) -> str:
        """Create a new state snapshot."""
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore files from a snapshot."""
    
    def list_snapshots(self) -> list[BasicSnapshot]:
        """List all available snapshots."""
    
    def undo(self) -> str | None:
        """Undo to previous snapshot."""
    
    def redo(self) -> str | None:
        """Redo to next snapshot."""

# Usage
state_mgr = get_state_manager()
state_mgr.track_files(["*.py", "*.yaml"])
snapshot_id = state_mgr.create_snapshot("Before refactoring")
```

### Workflow Detection

```python
class SimpleWorkflowDetector:
    """Detects development workflows from events."""
    
    def get_current_workflows(self) -> list[WorkflowInstance]:
        """Get currently active workflows."""
    
    def get_workflow_suggestions(self) -> list[str]:
        """Get workflow optimization suggestions."""
    
    def get_workflow_stats(self) -> dict[str, Any]:
        """Get workflow statistics."""

# Usage
workflow = get_workflow_detector()
current = workflow.get_current_workflows()
for wf in current:
    print(f"Active: {wf.workflow_type.value}")
```

### Hook Manager

```python
class SimpleHookManager:
    """Simplified hook manager for A1."""
    
    def execute_hooks(
        self,
        event_type: str,
        context: dict[str, Any]
    ) -> list[HookResult]:
        """Execute hooks for an event type."""
    
    def reload_hooks(self) -> None:
        """Reload hook configuration."""

# Usage
hooks = get_hook_manager()
results = hooks.execute_hooks("tool_use", {"tool": "pytest"})
```

### Persistence Manager

```python
class SimplePersistenceManager:
    """Manages data persistence for A1."""
    
    def save_manifest(self, manifest: ProjectManifest) -> None:
        """Save project manifest."""
    
    def load_manifest(self) -> ProjectManifest | None:
        """Load project manifest."""
    
    def backup_data(self) -> str:
        """Create backup of all data."""

# Usage
persistence = get_persistence_manager()
manifest = ProjectManifest(project_path="/path/to/project")
persistence.save_manifest(manifest)
```

## Utilities API

### Configuration Management

```python
class ConfigManager:
    """Centralized configuration manager."""
    
    def load(self) -> None:
        """Load configuration from file."""
    
    def save(self) -> None:
        """Save configuration to file."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
    
    def validate(self) -> list[str]:
        """Validate configuration."""

# Usage
config = ConfigManager()
config.set("extensions.prediction", True)
config.save()
```

### Performance Monitoring

```python
class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
    
    def create_alert(
        self,
        metric: str,
        threshold: float,
        callback: callable
    ) -> str:
        """Create performance alert."""

# Usage
monitor = PerformanceMonitor()
monitor.start_monitoring()
metrics = monitor.get_metrics()
print(f"CPU: {metrics.cpu_percent}%")
print(f"Memory: {metrics.memory_mb}MB")
```

### Logging Utilities

```python
class ActionLogger:
    """Structured action logging."""
    
    def log_action(
        self,
        action_type: str,
        details: dict[str, Any],
        level: str = "info"
    ) -> None:
        """Log an action with details."""
    
    def get_recent_actions(
        self,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get recent logged actions."""

# Usage
logger = ActionLogger()
logger.log_action("analysis_complete", {
    "files": 42,
    "duration": 1.5,
    "issues": 3
})
```

## System Functions

### Creating a System

```python
def create_basic_system(
    config_path: str = None,
    enable_extensions: bool = True
) -> dict[str, Any]:
    """Create a basic A1 system with default components."""

# Usage
system = create_basic_system(enable_extensions=True)
event_bus = system["event_bus"]
context_mgr = system["context_manager"]
quality = system["quality_guardian"]
```

### Version Information

```python
def get_version_info() -> dict[str, Any]:
    """Get detailed version information."""

# Usage
info = get_version_info()
print(f"Version: {info['version']}")
print(f"Components: {info['components']}")
```

### Extension Management

```python
# Initialize specific extensions
def initialize_prediction_engine(event_bus: EventBus) -> BasicPredictionEngine:
    """Initialize prediction engine with event bus."""

def initialize_state_manager(root_path: Path) -> SimpleStateManager:
    """Initialize state manager with root path."""

def initialize_workflow_detector(event_bus: EventBus) -> SimpleWorkflowDetector:
    """Initialize workflow detector with event bus."""

def initialize_hook_manager(config_file: str) -> SimpleHookManager:
    """Initialize hook manager with config file."""

def initialize_persistence(root_path: Path) -> SimplePersistenceManager:
    """Initialize persistence manager with root path."""
```

## Type Definitions

### Enums

```python
class ContextType(Enum):
    """Context types for different work modes."""
    RESEARCH = "research"
    DEVELOPMENT = "development"
    DEBUGGING = "debugging"
    TESTING = "testing"

class QualityLevel(Enum):
    """Quality level classifications."""
    EXCELLENT = "excellent"  # >= 90
    GOOD = "good"           # >= 80
    ACCEPTABLE = "acceptable"  # >= 70
    POOR = "poor"           # < 70

class WorkflowType(Enum):
    """Types of development workflows."""
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIXING = "bug_fixing"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
```

### Data Classes

```python
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

@dataclass
class CodeMetrics:
    """Code analysis metrics."""
    file_count: int = 0
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    function_count: int = 0
    class_count: int = 0
    average_complexity: float = 0.0

@dataclass
class Suggestion:
    """AI-generated suggestion."""
    type: str
    description: str
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)

@dataclass
class Pattern:
    """Detected pattern in development."""
    pattern_type: str
    description: str
    occurrences: int
    confidence: float
    examples: list[str] = field(default_factory=list)
```

## Examples

### Complete System Setup

```python
import asyncio
from quaestor.a1 import (
    create_basic_system,
    ToolUseEvent,
    FileChangeEvent,
    ContextType,
    QualityMetrics,
)

async def main():
    # Create system
    system = create_basic_system(enable_extensions=True)
    
    # Get components
    event_bus = system["event_bus"]
    context_mgr = system["context_manager"]
    quality = system["quality_guardian"]
    learning = system["learning_manager"]
    
    # Create context session
    session = context_mgr.create_session(ContextType.DEVELOPMENT)
    
    # Subscribe to events
    async def on_tool_use(event: ToolUseEvent):
        print(f"Tool used: {event.tool_name}")
        # Learn from event
        await learning.learn_from_event(event)
    
    event_bus.subscribe(ToolUseEvent, on_tool_use)
    
    # Simulate development
    # 1. Tool usage
    await event_bus.publish(ToolUseEvent(tool_name="vim", success=True))
    await event_bus.publish(ToolUseEvent(tool_name="pytest", success=True))
    
    # 2. File changes
    await event_bus.publish(FileChangeEvent(
        file_path="src/main.py",
        change_type="modified"
    ))
    
    # 3. Quality check
    metrics = QualityMetrics(
        file_path="src/main.py",
        overall_score=85.0,
        maintainability=80.0,
        readability=90.0,
        complexity=75.0,
        testability=85.0,
        documentation=90.0
    )
    report = quality.analyze_quality([metrics])
    print(f"Quality: {report.quality_level.value}")
    
    # 4. Get suggestions
    suggestions = learning.get_suggestions({
        "current_tool": "pytest",
        "recent_tools": ["vim", "pytest"]
    })
    for suggestion in suggestions:
        print(f"Suggestion: {suggestion.description}")

# Run
asyncio.run(main())
```

### Custom Event Handler

```python
from quaestor.a1 import EventBus, Event, EventHandler

class CustomHandler(EventHandler):
    """Custom event handler with filtering."""
    
    def __init__(self, event_filter: callable = None):
        self.event_filter = event_filter
        self.handled_count = 0
    
    async def handle(self, event: Event) -> None:
        if self.event_filter and not self.event_filter(event):
            return
        
        self.handled_count += 1
        print(f"Handled event #{self.handled_count}: {event.get_event_type()}")

# Usage
event_bus = EventBus()
handler = CustomHandler(
    event_filter=lambda e: hasattr(e, 'success') and e.success
)
event_bus.subscribe(ToolUseEvent, handler)
```

### Extension Integration

```python
from quaestor.a1 import (
    get_prediction_engine,
    get_state_manager,
    get_workflow_detector,
)

# Setup extensions
prediction = get_prediction_engine()
state = get_state_manager()
workflow = get_workflow_detector()

# Use prediction
next_tools = prediction.predict_next_tool(limit=3)
print(f"Predicted tools: {[t[0] for t in next_tools]}")

# Use state management
state.track_files(["src/*.py"])
snapshot_id = state.create_snapshot("Initial state")
print(f"Created snapshot: {snapshot_id}")

# Check workflows
active_workflows = workflow.get_current_workflows()
for wf in active_workflows:
    print(f"Active workflow: {wf.workflow_type.value}")
```

## Best Practices

1. **Always use async/await** with event publishing
2. **Handle exceptions** in event handlers
3. **Clean up subscriptions** when done
4. **Use type hints** for better IDE support
5. **Configure components** appropriately for your project
6. **Monitor performance** in production
7. **Enable only needed extensions**
8. **Use context sessions** for isolation

## Error Handling

```python
from quaestor.a1.exceptions import (
    ConfigurationError,
    AnalysisError,
    ExtensionError,
)

try:
    system = create_basic_system()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ExtensionError as e:
    print(f"Extension error: {e}")
    # System still works without the extension
```

## Thread Safety

- EventBus: Thread-safe with async support
- ContextManager: Thread-safe with session isolation
- QualityGuardian: Thread-safe for reading
- LearningManager: Thread-safe with async learning
- Extensions: Varies by extension

## Performance Considerations

- Event publishing: < 1ms overhead
- Context switching: < 1ms
- Quality analysis: Linear with file count
- Learning: Constant time for most operations
- Extensions: Minimal overhead when disabled