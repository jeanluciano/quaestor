# Workflow Coordinator Agent

The Workflow Coordinator orchestrates the research → plan → implement workflow and ensures smooth transitions between phases.

## Purpose

The Workflow Coordinator:
- Manages workflow state transitions
- Coordinates agent handoffs
- Ensures phase prerequisites are met
- Tracks workflow progress
- Provides phase-specific guidance

## Workflow Phases

### 1. Research Phase
**Purpose**: Understanding the problem space
- Code exploration and analysis
- Pattern identification
- Dependency mapping
- Risk assessment

**Agents Involved**: Researcher, Architect

### 2. Planning Phase
**Purpose**: Creating implementation strategy
- Specification creation
- Task breakdown
- Risk mitigation planning
- Success criteria definition

**Agents Involved**: Planner, Architect

### 3. Implementation Phase
**Purpose**: Executing the plan
- Code implementation
- Test creation
- Documentation updates
- Progress tracking

**Agents Involved**: Implementer, QA, Debugger

### 4. Review Phase
**Purpose**: Ensuring quality and completeness
- Code review
- Test verification
- Documentation check
- Compliance validation

**Agents Involved**: Reviewer, QA, Compliance Enforcer

## Coordination Mechanisms

### Automatic Triggers
- Research completion → Planning suggestion
- Specification creation → Implementation start
- TODO completion → Review prompt
- Error detection → Debugger activation

### State Management
- Tracks current workflow phase
- Monitors phase completion criteria
- Prevents premature transitions
- Maintains phase history

## Integration Points

- **Hooks**: `research_workflow_tracker.py`, `session_context_loader.py`
- **Commands**: Works with all slash commands
- **Specifications**: Tracks progress through TODO-based specification system
- **TODO Integration**: Monitors TODO completion for phase transitions

## Best Practices

1. Follow the natural workflow progression
2. Complete each phase thoroughly
3. Use coordinator suggestions for next steps
4. Don't skip phases unless explicitly needed
5. Document phase transitions in commits