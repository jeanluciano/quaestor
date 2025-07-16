# AUTOMATION.md - Hook Behaviors and Automation Details

<!-- QUAESTOR:version:1.0 -->

## Overview

This document describes the automated workflows, hooks, and behaviors that streamline development in {{ project_name }}. These automations ensure consistency, quality, and efficiency throughout the development process.

## Hook System Architecture

<!-- DATA:hook-architecture:START -->
```yaml
hook_system:
  categories:
    enforcement:
      purpose: "Ensure compliance with project rules"
      priority: high
      can_block: true
    
    automation:
      purpose: "Streamline repetitive tasks"
      priority: medium
      can_block: false
    
    intelligence:
      purpose: "Provide smart assistance and suggestions"
      priority: low
      can_block: false
  
  execution_order:
    - enforcement
    - automation
    - intelligence
```
<!-- DATA:hook-architecture:END -->

## Enforcement Hooks

### Pre-Implementation Validation

<!-- HOOK:pre-implementation:START -->
**Hook:** `pre-implementation-declaration.py`
**Triggers:** Before any Write/Edit operation
**Purpose:** Ensure Research → Plan → Implement workflow

```yaml
enforcement:
  research_check:
    condition: "First code modification"
    action: "Verify research phase completed"
    failure: "Block with reminder"
  
  plan_check:
    condition: "Complex implementation"
    action: "Request implementation plan"
    failure: "Guide to planning phase"
```

**Override:** Use `--skip-validation` flag (requires justification)
<!-- HOOK:pre-implementation:END -->

### Quality Enforcement

<!-- HOOK:quality-enforcement:START -->
**Hook:** `comprehensive-compliance-check.py`
**Triggers:** After Write/Edit operations
**Purpose:** Enforce code quality standards

```yaml
quality_checks:
  syntax_validation:
    tools: [{{ lint_command }}]
    blocking: true
  
  type_checking:
    tools: [{{ type_check_command if type_check_command else "mypy" }}]
    blocking: {{ "true" if type_checking else "false" }}
  
  test_execution:
    tools: [{{ test_command }}]
    blocking: on_critical_files
```
<!-- HOOK:quality-enforcement:END -->

## Automation Hooks

### Auto-Commit System

<!-- HOOK:auto-commit:START -->
**Hook:** `auto-commit-trigger.py`
**Triggers:** When TODO items marked complete
**Purpose:** Create atomic commits for completed work

```yaml
auto_commit:
  triggers:
    - todo_completion: "TodoWrite status → completed"
    - milestone_progress: "Subtask marked done"
  
  behavior:
    commit_message:
      format: "{{ commit_prefix }}: {task_description}"
      include:
        - changed_files
        - related_issue
        - milestone_reference
    
    validation:
      - all_tests_pass
      - no_lint_errors
      - files_saved
```

**Example commit:**
```
feat: implement user authentication

- Added login/logout endpoints
- Integrated JWT tokens
- Added session management

Related: #123
Milestone: Phase 1 - Core Features (2/5 complete)
```
<!-- HOOK:auto-commit:END -->

### Memory Synchronization

<!-- HOOK:memory-sync:START -->
**Hook:** `update-memory-enhanced.py`
**Triggers:** TODO state changes, milestone updates
**Purpose:** Keep MEMORY.md synchronized with progress

```yaml
memory_sync:
  todo_tracking:
    on_create: "Add to current_tasks"
    on_progress: "Update status"
    on_complete: "Move to completed"
  
  milestone_tracking:
    on_progress: "Update percentage"
    on_complete: "Create summary"
    on_blocked: "Document blockers"
```
<!-- HOOK:memory-sync:END -->

### Context Refresh

<!-- HOOK:context-refresh:START -->
**Hook:** `refresh-context.py`
**Triggers:** Long-running sessions, context switches
**Purpose:** Maintain accurate project understanding

```yaml
context_refresh:
  triggers:
    - session_duration: "> 30 minutes"
    - file_changes: "> 10 files"
    - context_switch: "New feature area"
  
  actions:
    - reload_architecture
    - scan_recent_changes
    - update_dependencies
    - refresh_test_status
```
<!-- HOOK:context-refresh:END -->

## Intelligence Hooks

### Smart Suggestions

<!-- HOOK:smart-suggestions:START -->
**Hook:** `intelligent-suggestions.py`
**Triggers:** Pattern detection during development
**Purpose:** Provide contextual assistance

```yaml
smart_patterns:
  code_duplication:
    detection: "Similar code blocks"
    suggestion: "Extract to shared function"
  
  performance_issue:
    detection: "N+1 queries, nested loops"
    suggestion: "Optimization approach"
  
  security_risk:
    detection: "Unsafe patterns"
    suggestion: "Secure alternative"
```
<!-- HOOK:smart-suggestions:END -->

