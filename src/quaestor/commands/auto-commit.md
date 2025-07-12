---
allowed-tools: all
description: Automatically create atomic commits for completed milestone items using conventional commit spec
---

# AUTO COMMIT - Atomic Commits for Completed Items
<!-- META:command:auto:commit -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

## 🎯 PURPOSE: One Commit Per Completed Task

**Automatically create conventional commits when individual milestone items are completed.**

<!-- SECTION:auto-commit:overview:START -->
## Overview

<!-- DATA:workflow-summary:START -->
```yaml
workflow:
  trigger: "Single TODO item marked as completed"
  actions:
    - detect_completion: "TodoWrite status change to 'completed'"
    - analyze_changes: "Find files modified for this task"
    - run_checks: "Ensure code quality"
    - generate_commit: "Create conventional commit"
    - update_tracking: "Update milestone progress"
  
benefits:
  - "Atomic, focused commits"
  - "Clean git history"
  - "Automatic conventional commits"
  - "Real-time progress tracking"
```
<!-- DATA:workflow-summary:END -->
<!-- SECTION:auto-commit:overview:END -->

<!-- SECTION:auto-commit:trigger-detection:START -->
## Trigger Detection

<!-- DATA:completion-triggers:START -->
```yaml
completion_triggers:
  primary_source:
    tool: "TodoWrite"
    event: "Status change to 'completed'"
    data:
      - todo_id: "Unique identifier"
      - content: "Task description"
      - priority: "Task priority"
      - previous_status: "in_progress"
  
  context_detection:
    milestone_link:
      search_in: ".quaestor/milestones/*/tasks.yaml"
      match: "TODO content with milestone task"
    
    affected_files:
      git_status: "Modified files since task started"
      time_window: "Since todo was set to in_progress"
      heuristics:
        - "Files in same directory as task"
        - "Files imported by changed files"
        - "Test files for changed code"
```
<!-- DATA:completion-triggers:END -->
<!-- SECTION:auto-commit:trigger-detection:END -->

<!-- SECTION:auto-commit:commit-generation:START -->
## Conventional Commit Generation

<!-- DATA:commit-spec:START -->
```yaml
conventional_commits:
  specification: "https://www.conventionalcommits.org/en/v1.0.0/"
  
  type_detection:
    from_todo_content:
      patterns:
        - "implement|add|create" → "feat"
        - "fix|resolve|repair" → "fix"
        - "update docs|document" → "docs"
        - "refactor|restructure" → "refactor"
        - "test|testing" → "test"
        - "optimize|performance" → "perf"
        - "update deps|dependency" → "build"
        - "ci/cd|pipeline" → "ci"
        - "formatting|lint" → "style"
        - "cleanup|maintenance" → "chore"
    
    from_file_patterns:
      "test_*.py|*.test.js|*.spec.ts" → "test"
      "*.md|docs/*" → "docs"
      ".github/workflows/*" → "ci"
      "package.json|requirements.txt" → "build"
    
    default: "feat"  # When unclear, assume feature
  
  scope_extraction:
    strategies:
      1_from_milestone:
        example: "Phase 1: Authentication" → "auth"
        
      2_from_directory:
        example: "src/components/Button.jsx" → "components"
        
      3_from_module:
        example: "quaestor.hooks.automation" → "hooks"
        
      4_explicit_in_todo:
        pattern: "[scope:xxx]"
        example: "Add login [scope:auth]" → "auth"
    
    max_length: 20
    optional: true
  
  description_generation:
    source: "TODO content"
    transformations:
      - "Convert to imperative mood"
      - "Remove task metadata"
      - "Lowercase first letter"
      - "Remove trailing punctuation"
      - "Limit to 50 characters"
    
    examples:
      input: "Implement user authentication with OAuth2"
      output: "implement user authentication with OAuth2"
      
      input: "Fix the bug in payment processing"
      output: "fix bug in payment processing"
      
      input: "TODO: Update README with new API endpoints"
      output: "update README with new API endpoints"
```
<!-- DATA:commit-spec:END -->

<!-- DATA:message-template:START -->
```yaml
commit_message_template: |
  {{ type }}{% if scope %}({{ scope }}){% endif %}: {{ description }}
  {% if body %}

  {{ body }}
  {% endif %}
  {% if milestone %}

  Part of: {{ milestone }}
  {% endif %}
  {% if todo_id %}
  Completes: TODO #{{ todo_id }}
  {% endif %}
  {% if breaking %}

  BREAKING CHANGE: {{ breaking }}
  {% endif %}
  {% if issues %}
  {% for issue in issues %}
  Refs: #{{ issue }}
  {% endfor %}
  {% endif %}

example_outputs:
  - |
    feat(auth): implement OAuth2 login flow
    
    - Added OAuth2 provider configuration
    - Implemented callback handling
    - Added token refresh logic
    
    Part of: Phase 1 - User Authentication
    Completes: TODO #42
    
  - |
    fix: resolve null pointer in payment processor
    
    The payment processor was not handling null customer IDs
    properly, causing crashes in production.
    
    Completes: TODO #17
    Refs: #156
```
<!-- DATA:message-template:END -->
<!-- SECTION:auto-commit:commit-generation:END -->

<!-- SECTION:auto-commit:quality-gates:START -->
## Quality Gates

