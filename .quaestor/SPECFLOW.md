# Quaestor Specification Lifecycle

## Overview

The Specification Lifecycle defines how Quaestor manages specifications from creation through completion, ensuring continuous progress tracking and automated updates as work proceeds.

## Core Concept

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    DRAFT    │────▶│    ACTIVE   │────▶│  COMPLETED  │────▶│   ARCHIVED  │
│  (Planning) │     │  (Working)  │     │  (Testing)  │     │ (Reference) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                    │
       └─────────── Continuous Progress Tracking ────────────────────┘
```

## Specification States

### 1. DRAFT
- **Location**: `.quaestor/specs/draft/`
- **Trigger**: `/plan` command creates new specification
- **Characteristics**:
  - Initial specification created
  - Acceptance criteria defined
  - Not yet linked to branch
  - Progress: 0%
- **Auto-Updates**: None (planning phase)
- **Next State**: ACTIVE (via `/plan --activate` or `/impl`)

### 2. ACTIVE
- **Location**: `.quaestor/specs/active/`
- **Trigger**: Specification activated for implementation
- **Characteristics**:
  - Linked to feature branch
  - Progress tracked automatically
  - Acceptance criteria being worked on
  - Test scenarios tracked
- **Auto-Updates**:
  - File changes trigger progress calculation
  - TODO completions update acceptance criteria
  - Test results update test scenarios
  - Git commits reference spec ID
- **Progress Tracking**:
  ```yaml
  progress_indicators:
    - acceptance_criteria: "Checkboxes in criteria"
    - test_scenarios: "Test completion status"
    - file_changes: "Implementation detected"
    - todo_items: "Task completion"
  ```
- **Next State**: COMPLETED (all criteria met)

### 3. COMPLETED
- **Location**: `.quaestor/specs/completed/`
- **Trigger**: All acceptance criteria met + tests passing
- **Characteristics**:
  - Implementation finished
  - All tests passing
  - Ready for PR creation
  - Progress: 100%
- **Auto-Updates**:
  - Completion timestamp added
  - Implementation notes captured
  - PR link added when created
- **Archive Format**:
  ```yaml
  completed_at: "ISO-8601 timestamp"
  pr_number: 123
  implementation_notes: |
    - Key decisions made
    - Challenges resolved
    - Performance considerations
  ```
- **Next State**: ARCHIVED (after PR merge)

### 4. ARCHIVED
- **Location**: `.quaestor/specs/completed/` (with archived flag)
- **Trigger**: PR merged to main branch
- **Characteristics**:
  - Historical reference
  - Immutable record
  - Linked to git history
- **Metadata**:
  ```yaml
  archived: true
  merged_at: "ISO-8601 timestamp"
  merge_commit: "SHA"
  ```

## Automatic Progress Tracking by Claude

### TODO-Based Progress Tracking
Progress tracking happens automatically through the todo_spec_progress hook. Your role:

1. **When Starting Work on a Specification**:
   - Create TODO items that map to acceptance criteria
   - Example:
     ```
     TodoWrite:
     - "Implement user authentication logic" (maps to criterion #1)
     - "Add password validation" (maps to criterion #1) 
     - "Create password reset flow" (maps to criterion #2)
     - "Integrate email service" (maps to criterion #3)
     ```

2. **When Completing Work**:
   - Simply mark TODOs as completed using TodoWrite
   - DO NOT manually edit specification YAML files
   - The hook handles all spec updates automatically

3. **What Happens Automatically**:
   - todo_spec_progress hook detects TODO completions
   - Hook checks if acceptance criteria are satisfied
   - Hook updates spec YAML with "✓" marks
   - Hook recalculates progress percentages
   - You see updated progress in next session

**IMPORTANT**: Never manually edit spec files to update progress. Only use TodoWrite to track work completion.

### Progress Tracking Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│Create TODOs │────▶│Complete TODO│────▶│Check Criteria│────▶│Update Spec │
│(from spec)  │     │   Mark [x]  │     │  Satisfied? │     │   Add ✓    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Example Workflow

1. **Starting Implementation**:
   ```
   User: "Implement auth-001 specification"
   
   Claude reads spec and creates TODOs:
   - [ ] Implement login endpoint
   - [ ] Add JWT token generation  
   - [ ] Create user session management
   - [ ] Implement password hashing
   ```

2. **During Work**:
   ```
   Claude completes TODO: "Implement login endpoint" → [x]
   Claude completes TODO: "Add JWT token generation" → [x]
   Claude completes TODO: "Create user session management" → [x]
   Claude completes TODO: "Implement password hashing" → [x]
   
   All TODOs for criterion #1 done → Update spec:
   acceptance_criteria:
     - "✓ Implement user authentication"  # Auto-updated
   ```

3. **Progress Calculation**:
   ```yaml
   # Claude automatically updates after TODO completion:
   progress: 0.25  # 1 of 4 criteria completed
   updated_at: "2024-01-10T10:30:00Z"
   implementation_notes: |
     - Completed authentication implementation
     - Using JWT for session management
   ```

### Progress Calculation Formula
```yaml
progress_components:
  acceptance_criteria:
    weight: 0.7
    calculation: "completed_criteria / total_criteria"
  
  todo_completion:
    weight: 0.2
    calculation: "completed_todos / total_todos"
  
  test_scenarios:
    weight: 0.1
    calculation: "passing_tests / total_tests"

total_progress: "Σ(component_value * component_weight)"
```

### Benefits of TODO-Based Tracking

1. **Natural Workflow**: TODOs are already part of development workflow
2. **No Code Pollution**: No inline comments needed
3. **Clear Mapping**: Each TODO maps to specification work
4. **Automatic Updates**: Completing TODOs triggers spec updates
5. **Progress Visibility**: See progress through TODO completion

### In Specification YAML
```yaml
# Acceptance criteria with completion status
acceptance_criteria:
  - "✓ Implement user authentication" # Auto-updated when TODOs complete
  - "✓ Add password reset flow" # Auto-updated when TODOs complete
  - "[ ] Integrate with email service" # PENDING
  - "[ ] Add 2FA support" # PENDING

# Progress tracked automatically
progress: 0.5  # 2/4 criteria completed
todos_completed: 8  # of 16 total
last_updated: "2024-01-10T10:30:00Z"
```

### In Commit Messages
```
feat(auth-001): Complete user authentication

- Implemented login endpoint with JWT
- Added password hashing with bcrypt
- Created session management

Completes acceptance criterion #1
Progress: 25% (1/4 criteria completed)
```

## Automation Hooks

### Session Context Loader Enhancement
```yaml
session_start:
  - Load active specs with current progress
  - Show visual progress bars
  - Highlight next tasks
  - Display blocking issues
```

### Pre-Tool Use
```yaml
before_edit:
  - Detect spec context
  - Suggest spec markers
  - Validate against criteria
```

### Post-Tool Use
```yaml
after_edit:
  - Scan for progress markers
  - Update spec progress
  - Notify if criterion completed
  - Suggest next steps
```

## Progress Reporting

### Visual Progress Display
```
auth-001: User Authentication System
Progress: [████████████░░░░░░░░] 60%
├─ Acceptance Criteria: 2/4 completed
├─ Test Scenarios: 3/5 passing
└─ Implementation: Active

Next: Integrate with email service
```


## Quality Gates

### Completion Requirements
```yaml
ready_for_completion:
  - all_criteria_met: true
  - all_tests_passing: true
  - no_todo_remaining: true
  - code_review_ready: true
  - documentation_updated: true
```

### Auto-Completion Triggers
```yaml
when_complete:
  - Move to completed folder
  - Generate completion summary
  - Suggest PR creation
  - Recommend next spec
```

## Integration Points

### With Agents
- **spec-manager**: Handles lifecycle transitions
- **implementer**: Updates progress during coding
- **qa**: Validates completion criteria
- **workflow-coordinator**: Ensures proper sequencing

### With Hooks
- **session_context_loader**: Shows current progress
- **spec_tracker**: Updates progress in real-time
- **spec_lifecycle**: Manages state transitions

### With Commands
- **/plan**: Creates and manages specs
- **/impl**: Activates and tracks implementation
- **/review**: Validates completion
- **/debug**: Troubleshoots progress issues

## Best Practices

### Progress Tracking
1. Update progress incrementally, not in batches
2. Use clear markers in code and commits
3. Keep acceptance criteria atomic and measurable
4. Link all work to specific spec IDs

### Automation
1. Let hooks track progress automatically
2. Use commands for major transitions
3. Trust the calculation formula
4. Review progress in session context

### Communication
1. Reference spec IDs in all commits
2. Update specs with implementation notes
3. Document decisions and deviations

## Troubleshooting

### Common Issues
1. **Progress stuck at 0%**
   - Check if spec is activated
   - Verify branch linkage
   - Ensure work references spec ID

2. **Progress not updating**
   - Check hook execution
   - Verify file changes detected
   - Review progress markers

3. **Incorrect progress calculation**
   - Validate acceptance criteria format
   - Check test scenario status
   - Review calculation weights


---

*The Specification Lifecycle ensures that every piece of work is tracked, measured, and progressed systematically through Quaestor's specification-driven development process.*