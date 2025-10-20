# Specification Writing Guide

This file provides complete details for creating specifications. Only load when user needs template details or writing guidance.

## When to Load This File

- User asks: "What fields does a spec have?", "Show me the template"
- User wants examples of well-written specs
- User is confused about spec format
- Creating first spec and needs structure guidance

## The Markdown Specification Template

```markdown
---
id: spec-TYPE-NNN
type: feature  # feature, bugfix, refactor, documentation, performance, security, testing
status: draft
priority: medium  # critical, high, medium, or low
created_at: 2025-01-10T10:00:00
updated_at: 2025-01-10T10:00:00
---

# Descriptive Title

## Description
What needs to be done. Be specific and detailed.
Multiple paragraphs are fine.

## Rationale
Why this is needed.
What problem it solves.
Business or technical justification.

## Dependencies
- **Requires**: spec-001, spec-002 (specs that must be completed first)
- **Blocks**: spec-003 (specs that can't start until this is done)
- **Related**: spec-004 (related specs for context)

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
- [ ] Error cases handled gracefully
- [ ] Performance meets requirements

## Test Scenarios

### Happy path test
**Given**: Initial state
**When**: Action taken
**Then**: Expected result

### Error case test
**Given**: Invalid input
**When**: Action attempted
**Then**: Appropriate error message shown

## Metadata
estimated_hours: 8
technical_notes: Any technical considerations
branch: feat/feature-name (added when work starts)
```

## Spec ID Generation

I generate unique IDs based on type and existing specs:

```yaml
id_patterns:
  feature: "spec-feature-NNN"
  bugfix: "spec-bugfix-NNN"
  refactor: "spec-refactor-NNN"
  performance: "spec-perf-NNN"
  security: "spec-sec-NNN"
  testing: "spec-test-NNN"
  documentation: "spec-docs-NNN"

generation_process:
  1. Check existing specs in draft/ folder
  2. Find highest number for that type
  3. Increment by 1
  4. Zero-pad to 3 digits: 001, 002, etc.
```

**Example**: If `spec-feature-001` and `spec-feature-002` exist, next is `spec-feature-003`

## Field Descriptions

### Frontmatter Fields

**id** (required): Unique identifier
- Format: `spec-TYPE-NNN`
- Auto-generated from type and sequence
- Never changes once created

**type** (required): Category of work
- `feature` - New functionality
- `bugfix` - Fix broken behavior
- `refactor` - Improve code structure
- `documentation` - Docs/comments
- `performance` - Speed/efficiency
- `security` - Security improvements
- `testing` - Test coverage

**status** (auto-managed): Current state
- `draft` - Not started
- `active` - Work in progress
- `completed` - Finished
- **Folder determines status**, not this field

**priority** (required): Urgency level
- `critical` - Drop everything, do this now
- `high` - Important, schedule soon
- `medium` - Normal priority
- `low` - Nice to have, do when time allows

**created_at** / **updated_at** (auto): ISO timestamps
- Format: `2025-01-10T14:30:00`
- Created when spec is written
- Updated when spec is modified

### Content Sections

**Title** (required): Clear, descriptive name
- Bad: "Auth", "Fix bug", "Update code"
- Good: "User Authentication System", "Fix memory leak in processor", "Refactor payment validation logic"

**Description** (required): What needs to be done
- Be specific about functionality
- Include scope and boundaries
- Mention key components affected
- Multiple paragraphs encouraged

**Rationale** (required): Why this matters
- Business value or technical benefit
- Problem being solved
- Impact if not done

**Dependencies** (optional): Related specs
- **Requires**: Must be completed first
- **Blocks**: Prevents other specs from starting
- **Related**: Provides context

**Risks** (optional): Potential issues
- Technical risks
- Schedule risks
- Dependency risks

**Success Metrics** (optional): Measurable outcomes
- Performance targets
- Usage metrics
- Quality metrics

**Acceptance Criteria** (required): How to know it's done
- Use checkboxes: `- [ ]` and `- [x]`
- Be specific and testable
- Include error cases
- Minimum 3 criteria recommended

**Test Scenarios** (required): How to verify
- Happy path (success case)
- Error cases (failure handling)
- Edge cases (boundary conditions)
- Use Given/When/Then format

**Metadata** (optional): Additional info
- `estimated_hours`: Time estimate
- `technical_notes`: Implementation notes
- `branch`: Git branch name

## Writing Process

### Step 1: Interactive Requirements Gathering

**ALWAYS ask clarifying questions using AskUserQuestion tool:**

