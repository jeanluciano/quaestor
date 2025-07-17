# Quaestor A1 Extension Development Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Extension Architecture](#extension-architecture)
3. [Creating an Extension](#creating-an-extension)
4. [Extension API](#extension-api)
5. [Built-in Extensions](#built-in-extensions)
6. [Testing Extensions](#testing-extensions)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Introduction

A1's extension system allows you to add optional functionality without bloating the core system. Extensions are modular, can be enabled/disabled at runtime, and integrate seamlessly with the event-driven architecture.

### Key Principles

- **Modularity**: Extensions are self-contained units
- **Optional**: Core system works without any extensions
- **Event-Driven**: Extensions communicate via events
- **Performance**: Minimal overhead when disabled
- **Simplicity**: Easy to create and maintain

## Extension Architecture

### Extension Structure

```
quaestor/a1/extensions/
├── __init__.py           # Extension registry
├── prediction.py         # Prediction engine
├── hooks.py             # Hook system
├── state.py             # State management
├── workflow.py          # Workflow detection
└── persistence.py       # Data persistence
```

### Extension Lifecycle

1. **Registration**: Extension registers with the system
2. **Initialization**: Extension initialized with dependencies
3. **Event Subscription**: Extension subscribes to relevant events
4. **Operation**: Extension processes events and provides services
5. **Shutdown**: Extension cleans up resources

### Extension Interface

Every extension should follow this pattern:

```python
# 1. Module-level singleton
_extension_instance = None

# 2. Initialization function
def initialize_extension(dependencies):
    global _extension_instance
    _extension_instance = ExtensionClass(dependencies)
    return _extension_instance

# 3. Getter function
def get_extension():
    return _extension_instance

# 4. Main extension class
class ExtensionClass:
    def __init__(self, dependencies):
        # Initialize extension
        pass
```

## Creating an Extension

### Step 1: Define Extension Class

```python
# my_extension.py
from dataclasses import dataclass
from typing import Optional, Any
from quaestor.a1.core.events import Event, EventBus

@dataclass
class MyExtensionConfig:
    """Configuration for my extension."""
    enabled: bool = True
    custom_setting: str = "default"
    max_items: int = 100

class MyExtension:
    """Custom extension for Quaestor A1."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus
        self.config = MyExtensionConfig()
        self.data = {}
        
        # Subscribe to events if event bus provided
        if self.event_bus:
            self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        from quaestor.a1.core.events import ToolUseEvent
        
        self.event_bus.subscribe(
            ToolUseEvent,
            self._handle_tool_use
        )
    
    async def _handle_tool_use(self, event: ToolUseEvent):
        """Handle tool use events."""
        # Process event
        self.data[event.tool_name] = self.data.get(event.tool_name, 0) + 1
    
    def get_statistics(self) -> dict[str, Any]:
        """Get extension statistics."""
        return {
            "total_events": sum(self.data.values()),
            "unique_tools": len(self.data),
            "top_tools": sorted(
                self.data.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
```

### Step 2: Add Module-Level Functions

```python
# Module-level singleton
_my_extension: Optional[MyExtension] = None

def initialize_my_extension(
    event_bus: Optional[EventBus] = None
) -> MyExtension:
    """Initialize the extension."""
    global _my_extension
    
    if _my_extension is None:
        _my_extension = MyExtension(event_bus)
    
    return _my_extension

def get_my_extension() -> Optional[MyExtension]:
    """Get the extension instance."""
    return _my_extension

# Convenience functions
def get_tool_statistics() -> dict[str, Any]:
    """Get tool usage statistics."""
    if _my_extension:
        return _my_extension.get_statistics()
    return {}
```

### Step 3: Register Extension

Add to `extensions/__init__.py`:

```python
# Import extension
from .my_extension import (
    MyExtension,
    initialize_my_extension,
    get_my_extension,
    get_tool_statistics,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "MyExtension",
    "initialize_my_extension", 
    "get_my_extension",
    "get_tool_statistics",
]
```

### Step 4: Integrate with System

Update `create_basic_system()`:

```python
def create_basic_system(config_path=None, enable_extensions=True):
    # ... existing code ...
    
    if enable_extensions:
        try:
            # ... existing extensions ...
            system["my_extension"] = initialize_my_extension(event_bus)
        except Exception as e:
            print(f"Warning: Could not initialize extension: {e}")
    
    return system
```

## Extension API

### Event Integration

Extensions primarily interact through events:

```python
class EventAwareExtension:
    """Extension that processes events."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.stats = {"events_processed": 0}
        
        # Subscribe to multiple event types
        self.event_bus.subscribe(ToolUseEvent, self.handle_tool_event)
        self.event_bus.subscribe(FileChangeEvent, self.handle_file_event)
        self.event_bus.subscribe(SystemEvent, self.handle_system_event)
    
    async def handle_tool_event(self, event: ToolUseEvent):
        """Process tool events."""
        self.stats["events_processed"] += 1
        
        # Emit derived event
        if event.tool_name == "pytest" and event.success:
            await self.event_bus.publish(
                SystemEvent(
                    event_name="tests_passed",
                    component="my_extension"
                )
            )
```

### Configuration Management

Extensions should support configuration:

```python
from quaestor.a1.utilities.config import BaseConfig

@dataclass
class MyExtensionConfig(BaseConfig):
    """Configuration for my extension."""
    
    # Required fields
    enabled: bool = True
    
    # Optional settings
    cache_size: int = 1000
    timeout_seconds: float = 30.0
    allowed_patterns: list[str] = field(default_factory=lambda: ["*.py"])
    
    def validate(self) -> list[str]:
        """Validate configuration."""
        errors = []
        
        if self.cache_size < 0:
            errors.append("cache_size must be non-negative")
        
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        
        return errors
```

### State Persistence

Extensions can persist state:

```python
class PersistentExtension:
    """Extension with persistent state."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.state_file = storage_path / "extension_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load persisted state."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"initialized": time.time()}
    
    def _save_state(self):
        """Save state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def update_state(self, key: str, value: Any):
        """Update and persist state."""
        self.state[key] = value
        self._save_state()
```

### Performance Monitoring

Extensions should monitor their performance:

```python
from quaestor.a1.utilities.monitoring import PerformanceTimer

class MonitoredExtension:
    """Extension with performance monitoring."""
    
    def __init__(self):
        self.metrics = {
            "operation_count": 0,
            "total_time": 0.0,
            "errors": 0
        }
    
    async def perform_operation(self, data: Any) -> Any:
        """Perform operation with monitoring."""
        with PerformanceTimer() as timer:
            try:
                self.metrics["operation_count"] += 1
                
                # Actual operation
                result = await self._process_data(data)
                
                self.metrics["total_time"] += timer.elapsed
                return result
                
            except Exception as e:
                self.metrics["errors"] += 1
                raise
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        count = self.metrics["operation_count"]
        return {
            "operations": count,
            "errors": self.metrics["errors"],
            "avg_time_ms": (self.metrics["total_time"] / count * 1000) if count > 0 else 0
        }
```

## Built-in Extensions

### 1. Prediction Engine

Predicts next tools and files based on patterns:

```python
# Extension structure
class BasicPredictionEngine:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.pattern_recognizer = SimplePatternRecognizer()
        self.sequence_predictor = SequencePredictor()
        self.file_predictor = FilePredictor()
    
    def predict_next_tool(self, limit: int = 5) -> list[tuple[str, float]]:
        """Predict next tool usage."""
    
    def predict_next_file(self, current_file: str, limit: int = 5) -> list[tuple[str, float]]:
        """Predict next file to work on."""
```

### 2. State Management

Tracks file states and provides snapshots:

```python
# Extension structure
class SimpleStateManager:
    def __init__(self, project_root: Path, event_bus: Optional[EventBus] = None):
        self.project_root = project_root
        self.snapshots = []
        self.tracked_files = []
    
    def create_snapshot(self, description: str) -> str:
        """Create state snapshot."""
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore from snapshot."""
```

### 3. Workflow Detection

Identifies development workflows:

```python
# Extension structure
class SimpleWorkflowDetector:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.active_workflows = {}
        self.workflow_patterns = self._initialize_patterns()
    
    def detect_workflow(self, events: list[Event]) -> Optional[WorkflowType]:
        """Detect workflow from event sequence."""
```

### 4. Hook System

Executes actions based on events:

```python
# Extension structure
class SimpleHookManager:
    def __init__(self, config_file: str = ".quaestor/hooks.json"):
        self.hooks = self._load_hooks()
    
    def execute_hooks(self, event_type: str, context: dict) -> list[HookResult]:
        """Execute hooks for event."""
```

### 5. Persistence

Manages data storage:

```python
# Extension structure  
class SimplePersistenceManager:
    def __init__(self, storage_backend: StorageBackend):
        self.backend = storage_backend
    
    def save(self, key: str, data: Any) -> None:
        """Save data."""
    
    def load(self, key: str) -> Any:
        """Load data."""
```

## Testing Extensions

### Unit Testing

```python
import pytest
from quaestor.a1.core.events import EventBus, ToolUseEvent
from my_extension import MyExtension, initialize_my_extension

@pytest.fixture
def extension():
    """Create extension instance."""
    event_bus = EventBus()
    return MyExtension(event_bus)

@pytest.mark.asyncio
async def test_event_handling(extension):
    """Test event handling."""
    # Publish event
    event = ToolUseEvent(tool_name="pytest", success=True)
    await extension.event_bus.publish(event)
    
    # Check processing
    stats = extension.get_statistics()
    assert stats["total_events"] == 1
    assert "pytest" in extension.data

def test_statistics(extension):
    """Test statistics generation."""
    # Add test data
    extension.data = {
        "pytest": 10,
        "black": 5,
        "mypy": 3
    }
    
    stats = extension.get_statistics()
    assert stats["total_events"] == 18
    assert stats["unique_tools"] == 3
    assert stats["top_tools"][0] == ("pytest", 10)
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_extension_integration():
    """Test extension integration with system."""
    from quaestor.a1 import create_basic_system
    
    # Create system with extension
    system = create_basic_system(enable_extensions=True)
    
    # Verify extension loaded
    assert "my_extension" in system
    
    # Test functionality
    event_bus = system["event_bus"]
    await event_bus.publish(ToolUseEvent(tool_name="test"))
    
    # Verify processing
    extension = system["my_extension"]
    stats = extension.get_statistics()
    assert stats["total_events"] > 0
```

### Performance Testing

```python
import time
import asyncio

@pytest.mark.asyncio
async def test_extension_performance(extension):
    """Test extension performance."""
    start_time = time.time()
    
    # Generate many events
    events = [
        ToolUseEvent(tool_name=f"tool_{i}", success=True)
        for i in range(1000)
    ]
    
    # Publish all events
    for event in events:
        await extension.event_bus.publish(event)
    
    elapsed = time.time() - start_time
    
    # Performance assertions
    assert elapsed < 1.0  # Should process 1000 events in < 1 second
    assert extension.get_statistics()["total_events"] == 1000
```

## Best Practices

### 1. Keep Extensions Focused

Each extension should have a single, clear purpose:

```python
# Good: Focused extension
class SecurityScanner:
    """Scans code for security issues."""
    
# Bad: Kitchen sink extension
class SuperExtension:
    """Does security, performance, formatting, and more!"""
```

### 2. Make Extensions Optional

Core functionality should work without any extension:

```python
# Good: Graceful handling
def use_extension():
    extension = get_my_extension()
    if extension:
        return extension.get_data()
    return []  # Sensible default

# Bad: Assumes extension exists
def use_extension():
    return get_my_extension().get_data()  # Will crash if None
```

### 3. Use Events for Communication

Extensions should communicate via events, not direct calls:

```python
# Good: Event-based communication
async def process_data(self, data):
    result = self._analyze(data)
    await self.event_bus.publish(
        AnalysisCompleteEvent(result=result)
    )

# Bad: Direct coupling
def process_data(self, data):
    result = self._analyze(data)
    other_extension.handle_result(result)  # Direct coupling!
```

### 4. Handle Errors Gracefully

Extensions should not crash the system:

```python
class ResilientExtension:
    async def handle_event(self, event: Event):
        try:
            await self._process_event(event)
        except Exception as e:
            # Log error but don't crash
            self.logger.error(f"Error processing event: {e}")
            
            # Optionally emit error event
            await self.event_bus.publish(
                SystemEvent(
                    event_name="extension_error",
                    severity="warning",
                    component=self.__class__.__name__
                )
            )
```

### 5. Provide Configuration

Make extensions configurable:

```python
@dataclass
class ExtensionConfig(BaseConfig):
    """Extension configuration."""
    enabled: bool = True
    feature_x: bool = False
    cache_size: int = 1000
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExtensionConfig':
        """Create from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })
```

### 6. Document Your Extension

Provide clear documentation:

```python
class MyExtension:
    """
    Custom extension for tracking code metrics.
    
    This extension monitors code changes and provides insights
    about code quality trends over time.
    
    Configuration:
        - enabled: Whether extension is active
        - threshold: Quality threshold (0-100)
        - report_interval: Seconds between reports
    
    Events:
        Subscribes to:
            - FileChangeEvent
            - QualityCheckEvent
        
        Publishes:
            - MetricsReportEvent
            - QualityAlertEvent
    
    Usage:
        extension = get_metrics_extension()
        report = extension.generate_report()
    """
```

### 7. Version Compatibility

Handle version differences:

```python
from quaestor.a1 import get_version_info

class VersionAwareExtension:
    def __init__(self):
        version_info = get_version_info()
        self.version = version_info["version"]
        
        # Adjust behavior based on version
        if self.version >= "2.2.0":
            self._use_new_api()
        else:
            self._use_legacy_api()
```

## Examples

### Example 1: Metrics Collector Extension

```python
# metrics_extension.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from collections import defaultdict
import time

from quaestor.a1.core.events import (
    Event, EventBus, FileChangeEvent, 
    QualityCheckEvent, SystemEvent
)

@dataclass
class MetricsData:
    """Metrics for a specific file."""
    file_path: str
    changes: int = 0
    quality_scores: list[float] = field(default_factory=list)
    last_modified: float = field(default_factory=time.time)

class MetricsCollector:
    """Collects and analyzes code metrics over time."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus
        self.metrics: Dict[str, MetricsData] = {}
        self.start_time = time.time()
        
        if self.event_bus:
            self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_bus.subscribe(FileChangeEvent, self._handle_file_change)
        self.event_bus.subscribe(QualityCheckEvent, self._handle_quality_check)
    
    async def _handle_file_change(self, event: FileChangeEvent):
        """Track file changes."""
        if event.file_path not in self.metrics:
            self.metrics[event.file_path] = MetricsData(event.file_path)
        
        self.metrics[event.file_path].changes += 1
        self.metrics[event.file_path].last_modified = time.time()
    
    async def _handle_quality_check(self, event: QualityCheckEvent):
        """Track quality scores."""
        for file_metrics in event.metrics:
            path = file_metrics.file_path
            if path not in self.metrics:
                self.metrics[path] = MetricsData(path)
            
            self.metrics[path].quality_scores.append(
                file_metrics.overall_score
            )
    
    def get_hot_files(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequently changed files."""
        sorted_files = sorted(
            self.metrics.items(),
            key=lambda x: x[1].changes,
            reverse=True
        )
        return [(path, data.changes) for path, data in sorted_files[:limit]]
    
    def get_quality_trends(self) -> dict[str, dict[str, float]]:
        """Get quality score trends."""
        trends = {}
        for path, data in self.metrics.items():
            if data.quality_scores:
                trends[path] = {
                    "current": data.quality_scores[-1],
                    "average": sum(data.quality_scores) / len(data.quality_scores),
                    "trend": data.quality_scores[-1] - data.quality_scores[0]
                    if len(data.quality_scores) > 1 else 0
                }
        return trends
    
    def generate_report(self) -> dict[str, Any]:
        """Generate metrics report."""
        return {
            "duration_hours": (time.time() - self.start_time) / 3600,
            "files_tracked": len(self.metrics),
            "total_changes": sum(d.changes for d in self.metrics.values()),
            "hot_files": self.get_hot_files(5),
            "quality_trends": self.get_quality_trends(),
        }

# Module-level singleton
_metrics_collector: Optional[MetricsCollector] = None

def initialize_metrics_collector(
    event_bus: Optional[EventBus] = None
) -> MetricsCollector:
    """Initialize metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(event_bus)
    return _metrics_collector

def get_metrics_collector() -> Optional[MetricsCollector]:
    """Get metrics collector instance."""
    return _metrics_collector
```

### Example 2: Auto-Format Extension

```python
# autoformat_extension.py
import subprocess
from pathlib import Path
from typing import Optional, Set

from quaestor.a1.core.events import (
    EventBus, FileChangeEvent, SystemEvent
)

class AutoFormatter:
    """Automatically formats code on file changes."""
    
    def __init__(
        self, 
        event_bus: Optional[EventBus] = None,
        config: Optional[dict] = None
    ):
        self.event_bus = event_bus
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.formatters = self._setup_formatters()
        self.processing: Set[str] = set()
        
        if self.event_bus and self.enabled:
            self._subscribe_to_events()
    
    def _setup_formatters(self) -> dict[str, list[str]]:
        """Setup formatters by file extension."""
        return {
            ".py": ["black", "{file}"],
            ".js": ["prettier", "--write", "{file}"],
            ".ts": ["prettier", "--write", "{file}"],
            ".rs": ["rustfmt", "{file}"],
            ".go": ["gofmt", "-w", "{file}"],
        }
    
    def _subscribe_to_events(self):
        """Subscribe to file change events."""
        self.event_bus.subscribe(
            FileChangeEvent, 
            self._handle_file_change
        )
    
    async def _handle_file_change(self, event: FileChangeEvent):
        """Format file on change."""
        if not self.enabled:
            return
            
        if event.change_type != "modified":
            return
            
        # Avoid recursive formatting
        if event.file_path in self.processing:
            return
            
        file_path = Path(event.file_path)
        if not file_path.exists():
            return
            
        # Get formatter for file type
        formatter_cmd = self.formatters.get(file_path.suffix)
        if not formatter_cmd:
            return
            
        # Format file
        self.processing.add(event.file_path)
        try:
            cmd = [arg.replace("{file}", str(file_path)) 
                   for arg in formatter_cmd]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                await self.event_bus.publish(
                    SystemEvent(
                        event_name="file_formatted",
                        component="autoformat",
                        severity="info"
                    )
                )
            else:
                await self.event_bus.publish(
                    SystemEvent(
                        event_name="format_failed",
                        component="autoformat",
                        severity="warning"
                    )
                )
        finally:
            self.processing.remove(event.file_path)
    
    def toggle(self) -> bool:
        """Toggle auto-formatting on/off."""
        self.enabled = not self.enabled
        return self.enabled
    
    def add_formatter(
        self, 
        extension: str, 
        command: list[str]
    ):
        """Add custom formatter."""
        self.formatters[extension] = command
```

### Example 3: Smart Context Extension

```python
# smart_context_extension.py
from collections import deque
from typing import Optional, Set, Deque
import time

from quaestor.a1.core.events import (
    EventBus, FileChangeEvent, ToolUseEvent
)
from quaestor.a1.core.context import ContextManager

class SmartContextManager:
    """Automatically manages context based on activity."""
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        context_manager: Optional[ContextManager] = None
    ):
        self.event_bus = event_bus
        self.context_manager = context_manager
        self.recent_files: Deque[str] = deque(maxlen=50)
        self.file_scores: dict[str, float] = {}
        self.last_cleanup = time.time()
        
        if self.event_bus:
            self._subscribe_to_events()
    
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            FileChangeEvent,
            self._handle_file_event
        )
        self.event_bus.subscribe(
            ToolUseEvent,
            self._handle_tool_event  
        )
    
    async def _handle_file_event(self, event: FileChangeEvent):
        """Track file activity."""
        self.recent_files.append(event.file_path)
        
        # Update scores
        self.file_scores[event.file_path] = self.file_scores.get(
            event.file_path, 0
        ) + 1
        
        # Auto-add to context if score high enough
        if self.context_manager and self.file_scores[event.file_path] > 3:
            session = self._get_active_session()
            if session:
                self.context_manager.add_file(
                    session.id,
                    event.file_path
                )
        
        # Periodic cleanup
        if time.time() - self.last_cleanup > 300:  # 5 minutes
            self._cleanup_context()
    
    async def _handle_tool_event(self, event: ToolUseEvent):
        """Adjust context based on tool usage."""
        if not self.context_manager:
            return
            
        session = self._get_active_session()
        if not session:
            return
            
        # Heuristics for context adjustment
        if event.tool_name in ["pytest", "unittest"]:
            # Testing tools - add test files
            self._add_pattern_to_context("**/test_*.py", session.id)
        elif event.tool_name in ["mypy", "pylint", "flake8"]:
            # Linting tools - focus on recent files
            for file in list(self.recent_files)[-5:]:
                self.context_manager.add_file(session.id, file)
    
    def _get_active_session(self):
        """Get active context session."""
        if not self.context_manager.sessions:
            return None
        return list(self.context_manager.sessions.values())[0]
    
    def _add_pattern_to_context(self, pattern: str, session_id: str):
        """Add files matching pattern to context."""
        from pathlib import Path
        for file_path in Path.cwd().rglob(pattern):
            if file_path.is_file():
                self.context_manager.add_file(
                    session_id,
                    str(file_path)
                )
    
    def _cleanup_context(self):
        """Remove stale files from context."""
        self.last_cleanup = time.time()
        
        # Decay scores
        for file in list(self.file_scores.keys()):
            self.file_scores[file] *= 0.9
            if self.file_scores[file] < 0.1:
                del self.file_scores[file]
        
        # Remove low-score files from context
        if self.context_manager:
            session = self._get_active_session()
            if session and session.current_context:
                for file in session.current_context.relevant_files[:]:
                    if self.file_scores.get(file, 0) < 1:
                        self.context_manager.remove_file(
                            session.id,
                            file
                        )
```

## Conclusion

A1's extension system provides a powerful way to add functionality while maintaining the simplicity of the core system. By following the patterns and best practices in this guide, you can create extensions that integrate seamlessly and provide valuable features to users.

Key takeaways:
- Keep extensions focused and optional
- Use events for loose coupling
- Handle errors gracefully
- Provide good configuration options
- Test thoroughly
- Document your extension well

For more examples, see the built-in extensions in `quaestor/a1/extensions/`.