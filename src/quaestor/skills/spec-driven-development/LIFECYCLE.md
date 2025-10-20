# Specification Lifecycle Management

This file provides complete details for managing specifications through their lifecycle. Only load when user needs management operations beyond basic "show status" or "activate spec".

## When to Load This File

- User asks about lifecycle details: "How do I move specs?", "What are the rules?"
- User wants batch operations: "Show all high priority specs"
- User needs validation info: "Why can't I activate this spec?"
- User wants progress tracking details: "How is progress calculated?"

## The Folder-Based Lifecycle

Specifications move through three folders representing their state:

```
.quaestor/specs/
├── draft/              # New specs, not started (unlimited)
│   └── spec-*.md
├── active/             # Work in progress (MAX 3 enforced)
│   └── spec-*.md
└── completed/          # Finished work (archived, unlimited)
    └── spec-*.md
```

**Core principle**: The folder IS the state. No separate tracking database needed.

## State Transitions

```
draft/ → active/ → completed/
  ↑         ↓
  └─────────┘
  (can move back to draft if needed)
```

### Draft → Active (Activation)

**When**: User starts working on a specification

**Command**: "activate spec-feature-001" or "start working on spec-feature-001"

**Process**:
1. Check: Is spec in draft/ folder?
2. Check: Are there < 3 specs in active/?
3. Move file: `draft/spec-*.md` → `active/`
4. Update frontmatter: `status: draft` → `status: active`
5. Add timestamp: `updated_at: [current time]`
6. Report success

**Active Limit Enforcement**:
```yaml
limit: 3 active specifications maximum

if_limit_reached:
  action: Block activation
  message: |
    ❌ Cannot activate - 3 specifications already active:
      - spec-feature-001 (80% complete)
      - spec-feature-002 (40% complete)
      - spec-bugfix-001 (95% complete)

    💡 Suggestion: Complete spec-bugfix-001 first (almost done!)

user_options:
  - Complete an active spec
  - Move an active spec back to draft
  - Choose which active spec to pause
```

### Active → Completed (Completion)

**When**: All acceptance criteria are checked off

**Command**: "complete spec-feature-001" or "mark spec-feature-001 as done"

**Validation Before Completion**:
```yaml
required_checks:
  - spec_in_active_folder: true
  - all_criteria_checked: true  # All [ ] became [x]
  - status_field: "active"

optional_warnings:
  - no_test_scenarios: "⚠️ No test scenarios documented"
  - no_branch_linked: "⚠️ No branch linked to spec"
  - estimated_hours_missing: "⚠️ No time estimate"
```

**Process**:
1. Verify: All checkboxes marked `[x]`
2. Verify: Spec is in active/ folder
3. Move file: `active/spec-*.md` → `completed/`
4. Update frontmatter: `status: active` → `status: completed`
5. Add completion timestamp: `updated_at: [current time]`
6. Report success + suggest PR creation

**If Incomplete**:
```
❌ Cannot complete spec-feature-001

Progress: 3/5 criteria complete (60%)

⏳ Remaining:
- [ ] User can reset password via email
- [ ] Session timeout after 24 hours

Mark these complete or continue implementation with /impl spec-feature-001
```

### Completed → Draft (Reopening)

**When**: Need to reopen completed work (rare)

**Command**: "reopen spec-feature-001" or "move spec-feature-001 back to draft"

**Process**:
1. Move file: `completed/spec-*.md` → `draft/`
2. Update frontmatter: `status: completed` → `status: draft`
3. Uncheck acceptance criteria (reset to `[ ]`)
4. Add note about why reopened

### Active → Draft (Pausing)

**When**: Need to pause work temporarily

**Command**: "pause spec-feature-001" or "move spec-feature-001 to draft"

