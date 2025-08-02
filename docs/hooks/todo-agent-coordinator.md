# TODO Agent Coordinator Hook

The TODO Agent Coordinator monitors TODO patterns and suggests appropriate agents based on task types and completion patterns.

## Purpose

This hook:
- Analyzes TODO items for patterns
- Suggests relevant agents for tasks
- Detects workflow transitions
- Identifies completion milestones
- Coordinates multi-agent workflows

## Pattern Recognition

### Task Type Detection
The hook identifies:
- **Bug fixes** → Suggests Debugger agent
- **Refactoring** → Suggests Refactorer agent
- **New features** → Suggests Planner + Implementer
- **Documentation** → Suggests appropriate doc updates
- **Testing** → Suggests QA agent

### Completion Patterns
Monitors for:
- High-priority task completions
- Related task groupings
- Workflow phase completions
- Milestone achievements
- Critical path progress

## Agent Suggestions

### Automatic Recommendations
When detecting:
- 3+ bug-related TODOs → "Use debugger agent for systematic fixes"
- 5+ completed tasks → "Use QA agent to review implementation"
- Planning phase done → "Use implementer agent to start coding"
- Complex refactoring → "Use architect agent for design review"

### Threshold-Based Triggers
```python
# Example thresholds
HIGH_PRIORITY_COMPLETED = 3  # Suggest QA review
BUGS_ACCUMULATED = 3         # Suggest debugger
TASKS_IN_PHASE = 5          # Suggest phase transition
```

## Integration Points

### With TODO System
- Monitors TodoWrite operations
- Tracks status changes
- Analyzes task descriptions
- Groups related items

### With Workflow Coordinator
- Signals phase transitions
- Coordinates agent handoffs
- Maintains workflow state
- Prevents phase skipping

## Output Format

```
🎯 Significant Progress Detected: 4 high-priority TODOs completed!

This indicates major implementation progress that needs quality review.

Please run: Use the qa agent to review the completed implementation

Recent completions:
- Implemented authentication system
- Added user management API
- Created permission middleware
- Set up test fixtures
```

## Best Practices

1. Use descriptive TODO content
2. Set appropriate priorities
3. Group related tasks
4. Follow agent suggestions
5. Complete tasks in logical order

## Configuration

Customize via:
- Threshold adjustments
- Pattern definitions
- Agent mappings
- Suggestion templates