---
name: Specification Management
description: Manage specification lifecycle including activation, progress tracking, status updates, and completion. Use when user asks about spec status, wants to activate/complete specs, check progress, or move specs between folders.
allowed-tools: [Read, Edit, Bash, Grep, Glob]
---

# Specification Management

I manage the complete lifecycle of specifications - from draft to active to completed. I track progress, enforce limits, and ensure smooth transitions.

## When to Use Me

- User asks: "What's the status of my specs?"
- User wants to: "activate spec-feature-001"
- User says: "complete spec-feature-001"
- User asks: "how's the progress on authentication?"
- User wants to: "show me active specifications"
- Any mention of: specification status, spec progress, complete, activate

## Folder-Based Lifecycle

Specifications live in three folders that represent their state:

```
.quaestor/specs/
├── draft/              # New specs (unlimited)
│   └── spec-*.md
├── active/             # Work in progress (MAX 3)
│   └── spec-*.md
└── completed/          # Finished work (archived)
    └── spec-*.md
```

**The folder IS the state** - no separate tracking needed!

## My Capabilities

### 1. Check Specification Status

When asked about status, I scan all folders and report:

```
📊 Specification Status

📁 Draft: 5 specifications
  - spec-feature-003: User Profile Management
  - spec-feature-004: API Rate Limiting
  - spec-bugfix-002: Fix memory leak
  - spec-refactor-001: Simplify auth logic
  - spec-docs-001: API documentation

📋 Active: 2/3 slots used
  - spec-feature-001: User Authentication
    Progress: [████████░░] 80% (4/5 criteria complete)
    Branch: feat/user-authentication

  - spec-feature-002: Email Notifications
    Progress: [████░░░░░░] 40% (2/5 criteria complete)
    Branch: feat/email-notifications

✅ Completed: 12 specifications
  - Last completed: spec-bugfix-001 (2 days ago)

💡 You can activate 1 more specification
```

### 2. Activate Specifications

Move a spec from `draft/` to `active/`:

**Command flow**:
```bash
User: "activate spec-feature-003"

Me:
1. Check active limit (max 3)
2. Move spec: draft/spec-feature-003.md → active/
3. Update status in frontmatter: status: draft → status: active
4. Report success
```

**Active Limit Enforcement**:
- ❌ Cannot activate if 3 specs already active
- ✅ Must complete or cancel one first
- 💡 Suggests which active specs to complete

### 3. Track Progress

I calculate progress by parsing checkbox completion in the spec:

```markdown
## Acceptance Criteria
- [x] User can login with email and password  ✓
- [x] Invalid credentials show error message   ✓
- [x] Sessions persist across browser restarts ✓
- [ ] User can logout and clear session        ✗
- [ ] Password reset via email                 ✗

Progress: 3/5 complete (60%)
```

**Progress Calculation**:
- Total: Count all checkboxes in entire spec
- Completed: Count `- [x]` checkboxes
- Percentage: (completed / total) * 100

### 4. Complete Specifications

Move a spec from `active/` to `completed/`:

**Completion Checklist** (I verify):
```yaml
Required:
  - ✅ All acceptance criteria checked: [ ] → [x]
  - ✅ Status is 'active' (not draft)
  - ✅ Spec file exists in active/ folder

Optional (I warn if missing):
  - ⚠️ Test scenarios documented
  - ⚠️ Technical notes added
  - ⚠️ Branch linked to spec
```

**Command flow**:
```bash
User: "complete spec-feature-001"

Me:
1. Verify all checkboxes marked [x]
2. Move spec: active/spec-feature-001.md → completed/
3. Update status: status: active → status: completed
4. Add completion timestamp
5. Report success + suggest PR creation
```

### 5. Update Specification Metadata

I can update specs inline:

```bash
# Update priority
User: "set spec-feature-001 priority to high"
Me: Edit frontmatter: priority: medium → priority: high

# Add branch linkage
User: "link spec-feature-001 to feat/user-auth"
Me: Add to frontmatter: branch: feat/user-auth

# Add notes
User: "add note to spec-feature-001: using JWT for tokens"
Me: Append to metadata section
```

## Operations Guide

### Activate a Specification

```bash
# Check what's available
User: "show draft specs"
Me: List all specs in draft/

# Activate one
User: "activate spec-feature-003"
Me:
  1. Check: active/ has < 3 specs? ✓
  2. Move: draft/spec-feature-003.md → active/
  3. Edit frontmatter: status: draft → status: active
  4. Confirm: "spec-feature-003 is now active"
```

**If limit reached**:
```
❌ Cannot activate - 3 specifications already active:
  - spec-feature-001 (80% complete)
  - spec-feature-002 (40% complete)
  - spec-bugfix-001 (95% complete)

💡 Suggestion: Complete spec-bugfix-001 first (almost done!)
```

### Calculate Progress

```bash
User: "What's the progress on spec-feature-001?"

Me:
1. Read: .quaestor/specs/active/spec-feature-001.md
2. Parse: Find all checkboxes (- [ ] and - [x])
3. Count: Completed vs Total
4. Calculate: Percentage
5. Report:

   📊 spec-feature-001: User Authentication
   Progress: [████████░░] 80%

   ✅ Completed (4):
   - User can login with email and password
   - Invalid credentials show error message
   - Sessions persist across browser restarts
   - User can logout and clear session

   ⏳ Remaining (1):
   - Password reset via email
```

