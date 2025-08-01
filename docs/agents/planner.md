# Planner Agent

The Planner agent specializes in creating detailed specifications, strategic planning, and project organization. It transforms ideas and requirements into actionable specifications with clear contracts and acceptance criteria.

## Core Capabilities

### Specification Design
- Creates detailed specifications with unique IDs
- Defines clear inputs, outputs, and behavior contracts
- Writes comprehensive acceptance criteria
- Designs test scenarios using BDD format
- Maps dependencies between specifications

### Strategic Planning
- Breaks down complex projects into manageable specifications
- Estimates effort and complexity
- Identifies risks and mitigation strategies
- Creates implementation roadmaps
- Suggests optimal implementation order

### Use Case Analysis
- Identifies primary actors and goals
- Documents main success scenarios
- Captures edge cases and exceptions
- Defines preconditions and postconditions
- Creates comprehensive use case narratives

## When to Use

The Planner agent excels at:
- **Creating new specifications** for features or improvements
- **Breaking down epics** into smaller, implementable specs
- **Estimating work** with complexity-based sizing
- **Planning sprints** or development phases
- **Documenting requirements** in a structured format

## Specification Format

The Planner creates specifications following this structure:

```yaml
---
spec_id: "feat-auth-001"
title: "Implement JWT Authentication"
type: "feature"
status: "draft"
priority: "high"
created: "2024-01-15"
author: "planner"
---

# Specification: [Title]

## Use Case Overview
- **ID**: [spec-id]
- **Primary Actor**: [Who uses this]
- **Goal**: [What they want to achieve]
- **Priority**: [critical|high|medium|low]

## Context & Background
[Why this is needed and relevant context]

## Main Success Scenario
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Contract Definition

### Inputs
```yaml
inputs:
  param_name:
    type: "string"
    description: "What this parameter does"
    required: true
    validation: "regex or rules"
```

### Outputs
```yaml
outputs:
  result_name:
    type: "object"
    description: "What this returns"
    schema:
      field1: "type"
      field2: "type"
```

### Behavior Rules
- Rule 1: Clear behavioral requirement
- Rule 2: Another requirement
- Rule 3: Edge case handling

## Acceptance Criteria
- [ ] Criterion 1: Measurable success condition
- [ ] Criterion 2: Another success condition
- [ ] Criterion 3: Quality requirement

## Test Scenarios

### Scenario 1: Happy Path
```gherkin
Given a valid user credential
When the user attempts to login
Then a JWT token should be returned
And the token should be valid for 24 hours
```

### Scenario 2: Error Case
```gherkin
Given invalid credentials
When the user attempts to login
Then a 401 error should be returned
And no token should be generated
```

## Dependencies
- Depends on: [other-spec-id]
- Blocks: [dependent-spec-id]

## Estimated Effort
- Complexity: Medium (5-8 hours)
- Testing: 2-3 hours
- Documentation: 1 hour
```

## Planning Methodology

### Requirements Analysis
1. **Understand the need**: What problem are we solving?
2. **Identify stakeholders**: Who cares about this?
3. **Define success**: How do we know it's working?
4. **Consider constraints**: What limits us?

### Specification Creation
1. **Unique identification**: spec-type-number format
2. **Clear contracts**: Define inputs/outputs precisely
3. **Testable criteria**: Each criterion must be verifiable
4. **Complete scenarios**: Cover happy path and edge cases

### Estimation Approach
- **Simple (2-4 hours)**: CRUD operations, simple logic
- **Medium (4-8 hours)**: Business logic, integrations
- **Complex (8-16 hours)**: System changes, multiple components
- **Epic**: Break into multiple specifications

## Integration with Commands

### `/plan` Command
The planner is the primary agent for the `/plan` command:

```bash
/plan --spec "User Authentication"
# Planner creates detailed specification

/plan --analyze
# Planner provides strategic analysis
```

### Working with Other Agents
The planner coordinates with:
- **Architect**: Validates technical feasibility
- **Security**: Reviews security implications
- **QA**: Ensures testability
- **Implementer**: Confirms realistic estimates

## Best Practices

### Writing Good Specifications
1. **Be specific**: Avoid ambiguity in requirements
2. **Think contracts**: Define clear interfaces
3. **Consider errors**: What can go wrong?
4. **Make it testable**: Can we verify success?
5. **Keep it focused**: One concern per spec

### Estimation Guidelines
- Add 20% buffer for well-understood work
- Add 40% buffer for new technology
- Consider testing time (usually 30-40% of implementation)
- Include documentation time
- Account for code review cycles

### Dependency Management
- Identify hard dependencies (blockers)
- Note soft dependencies (nice to have)
- Consider parallel work opportunities
- Plan for integration points

## Configuration

Customize planner behavior in settings:

```json
{
  "agent_preferences": {
    "planner": {
      "estimation_style": "conservative",
      "include_test_scenarios": true,
      "max_spec_complexity": "medium"
    }
  }
}
```

## Common Patterns

### Feature Specification
Best for new functionality:
- Clear user story format
- Comprehensive acceptance criteria
- Multiple test scenarios
- UI/UX considerations

### Bug Fix Specification
For addressing issues:
- Root cause analysis section
- Regression test scenarios
- Minimal acceptance criteria
- Focus on preventing recurrence

### Refactoring Specification
For code improvements:
- Current state documentation
- Target state definition
- Migration strategy
- Performance benchmarks

## Tips for Success

1. **Collaborate early**: Get architect input on complex specs
2. **Iterate**: Specifications can evolve
3. **Link related work**: Use dependency tracking
4. **Consider the future**: How might this grow?
5. **Document decisions**: Why this approach?

## Next Steps

- Learn about the [Architect Agent](architect.md) for system design
- Explore the [Implementer Agent](implementer.md) for building features
- Understand [Creating Specifications](../specs/creating.md)
- Read about the [/plan Command](../commands/plan.md)