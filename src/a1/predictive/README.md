# A1 Predictive Engine - Phase 5

The Predictive Engine provides intelligent pattern recognition and next-action prediction capabilities for the A1 system. It learns from user behavior and system events to offer contextual suggestions and workflow assistance.

## Overview

The predictive engine consists of several key components:

### 1. Pattern Recognition System
- **Pattern Types**: Command sequences, workflows, file access patterns, error recovery, time-based patterns
- **Sequence Mining**: Uses PrefixSpan-inspired algorithms to discover frequent sequences
- **Confidence Scoring**: Adaptive confidence based on observation frequency and success rates

### 2. Pattern Storage
- **Persistent Storage**: JSON-based storage in `.quaestor/.a1/predictive_patterns.json`
- **Pattern Indexing**: Fast lookup by type, confidence, and frequency
- **Pattern Merging**: Automatic consolidation of similar patterns

### 3. Pattern Matching
- **Context Matching**: Matches current context against discovered patterns
- **Partial Matching**: Recognizes incomplete sequences for prediction
- **Next Action Prediction**: Suggests likely next steps based on patterns

### 4. Predictive Engine
- **Event Processing**: Real-time pattern learning from event streams
- **Periodic Mining**: Automatic pattern extraction at configurable intervals
- **Suggestion Generation**: Context-aware suggestions with confidence scores

## Usage

### CLI Commands

```bash
# Show predictive engine status
quaestor a1 predictive status

# List discovered patterns
quaestor a1 predictive patterns --type command_sequence --min-confidence 0.7

# Get suggestions for current context
quaestor a1 predictive suggest

# Export patterns for analysis
quaestor a1 predictive export patterns.json

# Analyze historical event log
quaestor a1 predictive analyze events.log

# Prune old patterns
quaestor a1 predictive prune --days 30
```

### Python API

```python
from a1.core.event_bus import EventBus
from a1.predictive import PredictiveEngine

# Initialize engine
event_bus = EventBus()
engine = PredictiveEngine(event_bus)

# Get suggestions
suggestions = engine.get_suggestions(context={
    "current_file": "main.py",
    "recent_command": "grep"
})

# Check workflow status
status = engine.get_workflow_status()

# Export patterns
engine.export_patterns(Path("patterns.json"))
```

## Pattern Types

### Command Sequence Patterns
Captures sequences of tool/command usage:
```python
CommandPattern(
    command_sequence=["grep", "read", "edit"],
    context_requirements={"file_type": "python"},
    success_rate=0.85
)
```

### Workflow Patterns
Identifies complete task workflows:
```python
WorkflowPattern(
    workflow_name="add_feature",
    workflow_steps=[
        {"id": "research", "description": "Research implementation"},
        {"id": "implement", "description": "Write code"},
        {"id": "test", "description": "Add tests"},
        {"id": "commit", "description": "Commit changes"}
    ]
)
```

### File Access Patterns
Tracks file navigation and editing patterns:
```python
FilePattern(
    file_sequence=["main.py", "utils.py", "test_main.py"],
    related_files={"utils.py": 0.9, "config.py": 0.7}
)
```

### Error Recovery Patterns
Learns from error resolution sequences:
```python
ErrorRecoveryPattern(
    error_type="ImportError",
    recovery_actions=[
        {"action": "install_package", "success_rate": 0.8},
        {"action": "fix_import", "success_rate": 0.9}
    ]
)
```

### Time-Based Patterns
Recognizes time-of-day usage patterns:
```python
TimeBasedPattern(
    time_slots=[{"start": 9, "end": 12}],
    common_activities=["code_review", "testing"]
)
```

## Architecture

### Event Flow
1. Events published to EventBus → PredictiveEngine
2. Events added to SequenceMiner for pattern extraction
3. Patterns discovered and stored in PatternStore
4. PatternMatcher matches context against patterns
5. Suggestions generated and published back to EventBus

### Storage Schema
```json
{
  "version": "1.0",
  "last_updated": 1234567890,
  "patterns": [
    {
      "id": "cmd_seq_12345",
      "pattern_type": "command_sequence",
      "confidence": 0.85,
      "frequency": 12,
      "command_sequence": ["grep", "read", "edit"],
      "context_requirements": {},
      "success_rate": 0.9
    }
  ]
}
```

### Performance Characteristics
- **Pattern Mining**: O(n²) worst case, optimized with pruning
- **Pattern Matching**: O(m) where m is number of patterns
- **Storage**: O(p) where p is number of unique patterns
- **Memory**: Bounded by event buffer size (default 100 events)

## Configuration

Key configuration options:
```python
# Sequence mining
min_support = 2  # Minimum pattern occurrences
max_gap = 300    # Max seconds between sequential events

# Pattern mining
mining_interval = 300  # Mine patterns every 5 minutes
events_since_mining = 10  # Minimum events before mining

# Event buffer
max_buffer_size = 100  # Maximum events in context buffer

# Pattern pruning
days_inactive = 30  # Prune patterns not seen in N days
```

## Integration with A1

The predictive engine integrates seamlessly with other A1 components:

1. **Event Bus**: Subscribes to all relevant event types
2. **Learning Framework**: Complements rule-based learning with behavior patterns
3. **Context Management**: Uses context for pattern matching
4. **Quality Guardian**: Can suggest quality improvements

## Future Enhancements

Planned improvements for the predictive engine:

1. **Machine Learning Models**: Integrate neural sequence models
2. **Cross-User Learning**: Learn from aggregated anonymized patterns
3. **Pattern Visualization**: Rich UI for pattern exploration
4. **Pattern Sharing**: Export/import pattern libraries
5. **A/B Testing**: Test suggestion effectiveness

## Privacy and Security

- All patterns stored locally in `.quaestor/.a1/`
- No data sent to external services
- Patterns can be exported/deleted at any time
- Sensitive information excluded from patterns