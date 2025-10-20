# /plan Command

The `/plan` command activates the spec-driven-development skill to create lightweight specifications from requirements. It transforms ideas into actionable specs with acceptance criteria.

## Overview

The /plan command helps you:
- Create specifications with unique IDs
- Define acceptance criteria as checkboxes
- Track progress through folder-based state
- Maintain focus with max 3 active specs

## Usage

### Basic Planning
```bash
/plan "Add user authentication system"
```

Creates a specification in `.quaestor/specs/draft/` including:
- Title and description
- Motivation (why you're building it)
- Acceptance criteria (checkboxes)
- Unique spec ID (e.g., spec-auth-001)

### Managing Specifications

You can also use natural language to manage specs:
```bash
"Show my active specs"
"Activate spec-feature-001"
"Complete spec-auth-001"
```

The spec-driven-development skill handles lifecycle management automatically.

## Specification Structure

Specifications are lightweight markdown files:

```markdown
---
spec_id: "spec-auth-001"
title: "User Authentication"
status: "draft"
created: "2024-01-15"
---

# User Authentication

## Motivation
Users need secure authentication to access protected resources.

## Acceptance Criteria
- [ ] User can login with email/password
- [ ] System returns JWT access token
- [ ] Invalid credentials return 401 error
- [ ] Rate limiting prevents brute force attacks
- [ ] Tokens expire after 24 hours
```

## Spec Lifecycle

Specs move through folders as they progress:

```
.quaestor/specs/
├── draft/      # Planned work (unlimited)
├── active/     # In progress (max 3)
└── completed/  # Finished work
```

**Lifecycle transitions:**
- `draft/` → `active/` : Start working on a spec
- `active/` → `completed/` : All criteria checked off
- Max 3 active specs enforced (finish before starting new work)

## Progress Tracking

Progress is automatically calculated from checkboxes:
- `- [ ]` = incomplete
- `- [x]` = complete
- Progress: 3/5 complete = 60%

## Integration with Other Commands

### Sequential Workflow
```bash
/plan "Add user profiles"         # Create spec
/implement spec-profiles-001      # Implement it
"Create a pull request"           # Ship it
```

## Tips for Effective Planning

### 1. Be Specific
```bash
# Good
/plan "Add JWT authentication with refresh tokens and rate limiting"

# Too vague
/plan "add auth"
```

### 2. Define Clear Success Criteria
Each spec should have measurable acceptance criteria:
- ✅ "User can complete checkout in under 30 seconds"
- ❌ "Checkout should be fast"

### 3. Break Down Large Features
```bash
# Instead of one large spec
/plan "Complete e-commerce platform"

# Create focused specifications
/plan "Product catalog with search"
/plan "Shopping cart functionality"
/plan "Checkout and payment processing"
```

## Next Steps

- Use [/implement Command](implement.md) to implement specifications
- Learn about [Specification-Driven Development](../specs/overview.md)
- Explore [Skills](../skills/overview.md) that power /plan
