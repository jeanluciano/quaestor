---
allowed-tools: all
description: Create atomic commits and PRs for completed milestone items
---

# MILESTONE COMMIT - Automated Progress Tracking
<!-- META:command:milestone:commit -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

## 🎯 PURPOSE: Atomic Commits for Completed Work

**Automatically commit completed TODOs and create PRs when milestones are done.**

<!-- SECTION:milestone:overview:START -->
## Overview

<!-- DATA:workflow-summary:START -->
```yaml
workflow:
  trigger: "Completed TODO items or MEMORY.md update"
  actions:
    - scan_todos: "Find completed items"
    - validate_code: "Run quality checks"
    - create_commits: "Atomic commit per item"
    - update_memory: "Sync progress tracking"
    - check_milestone: "Create PR if complete"
  
benefits:
  - "Clean git history"
  - "Automatic quality gates"
  - "Progress tracking"
  - "Reduced manual work"
```
<!-- DATA:workflow-summary:END -->
<!-- SECTION:milestone:overview:END -->

<!-- SECTION:milestone:pre-flight:START -->
## Pre-Flight Checks

<!-- DATA:pre-flight-validation:START -->
```yaml
pre_flight_checks:
  1_git_status:
    command: "git status --porcelain"
    ensure: "Working directory has changes"
    abort_if: "No changes to commit"
  
  2_branch_check:
    command: "git branch --show-current"
    ensure: "Not on main/master branch"
    action: "Create feature branch if needed"
  
  3_quality_validation:
    command: "/quaestor:check"
    requirement: "ALL checks must pass"
    abort_if: "Any quality issues found"
  
  4_todo_scan:
    action: "Review TodoWrite outputs"
    find: "Items marked as 'completed'"
    abort_if: "No completed items found"
```
<!-- DATA:pre-flight-validation:END -->
<!-- SECTION:milestone:pre-flight:END -->

<!-- SECTION:milestone:todo-scanning:START -->
## TODO Scanning Logic

<!-- DATA:todo-detection:START -->
```yaml
todo_scanning:
  sources:
    - location: "In-memory TODO list"
      via: "TodoWrite tool state"
    - location: "MEMORY.md milestones"
      pattern: "✅ Completed tasks"
    - location: "Code comments"
      pattern: "TODO: [DONE]"
  
  completed_indicators:
    - status: "completed"
    - prefix: "✅"
    - suffix: "[DONE]"
    - strikethrough: "~~task~~"
  
  extraction:
    - todo_id: "Unique identifier"
    - description: "Task description"
    - context: "Related code/feature"
    - priority: "high/medium/low"
```
<!-- DATA:todo-detection:END -->
<!-- SECTION:milestone:todo-scanning:END -->

<!-- SECTION:milestone:commit-strategy:START -->
## Commit Strategy

<!-- DATA:atomic-commits:START -->
```yaml
commit_rules:
  conventional_commits_spec:
    version: "1.0.0"
    format: |
      <type>[optional scope]: <description>
      
      [optional body]
      
      [optional footer(s)]
    
  one_commit_per_todo:
    rationale: "Clean, searchable history"
    format: |
      <type>(<scope>): <description>
      
      - Completed TODO #<todo-id>
      - <detailed-changes>
      
      BREAKING CHANGE: <breaking changes if any>
      Closes: #<issue-number>
  
  commit_types:
    # From Conventional Commits spec
    feat: "new feature for the user"
    fix: "bug fix for the user"
    docs: "documentation only changes"
    style: "formatting, missing semi colons, etc"
    refactor: "refactoring production code"
    test: "adding missing tests, refactoring tests"
    chore: "updating grunt tasks etc; no production code change"
    perf: "performance improvements"
    ci: "changes to CI configuration files and scripts"
    build: "changes affecting build system or dependencies"
    revert: "reverts a previous commit"
  
  type_mapping:
    feature_todo: "feat"
    bugfix_todo: "fix"
    refactor_todo: "refactor"
    docs_todo: "docs"
    test_todo: "test"
    chore_todo: "chore"
    performance_todo: "perf"
  
  scope_detection:
    from_file_path: "Extract module/component"
    from_todo_context: "Use feature area"
    examples:
      - "feat(auth): add OAuth2 support"
      - "fix(api): handle null responses"
      - "docs(readme): update installation steps"
    default: null  # Scope is optional
  
  description_rules:
    - "use the imperative, present tense"
    - "don't capitalize first letter"
    - "no dot (.) at the end"
    - "limit to 50 characters"
    examples:
      good:
        - "add OAuth2 authentication"
        - "fix null pointer in API handler"
        - "update installation documentation"
      bad:
        - "Added OAuth2 authentication"  # Past tense
        - "Fix null pointer."  # Dot at end
        - "ADDING OAUTH"  # All caps
  
  message_generation:
    header: "<type>(<scope>): <short description>"
    body:
      - "Longer explanation if needed"
      - "Bullet points for multiple changes"
      - "Reference to TODO or issue"
    footer:
      - "BREAKING CHANGE: <description>"
      - "Closes: #<issue>"
      - "Refs: #<related-issues>"
```
<!-- DATA:atomic-commits:END -->

