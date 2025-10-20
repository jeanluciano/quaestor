# /implement Command

The `/implement` command activates the implementation-workflow skill to turn specifications into working code with quality gates and automatic progress tracking.

## Overview

The implementation-workflow skill:
- Loads specifications and requirements
- Guides implementation with quality checks
- Tracks progress via TODOs
- Runs tests and validates acceptance criteria
- Updates spec status automatically

## Usage

### Implement from Specification
```bash
/implement spec-auth-001
```

The skill will:
1. Load the specification
2. Review acceptance criteria
3. Set up TODO tracking
4. Guide you through implementation
5. Run tests and verify criteria
6. Update specification progress

### Implement by Description
```bash
/implement "Add user profile management"
```

If no specification exists, the skill will create one first, then proceed with implementation.

## Implementation Workflow

The implementation-workflow skill coordinates multiple sub-agents internally:

**Research Phase:**
- Analyzes existing codebase patterns
- Identifies similar implementations
- Maps dependencies and integration points

**Design Phase:**
- Reviews research findings
- Designs technical approach
- Defines component boundaries

**Implementation Phase:**
- Writes production-quality code
- Follows established patterns
- Implements error handling and logging

**Testing Phase:**
- Creates unit tests for all components
- Implements integration tests
- Validates edge cases

**Review Phase:**
- Validates code quality standards
- Checks security best practices
- Reviews test coverage
- Ensures documentation completeness

## Quality Standards

The skill enforces:
- Clean, readable code with meaningful names
- Comprehensive error handling
- Proper input validation
- Minimum 80% test coverage
- Security best practices
- No hardcoded secrets

## Progress Tracking

The skill uses TODOs to track implementation progress:
```bash
# Creates TODOs automatically based on acceptance criteria
✓ Implement login endpoint
✓ Add JWT token generation
⧖ Create token validation middleware
  Implement logout functionality
  Add password hashing
```

As you complete TODOs, the specification progress updates automatically.

## Integration Patterns

### Database Changes
```bash
/implement "Add user preferences table"
```

Automatically handles:
- Database schema design
- Migration script creation
- Model updates
- Repository pattern implementation

### API Endpoints
```bash
/implement "Create REST API for task management"
```

Includes:
- Route definitions and handlers
- Input validation and serialization
- Error handling and responses
- API documentation updates

### Bug Fixes
```bash
/implement "Fix race condition in order processing"
```

Systematic approach:
- Root cause analysis
- Minimal invasive fixes
- Regression test creation
- Performance impact assessment

## Best Practices

### 1. Start with Specifications
```bash
# Better: Use existing specification
/implement spec-notifications-001

# Good: Let skill create specification first
/implement "Add push notifications"
```

### 2. Provide Clear Context
```bash
# Good context
/implement "Add rate limiting using Redis, supporting 1000 requests per minute per user"

# Insufficient context
/implement "add rate limiting"
```

### 3. Review Before Shipping
After implementation completes:
```bash
"Create a pull request for spec-auth-001"
```

The review-and-ship skill will validate code quality before creating the PR.

## Next Steps

- Learn about the [/plan Command](plan.md) for creating specifications
- Explore [Specification-Driven Development](../specs/workflow.md)
- Understand [Skills](../skills/overview.md) that power /implement
