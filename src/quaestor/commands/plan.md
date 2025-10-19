---
allowed-tools: [Read, Grep, Glob, TodoWrite]
description: "Create specifications and track project progress through interactive planning"
---

# /plan - Specification Creation & Progress Tracking

ARGUMENTS: $DESCRIPTION

## Purpose
Create specifications for features and fixes, track progress, and manage project planning. Simple, interactive, and Skills-powered.

## Usage
```
/plan                    # Create new specification (interactive)
/plan "User Auth"        # Create spec with title
/plan --status          # Show specification dashboard
```

## How It Works

Quaestor uses **Agent Skills** that automatically activate based on your needs:
- **Spec Writing Skill**: Creates specifications from your requirements
- **Spec Management Skill**: Tracks progress and manages lifecycle
- **PR Generation Skill**: Creates pull requests from completed specs

You don't need to invoke these manually - they activate automatically!

## Specification Creation (Default)

When you run `/plan` or `/plan "Feature Name"`, you'll go through an interactive wizard:

### Step 1: Gather Requirements
I'll ask you questions to understand what you're building:
- **Title**: What feature/fix are you planning?
- **Type**: Feature, bugfix, refactor, documentation, etc.?
- **Description**: What exactly needs to be built?
- **Rationale**: Why is this needed?
- **Priority**: Critical, high, medium, or low?

### Step 2: Define Acceptance Criteria
Together we'll define how to know when it's done:
- List measurable success conditions
- Create test scenarios (Given/When/Then)
- Identify dependencies on other specs

### Step 3: Generate Specification
The **Spec Writing Skill** automatically creates a Markdown file in `.quaestor/specs/draft/`:

```markdown
---
id: spec-feature-001
type: feature
status: draft
priority: high
created_at: 2025-01-10T14:30:00
---

# User Authentication System

## Description
[Your detailed description]

## Rationale
[Why this is needed]

## Acceptance Criteria
- [ ] User can login with email and password
- [ ] Invalid credentials show error message
- [ ] Sessions persist across browser restarts

## Test Scenarios
### Successful login
**Given**: Valid credentials
**When**: User submits login form
**Then**: User is logged in and redirected

[More sections...]
```

### Step 4: Next Actions
Once created, you can:
- Review and edit the spec file directly
- Activate it: "activate spec-feature-001"
- Start implementing: `/impl spec-feature-001`

## Folder Structure

Specifications live in three folders representing their state:

```
.quaestor/specs/
├── draft/              # New specs (unlimited)
│   └── spec-*.md
├── active/             # Work in progress (MAX 3)
│   └── spec-*.md
└── completed/          # Finished work (archived)
    └── spec-*.md
```

**The folder IS the state** - no complex tracking needed!

## Specification Lifecycle

```mermaid
draft → active → completed
```

### Draft → Active
When ready to start work:
```
"activate spec-feature-001"
```

The **Spec Management Skill** will:
- Check the 3-active-spec limit
- Move the file from `draft/` to `active/`
- Update the status in frontmatter

### Active → Completed
When all checkboxes are marked:
```
"complete spec-feature-001"
```

The **Spec Management Skill** will:
- Verify all acceptance criteria checked
- Move the file from `active/` to `completed/`
- Suggest creating a pull request

### Creating a Pull Request
After completion:
```
"create a pull request for spec-feature-001"
```

The **PR Generation Skill** automatically:
- Reads the completed spec
- Generates comprehensive PR description
- Creates GitHub PR via `gh` CLI

## Status Dashboard (--status)

View your project's specification status:

```
/plan --status
```

You'll see:

```
📊 Specification Status Dashboard

Summary:
  📁 Draft: 5 specs ready to start
  📋 Active: 2/3 slots used (can add 1 more)
  ✅ Completed: 12 specs finished
  📈 Overall: 63% complete (12/19)

Active Work:
  1. spec-feature-001: User Authentication [████████░░] 80%
     Last updated: 2 hours ago
     Remaining: 1 criteria

  2. spec-feature-002: Email Notifications [████░░░░░░] 40%
     Last updated: 1 day ago
     Remaining: 3 criteria

Ready to Start (Draft):
  - spec-feature-003: User Profile Management [high priority]
  - spec-bugfix-002: Fix memory leak [critical]
  - spec-feature-004: API Rate Limiting [medium]

💡 Suggestions:
  - Complete spec-feature-001 (almost done!)
  - Start spec-bugfix-002 (critical)
```

## Progress Tracking

Progress is calculated automatically from checkbox completion:

```markdown
## Acceptance Criteria
- [x] User can login with email and password  ✓
- [x] Invalid credentials show error message   ✓
- [x] Sessions persist across browser restarts ✓
- [ ] User can logout and clear session        ✗
- [ ] Password reset via email                 ✗

Progress: 3/5 complete (60%)
```

Just mark checkboxes as you complete work - the **Spec Management Skill** calculates progress automatically when you check status.

## Working with Specifications

### Check Spec Status
```
"what's the status of spec-feature-001?"
"show my active specs"
"how's progress on authentication?"
```

### Move Between States
```
"activate spec-feature-003"
"complete spec-feature-001"
```

### Update Metadata
```
"set spec-feature-001 priority to critical"
"link spec-feature-001 to feat/user-auth branch"
```

### List Specifications
```
"show draft specs"
"what high priority specs do we have?"
"list all feature specs"
```

## Best Practices

### Respect the 3-Active Limit
Focus on finishing work before starting new specs. This prevents work-in-progress sprawl and maintains focus.

If you try to activate a 4th spec:
```
❌ Cannot activate - already at maximum (3 active specs)

Active:
  1. spec-feature-001 (80% complete - almost done!)
  2. spec-feature-002 (40% complete)
  3. spec-refactor-001 (10% complete - just started)

💡 Complete spec-feature-001 first
```

### Keep Specs Small and Focused
Break large features into multiple specs:
- spec-auth-001: Basic login/logout
- spec-auth-002: Password reset
- spec-auth-003: OAuth integration

Each spec should be completable in a reasonable timeframe.

### Update Checkboxes Regularly
Mark acceptance criteria as you complete them:
```markdown
- [x] ✅ Done today
- [ ] ⏳ Working on this
- [ ] 📋 Todo
```

This keeps your progress tracking accurate.

### Link Specs to Branches
Add branch info in the spec frontmatter:
```yaml
branch: feat/user-authentication
```

This helps connect specs to git history.

## Integration with Other Commands

### With /impl
```
/impl spec-feature-001
```
Implementation starts → mark criteria complete as you go

### With /review
```
/review
```
Review completed → create PR for finished spec

### With /research
```
/research "authentication patterns"
```
Research first → create spec with findings

## Skills in Action

Remember, you don't need to know about Skills - they just work:

**When you describe a feature:**
→ Spec Writing Skill activates
→ Creates specification automatically

**When you mention "spec status":**
→ Spec Management Skill activates
→ Calculates and displays progress

**When you say "create pr":**
→ PR Generation Skill activates
→ Generates and submits pull request

**It's that simple!**

## Quick Reference

### Creating
```
/plan                              # Interactive wizard
/plan "Feature description"        # Quick create
```

### Checking Status
```
/plan --status                     # Dashboard
"show spec progress"               # Progress
"what's the status of spec-X"      # Specific spec
```

### Managing
```
"activate spec-X"                  # Start work
"complete spec-X"                  # Mark done
"create pr for spec-X"             # Submit PR
```

### Editing
Specs are Markdown files - edit them directly:
```bash
code .quaestor/specs/draft/spec-feature-001.md
```

---

*Simple, interactive specification planning powered by Agent Skills*