### Test Generation

<!-- HOOK:test-generation:START -->
**Hook:** `test-suggestion.py`
**Triggers:** New functions without tests
**Purpose:** Suggest test cases

```yaml
test_suggestions:
  trigger_conditions:
    - new_function: "No corresponding test"
    - modified_logic: "Test coverage decreased"
  
  suggestions:
    - happy_path_test
    - edge_case_test
    - error_handling_test
```
<!-- HOOK:test-generation:END -->

## Hook Configuration

### Enabling/Disabling Hooks

<!-- CONFIG:hooks:START -->
**Global configuration:** `.claude/settings.json`
```json
{
  "hooks": {
    "enforcement": {
      "enabled": true,
      "strict_mode": {{ "true" if strict_mode else "false" }}
    },
    "automation": {
      "enabled": true,
      "auto_commit": true,
      "memory_sync": true
    },
    "intelligence": {
      "enabled": true,
      "suggestion_level": "moderate"
    }
  }
}
```

**Per-project override:** `.quaestor/hook-config.yaml`
```yaml
hooks:
  disable:
    - test-suggestion  # Temporarily disabled
  
  customize:
    auto-commit:
      prefix: "custom"
      include_stats: false
```
<!-- CONFIG:hooks:END -->

### Hook Customization

<!-- CUSTOMIZE:hooks:START -->
**Creating custom hooks:**

1. **Add hook script** to `.quaestor/hooks/`
2. **Register in settings.json**:
```json
{
  "customHooks": {
    "my-custom-hook": {
      "script": ".quaestor/hooks/my-hook.py",
      "triggers": ["Write", "Edit"],
      "enabled": true
    }
  }
}
```

3. **Hook template:**
```python
#!/usr/bin/env python3
"""Custom hook for {{ project_name }}"""

import sys
import json

def main():
    # Read context from stdin
    context = json.load(sys.stdin)
    
    # Your hook logic here
    if should_block(context):
        print("ERROR: Validation failed")
        sys.exit(1)
    
    print("Hook passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
```
<!-- CUSTOMIZE:hooks:END -->

## Automation Workflows

### Continuous Integration

<!-- WORKFLOW:ci:START -->
```yaml
ci_workflow:
  on_push:
    - syntax_check
    - type_check
    - unit_tests
    - integration_tests
  
  on_pull_request:
    - full_test_suite
    - security_scan
    - performance_tests
    - documentation_check
  
  on_merge:
    - deploy_staging
    - smoke_tests
    - notification
```
<!-- WORKFLOW:ci:END -->

### Release Automation

<!-- WORKFLOW:release:START -->
```yaml
release_workflow:
  prepare:
    - version_bump
    - changelog_generation
    - dependency_update
  
  validate:
    - full_test_suite
    - security_audit
    - performance_baseline
  
  execute:
    - tag_creation
    - package_build
    - deployment
    - announcement
```
<!-- WORKFLOW:release:END -->

## Troubleshooting Hooks

### Common Issues

<!-- TROUBLESHOOT:common:START -->
**Hook not triggering:**
- Check `.claude/settings.json` configuration
- Verify hook file permissions
- Check hook script syntax
- Review trigger conditions

**Hook blocking incorrectly:**
- Use `--skip-validation` for emergency bypass
- Check hook logic for false positives
- Review recent changes to hook scripts
<!-- TROUBLESHOOT:common:END -->

### Debug Mode

<!-- TROUBLESHOOT:debug:START -->
**Enable hook debugging:**
```json
{
  "hooks": {
    "debug": true,
    "logLevel": "verbose"
  }
}
```

**View hook execution:**
```bash
# Check hook logs
tail -f ~/.claude/logs/hooks.log

# Test hook manually
python .quaestor/hooks/hook-name.py < test-context.json
```
<!-- TROUBLESHOOT:debug:END -->

## Best Practices

### Hook Development

<!-- PRACTICES:development:START -->
1. **Fast Execution**: Hooks should complete in < 1 second
2. **Clear Messages**: Provide actionable feedback
3. **Graceful Failure**: Don't block on non-critical issues
4. **Idempotent**: Running twice should have same result
5. **Well-Tested**: Include tests for hook logic
<!-- PRACTICES:development:END -->

### Hook Maintenance

<!-- PRACTICES:maintenance:START -->
- **Regular Review**: Audit hooks monthly
- **Performance Monitoring**: Track execution time
- **User Feedback**: Adjust based on team input
- **Version Control**: Track hook changes
- **Documentation**: Keep hook docs updated
<!-- PRACTICES:maintenance:END -->

Remember: Automation should accelerate development, not hinder it. If a hook becomes a bottleneck, fix it or remove it.