<!-- DATA:pre-commit-checks:START -->
```yaml
quality_checks:
  mandatory:
    1_syntax_check:
      description: "Ensure code is syntactically valid"
      commands:
        python: "python -m py_compile"
        javascript: "node --check"
        typescript: "tsc --noEmit"
    
    2_linting:
      description: "Code meets style standards"
      commands:
        python: "ruff check"
        javascript: "eslint"
        rust: "cargo clippy"
    
    3_tests:
      description: "Related tests pass"
      strategy: "Run tests in affected modules only"
      fast_mode: true
  
  optional:
    formatting:
      auto_fix: true
      commands:
        python: "ruff format"
        javascript: "prettier --write"
  
  on_failure:
    action: "Abort commit and show errors"
    suggestion: "Run /quaestor:check to fix issues"
```
<!-- DATA:pre-commit-checks:END -->
<!-- SECTION:auto-commit:quality-gates:END -->

<!-- SECTION:auto-commit:file-staging:START -->
## Intelligent File Staging

<!-- DATA:staging-logic:START -->
```yaml
file_staging:
  automatic_detection:
    1_direct_changes:
      description: "Files modified for this TODO"
      detection: "git diff --name-only"
      
    2_test_files:
      description: "Test files for changed code"
      patterns:
        - "test_{{ module }}.py"
        - "{{ module }}.test.js"
        - "{{ module }}.spec.ts"
    
    3_documentation:
      description: "Related documentation"
      patterns:
        - "README.md (if changed)"
        - "docs/* (if related)"
        - "*.md (in same directory)"
    
    4_configuration:
      description: "Config files if needed"
      patterns:
        - "package.json (if deps added)"
        - "requirements.txt (if deps added)"
        - "*.config.* (if modified)"
  
  exclusions:
    never_stage:
      - "*.log"
      - "*.tmp"
      - ".env*"
      - "*.secret"
      - "__pycache__"
      - "node_modules"
    
    ask_before_staging:
      - "*.generated.*"
      - "package-lock.json"
      - "poetry.lock"
  
  validation:
    ensure_related: "Only stage files related to TODO"
    prevent_mixing: "Don't mix unrelated changes"
```
<!-- DATA:staging-logic:END -->
<!-- SECTION:auto-commit:file-staging:END -->

<!-- SECTION:auto-commit:milestone-integration:START -->
## Milestone Integration

<!-- DATA:milestone-tracking:START -->
```yaml
milestone_tracking:
  on_commit:
    1_find_milestone:
      search: ".quaestor/milestones/*/tasks.yaml"
      match: "TODO content in task list"
    
    2_update_task:
      add_fields:
        completed_at: "{{ timestamp }}"
        commit_sha: "{{ git_commit_sha }}"
        status: "completed"
    
    3_update_progress:
      recalculate: "completed / total * 100"
      update_memory: true
    
    4_check_milestone_completion:
      if_all_tasks_done:
        notification: "🎉 Milestone complete! Ready for PR"
        next_action: "Suggest running /quaestor:milestone-pr"
  
  progress_tracking:
    memory_update:
      location: "## Current Milestone"
      format: |
        - ✅ {{ task_description }} ({{ commit_sha_short }})
```
<!-- DATA:milestone-tracking:END -->
<!-- SECTION:auto-commit:milestone-integration:END -->

<!-- SECTION:auto-commit:hook-configuration:START -->
## Hook Configuration

<!-- DATA:hook-setup:START -->
```yaml
hook_integration:
  trigger_hook:
    location: ".claude/settings.json"
    configuration: |
      {
        "hooks": {
          "PostToolUse": [
            {
              "matcher": "TodoWrite",
              "hooks": [
                {
                  "type": "command",
                  "command": "quaestor auto-commit --check"
                }
              ]
            }
          ]
        }
      }
  
  auto_commit_check:
    description: "Check if any TODOs were completed"
    logic:
      - "Parse TodoWrite output"
      - "Find status: 'completed' items"
      - "Trigger auto-commit for each"
```
<!-- DATA:hook-setup:END -->
<!-- SECTION:auto-commit:hook-configuration:END -->

<!-- SECTION:auto-commit:usage:START -->
## Usage

<!-- EXAMPLE:automatic:START -->
```yaml
# Automatic trigger (recommended)
- Complete a TODO item via TodoWrite
- Auto-commit runs automatically
- Creates conventional commit
- Updates milestone progress
```
<!-- EXAMPLE:automatic:END -->

<!-- EXAMPLE:manual:START -->
```bash
# Manual execution
/quaestor:auto-commit

# Check what would be committed
/quaestor:auto-commit --dry-run

# Commit specific TODO
/quaestor:auto-commit --todo-id 42

# Skip quality checks (not recommended)
/quaestor:auto-commit --skip-checks
```
<!-- EXAMPLE:manual:END -->
<!-- SECTION:auto-commit:usage:END -->

<!-- SECTION:auto-commit:configuration:START -->
## Configuration

<!-- DATA:settings:START -->
```yaml
auto_commit_settings:
  enabled: true
  
  behavior:
    require_all_checks: true
    auto_push: false
    sign_commits: true
    
  commit_style:
    conventional: true
    include_todo_id: true
    include_milestone: true
    
  notifications:
    on_success: "✅ Committed: {{ description }}"
    on_failure: "❌ Commit failed: {{ error }}"
```
<!-- DATA:settings:END -->
<!-- SECTION:auto-commit:configuration:END -->

**One task completed = One atomic commit. Clean history, automatic tracking!**