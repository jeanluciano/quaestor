# Specification Integration & Tracking

This file describes how to integrate with Quaestor's specification system for tracking implementation progress.

## Specification Folder Structure

```yaml
.quaestor/specs/
├── draft/           # Planned specifications (not yet started)
├── active/          # In-progress implementations (max 3)
├── completed/       # Finished implementations
└── archived/        # Old/cancelled specifications
```

---

## Specification Lifecycle

### States and Transitions

```yaml
States:
  draft: "Specification created but not started"
  active: "Currently being implemented"
  completed: "Implementation finished and validated"
  archived: "Old or cancelled"

Transitions:
  draft → active: "Start implementation"
  active → completed: "Finish implementation"
  active → draft: "Pause work"
  any → archived: "Cancel or archive"

Limits:
  active: "Maximum 3 active specs"
  draft: "Unlimited"
  completed: "Unlimited"
  archived: "Unlimited"
```

---

## Phase 1: Specification Discovery

### No Arguments Provided

**Discovery Protocol:**
```yaml
Step 1: Check Active Specs
  Location: .quaestor/specs/active/*.md
  Purpose: Find in-progress work
  Output: List of active specifications

Step 2: Check Draft Specs (if no active)
  Location: .quaestor/specs/draft/*.md
  Purpose: Find available work
  Output: List of draft specifications

Step 3: Present to User
  Format:
    "Found 2 specifications:
     - [active] spec-feature-001: User Authentication
     - [draft] spec-feature-002: Data Export API

     Which would you like to work on?"

Step 4: User Selection
  User provides: spec ID or description
  Match: Find corresponding specification
  Activate: Move draft → active (if needed)
```

### Arguments Provided

**Match Specification by ID or Description:**
```yaml
Argument Examples:
  - "spec-feature-001"
  - "feature-001"
  - "001"
  - "user authentication"
  - "auth system"

Matching Strategy:
  1. Exact ID match: spec-feature-001.md
  2. Partial ID match: Contains "feature-001"
  3. Description match: Title contains "user authentication"
  4. Fuzzy match: Similar words in title

Result:
  Match Found:
    → Load specification
    → Display: "Found: spec-feature-001 - User Authentication System"
    → Activate if in draft/

  No Match:
    → Display: "No matching specification found"
    → Suggest: "Available specs: [list]"
    → Ask: "Would you like to create a new spec?"
```

---

## Phase 2: Specification Activation

### Pre-Activation Validation

**Before Moving to Active:**
```yaml
Validation Checks:
  1. Spec Location:
     - If already active: "Already working on this spec"
     - If in completed: "Spec already completed"
     - If in draft: Proceed with activation

  2. Active Limit:
     - Count: Active specs in .quaestor/specs/active/
     - Limit: Maximum 3 active specs
     - If at limit: "Active limit reached (3 specs). Complete one before starting another."
     - If under limit: Proceed with activation

  3. Specification Validity:
     - Check: Has phases defined
     - Check: Has acceptance criteria
     - If invalid: "Specification incomplete. Please update before starting."
```

### Activation Process

**Move from Draft to Active:**
```yaml
Atomic Operation:
  1. Read Specification:
     Source: .quaestor/specs/draft/spec-feature-001.md
     Parse: Extract metadata and phases

  2. Update Status:
     Field: status
     Change: "draft" → "in_progress"
     Add: start_date (current date)

  3. Move File:
     From: .quaestor/specs/draft/spec-feature-001.md
     To: .quaestor/specs/active/spec-feature-001.md
     Method: Git mv (preserves history)

  4. Confirm:
     Display: "✅ Activated: spec-feature-001 - User Authentication"
     Display: "Status: in_progress"
     Display: "Phases: 4 total, 0 completed"
```

---

## Phase 3: Progress Tracking

### Phase Status Updates