#### Required Information
If any of these are missing, ask:
- **Title**: "What are we building/fixing?" (if not provided)
- **Type**: Present options using AskUserQuestion - Feature, Bugfix, Refactor, Performance, Security, Testing, Documentation
- **Description**: "What exactly needs to be done?"
- **Scope**: "Should this include [related functionality]?"
- **Priority**: Ask to choose - Critical, High, Medium, or Low?

#### Decision Points
When multiple approaches exist, use AskUserQuestion:

**Example Question Pattern:**
```yaml
question: "I see multiple approaches for implementing [feature]. Which direction should we take?"
options:
  - label: "Approach A: [name]"
    description: "[description with trade-offs like: Simple but limited, Fast but complex, etc.]"
  - label: "Approach B: [name]"
    description: "[description with trade-offs]"
  - label: "Approach C: [name]"
    description: "[description with trade-offs]"
```

#### Trade-off Clarifications
When design choices exist, ask user to decide:
- "Optimize for speed or simplicity?"
- "Comprehensive feature OR minimal initial version?"
- "Integrate with [existing system] OR standalone?"
- "High performance OR easier maintenance?"

**Always use structured questions (AskUserQuestion tool) rather than open-ended prompts.**

### Step 2: Generate Unique ID

Check existing specs and create next available ID:
```bash
# Check what exists
ls .quaestor/specs/draft/spec-feature-*.md

# If spec-feature-001 and spec-feature-002 exist
# Create spec-feature-003
```

### Step 3: Fill Template with Actual Values

**Always use real values, never placeholders:**

✅ Good:
```yaml
id: spec-feature-001
title: User Authentication System
description: Implement secure login with JWT tokens and password hashing
```

❌ Bad:
```yaml
id: [SPEC_ID]
title: [Feature Title]
description: TODO: Add description
```

### Step 4: Create Checkboxes for Criteria

Make criteria specific and testable:

✅ Good:
```markdown
- [ ] User can login with email and password
- [ ] Invalid credentials show error within 500ms
- [ ] Session expires after 24 hours
- [ ] Logout clears session completely
```

❌ Bad:
```markdown
- [ ] Login works
- [ ] Errors handled
- [ ] Security is good
```

### Step 5: Save to Draft Folder

Write to `.quaestor/specs/draft/[spec-id].md`

All specs start in draft/ regardless of when they'll be worked on.

### Step 6: Report Success

Tell user:
- Spec ID created
- File location
- Next steps: "Run `/impl spec-feature-001` to start implementation"

## Important Rules

### ✅ Always Use Actual Values

Never use placeholders like `[TODO]`, `[REPLACE THIS]`, `[SPEC_ID]`

### ✅ Generate Sequential IDs

Check existing files to find next number for each type

### ✅ Include Test Scenarios

Every spec needs at least:
1. Happy path test
2. Error case test

### ✅ Make Criteria Testable

Each acceptance criterion should be verifiable:
- Can you write a test for it?
- Is success/failure clear?
- Is it specific enough?

## Examples

### Example 1: Feature Spec

**User request**: "I want to add email notifications when orders are placed"

**Created spec**: `spec-feature-001.md`
```markdown
---
id: spec-feature-001
type: feature
status: draft
priority: high
created_at: 2025-01-19T10:30:00
updated_at: 2025-01-19T10:30:00
---

# Order Confirmation Email Notifications

## Description
Send automated email notifications to customers when they successfully place an order. The email should include order details (items, quantities, total price), estimated delivery date, and a link to track the order.

## Rationale
Customers need immediate confirmation that their order was received. This reduces support inquiries about order status and provides professional customer experience. Industry standard for e-commerce platforms.

## Dependencies
- **Requires**: spec-email-001 (Email service integration)
- **Related**: spec-order-003 (Order processing system)

## Risks
- Email delivery failures (use queuing system)
- High volume during peak times (rate limiting needed)

## Success Metrics
- 95% email delivery rate within 30 seconds
- Less than 1% bounce rate
- Customer satisfaction score improvement

## Acceptance Criteria
- [ ] Email sent within 30 seconds of order placement
- [ ] Email contains all order items with prices
- [ ] Email includes estimated delivery date
- [ ] Tracking link works and shows order status
- [ ] Failed emails retry 3 times with exponential backoff
- [ ] Admin dashboard shows email delivery status

## Test Scenarios

### Successful order email
**Given**: User places order successfully
**When**: Order is confirmed in database
**Then**: Email is queued and sent within 30 seconds

### Email delivery failure
**Given**: Email service is temporarily down
**When**: System attempts to send email
**Then**: Email is queued for retry with exponential backoff

### High volume scenario
**Given**: 1000 orders placed simultaneously
**When**: System processes order confirmations
**Then**: All emails delivered within 5 minutes, no failures

## Metadata
estimated_hours: 12
technical_notes: Use SendGrid API, implement queue with Redis
```

