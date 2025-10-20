---
name: Specification Writing
description: Generate clean Markdown specification files from user requirements or planning data. Use when user wants to create a new specification, plan a feature, or convert planning notes into structured specs.
allowed-tools: [Write, Read, Glob]
---

# Specification Writing

I help you create clean, readable Markdown specification files for your project features, fixes, and improvements.

## When to Use Me

- User describes a new feature to implement
- User wants to plan a bug fix or refactoring
- User provides planning data that needs to be turned into a spec
- User says "create a spec", "plan a feature", or "write a specification"

## Markdown Specification Template

I use this flexible, forgiving template:

```markdown
---
id: spec-TYPE-NNN
type: feature  # Can be: feature, bugfix, refactor, documentation, performance, security, testing
status: draft
priority: medium  # critical, high, medium, or low
created_at: 2025-01-10T10:00:00
updated_at: 2025-01-10T10:00:00
---

# Actual Descriptive Title Here

## Description
Actual description of what needs to be done.
Be specific and detailed.
Multiple paragraphs are fine.

## Rationale
Why this is needed.
What problem it solves.
Business or technical justification.

## Dependencies
- **Requires**: spec-001, spec-002 (or leave empty)
- **Blocks**: spec-003 (or leave empty)
- **Related**: spec-004 (or leave empty)

## Risks
- Risk description if any
- Another risk if applicable

## Success Metrics
- Measurable success metric
- Another measurable metric

## Acceptance Criteria
- [ ] User can do X
- [ ] System performs Y
- [ ] Feature handles Z
- [ ] Error cases are handled gracefully
- [ ] Performance meets requirements

## Test Scenarios

### Basic test
**Given**: Initial state
**When**: Action taken
**Then**: Expected result

### Error case
**Given**: Invalid input
**When**: Action attempted
**Then**: Appropriate error message shown

## Metadata
estimated_hours: 8
technical_notes: Any technical considerations
```

## My Process

### Step 1: Gather Requirements
If user provides incomplete information, I'll ask:
- **Title**: What are we building/fixing?
- **Type**: Is this a feature, bugfix, refactor, etc.?
- **Description**: What exactly needs to be done?
- **Rationale**: Why is this needed?
- **Acceptance Criteria**: How will we know it's done?

### Step 2: Generate Spec ID
I create a unique ID based on the type and title:
- Feature: `spec-feature-001`, `spec-feature-002`, etc.
- Bugfix: `spec-bugfix-001`
- Refactor: `spec-refactor-001`
- Performance: `spec-perf-001`
- Security: `spec-sec-001`
- Testing: `spec-test-001`
- Documentation: `spec-docs-001`

I'll check existing specs in `.quaestor/specs/draft/` to ensure uniqueness.

### Step 3: Fill Template
I populate the template with:
- **Actual values** - no placeholders like `[TODO]` or `[REPLACE THIS]`
- **Current timestamps** - using ISO format: `2025-01-10T14:30:00`
- **Specific descriptions** - clear, actionable content
- **Measurable criteria** - testable acceptance criteria with checkboxes

### Step 4: Save Specification
I save the spec to: `.quaestor/specs/draft/[spec-id].md`

The parser is forgiving:
- Wrong type? Auto-corrects (e.g., "removal" → "refactor")
- Missing fields? Uses sensible defaults
- Focus on content, not perfect formatting

### Step 5: Report Success
I confirm creation with:
- Spec ID
- File location
- Next steps (e.g., "Run `/impl spec-feature-001` to start implementation")

## Important Rules

### ✅ Always Use Actual Values
```markdown
# Good
id: spec-feature-001
type: feature
title: User Authentication System
description: Implement secure login with JWT tokens

# Bad
id: [SPEC_ID]
type: [TYPE]
title: [Feature Title]
description: TODO: Add description
```

### ✅ Generate Next Available Number
```bash
# Check existing specs
ls .quaestor/specs/draft/spec-feature-*.md
# If spec-feature-001 and spec-feature-002 exist, create spec-feature-003
```

### ✅ Use Checkboxes for Acceptance Criteria
```markdown
## Acceptance Criteria
- [ ] User can login with email and password
- [ ] Invalid credentials show error message
- [ ] Session expires after 24 hours
```

### ✅ Include Test Scenarios
Every spec should have at least 2 test scenarios:
1. Happy path (successful case)
2. Error case (failure handling)

## Examples

### Example 1: User Request
**User says**: "I want to add user authentication to the app"

**I respond**:
```
I'll create a specification for user authentication. Let me gather some details:

1. What authentication method? (email/password, OAuth, etc.)
2. Should sessions persist? For how long?
3. Any specific security requirements?
4. Password reset functionality needed?
```

After getting answers, I create `spec-feature-001.md` in `.quaestor/specs/draft/`

### Example 2: From Planning Data
**User provides**:
```yaml
title: "Fix memory leak in background processor"
type: bugfix
description: "Process doesn't release memory after job completion"
priority: high
```

**I create**: `spec-bugfix-001.md` with full template populated, including:
- Detailed description
- Steps to reproduce
- Acceptance criteria (memory usage tests)
- Test scenarios (monitor memory before/after)

## Integration

### Folder Structure
All new specs start in the draft folder:
```
.quaestor/specs/
├── draft/              # ← I create specs here
│   └── spec-*.md
├── active/             # User moves here when starting work (max 3)
└── completed/          # Moved here when done
```

### Next Steps After Creation
Once I create a spec, users can:
1. Review and edit the spec file directly
2. Move to active: "activate spec-feature-001"
3. Start implementation: `/impl spec-feature-001`
4. Check progress: "what's the status of spec-feature-001?"

## Tips for Best Results

### Be Specific
Instead of: "Add authentication"
Better: "Add email/password authentication with JWT tokens, 24-hour session expiry, and password reset via email"

### Define Success Clearly
Bad: "System works"
Good: "User can login in < 2 seconds, sessions persist across browser restarts, invalid credentials show within 500ms"

### Break Down Large Features
If a feature feels too big (> 5 acceptance criteria), suggest breaking into multiple specs:
- spec-auth-001: Basic login/logout
- spec-auth-002: Password reset
- spec-auth-003: OAuth integration

---

*I create clean, structured specifications that guide implementation and track progress. Just describe what you want to build, and I'll turn it into a proper spec!*