**During Implementation:**
```yaml
Phase Tracking:
  Format in Specification:
    ## Phases

    ### Phase 1: Authentication Flow Design
    - [ ] Task 1
    - [ ] Task 2
    Status: ⏳ in_progress

    ### Phase 2: JWT Implementation
    - [ ] Task 1
    - [ ] Task 2
    Status: ⏳ pending

  Update Protocol:
    1. Complete tasks: Mark checkboxes [x]
    2. Update status: pending → in_progress → completed
    3. Add notes: Implementation details
    4. Track blockers: If any issues

  Example Update:
    ### Phase 1: Authentication Flow Design
    - [x] Design login flow
    - [x] Design registration flow
    - [x] Design password reset flow
    Status: ✅ completed

    Implementation Notes:
    - Used JWT with 15min access, 7day refresh
    - Implemented token rotation for security
    - Added rate limiting on auth endpoints
```

### Acceptance Criteria Tracking

**Track Progress Against Criteria:**
```yaml
Acceptance Criteria Format:
  ## Acceptance Criteria

  - [ ] AC1: Users can register with email/password
  - [ ] AC2: Users can log in and receive JWT
  - [ ] AC3: Tokens expire after 15 minutes
  - [ ] AC4: Refresh tokens work correctly
  - [ ] AC5: Rate limiting prevents brute force

Update During Implementation:
  As Each Criterion Met:
    - Mark checkbox: [x]
    - Add evidence: Link to test or code
    - Validate: Ensure actually working

  Example:
    - [x] AC1: Users can register with email/password
      ✓ Implemented in auth/registration.py
      ✓ Tests: test_registration_flow.py (8 tests passing)
```

---

## Phase 4: Completion & Transition

### Completion Criteria

**Before Moving to Completed:**
```yaml
All Must Be True:
  1. All Phases Completed:
     - Every phase status: ✅ completed
     - All phase tasks: [x] checked

  2. All Acceptance Criteria Met:
     - Every criterion: [x] checked
     - Evidence provided for each
     - Tests passing for each

  3. Quality Gates Passed:
     - All tests passing
     - Linting clean
     - Type checking passed
     - Documentation complete

  4. No Blockers:
     - All issues resolved
     - No pending decisions
     - Ready for review
```

### Move to Completed

**Atomic Transition:**
```yaml
Operation:
  1. Update Specification:
     Field: status
     Change: "in_progress" → "completed"
     Add: completion_date (current date)
     Add: final_notes (summary of implementation)

  2. Move File:
     From: .quaestor/specs/active/spec-feature-001.md
     To: .quaestor/specs/completed/spec-feature-001.md
     Method: Git mv (preserves history)

  3. Create Commit:
     Message: "feat: implement spec-feature-001 - User Authentication"
     Body: Include spec summary and changes
     Reference: Link to specification

  4. Confirm:
     Display: "✅ Completed: spec-feature-001 - User Authentication"
     Display: "Status: completed"
     Display: "All phases completed, all criteria met"
     Display: "Ready for review and PR creation"
```

---

## Specification File Format

### Markdown Structure

**Required Sections:**
```markdown
---
id: spec-feature-001
title: User Authentication System
status: in_progress
priority: high
type: feature
start_date: 2024-01-15
---

# User Authentication System

## Overview
Brief description of what this spec implements.

## Phases

### Phase 1: Phase Name
- [ ] Task 1
- [ ] Task 2
Status: ⏳ in_progress

### Phase 2: Phase Name
- [ ] Task 1
- [ ] Task 2
Status: ⏳ pending

## Acceptance Criteria
- [ ] AC1: Criterion 1
- [ ] AC2: Criterion 2

## Technical Details
Technical implementation notes.

## Testing Strategy
How this will be tested.

## Implementation Notes
Notes added during implementation.
```

### Metadata Fields

```yaml
Required Fields:
  id: "Unique identifier (spec-feature-001)"
  title: "Human-readable title"
  status: "draft|in_progress|completed|archived"
  priority: "low|medium|high|critical"
  type: "feature|bugfix|refactor|docs|other"

Optional Fields:
  start_date: "When implementation started"
  completion_date: "When implementation finished"
  estimated_hours: "Time estimate"
  actual_hours: "Actual time spent"
  assignee: "Who implemented it"
  blockers: "Any blocking issues"
```

---

## Integration with Git

### Commit Messages

