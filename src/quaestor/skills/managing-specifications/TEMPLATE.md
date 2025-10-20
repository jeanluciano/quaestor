# Specification Template Reference

This file provides a field-by-field reference for the specification template. Only load when user asks specific questions about template structure or field meanings.

## When to Load This File

- User asks: "What does the rationale field mean?"
- User wants field examples: "Show me examples of good acceptance criteria"
- User is confused about a specific section
- User wants to understand optional vs required fields

## Complete Template Structure

```markdown
---
# FRONTMATTER (YAML metadata)
id: spec-TYPE-NNN                    # Required: Unique identifier
type: feature                        # Required: Category of work
status: draft                        # Required: Current state
priority: medium                     # Required: Urgency level
created_at: 2025-01-19T10:00:00     # Required: Creation timestamp
updated_at: 2025-01-19T10:00:00     # Required: Last modified timestamp
---

# Title                              # Required: Clear, descriptive name

## Description                       # Required: What needs to be done
What exactly needs to be implemented, fixed, or changed.
Be specific about functionality, scope, and affected components.

## Rationale                         # Required: Why this matters
Business value, technical benefit, or problem being solved.
Explain the impact if this is not done.

## Dependencies                      # Optional: Related specifications
- **Requires**: spec-001            # Must be done before this
- **Blocks**: spec-003              # This blocks other work
- **Related**: spec-004             # Context, not blocking

## Risks                             # Optional: Potential issues
- Technical risks
- Schedule risks
- Dependency risks

## Success Metrics                   # Optional: Measurable outcomes
- Performance targets
- Usage metrics
- Quality metrics

## Acceptance Criteria               # Required: How to know it's done
- [ ] Specific, testable criterion
- [ ] Another specific criterion
- [ ] Include error cases
- [ ] Minimum 3 criteria recommended

## Test Scenarios                    # Required: How to verify

### Happy path test                  # At least one success case
**Given**: Initial state
**When**: Action taken
**Then**: Expected result

### Error case test                  # At least one failure case
**Given**: Invalid input
**When**: Action attempted
**Then**: Appropriate error shown

## Metadata                          # Optional: Additional info
estimated_hours: 8
technical_notes: Implementation notes
branch: feat/feature-name           # Added when work starts
```

## Field Reference

### Frontmatter Fields

#### id (Required)
**Format**: `spec-TYPE-NNN`

**Purpose**: Unique identifier that never changes

**Type Prefixes**:
- `spec-feature-NNN` - New functionality
- `spec-bugfix-NNN` - Fix broken behavior
- `spec-refactor-NNN` - Improve code structure
- `spec-perf-NNN` - Performance improvements
- `spec-sec-NNN` - Security enhancements
- `spec-test-NNN` - Test coverage
- `spec-docs-NNN` - Documentation

**Numbering**: Zero-padded 3 digits (001, 002, ..., 999)

**Examples**:
```yaml
id: spec-feature-001
id: spec-bugfix-023
id: spec-refactor-005
```

**Rules**:
- Generated automatically from type + next available number
- Never changes once created
- Must be unique across all specs

---

#### type (Required)
**Values**: `feature | bugfix | refactor | documentation | performance | security | testing`

**Purpose**: Categorize the work type

**Descriptions**:
```yaml
feature:
  description: "New functionality or capability"
  examples:
    - "User authentication system"
    - "Export to PDF feature"
    - "Real-time notifications"

bugfix:
  description: "Fix broken or incorrect behavior"
  examples:
    - "Fix memory leak in processor"
    - "Correct calculation error"
    - "Resolve null pointer exception"

refactor:
  description: "Improve code structure without changing behavior"
  examples:
    - "Consolidate authentication logic"
    - "Simplify database queries"
    - "Extract reusable components"

documentation:
  description: "Add or improve documentation"
  examples:
    - "API documentation"
    - "Add code comments"
    - "Update README"

performance:
  description: "Improve speed, efficiency, or resource usage"
  examples:
    - "Optimize database queries"
    - "Implement caching"
    - "Reduce memory usage"

security:
  description: "Security improvements or vulnerability fixes"
  examples:
    - "Add input validation"
    - "Implement rate limiting"
    - "Fix SQL injection vulnerability"

testing:
  description: "Add or improve test coverage"
  examples:
    - "Add unit tests for auth module"
    - "Implement E2E tests"
    - "Improve test coverage to 80%"
```

