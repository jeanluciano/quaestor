# TASK COMMAND MILESTONE INTEGRATION

## Addition to task.md after line 27

```markdown
## 📋 MILESTONE AWARENESS PHASE (MANDATORY)

**BEFORE STARTING ANY WORK:**

1. **Check Active Milestones:**
   - Read all .quaestor/milestones/*/README.md files
   - Find tasks.yaml files with status: "in_progress" or "active"
   - Identify which phase/task/subtask relates to this work

2. **Declare Your Work Context:**
   - Announce: "Working on: [Phase] > [Task] > [Subtask]"
   - Example: "Working on: Phase 1 > vector_store > Create VectorStore abstraction"
   - If no match found, declare: "New work not in existing milestones"

3. **Update Task Status:**
   - If starting a new task, update status to "in_progress"
   - If continuing existing work, confirm current status
   - Document any changes to the original plan

**MILESTONE DECLARATION TEMPLATE:**
```
🎯 MILESTONE CONTEXT:
- Phase: [Phase Name]
- Task ID: [task_id]
- Task Name: [Task Name]
- Subtask: [Current Subtask] ([X/Y] completed)
- Progress: [X]%
- File: .quaestor/milestones/[phase]/tasks.yaml
```

**IF NO MILESTONE MATCH:**
Ask the user if this work should:
1. Be added to existing milestone
2. Create new task in current phase
3. Proceed as standalone work
```

## Addition to the end of task.md (after completion)

```markdown
## 📊 POST-COMPLETION MILESTONE UPDATE (MANDATORY)

**AFTER COMPLETING IMPLEMENTATION:**

1. **Update Milestone Files:**
   ```bash
   # Update .quaestor/milestones/[phase]/tasks.yaml
   # Mark completed subtasks with "# COMPLETED"
   # Update progress percentage
   # Add timestamped notes
   ```

2. **Update MEMORY.md:**
   ```markdown
   ### YYYY-MM-DD
   - **COMPLETED**: [Task Name] ([Phase] - [task_id], subtask [X/Y])
     - Implementation: [brief description]
     - Files created: [list key files]
     - Tests added: [count and brief description]
     - Status: [X]% complete
     - Next: [what's next in this task]
   ```

3. **Verification Checklist:**
   - [ ] Milestone task status updated
   - [ ] Subtasks marked complete
   - [ ] Progress percentage updated
   - [ ] MEMORY.md progress log added
   - [ ] Notes added with timestamp
   - [ ] Next steps identified

**COMPLIANCE CHECK:**
If you cannot complete the milestone updates, explain why and ask for guidance.
```

## Enhanced Auto-Detection

```markdown
## AUTO-DETECTION ENHANCEMENT

Add after existing auto-detection:

**MILESTONE AUTO-DETECTION:**
1. Scan .quaestor/milestones/ for keywords in task names
2. Match argument keywords to task descriptions
3. Identify related subtasks
4. Suggest milestone context to user

**EXAMPLE:**
Task: "implement vector store"
Detected: Phase 1 > vector_store task
Subtasks: ["Create VectorStore abstraction (ABC)", "Implement InMemoryVectorDB", ...]
Suggestion: "This appears to relate to Phase 1 vector_store task. Shall I work on the next incomplete subtask?"
```