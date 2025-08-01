# Specification Implementation Workflow

A complete guide to implementing features using specification-driven development.

## Overview

The specification workflow follows a structured path from creation to deployment:

1. **Create** specification with clear contract
2. **Review** and approve the specification
3. **Implement** according to the contract
4. **Test** against acceptance criteria
5. **Deploy** and mark complete

## Workflow Steps

### 1. Create Specification

Start by creating a detailed specification:

```
/plan --spec "Shopping Cart Checkout"
```

The planner agent helps define:
- Clear contract with inputs/outputs
- Behavioral requirements
- Acceptance criteria
- Test scenarios

### 2. Branch Creation and Linking

Specifications automatically create and link to git branches:

```
Branch: feat/spec-checkout-001-shopping-cart
```

Branch naming follows the pattern: `{type}/spec-{id}-{brief-title}`

If you need to link an existing branch:
```
/plan --link
```

### 3. Implementation

Implement according to the specification contract:

```
/impl "implement shopping cart checkout"
```

The implementation command:
- Loads the specification contract
- Follows defined behavior rules
- Implements according to acceptance criteria
- Updates specification status

### 4. Progress Tracking

View progress with the dashboard:

```
/plan
```

Shows:
- Active specifications and their status
- Implementation progress per spec
- Test coverage
- Release readiness

### 5. Status Updates

Specifications progress through these statuses:

- **Draft**: Initial creation
- **Approved**: Ready for implementation
- **In Progress**: Implementation started
- **Implemented**: Code complete
- **Tested**: All tests passing
- **Deployed**: Live in production

## Example: Complete Workflow

### Step 1: Create API Specification

```
/plan --spec "User Registration API"
```

**Generated Specification:**
```yaml
id: feat-api-002
title: User Registration API
contract:
  inputs:
    - email: string (valid email format)
    - password: string (min 8 chars, complexity rules)
    - name: string (required)
  outputs:
    - user: User object (without password)
    - token: JWT authentication token
    - status: 201 created, 400 validation error
  behavior:
    - Validate email format and uniqueness
    - Enforce password complexity rules
    - Hash password before storage
    - Generate JWT token
    - Send welcome email
```

### Step 2: Implementation

```
/impl "create user registration endpoint"
```

Implementation follows the contract:
- Validates inputs as specified
- Implements exact behavior rules
- Returns outputs in defined format
- Handles errors appropriately

### Step 3: Testing

Tests are based on specification scenarios:

```python
def test_valid_registration():
    """Test scenario: Valid user registration"""
    # Given: Valid user data
    data = {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }
    
    # When: Registration request sent
    response = client.post("/api/register", json=data)
    
    # Then: User created successfully
    assert response.status_code == 201
    assert "token" in response.json()
    assert "user" in response.json()
```

### Step 4: Status Updates

As work progresses, update the specification status:

```yaml
# In specification file or via agent
status: implemented  # When code is complete
status: tested      # When all tests pass
status: deployed    # When live in production
```

## Working with Multiple Specifications

### Viewing All Specifications

```
/plan
```

Dashboard shows:
```
📋 Active Specifications:
• [feat-api-002] User Registration API
  Status: IN_PROGRESS • Branch: feat/spec-api-002-user-reg
  Contract: ✅ Defined • Tests: [██████░░░░] 6/10
  
• [feat-ui-003] Login Form Component  
  Status: APPROVED • Branch: feat/spec-ui-003-login-form
  Contract: ✅ Defined • Tests: [░░░░░░░░░░] 0/8
```

### Prioritizing Work

Specifications include priority levels:
- **Critical**: Must be done immediately
- **High**: Important for current development cycle
- **Medium**: Should be done soon
- **Low**: Nice to have

### Managing Dependencies

Some specifications depend on others:

```yaml
dependencies:
  - feat-api-002  # User Registration API
  - feat-db-001   # User Database Schema
```

Implement dependencies first for smooth workflow.

## Best Practices

### During Implementation

1. **Follow the Contract**: Implement exactly what's specified
2. **Update Status**: Keep specification status current
3. **Test Continuously**: Validate against acceptance criteria
4. **Document Changes**: Note any deviations from spec

### Quality Checks

- All acceptance criteria met
- Test scenarios pass
- Code follows specification behavior
- Error handling matches contract
- Performance meets constraints

### Collaboration

- Specifications serve as documentation
- Team members can review contracts
- Clear interfaces between components
- Consistent implementation standards

## Troubleshooting

### Specification Not Linked to Branch

```
# Link current branch to specification
/plan --link

# Or rename branch to follow pattern
git branch -m feat/spec-{id}-{title}
```

### Unclear Requirements

```
# Use planner agent to refine specification
/plan --spec "refine existing specification"
```

### Implementation Deviations

If implementation needs to deviate from specification:
1. Update the specification first
2. Document the reason for changes
3. Update tests and acceptance criteria
4. Get review/approval if needed

The specification should always reflect the actual implementation.