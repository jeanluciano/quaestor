# Command Loading with Project Overrides

## How Claude Code Loads Commands

When you use a command like `/task`, Claude Code follows this hierarchy:

### 1. Project-Local Commands (Personal Mode)
```
project/.claude/commands/task.md  ← Highest priority
```

### 2. Project Overrides (Both Modes)  
```
project/.quaestor/commands/task.md  ← Project-specific override
```

### 3. Command Configuration (Both Modes)
```
project/.quaestor/command-config.yaml  ← Modifies base command
```

### 4. Global Commands
```
~/.claude/commands/task.md  ← Base command
```

## Command Configuration Example

The `command-config.yaml` file allows you to modify command behavior without rewriting the entire command:

```yaml
commands:
  task:
    enforcement: strict  # Make all rules mandatory
    parameters:
      minimum_test_coverage: 90  # Increase from default 80%
      max_function_lines: 30    # Stricter than default 50
    custom_rules:
      - "All database queries must use prepared statements"
      - "API endpoints require rate limiting"
      - "Use dependency injection for all services"
  
  check:
    auto_fix: true
    include_checks: [lint, test, type, security]
    
  milestone:
    require_pr: true
    auto_squash: true
```

## Creating Command Overrides

### Option 1: Full Override
Create a complete replacement for a command:
```bash
quaestor configure --command task --create-override
```

Then edit `.quaestor/commands/task.md` with your custom implementation.

### Option 2: Configuration-Based
Modify command behavior through configuration:
```bash
quaestor configure --init
```

Then edit `.quaestor/command-config.yaml` to adjust parameters.

## Example: Project-Specific Task Command

For a security-focused project, you might override the task command:

```markdown
# TASK COMMAND - SECURITY PROJECT OVERRIDE

## MANDATORY SECURITY CHECKS

Before ANY implementation:
1. Threat model the feature
2. Review OWASP guidelines
3. Check security test coverage

## IMPLEMENTATION REQUIREMENTS

- [ ] Input validation on all user data
- [ ] Output encoding for all responses  
- [ ] Authentication checks on all endpoints
- [ ] Authorization verified with tests
- [ ] Audit logging for sensitive operations
- [ ] Rate limiting implemented
- [ ] Security headers configured

## COMPLETION CRITERIA

Before marking complete:
```bash
npm run security:scan
npm run dependency:check
npm run penetration:test
```
```

This ensures your team follows security best practices automatically!