# Memory Tracking Hook

The Memory Tracking hook automatically updates MEMORY.md based on development activities and TODO completions.

## Purpose

This hook:
- Syncs TODO completions with MEMORY.md
- Tracks implementation decisions
- Records architectural changes
- Maintains project history
- Updates progress indicators

## Trigger Points

The memory tracker activates on:
- TODO status changes (especially completions)
- Specification phase transitions
- Major code changes
- Architecture decisions
- Pattern implementations

## Memory Structure

### Automatic Updates
```markdown
## Recent Progress
- ✅ Implemented user authentication (TODO-123)
- ✅ Added database migration system (TODO-124)
- 🚧 Working on API rate limiting (TODO-125)

## Implementation Decisions
- Chose JWT for authentication (2024-01-15)
- Implemented repository pattern for data access
- Added caching layer with Redis
```

### Decision Recording
The hook captures:
- What was implemented
- Why specific approaches were chosen
- Trade-offs considered
- Future implications

## Integration

### With TODO System
- Monitors TodoWrite tool usage
- Extracts completion context
- Groups related completions
- Creates progress summaries

### With Specifications
- Links implementations to specs
- Tracks spec completion
- Records deviations from plan
- Documents lessons learned

## Configuration

The hook reads from:
- `.quaestor/MEMORY.md` template
- Current TODO state
- Git commit history
- Specification status

## Best Practices

1. Write descriptive TODO items
2. Include context in completions
3. Review memory updates regularly
4. Keep architectural decisions current
5. Link memory items to specifications

## Customization

You can customize memory tracking by:
- Modifying the MEMORY.md template
- Adjusting update frequency
- Adding custom sections
- Integrating with external tools