**Auto-Correction**: Parser auto-corrects common mistakes
- "removal" → "refactor"
- "fix" → "bugfix"
- "test" → "testing"

---

#### status (Required, Auto-Managed)
**Values**: `draft | active | completed`

**Purpose**: Track current state (managed by folder location)

**Note**: Folder location is source of truth, this field is kept in sync

```yaml
status: draft      # In .quaestor/specs/draft/
status: active     # In .quaestor/specs/active/
status: completed  # In .quaestor/specs/completed/
```

---

#### priority (Required)
**Values**: `critical | high | medium | low`

**Purpose**: Indicate urgency and importance

**Guidelines**:
```yaml
critical:
  when: "Production down, security vulnerability, data loss risk"
  sla: "Drop everything, fix immediately"
  examples:
    - "Production outage"
    - "Security breach"
    - "Data corruption"

high:
  when: "Important feature, significant bug, blocking other work"
  sla: "Schedule this week"
  examples:
    - "Key customer feature"
    - "Major bug affecting users"
    - "Blocking other development"

medium:
  when: "Normal priority work, planned features, minor bugs"
  sla: "Schedule in sprint"
  examples:
    - "Planned feature work"
    - "Minor bug fixes"
    - "Technical debt"

low:
  when: "Nice to have, minor improvements, future work"
  sla: "Do when time allows"
  examples:
    - "Nice to have features"
    - "Minor improvements"
    - "Future enhancements"
```

---

#### created_at / updated_at (Required, Auto)
**Format**: ISO 8601 timestamp `YYYY-MM-DDTHH:MM:SS`

**Purpose**: Track when spec was created and last modified

**Examples**:
```yaml
created_at: 2025-01-19T10:30:00
updated_at: 2025-01-19T14:45:00
```

**Auto-Management**:
- `created_at`: Set once when spec is created
- `updated_at`: Updated whenever spec content changes

---

### Content Sections

#### Title (Required)
**Location**: First H1 heading after frontmatter

**Purpose**: Clear, descriptive name of the work

**Guidelines**:
```yaml
do:
  - Use clear, descriptive names
  - Be specific about what's being done
  - Include key context

dont:
  - Use vague terms: "Fix bug", "Update code"
  - Use technical jargon without context
  - Make it too long (> 80 chars)
```

**Examples**:
```markdown
# Good
- User Authentication System with JWT Tokens
- Fix Memory Leak in Background Job Processor
- Refactor Payment Validation Logic
- Optimize Database Query Performance

# Bad
- Auth
- Fix Bug
- Update Code
- Make It Faster
```

---

#### Description (Required)
**Location**: `## Description` section

**Purpose**: Detailed explanation of what needs to be done

**What to Include**:
- Specific functionality or changes
- Scope and boundaries
- Key components affected
- Current state vs desired state

**Example Structure**:
```markdown
## Description
[Opening paragraph: What needs to be done]

[Current state: How things work now]

[Desired state: How things should work]

[Scope: What's included and excluded]

[Key components: What parts of system affected]
```

**Good Example**:
```markdown
## Description
Implement a user authentication system with email/password login,
JWT-based session management, and secure password storage using bcrypt.

Current state: No authentication system exists. All endpoints are public.

Desired state: Users must authenticate to access protected endpoints.
Sessions persist for 24 hours with automatic renewal. Passwords are
securely hashed and never stored in plain text.

Scope includes:
- Login/logout endpoints
- JWT token generation and validation
- Password hashing with bcrypt
- Session management middleware

Scope excludes:
- OAuth/social login (future enhancement)
- Password reset (separate spec: spec-auth-002)
- Multi-factor authentication (future enhancement)
```

---

