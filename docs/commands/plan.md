# /plan Command

The `/plan` command is Quaestor's primary planning interface that uses the [Planner Agent](../agents/planner.md) to create detailed specifications from requirements. It transforms ideas into actionable, testable specifications with clear contracts and acceptance criteria.

## Overview

The planner specializes in:
- Creating detailed specifications with unique IDs
- Breaking down complex requirements into manageable parts
- Defining clear input/output contracts
- Writing comprehensive acceptance criteria
- Estimating implementation effort

## Usage

### Basic Planning
```bash
/plan "Add user authentication system"
```

Creates a comprehensive specification including:
- Use case analysis
- Input/output contracts
- Acceptance criteria
- Test scenarios in BDD format
- Effort estimation

### Complex Feature Planning
```bash
/plan "Implement real-time chat with presence indicators, message history, and file sharing"
```

The planner will:
1. Break down into multiple specifications
2. Identify dependencies between components
3. Create implementation roadmap
4. Estimate complexity for each part

### Analysis Mode
```bash
/plan --analyze
```

Provides strategic analysis of:
- Current specification status
- Implementation bottlenecks
- Resource allocation
- Timeline projections

## Specification Output Format

The planner creates specifications following this structure:

```yaml
---
spec_id: "feat-auth-001"
title: "Implement JWT Authentication"
type: "feature"
status: "draft"
priority: "high"
created: "2024-01-15"
author: "planner"
---

# Specification: JWT Authentication System

## Use Case Overview
- **ID**: feat-auth-001
- **Primary Actor**: Application users
- **Goal**: Secure authentication with JWT tokens
- **Priority**: high

## Context & Background
Users need secure authentication to access protected resources. Current system lacks proper session management and scalable authentication mechanisms.

## Main Success Scenario
1. User provides valid credentials (email/password)
2. System validates credentials against user database
3. System generates JWT access token (24h expiry)
4. System generates refresh token (30d expiry)
5. System returns both tokens to client
6. Client uses access token for API requests

## Contract Definition

### Inputs
```yaml
inputs:
  email:
    type: "string"
    description: "User's email address"
    required: true
    validation: "valid email format"
  password:
    type: "string"
    description: "User's password"
    required: true
    validation: "minimum 8 characters"
```

### Outputs
```yaml
outputs:
  auth_response:
    type: "object"
    description: "Authentication response with tokens"
    schema:
      access_token: "string (JWT)"
      refresh_token: "string"
      expires_in: "number (seconds)"
      user_id: "string"
```

### Behavior Rules
- Passwords must be hashed using bcrypt with salt rounds >= 12
- JWT tokens must include user_id, role, and expiration claims
- Refresh tokens must be stored securely and be revocable
- Failed login attempts must be rate limited (5 attempts per 15 minutes)
- Successful login resets failed attempt counter

## Acceptance Criteria
- [ ] User can login with valid email/password
- [ ] System returns JWT access token valid for 24 hours
- [ ] System returns refresh token valid for 30 days
- [ ] Invalid credentials return 401 error
- [ ] Rate limiting prevents brute force attacks
- [ ] Tokens can be used to access protected endpoints
- [ ] Refresh token can generate new access token

## Test Scenarios

### Scenario 1: Successful Login
```gherkin
Given a registered user with email "user@example.com"
And the user has password "SecurePass123!"
When the user attempts to login
Then a JWT access token should be returned
And the token should be valid for 24 hours
And a refresh token should be returned
And the user_id should match the authenticated user
```

### Scenario 2: Invalid Credentials
```gherkin
Given a user provides email "user@example.com"
And an incorrect password "wrongpass"
When the user attempts to login
Then a 401 Unauthorized error should be returned
And no tokens should be generated
And the failed attempt should be recorded
```

### Scenario 3: Rate Limiting
```gherkin
Given a user has failed login 5 times in 15 minutes
When the user attempts to login again
Then a 429 Too Many Requests error should be returned
And no authentication attempt should be processed
```

## Dependencies
- Depends on: user-db-001 (User database schema)
- Blocks: protected-routes-001 (Protected API endpoints)

## Estimated Effort
- Complexity: Medium (6-8 hours)
- Testing: 3-4 hours
- Documentation: 1 hour
- Total: 10-13 hours
```

## Planning Best Practices

### 1. Be Specific with Requirements
```bash
# Good
/plan "Add JWT authentication with refresh tokens, rate limiting, and password reset functionality"

# Too vague
/plan "add auth"
```

### 2. Include Context
```bash
/plan "Migrate user authentication from session-based to JWT tokens while maintaining backward compatibility"
```

### 3. Consider Non-Functional Requirements
```bash
/plan "Design file upload system that handles 100MB files with progress tracking and virus scanning"
```

## Command Options

### `--complexity` 
Specify expected complexity level:
```bash
/plan --complexity=high "Design distributed caching system"
```

### `--type`
Specify specification type:
```bash
/plan --type=bugfix "Fix memory leak in background processor"
/plan --type=refactor "Restructure authentication middleware"
```

### `--priority`
Set specification priority:
```bash
/plan --priority=critical "Fix security vulnerability in user session"
```

## Integration with Other Commands

### Sequential Workflow
```bash
/plan "Add user profiles"      # Creates specification
/impl feat-profiles-001        # Implements the specification
/review feat-profiles-001      # Reviews implementation
```

### Parallel Planning
```bash
/plan "Frontend user interface"
/plan "Backend API endpoints"
/plan "Database schema changes"
```

## Specification Management

### Viewing Specifications
```bash
quaestor specs list            # List all specifications
quaestor specs show feat-auth-001  # Show specific spec
```

### Updating Specifications
```bash
/plan --update feat-auth-001 "Add OAuth2 provider support"
```

### Specification Status
- `draft`: Initial creation
- `approved`: Ready for implementation
- `in_progress`: Being implemented
- `completed`: Implementation finished
- `blocked`: Waiting for dependencies

## Tips for Effective Planning

### 1. Break Down Large Features
```bash
# Instead of one large spec
/plan "Complete e-commerce platform"

# Create focused specifications
/plan "Product catalog with search"
/plan "Shopping cart functionality"
/plan "Checkout and payment processing"
/plan "Order management system"
```

### 2. Define Clear Success Criteria
Each specification should have measurable acceptance criteria:
- ✅ "User can complete checkout in under 30 seconds"
- ❌ "Checkout should be fast"

### 3. Consider Edge Cases
Include error scenarios and boundary conditions:
- What happens with invalid input?
- How are rate limits handled?
- What's the behavior during system failures?

### 4. Plan for Testing
Each specification includes:
- Happy path scenarios
- Error case scenarios
- Performance requirements
- Security considerations

## Common Planning Patterns

### Feature Development
```bash
/plan "Feature: Real-time notifications"
# Creates: UI components, WebSocket handling, notification storage
```

### Bug Fixes
```bash
/plan "Fix: Memory leak in image processing"
# Creates: Root cause analysis, fix strategy, regression tests
```

### Performance Improvements
```bash
/plan "Optimize: Database query performance"
# Creates: Performance benchmarks, optimization strategies, monitoring
```

### Security Enhancements
```bash
/plan "Security: Add input validation middleware"
# Creates: Threat analysis, validation rules, security tests
```

## Next Steps

- Learn about the [/impl Command](impl.md) for implementing specifications
- Explore [Specification-Driven Development](../specs/overview.md)
- Understand [Agent Collaboration](../agents/overview.md)
- Read about [Creating Specifications](../specs/creating.md)