**Process**:
1. Move file: `active/spec-*.md` → `draft/`
2. Update frontmatter: `status: active` → `status: draft`
3. Preserve progress (don't uncheck criteria)
4. Add note about why paused

## Progress Tracking

### Calculation Method

Progress is calculated by parsing checkbox completion:

```markdown
## Acceptance Criteria
- [x] User can login with email and password  ✓ Complete
- [x] Invalid credentials show error message   ✓ Complete
- [x] Sessions persist across browser restarts ✓ Complete
- [ ] User can logout and clear session        ✗ Incomplete
- [ ] Password reset via email                 ✗ Incomplete

Progress: 3/5 = 60%
```

**Algorithm**:
```python
def calculate_progress(spec_content):
    total = count_all_checkboxes(spec_content)
    completed = count_checked_boxes(spec_content)  # [x]
    percentage = (completed / total) * 100
    return {
        'total': total,
        'completed': completed,
        'percentage': percentage
    }
```

**What counts as a checkbox**:
- `- [ ]` or `- [x]` in acceptance criteria section
- `- [ ]` or `- [x]` in test scenarios (optional)
- Checkboxes in other sections (optional)

### Progress Visualization

```
📊 spec-feature-001: User Authentication
Progress: [████████░░] 80%

✅ Completed (4):
- User can login with email and password
- Invalid credentials show error message
- Sessions persist across browser restarts
- User can logout and clear session

⏳ Remaining (1):
- Password reset via email

Last updated: 2 hours ago
Branch: feat/user-authentication
```

## Status Dashboard

### Basic Status Check

**Command**: "show spec status" or "what's my spec status?"

**Output**:
```
📊 Specification Status

📁 Draft: 5 specifications
  - spec-feature-003: User Profile Management [high]
  - spec-feature-004: API Rate Limiting [medium]
  - spec-bugfix-002: Fix memory leak [critical]
  - spec-refactor-001: Simplify auth logic [medium]
  - spec-docs-001: API documentation [low]

📋 Active: 2/3 slots used
  - spec-feature-001: User Authentication [████████░░] 80%
    Branch: feat/user-authentication

  - spec-feature-002: Email Notifications [████░░░░░░] 40%
    Branch: feat/email-notifications

✅ Completed: 12 specifications
  - Last completed: spec-bugfix-001 (2 days ago)

💡 You can activate 1 more specification
```

### Detailed Status for Single Spec

**Command**: "status of spec-feature-001" or "show me spec-feature-001 progress"

**Output**:
```
📊 spec-feature-001: User Authentication

Status: Active
Progress: [████████░░] 80% (4/5 criteria)
Priority: High
Branch: feat/user-authentication
Created: 3 days ago
Updated: 2 hours ago

✅ Completed:
- User can login with email and password
- Invalid credentials show error message
- Sessions persist across browser restarts
- User can logout and clear session

⏳ Remaining:
- Password reset via email

Next steps:
- Continue implementation: /impl spec-feature-001
- Mark complete when done: "complete spec-feature-001"
```

## Batch Operations

### Filter by Type

**Command**: "show all feature specs" or "list bugfix specs"

```bash
# Search across all folders
grep -l "type: feature" .quaestor/specs/**/*.md
```

**Output**:
```
📂 Feature Specifications (8 total)

Draft (4):
- spec-feature-003: User Profile Management
- spec-feature-004: API Rate Limiting
- spec-feature-005: Search functionality
- spec-feature-006: Export to CSV

Active (2):
- spec-feature-001: User Authentication [80%]
- spec-feature-002: Email Notifications [40%]

Completed (2):
- spec-feature-000: Initial setup
- spec-feature-007: Login page
```

### Filter by Priority

**Command**: "show high priority specs" or "what critical specs do we have?"

```bash
grep -l "priority: critical" .quaestor/specs/**/*.md
```

**Output**:
```
🚨 Critical Priority Specifications

Draft:
- spec-bugfix-002: Fix memory leak [Not started]

Active:
- None

💡 Consider activating spec-bugfix-002 (critical priority)
```

### Check Dependencies

**Command**: "what specs are blocked?" or "show spec dependencies"

**Output**:
```
📊 Specification Dependencies

Blocked (waiting on other specs):
- spec-feature-003 (Requires: spec-feature-001)
- spec-feature-005 (Requires: spec-feature-002, spec-feature-003)

Blocking others:
- spec-feature-001 (Blocks: spec-feature-003, spec-refactor-001)

Ready to start (no dependencies):
- spec-feature-004
- spec-bugfix-002
- spec-docs-001
```

## Metadata Management

### Update Priority

**Command**: "set spec-feature-001 priority to critical"

**Process**:
1. Read spec file
2. Update frontmatter: `priority: medium` → `priority: critical`
3. Update timestamp
4. Save file

### Link to Branch

**Command**: "link spec-feature-001 to feat/user-auth"

**Process**:
1. Read spec file
2. Add/update metadata: `branch: feat/user-auth`
3. Update timestamp
4. Save file

### Add Technical Notes

**Command**: "add note to spec-feature-001: using JWT for tokens"

**Process**:
1. Read spec file
2. Append to metadata section or create notes field
3. Update timestamp
4. Save file

## Validation Rules

### Before Activation

```yaml
checks:
  valid_frontmatter:
    - id field exists and is unique
    - type is valid (feature|bugfix|refactor|etc)
    - priority is set
    - timestamps present

  content_quality:
    - title is not empty
    - description has content
    - rationale provided
    - at least 1 acceptance criterion

  warnings:
    - no test scenarios (⚠️ warn but allow)
    - estimated_hours missing (⚠️ warn but allow)
```

### Before Completion

```yaml
checks:
  required:
    - all checkboxes marked [x]
    - spec is in active/ folder
    - status field is "active"

  warnings:
    - no branch linked (⚠️ warn but allow)
    - no test scenarios (⚠️ warn but allow)
    - estimated_hours vs actual time
```

## Error Handling

### Spec Not Found

```
❌ Specification 'spec-feature-999' not found

Searched in:
  - .quaestor/specs/draft/
  - .quaestor/specs/active/
  - .quaestor/specs/completed/

💡 Run "show draft specs" to see available specifications
```

### Active Limit Reached

```
❌ Cannot activate - already at maximum (3 active specs)

Active specs:
  1. spec-feature-001 (80% complete - almost done!)
  2. spec-feature-002 (40% complete)
  3. spec-refactor-001 (10% complete - just started)

Options:
  - Complete spec-feature-001 (almost finished)
  - Pause spec-refactor-001 (just started)
  - Continue with one of the active specs

💡 The 3-spec limit encourages finishing work before starting new features
```

### Incomplete Spec

```
❌ Cannot complete spec-feature-001

Progress: 3/5 criteria (60%)

Missing:
  - [ ] User can reset password via email
  - [ ] Session timeout after 24 hours

Options:
  - Continue implementation: /impl spec-feature-001
  - Mark these criteria complete manually
  - Split into new spec: "create spec for password reset"

💡 All acceptance criteria must be checked before completion
```

## Git Integration

### Stage Spec Changes

When moving specs, stage the changes for commit:

```bash
# Stage all spec folder changes
git add .quaestor/specs/draft/
git add .quaestor/specs/active/
git add .quaestor/specs/completed/

# Commit with descriptive message
git commit -m "chore: activate spec-feature-001"
git commit -m "chore: complete spec-feature-001 - user authentication"
```

### Commit Message Patterns

```yaml
activation:
  format: "chore: activate [spec-id]"
  example: "chore: activate spec-feature-003"

completion:
  format: "chore: complete [spec-id] - [brief title]"
  example: "chore: complete spec-feature-001 - user authentication"

batch_update:
  format: "chore: update spec statuses"
  example: "chore: update spec statuses (2 completed, 1 activated)"
```

## Progress History

### Track Updates

**Command**: "when was spec-feature-001 last updated?"

```bash
# Read frontmatter
grep "updated_at:" .quaestor/specs/active/spec-feature-001.md
```

**Output**:
```
spec-feature-001 last updated: 2025-01-19T14:30:00 (2 hours ago)
```

### Show Velocity

**Command**: "how many specs completed this week?"

```bash
# Check completed folder, filter by completion timestamp
find .quaestor/specs/completed/ -name "*.md" -mtime -7
```

**Output**:
```
📊 Velocity Report (Last 7 Days)

Completed: 3 specifications
  - spec-feature-007: Login page (2 days ago)
  - spec-bugfix-001: Memory leak fix (4 days ago)
  - spec-docs-002: API docs update (6 days ago)

Average: 0.43 specs/day
Weekly rate: 3 specs/week
```

## Advanced Operations

### Bulk Priority Update

**Command**: "set all draft bugfix specs to high priority"

**Process**:
1. Find all draft specs with `type: bugfix`
2. Update each: `priority: medium` → `priority: high`
3. Report changes

### Archive Old Completed Specs

**Command**: "archive specs completed > 90 days ago"

```bash
# Create archive folder
mkdir -p .quaestor/specs/archived/

# Move old completed specs
find .quaestor/specs/completed/ -name "*.md" -mtime +90 \
  -exec mv {} .quaestor/specs/archived/ \;
```

### Generate Status Report

**Command**: "generate spec status report"

**Output**: Markdown file with:
- Current active specs and progress
- Draft specs by priority
- Recently completed specs
- Velocity metrics
- Blocked specs

## Best Practices

### Keep Active Limit Low

The 3-spec limit is intentional:
- ✅ Forces focus on completion
- ✅ Reduces context switching
- ✅ Makes priorities clear
- ✅ Encourages finishing work

### Link Specs to Branches

When starting work:
```yaml
# In spec frontmatter
branch: feat/user-authentication
```

Benefits:
- Easy to find related code
- Track implementation progress
- Connect commits to specs

### Update Progress Regularly

Check off criteria as you complete them:
```markdown
- [x] User can login  ← Mark done immediately
- [ ] User can logout ← Next to work on
```

Benefits:
- Accurate progress tracking
- Visibility into what's left
- Motivation from seeing progress

### Use Priority Ruthlessly

```yaml
priority: critical  # Drop everything, do now
priority: high      # Schedule this week
priority: medium    # Normal priority
priority: low       # Nice to have, do when time allows
```

### Review Draft Specs Weekly

Prune specs that are no longer needed:
- Requirements changed
- Feature no longer wanted
- Superseded by other work

---

*This guide provides complete lifecycle management details. Return to SKILL.md for overview or WRITING.md for spec creation guidance.*
