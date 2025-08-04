# Quick Start Guide

Get up and running with Quaestor in minutes.

## 1. Initialize Your Project

Navigate to your project directory and initialize Quaestor:

```bash
cd your-project
quaestor init
```

This creates the `.quaestor/` directory with:
- Configuration files
- Memory management templates
- Hook system
- Agent definitions

## 2. Create Your First Specification

Use the `/plan` command to create a specification:

```
/plan --spec "User Authentication System"
```

The planner agent will guide you through:
- Defining the specification title and description
- Creating the contract (inputs, outputs, behavior)
- Setting acceptance criteria
- Generating test scenarios
- Linking to a git branch

## 3. Implement the Specification

Once your specification is created, implement it:

```
/impl "implement user authentication according to spec"
```

The implementation command will:
- Load the specification contract
- Create implementation following the defined behavior
- Write tests based on the test scenarios
- Update specification status as work progresses

## 4. Track Progress

View your progress dashboard:

```
/plan
```

This shows:
- Active specifications and their status
- Implementation progress
- Test coverage
- Release readiness

## Example Workflow

Let's walk through creating a simple API endpoint:

### Step 1: Create Specification
```
/plan --spec "User Profile API Endpoint"
```

**Planner Agent Response:**
```yaml
Specification: feat-api-001
Title: User Profile API Endpoint
Contract:
  inputs:
    - user_id: string (UUID format)
    - request: HTTP GET request
  outputs:
    - user_profile: JSON object
    - status_code: 200 on success, 404 if not found
  behavior:
    - Validate user_id format
    - Query database for user profile
    - Return formatted JSON response
    - Handle missing user gracefully
```

### Step 2: Implement
```
/impl "create the user profile endpoint"
```

### Step 3: Test and Validate
The specification includes test scenarios that guide implementation:
```gherkin
Scenario: Valid user profile request
  Given a user exists with ID "123e4567-e89b-12d3-a456-426614174000"
  When GET /api/users/123e4567-e89b-12d3-a456-426614174000
  Then return status 200 and user profile JSON
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `/plan` | Show dashboard or create specifications |
| `/plan --spec "Title"` | Create new specification |
| `/plan --link` | Link current branch to specification |
| `/impl "description"` | Implement features |
| `/research "topic"` | Research and analyze |
| `/review` | Code review and quality checks |

## Project Structure

After initialization, your project will have:

```
your-project/
├── .quaestor/
│   ├── specs/                # Specification lifecycle folders
│   │   ├── draft/           # New specifications under review
│   │   ├── active/          # Currently being implemented
│   │   └── completed/       # Finished implementations
│   └── .workflow_state       # Current workflow state
├── .claude/
│   ├── commands/             # Slash command definitions
│   ├── agents/              # AI agent configurations
│   └── hooks/               # Automation hooks
└── your-code/
```

## Best Practices

1. **Start with Specifications**: Always create a specification before implementing
2. **Clear Contracts**: Define precise inputs, outputs, and behavior rules
3. **Test Scenarios**: Include comprehensive test cases in specifications
4. **Progress Tracking**: Use `/plan` regularly to monitor progress
5. **Branch Naming**: Follow the `feat/spec-{id}-{title}` pattern

## Next Steps

- Learn about [Configuration](configuration.md) options
- Explore [Specification-Driven Development](../specs/overview.md)
- Understand the [Agent System](../agents/overview.md)
- Set up [Custom Hooks](../hooks/custom.md)

## Troubleshooting

**Commands not working?**
- Ensure you're in a Quaestor-initialized project
- Check that Claude Code is running
- Verify `.quaestor/` directory exists

**Specifications not linking to branches?**
- Use `/plan --link` to manually link
- Check branch naming follows the spec pattern
- Ensure hooks are properly configured