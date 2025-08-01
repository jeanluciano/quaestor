# Creating Specifications

Learn how to create well-structured specifications that drive successful implementation.

## Using the /plan Command

The primary way to create specifications is through the `/plan --spec` command:

```
/plan --spec "User Profile Management"
```

This invokes the planner agent, which will guide you through:

1. **Title and Description**: What you want to build
2. **Type Classification**: Feature, bugfix, refactor, etc.
3. **Contract Definition**: Inputs, outputs, and behavior
4. **Acceptance Criteria**: Success conditions
5. **Test Scenarios**: Validation cases

## Interactive Creation Process

### Step 1: Basic Information
The planner agent will ask:
- What is the main objective?
- What type of work is this?
- Why is this needed?
- What's the priority level?

### Step 2: Contract Definition
Define the specification contract:

**Inputs**: What data/parameters are required?
```yaml
inputs:
  user_id: string (UUID format, required)
  profile_data: object (name, email, bio)
  auth_token: string (JWT format)
```

**Outputs**: What will be produced/returned?
```yaml
outputs:
  updated_profile: User object
  success_message: string
  status_code: HTTP status (200, 400, 500)
```

**Behavior**: What are the key rules and logic?
```yaml
behavior:
  - Validate user_id format and existence
  - Authenticate user via JWT token
  - Update profile fields with validation
  - Return success confirmation
  - Handle errors gracefully
```

### Step 3: Acceptance Criteria
Measurable conditions for completion:
- [ ] User can update profile with valid data
- [ ] Invalid data returns validation errors
- [ ] Unauthorized requests are rejected
- [ ] Profile changes are persisted
- [ ] Success/error messages are clear

### Step 4: Test Scenarios
Given/When/Then test cases:

```gherkin
Scenario: Valid profile update
  Given user is authenticated with valid token
  And profile data is valid
  When profile update request is sent
  Then profile is updated successfully
  And success message is returned

Scenario: Invalid authentication
  Given user has expired token
  When profile update request is sent
  Then request is rejected with 401 error
  And appropriate error message is returned
```

## Specification Output

After creation, you'll get a complete specification:

```yaml
Specification Created:
  ID: feat-profile-001
  Title: User Profile Management
  Type: feature
  Priority: high
  Status: DRAFT → APPROVED
  
  Contract:
    Inputs: [user_id, profile_data, auth_token]
    Outputs: [updated_profile, success_message, status_code]
    Behavior: [4 defined rules]
      
  Branch: feat/spec-profile-001-user-profile
  
  Next Steps:
  1. Review specification contract
  2. Begin implementation
  3. Update spec status as you progress
```

## Best Practices

### Contract Definition
- **Be Specific**: Exact data types and formats
- **Include Constraints**: Size limits, validation rules
- **Define Errors**: What can go wrong and how to handle it
- **Performance**: Response time requirements

### Acceptance Criteria
- **Measurable**: Can be objectively verified
- **Complete**: Cover all important functionality
- **User-Focused**: Written from user perspective
- **Testable**: Can be automated or manually tested

### Test Scenarios
- **Happy Path**: Normal, successful usage
- **Edge Cases**: Boundary conditions and limits
- **Error Cases**: Invalid inputs and failure conditions
- **Integration**: How it works with other components

## Common Patterns

### API Endpoint Specification
```yaml
contract:
  inputs:
    - endpoint: GET /api/users/{id}
    - path_params: {id: string}
    - headers: {Authorization: Bearer token}
  outputs:
    - response: JSON user object
    - status: 200 success, 404 not found
  behavior:
    - Validate user ID format
    - Check authentication
    - Query user database
    - Return formatted response
```

### UI Component Specification
```yaml
contract:
  inputs:
    - props: {user: object, onSave: function}
    - state: component internal state
  outputs:
    - rendered: JSX component
    - events: onSave callback with data
  behavior:
    - Display user information
    - Handle form interactions
    - Validate input data
    - Emit save events
```

### Data Processing Specification
```yaml
contract:
  inputs:
    - data: array of objects
    - filters: filtering criteria
    - options: processing options
  outputs:
    - processed_data: transformed array
    - metadata: processing statistics
  behavior:
    - Apply filters to dataset
    - Transform data according to rules
    - Generate processing metadata
    - Handle empty or invalid data
```

## Tips for Success

1. **Start Simple**: Basic contract first, refine later
2. **Think User-First**: What does the user need?
3. **Be Explicit**: Don't assume implicit behavior
4. **Include Examples**: Concrete examples clarify requirements
5. **Review Together**: Get feedback before implementation