### Example 2: Bugfix Spec

**User request**: "Memory leak in background processor needs fixing"

**Created spec**: `spec-bugfix-001.md`
```markdown
---
id: spec-bugfix-001
type: bugfix
status: draft
priority: critical
created_at: 2025-01-19T11:00:00
updated_at: 2025-01-19T11:00:00
---

# Fix Memory Leak in Background Job Processor

## Description
The background job processor accumulates memory over time and doesn't release it after job completion. Memory usage grows from 200MB to 2GB+ over 24 hours, eventually causing OOM crashes. Affects job processing for order fulfillment and email sending.

## Rationale
Critical production issue causing service restarts every 12 hours. Impacts order processing reliability and customer experience. Root cause is database connections not being properly closed after job completion.

## Dependencies
None

## Risks
- Fix might affect job processing throughput
- Need careful testing to avoid breaking existing jobs

## Success Metrics
- Memory usage stable at < 300MB over 72 hours
- No OOM crashes
- Job processing throughput unchanged

## Acceptance Criteria
- [ ] Memory usage remains stable over 72-hour test period
- [ ] Database connections properly closed after each job
- [ ] No memory leaks detected by profiler
- [ ] All existing job types still process correctly
- [ ] Performance benchmarks show no regression

## Test Scenarios

### Memory stability test
**Given**: Background processor running for 72 hours
**When**: 10,000 jobs processed during test period
**Then**: Memory usage remains under 300MB

### Connection cleanup verification
**Given**: Single job completes
**When**: Check database connection pool
**Then**: Connection is returned to pool and not held

## Metadata
estimated_hours: 6
technical_notes: Use context managers for DB connections, add memory profiling
```

### Example 3: Refactor Spec

**User request**: "Authentication logic is spread across 5 files, needs consolidation"

**Created spec**: `spec-refactor-001.md`
```markdown
---
id: spec-refactor-001
type: refactor
status: draft
priority: medium
created_at: 2025-01-19T11:30:00
updated_at: 2025-01-19T11:30:00
---

# Consolidate Authentication Logic

## Description
Authentication logic is currently scattered across 5 different files (api.py, middleware.py, services.py, utils.py, validators.py). This makes it hard to maintain, test, and understand the auth flow. Consolidate into a single AuthService class with clear responsibilities.

## Rationale
Technical debt causing maintenance issues. Recent security update required changes in 5 places. New developer onboarding takes longer due to scattered logic. Consolidation will improve testability and make security audits easier.

## Dependencies
None (existing functionality must continue working)

## Risks
- Regression in auth functionality
- Need comprehensive test coverage before refactoring

## Success Metrics
- Auth logic in single module with < 300 lines
- Test coverage > 90%
- No behavior changes (all existing tests pass)
- Reduced complexity score

## Acceptance Criteria
- [ ] All auth logic moved to single AuthService class
- [ ] Existing functionality unchanged (all tests pass)
- [ ] Test coverage increased to > 90%
- [ ] Documentation updated with new structure
- [ ] Code review approved by security team

## Test Scenarios

### Existing functionality preserved
**Given**: Complete existing test suite
**When**: Refactored code deployed
**Then**: All 127 existing tests pass without modification

### Improved testability
**Given**: New AuthService class
**When**: Write tests for edge cases
**Then**: Can test authentication logic in isolation

## Metadata
estimated_hours: 16
technical_notes: Start with comprehensive test coverage, refactor incrementally
```

## Tips for Best Specs

### Be Specific
- Instead of: "Add authentication"
- Better: "Add email/password authentication with JWT tokens, 24-hour session expiry, and password reset via email"

### Define Success Clearly
- Bad: "System works"
- Good: "User can login in < 2 seconds, sessions persist across browser restarts, invalid credentials show within 500ms"

### Break Down Large Features
If > 5 acceptance criteria, consider splitting:
- `spec-auth-001`: Basic login/logout
- `spec-auth-002`: Password reset
- `spec-auth-003`: OAuth integration

### Use Given/When/Then for Tests
Follows BDD format that's clear and testable:
```
Given: Initial state
When: Action taken
Then: Expected result
```

---

*This guide provides complete specification writing details. Return to SKILL.md for overview or LIFECYCLE.md for management operations.*
