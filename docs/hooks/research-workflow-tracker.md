# Research Workflow Tracker Hook

The Research Workflow Tracker monitors exploration activities and guides transitions from research to planning phases.

## Purpose

This hook:
- Tracks research activities (Read, Grep, Glob)
- Identifies research completion patterns
- Suggests workflow transitions
- Prevents premature implementation
- Guides systematic exploration

## Research Phase Tracking

### Activity Monitoring
Tracks usage of:
- **Read operations**: File explorations
- **Grep searches**: Pattern finding
- **Glob queries**: Structure mapping
- **Task agents**: Deep investigations

### Pattern Recognition
Identifies when research is:
- **Just starting**: Few operations, guides exploration
- **In progress**: Active searching, provides context
- **Comprehensive**: Many operations, suggests planning
- **Complete**: Patterns found, recommends transition

## Transition Guidelines

### Research → Planning
Suggests transition when:
- 10+ research operations completed
- Key patterns identified
- Architecture understood
- Requirements clear
- Dependencies mapped

### Example Output
```
📊 Research Progress Update

You've completed 15 research operations:
- Read 8 key files
- Searched for 5 patterns
- Explored 3 directories

Research appears comprehensive. Consider:
→ Use the planner agent to create an implementation plan
→ Or continue research if you need more context

Key findings ready for planning:
- Authentication uses JWT tokens
- Database follows repository pattern
- API uses REST conventions
```

## Workflow Enforcement

### Prevents Premature Implementation
When detecting early Write/Edit attempts:
```
⚠️ Workflow Notice: Currently in research phase

You're attempting to modify code before completing research.
Recommended: First understand the codebase structure.

Suggested approach:
1. Use researcher agent to explore the codebase
2. Create a plan with planner agent
3. Then proceed with implementation
```

### Guides Exploration
Provides contextual suggestions:
- "Explore the database schema next"
- "Search for similar implementations"
- "Check test files for usage examples"
- "Map out the API structure"

## Integration Points

### With Workflow Coordinator
- Reports research progress
- Signals phase readiness
- Maintains phase state
- Coordinates transitions

### With Agent System
- Suggests researcher agent
- Triggers planner agent
- Activates architect agent
- Coordinates with other agents

## Configuration

### Thresholds
```python
# Customizable thresholds
MIN_RESEARCH_OPS = 5      # Before planning allowed
COMPREHENSIVE_OPS = 10    # Suggests planning
MAX_RESEARCH_OPS = 20     # Encourages transition
```

### Research Patterns
- File exploration depth
- Search pattern complexity
- Directory coverage
- Concept discovery

## Best Practices

1. Complete thorough research before planning
2. Use researcher agent for systematic exploration
3. Document findings during research
4. Follow transition suggestions
5. Don't skip research for familiar codebases

## Benefits

- Prevents half-understood implementations
- Reduces refactoring needs
- Improves code quality
- Ensures architectural alignment
- Facilitates better planning