<!-- WORKFLOW:commit-process:START -->
```yaml
commit_workflow:
  for_each_completed_todo:
    1_analyze_todo:
      extract:
        - type: "From TODO category or content"
        - scope: "From affected files/modules"
        - description: "From TODO text (imperative mood)"
      
    2_stage_files:
      action: "git add <related-files>"
      smart_detection: "Find files modified for this TODO"
    
    3_generate_message:
      conventional_format: |
        {{type}}{% if scope %}({{scope}}){% endif %}: {{description}}
        
        {% if body %}
        {{body}}
        {% endif %}
        
        {% if breaking_change %}
        BREAKING CHANGE: {{breaking_change}}
        {% endif %}
        {% if closes_issue %}
        Closes: #{{issue_number}}
        {% endif %}
      
      example_outputs:
        - "feat(auth): add two-factor authentication"
        - "fix: resolve memory leak in image processing"
        - "docs(api): update endpoint documentation"
        - "refactor(db): extract repository pattern"
    
    4_validate_message:
      checks:
        - "Type is valid (feat/fix/docs/etc)"
        - "Description is imperative mood"
        - "No capital first letter"
        - "No period at end"
        - "Under 50 chars for header"
    
    5_create_commit:
      command: "git commit -m \"{{message}}\""
      sign: true
      verify: true
    
    6_update_tracking:
      memory_md: "Mark as committed"
      todo_list: "Add commit SHA"
```
<!-- WORKFLOW:commit-process:END -->
<!-- SECTION:milestone:commit-strategy:END -->

<!-- SECTION:milestone:memory-updates:START -->
## Memory Synchronization

<!-- DATA:memory-sync:START -->
```yaml
memory_updates:
  after_each_commit:
    - update_task_status: "Add commit reference"
    - update_progress: "Recalculate percentage"
    - add_completion_date: "Timestamp the completion"
  
  milestone_tracking:
    check_completion:
      all_todos_done: "All items in milestone completed"
      quality_passed: "All checks green"
      ready_for_pr: true
    
    update_section:
      location: "## Current Milestone"
      add:
        - "✅ {{todo_description}} - {{commit_sha}}"
        - "Completed: {{timestamp}}"
```
<!-- DATA:memory-sync:END -->
<!-- SECTION:milestone:memory-updates:END -->

<!-- SECTION:milestone:pr-creation:START -->
## Pull Request Creation

<!-- DATA:pr-automation:START -->
```yaml
pr_creation:
  trigger: "All TODOs in milestone completed"
  
  pr_title_template: |
    {{milestone_name}}: {{summary}}
  
  pr_body_template: |
    ## 🎯 Milestone Complete: {{milestone_name}}
    
    ### ✅ Completed Items
    {{#each completed_todos}}
    - {{description}} ({{commit_link}})
    {{/each}}
    
    ### 📊 Summary
    - Total items: {{total_count}}
    - Commits: {{commit_count}}
    - Files changed: {{files_changed}}
    
    ### 🔍 Quality Checks
    - ✅ All tests passing
    - ✅ Linting clean
    - ✅ Coverage maintained
    
    ### 🚀 What's Next
    {{next_milestone_preview}}
    
    ---
    🤖 Generated by milestone-commit command
  
  gh_command: |
    gh pr create \
      --title "{{title}}" \
      --body "{{body}}" \
      --label "milestone-complete" \
      --assign @me
```
<!-- DATA:pr-automation:END -->
<!-- SECTION:milestone:pr-creation:END -->

