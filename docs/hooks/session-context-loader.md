# Session Context Loader Hook

The Session Context Loader initializes each Claude Code session with project context and workflow recommendations.

## Purpose

This hook:
- Loads project context at session start
- Checks for active specifications
- Determines current workflow phase
- Provides contextual recommendations
- Suggests appropriate starting agents

## Session Initialization

### Context Loading
At session start, the hook:
1. Reads specification status
2. Checks workflow state
3. Loads recent activity
4. Analyzes current TODOs
5. Prepares recommendations

### Output Format
```
=== SESSION CONTEXT ===
ACTIVE SPECIFICATION: auth-spec-001 (Implementation Phase)
- Next step: Implement user registration endpoint
- Progress: 60% complete (3/5 tasks done)

WORKFLOW STATE: Implementation phase active
- Recently completed: Database schema design
- Current focus: API endpoint implementation
- Suggested: Use implementer agent to continue

TODO STATUS: 4 pending, 2 in progress
- High priority: Complete auth middleware
- In progress: User registration endpoint

AGENT RECOMMENDATIONS:
1. Continue with implementer agent for API work
2. Use debugger if encountering test failures
3. Consider qa agent after endpoint completion
==============================
```

## Workflow Detection

### Phase Recognition
The hook identifies:
- **No active spec** → Suggest research/planning
- **Research phase** → Guide exploration
- **Planning phase** → Focus on specification
- **Implementation** → Provide task context
- **Review phase** → Suggest validation steps

### Contextual Guidance
Based on project state:
- New projects → Start with research
- Active specs → Continue implementation
- Completed phases → Move to next phase
- Blocked work → Suggest debugging
- Near completion → Recommend review

## Integration

### With Specifications
- Loads active spec details
- Shows completion progress
- Highlights next tasks
- Tracks phase status

### With Memory System
- References recent decisions
- Shows implementation history
- Highlights patterns
- Suggests continuity

### With TODO System
- Displays pending tasks
- Shows priority items
- Groups related work
- Identifies blockers

## Smart Recommendations

### Agent Selection
Suggests agents based on:
- Current workflow phase
- TODO task types
- Recent activity
- Specification needs
- Detected issues

### Workflow Guidance
Provides:
- Next logical steps
- Phase transition hints
- Completion criteria
- Quality checkpoints

## Configuration

Customize by modifying:
- Context template
- Recommendation logic
- Phase detection rules
- Agent suggestion mappings

## Best Practices

1. Review session context at start
2. Follow workflow recommendations
3. Update specifications regularly
4. Maintain clear TODO items
5. Use suggested agents appropriately