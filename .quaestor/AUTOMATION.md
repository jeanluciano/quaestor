# Hook Behaviors and Automation

## Claude Code Hooks

This project uses Claude Code hooks for automated workflows:

### Available Hooks
- **pre-edit**: Validate before file changes
- **post-edit**: Process after file changes  
- **pre-command**: Setup before command execution
- **post-command**: Cleanup after command execution

### Hook Configuration
```json
{
  "hooks": {
    "pre-edit": ".quaestor/hooks/validation/research_enforcer.py",
    "post-edit": ".quaestor/hooks/workflow/research_tracker.py"
  }
}
```

## Automated Workflows

### Code Quality Automation
```bash
# Pre-edit validation
ruff check .

# Post-edit formatting
ruff format .
```

### Project Management
- **Auto-commit**: Atomic commits with descriptive messages
- **Branch Management**: Feature branches with PR workflow
- **PR Creation**: Auto-create PRs for completed milestones
- **Milestone Tracking**: Track progress and auto-update documentation

### Development Assistance
- **Context Management**: Maintain .quaestor files for AI context
- **Rule Enforcement**: Graduated enforcement with learning
- **Template Processing**: Process templates with project data
- **Documentation Updates**: Auto-update based on code changes

## Hook Behaviors

### Timeout Protection
- **Default Timeout**: 60 seconds
- **Retry Logic**: 3 attempts with exponential backoff
- **Fallback Actions**: Graceful degradation on failures

### Error Handling
```python
try:
    result = hook.run(input_data)
except TimeoutError:
    return fallback_result()
except Exception as e:
    log_error(e)
    return safe_default()
```

### Logging and Monitoring
- **Hook Execution**: Structured JSON logging
- **Performance Metrics**: Track execution time and success rate
- **Debug Information**: Enable with DEBUG=1 environment variable

## Configuration Examples

### Basic Setup
```json
{
  "hooks": {
    "pre-edit": "./scripts/validate.py",
    "post-edit": "./scripts/format.py"
  },
  "timeout": 60,
  "retry_attempts": 3
}
```

### Advanced Configuration
```json
{
  "hooks": {
    "pre-edit": {
      "script": "./scripts/advanced-validate.py",
      "timeout": 30,
      "required": true,
      "environment": {
        "VALIDATION_LEVEL": "strict"
      }
    }
  }
}
```

## Best Practices

### Hook Performance
- Keep hooks fast (<5 seconds typical)
- Use async operations where possible
- Cache expensive operations
- Provide meaningful feedback

### Error Recovery
- Graceful degradation on failures
- Clear error messages
- Automatic retry for transient failures
- Manual override capabilities

### Security Considerations
- Validate all inputs
- Sanitize file paths
- Limit hook execution permissions
- Log security-relevant events