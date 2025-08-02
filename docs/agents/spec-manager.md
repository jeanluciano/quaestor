# Specification Manager Agent

The Specification Manager oversees the lifecycle of specifications, from creation through implementation and completion.

## Purpose

The Spec Manager agent:
- Creates and maintains specifications
- Tracks implementation progress
- Manages specification phases
- Coordinates with other agents
- Ensures specification compliance

## When to Use

Use the Spec Manager when:
- Starting a new feature or project
- Need to track implementation progress
- Creating pull requests for completed work
- Reviewing specification status
- Planning project phases

## Specification Lifecycle

### 1. Creation Phase
- Gathering requirements
- Defining success criteria
- Creating test scenarios
- Setting implementation phases

### 2. Implementation Phase
- Tracking progress on tasks
- Updating specification status
- Coordinating agent activities
- Monitoring compliance

### 3. Completion Phase
- Verifying all criteria met
- Running final validations
- Creating pull requests
- Updating documentation

## Integration Points

The Spec Manager integrates with:
- `/spec` command for creation
- `spec_tracker.py` hook for progress tracking
- TODO system for task management
- Git for PR creation
- Memory system for documentation

## Commands and Usage

```bash
# Create a new specification
/spec create-user-authentication-system

# Check specification status
/spec status

# Complete a specification
/spec complete auth-spec-001
```

## Best Practices

1. Create detailed specifications before implementation
2. Break work into clear, testable phases
3. Update progress regularly
4. Link commits to specifications
5. Review specifications before marking complete
6. Use specifications for PR descriptions