<!-- SECTION:milestone:hooks:START -->
## Hook Integration

<!-- DATA:hook-triggers:START -->
```yaml
incoming_hooks:
  from_memory_update:
    trigger: "MEMORY.md modified"
    condition: "Contains completed TODOs"
    action: "Run milestone-commit"
  
  from_todo_complete:
    trigger: "TodoWrite status change"
    condition: "Status = completed"
    action: "Queue for commit"
  
  from_task_command:
    trigger: "Task marked done"
    condition: "All checks pass"
    action: "Auto-commit if enabled"

outgoing_hooks:
  after_commit:
    notify: "Update MEMORY.md"
    trigger: "Progress recalculation"
  
  after_pr:
    notify: "Team notification"
    trigger: "Review request"
```
<!-- DATA:hook-triggers:END -->
<!-- SECTION:milestone:hooks:END -->

<!-- SECTION:milestone:configuration:START -->
## Configuration Options

<!-- DATA:config-options:START -->
```yaml
configuration:
  auto_commit:
    enabled: true
    require_confirmation: false
    batch_size: 1  # One commit per TODO
  
  quality_gates:
    enforce_checks: true
    allow_warnings: false
    required_coverage: 90
  
  pr_automation:
    auto_create: true
    draft_if_incomplete: false
    assign_reviewers: true
  
  commit_signing:
    gpg_sign: true
    verified_commits_only: true
```
<!-- DATA:config-options:END -->
<!-- SECTION:milestone:configuration:END -->

<!-- SECTION:milestone:error-handling:START -->
## Error Handling

<!-- DATA:error-scenarios:START -->
```yaml
error_handling:
  merge_conflicts:
    action: "Abort and notify user"
    message: "Manual intervention required"
  
  check_failures:
    action: "Run check command to fix"
    retry: "After fixes complete"
  
  partial_completion:
    action: "Commit completed items only"
    flag: "Incomplete milestone"
  
  git_errors:
    action: "Rollback and report"
    preserve: "Work in progress"
```
<!-- DATA:error-scenarios:END -->
<!-- SECTION:milestone:error-handling:END -->

<!-- SECTION:milestone:usage:START -->
## Usage Examples

<!-- EXAMPLE:manual-trigger:START -->
```bash
# Manual trigger after completing TODOs
/quaestor:milestone-commit

# With specific milestone
/quaestor:milestone-commit --milestone "Phase 1"

# Dry run to see what would be committed
/quaestor:milestone-commit --dry-run
```
<!-- EXAMPLE:manual-trigger:END -->

<!-- EXAMPLE:automatic-trigger:START -->
```yaml
# Automatically triggered by:
- Completing a TODO via TodoWrite
- Updating MEMORY.md with completions
- Task command marking work done
- Check command passing after changes
```
<!-- EXAMPLE:automatic-trigger:END -->
<!-- SECTION:milestone:usage:END -->

<!-- SECTION:milestone:best-practices:START -->
## Best Practices

<!-- DATA:best-practices:START -->
```yaml
best_practices:
  todo_management:
    - "Keep TODOs focused and atomic"
    - "Include clear descriptions"
    - "Link to issues/tickets"
    - "Group by milestone"
  
  commit_hygiene:
    - "One logical change per commit"
    - "Descriptive commit messages"
    - "Reference TODO IDs"
    - "Include why, not just what"
  
  milestone_planning:
    - "5-10 TODOs per milestone"
    - "Clear completion criteria"
    - "Logical feature boundaries"
    - "Regular milestone reviews"
```
<!-- DATA:best-practices:END -->
<!-- SECTION:milestone:best-practices:END -->

**This command ensures quality, tracking, and clean git history automatically!**