#### Rationale (Required)
**Location**: `## Rationale` section

**Purpose**: Explain WHY this work matters

**What to Include**:
- Business value or technical benefit
- Problem being solved
- Impact if not done
- Alignment with goals

**Example Structure**:
```markdown
## Rationale
[Why this is needed]

[Problem being solved]

[Business/technical impact]

[What happens if not done]
```

**Good Example**:
```markdown
## Rationale
User authentication is essential for protecting user data and enabling
personalized features. Currently, all endpoints are public, exposing
sensitive user information and preventing per-user customization.

Problem solved: Unauthorized access to user data and inability to track
user-specific actions.

Business impact: Enables premium features, protects user privacy, meets
security compliance requirements.

If not done: Cannot launch paid features, risk data breaches, fail
security audits, lose customer trust.
```

---

#### Dependencies (Optional)
**Location**: `## Dependencies` section

**Purpose**: Link to related specifications

**Format**:
```markdown
## Dependencies
- **Requires**: spec-001, spec-002
- **Blocks**: spec-003, spec-004
- **Related**: spec-005
```

**Relationship Types**:
```yaml
Requires:
  meaning: "These must be completed before this spec can start"
  use_when: "Hard dependency on other work"
  example: "Requires: spec-email-001 (email service must exist)"

Blocks:
  meaning: "This spec prevents other specs from starting"
  use_when: "Other work depends on this being done"
  example: "Blocks: spec-auth-002 (password reset needs auth)"

Related:
  meaning: "Related for context, not blocking"
  use_when: "Useful context, not a hard dependency"
  example: "Related: spec-user-001 (user profile system)"
```

---

#### Risks (Optional)
**Location**: `## Risks` section

**Purpose**: Identify potential issues or challenges

**Categories**:
```yaml
technical_risks:
  - "Complex integration with third-party service"
  - "Database migration required"
  - "Performance impact on existing features"

schedule_risks:
  - "Depends on external team's timeline"
  - "Blocked by infrastructure work"
  - "May require more time than estimated"

dependency_risks:
  - "Third-party API may change"
  - "Requires approval from security team"
  - "Depends on unstable library"

mitigation:
  - "Include how to reduce or handle each risk"
```

**Good Example**:
```markdown
## Risks
- **Performance risk**: Auth middleware adds latency to every request.
  Mitigation: Cache token validation, use fast JWT library.

- **Security risk**: Password storage vulnerability if implemented wrong.
  Mitigation: Use battle-tested bcrypt library, security review required.

- **Schedule risk**: Depends on database migration (spec-db-001).
  Mitigation: Can implement with mock data, migrate later.
```

---

#### Success Metrics (Optional)
**Location**: `## Success Metrics` section

**Purpose**: Define measurable outcomes

**What to Include**:
- Performance targets
- Usage metrics
- Quality metrics
- Business metrics

**Good Example**:
```markdown
## Success Metrics
- Authentication latency < 200ms (p95)
- Session validation < 50ms (p95)
- Zero security vulnerabilities in audit
- 99.9% uptime for auth service
- 100% of protected endpoints require auth
- Password hashing takes 200-300ms (bcrypt security)
```

---

#### Acceptance Criteria (Required)
**Location**: `## Acceptance Criteria` section

**Purpose**: Define what "done" means with testable criteria

**Format**: Checklist with `- [ ]` or `- [x]`

**Guidelines**:
```yaml
do:
  - Make each criterion specific and testable
  - Include happy path and error cases
  - Minimum 3 criteria (typically 5-8)
  - Use action verbs: "User can...", "System will..."
  - Be precise with numbers and timeframes

dont:
  - Use vague criteria: "System works well"
  - Forget error cases
  - Make criteria too large (break down if > 10)
  - Forget non-functional requirements
```