**Reference Specifications in Commits:**
```yaml
Format:
  type(scope): message

  Spec: spec-feature-001
  Description: Detailed description

Example:
  feat(auth): implement JWT authentication

  Spec: spec-feature-001
  - Add JWT token generation
  - Implement refresh token rotation
  - Add authentication middleware

  All acceptance criteria met.
  Tests: 42 new tests added (100% coverage)
```

### Git History Preservation

**Using Git MV:**
```yaml
Benefit:
  - Preserves file history across moves
  - Maintains specification evolution
  - Enables tracking changes over time

Command:
  git mv .quaestor/specs/draft/spec-feature-001.md \
         .quaestor/specs/active/spec-feature-001.md

History:
  - See full edit history
  - Track progress over time
  - Understand evolution of spec
```

---

## Auto-Update Protocol

### Pre-Implementation

**When Starting Implementation:**
```yaml
Actions:
  1. Find Specification:
     - Search draft/ and active/
     - Match by ID or description

  2. Activate Specification:
     - Move draft → active (if needed)
     - Update status → in_progress
     - Add start date

  3. Declare Intent:
     Output: "🎯 Working on Spec: spec-feature-001 - User Authentication System"
     Output: "Status: in_progress (moved to active/)"
     Output: "Phases: 4 total, starting Phase 1"

  4. Present Plan:
     - Show implementation strategy
     - Get user approval
     - Begin implementation
```

### During Implementation

**Progress Updates:**
```yaml
After Completing Each Phase:
  1. Update Specification:
     - Mark phase tasks complete: [x]
     - Update phase status: completed
     - Add implementation notes

  2. Track Progress:
     Output: "✅ Phase 1 complete (1/4 phases)"
     Output: "  - All tasks finished"
     Output: "  - Implementation notes added"
     Output: "Starting Phase 2..."

After Completing Acceptance Criterion:
  1. Update Specification:
     - Mark criterion complete: [x]
     - Add evidence (tests, code references)

  2. Track Progress:
     Output: "✅ AC1 met: Users can register"
     Output: "  - Tests: test_registration.py (8 passing)"
     Output: "  - Code: auth/registration.py"
     Output: "Progress: 1/5 criteria met"
```

### Post-Implementation

**When Implementation Complete:**
```yaml
Actions:
  1. Validate Completion:
     - All phases: ✅ completed
     - All criteria: [x] met
     - Quality gates: Passed

  2. Update Specification:
     - Status → completed
     - Add completion date
     - Add final summary

  3. Move to Completed:
     - From: active/spec-feature-001.md
     - To: completed/spec-feature-001.md
     - Method: Git mv

  4. Create Commit:
     - Reference spec in message
     - Include summary of changes
     - Link to relevant files

  5. Declare Complete:
     Output: "✅ Implementation Complete"
     Output: "Specification: spec-feature-001"
     Output: "Status: completed (moved to completed/)"
     Output: "All 4 phases completed, all 5 criteria met"
     Output: "Ready for review and PR creation"
```

---

## Error Handling

### Specification Not Found

```yaml
Issue: No matching specification

Actions:
  1. Search all folders: draft/, active/, completed/
  2. Try fuzzy matching on title
  3. If still no match:
     Output: "❌ No matching specification found"
     Output: "Available specifications:"
     Output: [List active and draft specs]
     Output: "Would you like to create a new spec?"

  4. If user wants to create:
     Delegate to spec-writing skill
```

### Active Limit Reached

```yaml
Issue: Already 3 active specs

Actions:
  1. Count active specs
  2. If at limit:
     Output: "❌ Active limit reached (3 specs)"
     Output: "Currently active:"
     Output: [List 3 active specs with progress]
     Output: "Complete one before starting another"

  3. Suggest:
     Output: "Would you like to:"
     Output: "1. Continue one of the active specs"
     Output: "2. Move one back to draft"
```

### Invalid Specification

```yaml
Issue: Spec missing required fields

Actions:
  1. Validate specification structure
  2. Check required fields: id, title, phases, criteria
  3. If invalid:
     Output: "❌ Specification incomplete"
     Output: "Missing: [list missing fields]"
     Output: "Please update specification before starting"

  4. Suggest fix:
     Output: "Use spec-writing skill to update specification"
```

---

*Complete specification integration for tracking implementation progress with Quaestor*