### Complete a Specification

```bash
User: "complete spec-feature-001"

Me:
1. Verify location: Is it in active/? ✓
2. Check progress: Are all checkboxes [x]? ✓
3. Move file: active/spec-feature-001.md → completed/
4. Update frontmatter:
   status: active → status: completed
   updated_at: 2025-01-10T15:30:00
5. Report:

   ✅ spec-feature-001 completed!

   📁 Moved to: .quaestor/specs/completed/
   🎯 Next steps:
   - Create PR: "create a pull request"
   - Start next: "activate spec-feature-002"
```

**If incomplete**:
```
❌ Cannot complete - 1 criteria remaining:

⏳ Not done:
- Password reset via email

Mark this as complete or run: /impl spec-feature-001
```

### Show Specification Dashboard

```bash
User: "show spec status" or "spec dashboard"

Me:
📊 Specification Status Dashboard

Summary:
  📁 Draft: 5 specs
  📋 Active: 2/3 slots
  ✅ Completed: 12 specs
  📈 Overall: 12/19 specs complete (63%)

Active Work:
  1. spec-feature-001: User Authentication [████████░░] 80%
     Branch: feat/user-auth
     Last updated: 2 hours ago

  2. spec-feature-002: Email Notifications [████░░░░░░] 40%
     Branch: feat/notifications
     Last updated: 1 day ago

Ready to Start (Draft):
  - spec-feature-003: User Profile Management [high]
  - spec-bugfix-002: Fix memory leak [critical]
  - spec-feature-004: API Rate Limiting [medium]

💡 Next actions:
- Complete spec-feature-001 (80% done)
- Start spec-bugfix-002 (critical priority)
```

## Advanced Features

### Batch Operations

```bash
# List all specs by type
User: "show all feature specs"
Me: Grep for type: feature across all folders

# Show high priority items
User: "what high priority specs do we have?"
Me: Grep for priority: high in draft/

# Check blocked specs
User: "any blocked specs?"
Me: Search for dependencies and cross-reference
```

### Progress History

```bash
# Track updates
User: "when was spec-feature-001 last updated?"
Me: Read frontmatter → updated_at: 2025-01-10T14:30:00

# Show velocity
User: "how many specs completed this week?"
Me: Check completed/ folder, filter by completion timestamp
```

### Validation

I automatically validate when moving specs:

```yaml
Before Activation:
  - ✅ Spec has valid frontmatter (id, type, status, priority)
  - ✅ Description and rationale present
  - ✅ At least 1 acceptance criterion defined
  - ⚠️ Warn if no test scenarios

Before Completion:
  - ✅ All acceptance criteria checked [x]
  - ✅ Status is 'active'
  - ⚠️ Warn if no branch linked
  - ⚠️ Warn if estimated_hours not set
```

## Folder Operations

### Move Specification

```bash
# Manual move (if needed)
mv .quaestor/specs/draft/spec-feature-001.md .quaestor/specs/active/

# I handle status update automatically
# Edit frontmatter: status: draft → status: active
```

### Git Integration

When moving specs, I can stage the changes:

```bash
git add .quaestor/specs/draft/
git add .quaestor/specs/active/
git add .quaestor/specs/completed/
git commit -m "chore: update spec statuses"
```

## Error Handling

### Common Issues

**Issue**: Spec not found
```
❌ Specification 'spec-feature-999' not found

Searched in:
  - .quaestor/specs/draft/
  - .quaestor/specs/active/
  - .quaestor/specs/completed/

💡 Run "show draft specs" to see available specifications
```

**Issue**: Active limit reached
```
❌ Cannot activate - already at maximum (3 active specs)

Active specs:
  1. spec-feature-001 (80% complete - almost done!)
  2. spec-feature-002 (40% complete)
  3. spec-refactor-001 (10% complete - just started)

💡 Complete or move spec-feature-001 first
```

**Issue**: Incomplete specification
```
❌ Cannot complete spec-feature-001

Missing:
  - [ ] User can reset password via email
  - [ ] Session timeout after 24 hours

Progress: 3/5 (60%)

💡 Mark these criteria complete or continue implementation
```

## Integration with Other Commands

### With /impl
```bash
User: "/impl spec-feature-001"
Implementation starts → I track progress → Mark criteria complete
```

### With PR Generation
```bash
User: "create pull request for spec-feature-001"
I verify complete → Pass to PR Generation Skill
```

### With /plan
```bash
User: "/plan new feature"
Spec Writing Skill creates spec → I manage its lifecycle
```

## Tips for Users

### Keep Specs Current
Update checkboxes as you complete work:
```markdown
- [x] ✅ Done today
- [ ] ⏳ Working on this
- [ ] 📋 Todo
```

### Use Branch Linking
Link specs to git branches for context:
```yaml
branch: feat/user-authentication
```

### Prioritize Ruthlessly
Use priority field to guide work:
```yaml
priority: critical  # Do this first!
priority: high      # Important
priority: medium    # Normal work
priority: low       # Nice to have
```

### Respect the 3-Active Limit
Focus on finishing before starting new work. Quality over quantity!

---

*I keep your specifications organized, track progress automatically, and enforce healthy work-in-progress limits. Just tell me what you need!*