**Good Example**:
```markdown
## Acceptance Criteria
- [ ] User can login with valid email and password
- [ ] Invalid credentials return 401 with error message
- [ ] Successful login returns JWT token valid for 24 hours
- [ ] Token automatically refreshes 1 hour before expiration
- [ ] User can logout and invalidate their token
- [ ] Logout clears session and prevents token reuse
- [ ] Protected endpoints return 401 without valid token
- [ ] Passwords are hashed with bcrypt (cost factor 12)
- [ ] Login attempts are rate-limited (5 per minute)
```

**Bad Example**:
```markdown
## Acceptance Criteria
- [ ] Login works
- [ ] Errors handled
- [ ] Security is good
```

---

#### Test Scenarios (Required)
**Location**: `## Test Scenarios` section

**Purpose**: Describe how to verify acceptance criteria

**Format**: Given/When/Then (BDD style)

**Minimum**: 2 scenarios (happy path + error case)

**Structure**:
```markdown
### [Scenario Name]
**Given**: [Initial state / preconditions]
**When**: [Action taken]
**Then**: [Expected result]
```

**Good Example**:
```markdown
## Test Scenarios

### Successful login
**Given**: User has account with email "user@example.com" and password "SecurePass123"
**When**: User submits correct credentials to /login endpoint
**Then**: System returns 200 status with JWT token valid for 24 hours

### Invalid password
**Given**: User exists with email "user@example.com"
**When**: User submits incorrect password
**Then**: System returns 401 status with error "Invalid credentials"

### Token expiration
**Given**: User has JWT token that expired 1 minute ago
**When**: User attempts to access protected endpoint
**Then**: System returns 401 status with error "Token expired"

### Rate limiting
**Given**: User has attempted login 5 times in last minute
**When**: User attempts 6th login
**Then**: System returns 429 status with error "Too many attempts"
```

---

#### Metadata (Optional)
**Location**: `## Metadata` section

**Purpose**: Additional information for tracking

**Common Fields**:
```markdown
## Metadata
estimated_hours: 8
actual_hours: 10
technical_notes: Using JWT library "jsonwebtoken", bcrypt cost factor 12
branch: feat/user-authentication
assignee: @developer-name
labels: security, backend, high-priority
```

**Field Meanings**:
```yaml
estimated_hours:
  description: "Time estimate before starting"
  use: "Planning and capacity"

actual_hours:
  description: "Actual time spent (filled after completion)"
  use: "Improve future estimates"

technical_notes:
  description: "Implementation details, library choices, etc"
  use: "Context for implementers"

branch:
  description: "Git branch name for this work"
  use: "Link spec to code changes"
  added_when: "Work starts (activation)"

assignee:
  description: "Who's working on this"
  use: "Track ownership"

labels:
  description: "Tags for categorization"
  use: "Filtering and reporting"
```

---

## Template Validation

### Required Fields Check
```yaml
must_have:
  - id
  - type
  - status
  - priority
  - created_at
  - updated_at
  - title
  - description
  - rationale
  - acceptance_criteria (at least 1)
  - test_scenarios (at least 1)

can_warn_if_missing:
  - dependencies
  - risks
  - success_metrics
  - metadata
```

### Quality Checks
```yaml
description:
  min_length: 50 characters
  recommendation: "2-4 paragraphs"

rationale:
  min_length: 30 characters
  recommendation: "Explain business/technical value"

acceptance_criteria:
  min_count: 3
  recommendation: "5-8 criteria typical"
  format: "Use checkboxes [ ] or [x]"

test_scenarios:
  min_count: 2
  recommendation: "At least happy path + error case"
  format: "Use Given/When/Then"
```

---

## Quick Reference

### Minimal Valid Spec
```markdown
---
id: spec-feature-001
type: feature
status: draft
priority: medium
created_at: 2025-01-19T10:00:00
updated_at: 2025-01-19T10:00:00
---

# Feature Title

## Description
What needs to be done.

## Rationale
Why this matters.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Test Scenarios

### Happy path
**Given**: Initial state
**When**: Action
**Then**: Result
```

### Complete Spec
See WRITING.md for complete examples with all optional sections filled.

---

*This template reference provides field-by-field details. Return to SKILL.md for overview, WRITING.md for creation process, or LIFECYCLE.md for management operations.*
