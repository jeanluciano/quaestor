---
allowed-tools: [Read, Edit, MultiEdit, Write, Bash]
description: Create or complete project milestones
---

# MILESTONE - Project Phase Management
<!-- META:command:milestone -->
<!-- META:version:1.0 -->

## 🎯 Milestone Management

**Purpose:** Create new milestones or mark current milestone as complete.

### Command Options

```yaml
usage_patterns:
  - "/milestone --create 'MVP Complete'"  # Start new milestone
  - "/milestone --complete"                # Complete current milestone
  - "/milestone --status"                  # Show milestone progress
  - "/milestone"                          # Interactive mode
```

### Workflow

#### 1. Check Current Status
First, I'll read MEMORY.md to understand:
- Current milestone name and progress
- Completed items in this milestone
- Any pending items
- Overall project phase

#### 2. For Milestone Completion

<!-- DATA:completion-workflow:START -->
```yaml
completion_steps:
  - validate_readiness:
      check: "All tasks marked complete"
      verify: "No failing tests"
      ensure: "Documentation updated"
  
  - archive_progress:
      action: "Move completed items to history"
      location: "MEMORY.md → Milestone History"
      format: "Dated milestone summary"
  
  - generate_summary:
      include:
        - "Key achievements"
        - "Technical decisions made"
        - "Patterns established"
        - "Lessons learned"
  
  - update_architecture:
      if_needed: "Update ARCHITECTURE.md with new patterns"
      document: "Major architectural decisions"
  
  - prepare_next_phase:
      prompt: "What's the focus of the next milestone?"
      create: "New milestone section in MEMORY.md"
```
<!-- DATA:completion-workflow:END -->

#### 3. For New Milestone Creation

<!-- DATA:creation-workflow:START -->
```yaml
creation_steps:
  - gather_context:
      ask: "What's the main goal of this milestone?"
      examples:
        - "User Authentication System"
        - "API Integration"
        - "Performance Optimization"
        - "MVP Launch"
  
  - define_scope:
      prompt: "What are the key deliverables?"
      format: "Bullet list of concrete items"
  
  - set_success_criteria:
      define: "How will we know this milestone is complete?"
      measurable: true
  
  - initialize_tracking:
      create_sections:
        - "Milestone: [Name]"
        - "Goals: [List]"
        - "Success Criteria: [Metrics]"
        - "Planned Items: [Tasks]"
        - "In Progress: []"
        - "Completed: []"
```
<!-- DATA:creation-workflow:END -->

### Output Format

#### Milestone Completion Output:
```markdown
## 🎉 Milestone Complete: [Name]

### Summary
Completed [X] tasks over [duration]

### Key Achievements
• [Achievement 1]
• [Achievement 2]
• ...

### Technical Highlights
• [Pattern or decision 1]
• [Pattern or decision 2]
• ...

### Metrics
- Tests: [count] passing
- Coverage: [percentage]
- Files Modified: [count]
- Commits: [count]

### Ready for Next Phase
✅ All tasks complete
✅ Tests passing
✅ Documentation updated
✅ Code reviewed

---
Milestone archived to history. Ready to start: [Next Milestone Name]
```

#### New Milestone Output:
```markdown
## 🚀 New Milestone: [Name]

### Goals
1. [Primary goal]
2. [Secondary goal]
3. ...

### Planned Tasks
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- ...

### Success Criteria
- [Measurable criterion 1]
- [Measurable criterion 2]
- ...

### Estimated Duration
[Estimate based on scope]

---
Milestone created! Use `/task "[first task]"` to begin.
```

### Interactive Mode

If no flags provided, I'll guide you through:

1. **Current Status Review**
   - Show what's been completed
   - List any pending items
   - Display overall progress

2. **Decision Point**
   - Complete current milestone?
   - Create new milestone?
   - Just view status?

3. **Guided Process**
   - Walk through appropriate workflow
   - Gather necessary information
   - Update all relevant files

### Integration Points

- **MEMORY.md**: Primary tracking document
- **ARCHITECTURE.md**: Update if architectural decisions made
- **Git**: Option to create milestone tag
- **GitHub**: Option to close related issues/PRs

### Best Practices

1. **Complete milestones when:**
   - All planned features implemented
   - Tests comprehensive and passing
   - Documentation current
   - Ready for next phase

2. **Create focused milestones:**
   - Single clear objective
   - Measurable completion criteria
   - Reasonable scope (1-2 weeks)
   - Concrete deliverables

3. **Archive properly:**
   - Document decisions made
   - Note patterns discovered
   - Record metrics
   - Preserve learning

---

**Ready to manage your project milestones!**