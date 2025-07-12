# MILESTONE TRACKING RULES

## 🎯 MANDATORY MILESTONE TRACKING

### Before Starting ANY Work

```yaml
pre_work_checklist:
  milestone_awareness:
    - action: "Check .quaestor/milestones/ for active phase"
    - action: "Read phase README.md for context"
    - action: "Find tasks.yaml with status: in_progress"
    - action: "Identify specific subtask to work on"
    - action: "Review acceptance criteria"
    
  announce_intent:
    - action: "State which milestone/task/subtask you're working on"
    - format: "Working on: Phase X > Task Y > Subtask Z"
    - example: "Working on: Phase 1 > vector_store > Create VectorStore abstraction"
```

### During Work

```yaml
during_work_tracking:
  update_status:
    - when: "Starting a new subtask"
      action: "Update task status to 'in_progress' if not already"
    
  track_progress:
    - what: "Files created or modified"
    - what: "Tests added or updated"
    - what: "Key decisions made"
    - what: "Deviations from plan"
```

### After Completing Work

```yaml
post_work_updates:
  required_updates:
    1_update_milestone:
      - file: ".quaestor/milestones/*/tasks.yaml"
      - actions:
        - "Mark completed subtasks with '# COMPLETED'"
        - "Update progress percentage"
        - "Add timestamped notes"
        - "Update status if all subtasks done"
      
    2_update_memory:
      - file: ".quaestor/MEMORY.md"
      - section: "## Progress Log"
      - format: |
          ### YYYY-MM-DD
          - **COMPLETED**: [Task Name] (Phase X - task_id, subtask Y/Z)
            - Implementation details...
            - Files created: [list files]
            - Tests added: [count and list]
            - Next: [what's next]
    
    3_update_workflow_state:
      - file: ".quaestor/.workflow_state"
      - update: "implementation_completed timestamp"
```

### Enforcement Hooks

```yaml
hook_reminders:
  pre_implementation:
    - message: "Check active milestone before implementing"
    - severity: "warning"
    
  post_implementation:
    - message: "Update milestone tracking after changes"
    - severity: "error if skipped"
    
  pre_commit:
    - message: "Verify milestone updates before commit"
    - checklist:
      - "[ ] Updated tasks.yaml"
      - "[ ] Added MEMORY.md entry"
      - "[ ] Marked completed items"
```

## 🚨 VIOLATIONS AND CORRECTIONS

```yaml
milestone_violations:
  forgot_to_update:
    - detection: "Files created but no milestone update"
    - correction: "Immediately update tasks.yaml and MEMORY.md"
    
  wrong_task_worked:
    - detection: "Worked on task not marked in_progress"
    - correction: "Update correct task status and document why"
    
  no_progress_log:
    - detection: "Completed work without MEMORY.md entry"
    - correction: "Add detailed progress log retroactively"
```

## 📋 QUICK REFERENCE

### Check Current Status
```bash
# Find active tasks
grep -r "status: in_progress" .quaestor/milestones/

# Check recent progress
tail -30 .quaestor/MEMORY.md
```

### Update Commands
```bash
# Example: Mark subtask complete in tasks.yaml
# Change: - "Create VectorStore abstraction (ABC)"
# To:     - "Create VectorStore abstraction (ABC)" # COMPLETED

# Example: Update progress
# Change: progress: "0%"
# To:     progress: "25%"
```

### Progress Log Template
```markdown
### 2025-01-12
- **COMPLETED**: VectorStore abstraction interface (Phase 1 - vector_store task, subtask 1/4)
  - Implemented abstract base class with async methods
  - Created data models: Document, SearchResult, QueryFilter
  - Added 33 tests with 100% coverage
  - Files created:
    - `/src/vector_store/abstract/base.py`
    - `/src/vector_store/models/models.py`
    - `/tests/vector_store/test_models.py`
  - Next: Implement InMemoryVectorDB with Redis
```

## 🔄 INTEGRATION WITH HOOKS

The milestone tracking integrates with these hooks:
- `track-research.py` - Updates research phase in workflow
- `track-implementation.py` - Marks implementation start
- `update-memory-enhanced.py` - Automates milestone updates
- `check-milestone.py` - Verifies tracking compliance

Remember: **NO WORK WITHOUT TRACKING!**