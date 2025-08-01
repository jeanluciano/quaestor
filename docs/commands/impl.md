# /impl Command

The `/impl` command orchestrates the implementation workflow by automatically coordinating multiple agents to turn specifications into working code. It uses the [Architect](../agents/architect.md), [Implementer](../agents/implementer.md), and [QA](../agents/qa.md) agents in sequence.

## Overview

The implementation process follows this workflow:

```
Research → Architect → Implementer → QA → Review
```

Each agent contributes specialized expertise:
- **Research**: Understands existing codebase patterns
- **Architect**: Designs the technical approach
- **Implementer**: Writes production-quality code
- **QA**: Creates comprehensive tests
- **Review**: Validates code quality

## Usage

### Implement from Specification
```bash
/impl feat-auth-001
```

Implements a specific specification by:
1. Loading specification details and requirements
2. Analyzing existing codebase architecture
3. Designing technical implementation approach
4. Writing production code following established patterns
5. Creating comprehensive test suite
6. Performing code quality review

### Direct Feature Implementation
```bash
/impl "Add user profile management with avatar upload"
```

When no specification exists:
1. Creates specification using planner agent
2. Follows standard implementation workflow
3. Ensures all requirements are captured

### Complex Implementation
```bash
/impl "Implement OAuth2 authentication with Google, GitHub, and Microsoft providers"
```

For complex features:
- Breaks down into multiple components
- Coordinates multiple agents
- Manages dependencies between parts
- Ensures architectural consistency

## Implementation Workflow

### Phase 1: Research & Analysis
The researcher agent:
- Analyzes existing codebase patterns
- Identifies similar implementations
- Maps dependencies and integration points
- Documents current architecture

```bash
# Research findings example
Found existing authentication patterns:
- JWT token handling in auth/tokens.py
- User model in models/user.py
- Password hashing utilities in utils/crypto.py
- API middleware in middleware/auth.py
```

### Phase 2: Architecture Design
The architect agent:
- Reviews research findings
- Designs technical approach
- Defines component boundaries
- Creates implementation plan

```yaml
# Architecture decisions
components:
  - OAuth2Manager: Handle provider configurations
  - TokenExchange: Convert OAuth tokens to JWT
  - UserProfile: Link OAuth accounts to users
  - ProviderFactory: Instantiate OAuth providers

integration_points:
  - Existing JWT system (preserve compatibility)
  - User model (extend with OAuth fields)
  - API endpoints (add OAuth routes)
```

### Phase 3: Implementation
The implementer agent:
- Follows architectural design
- Writes production-quality code
- Implements error handling
- Adds comprehensive logging

```python
# Code quality standards
class OAuth2Manager:
    """Manages OAuth2 authentication providers."""
    
    def __init__(self, config: OAuth2Config):
        self.providers = self._initialize_providers(config)
        self.logger = get_logger(__name__)
    
    async def authenticate(
        self, 
        provider: str, 
        code: str
    ) -> AuthResult:
        """Authenticate user via OAuth2 provider."""
        if provider not in self.providers:
            raise UnsupportedProviderError(f"Provider {provider} not configured")
        
        try:
            # Implementation details...
            pass
        except Exception as e:
            self.logger.error(f"OAuth2 auth failed: {e}")
            raise AuthenticationError("OAuth2 authentication failed")
```

### Phase 4: Testing
The QA agent:
- Creates unit tests for all components
- Implements integration tests
- Adds end-to-end test scenarios
- Validates edge cases

```python
# Test coverage example
class TestOAuth2Manager:
    """Comprehensive OAuth2 manager tests."""
    
    @pytest.fixture
    def oauth_manager(self):
        return OAuth2Manager(test_config)
    
    async def test_successful_authentication(self, oauth_manager):
        """Test successful OAuth2 flow."""
        # Test implementation
        
    async def test_invalid_provider(self, oauth_manager):
        """Test handling of unsupported provider."""
        # Test implementation
        
    async def test_network_failure(self, oauth_manager):
        """Test resilience to network failures."""
        # Test implementation
```

### Phase 5: Review
The reviewer agent:
- Validates code quality standards
- Checks security best practices
- Reviews test coverage
- Ensures documentation completeness

## Command Options

### `--fast`
Skip detailed analysis for simple implementations:
```bash
/impl --fast "Add logging to user service"
```

### `--agents`
Specify which agents to use:
```bash
/impl --agents=architect,implementer "Design and build API endpoint"
```

### `--test-coverage`
Set minimum test coverage requirement:
```bash
/impl --test-coverage=90 feat-payment-001
```

### `--review-level`
Control review thoroughness:
```bash
/impl --review-level=strict feat-security-001
```

## Integration Patterns

### Database Changes
```bash
/impl "Add user preferences table with migration"
```

Automatically handles:
- Database schema design
- Migration script creation
- Model updates
- Repository pattern implementation

### API Endpoints
```bash
/impl "Create REST API for task management"
```

Includes:
- Route definitions and handlers
- Input validation and serialization
- Error handling and responses
- API documentation updates

### Frontend Components
```bash
/impl "Build user dashboard with charts"
```

Covers:
- Component architecture
- State management integration
- Styling and responsive design
- Unit and integration tests

## Quality Standards

### Code Quality
- Clean, readable code with meaningful names
- Comprehensive error handling
- Proper input validation
- Consistent formatting and style

### Testing
- Unit tests for all business logic
- Integration tests for component interactions
- End-to-end tests for critical user flows
- Minimum 80% code coverage

### Documentation
- Clear docstrings for all public methods
- API documentation updates
- Usage examples where appropriate
- Architecture decision records

### Security
- Input sanitization and validation
- Proper authentication and authorization
- Secure data handling practices
- No hardcoded secrets or credentials

## Common Implementation Scenarios

### New Feature Development
```bash
/impl "Add two-factor authentication"
```

Complete implementation including:
- Backend authentication logic
- Database schema changes
- Frontend user interface
- Email/SMS integration
- Comprehensive testing

### Bug Fixes
```bash
/impl "Fix race condition in order processing"
```

Systematic approach:
- Root cause analysis
- Minimal invasive fixes
- Regression test creation
- Performance impact assessment

### Performance Optimization
```bash
/impl "Optimize database queries in user search"
```

Optimization strategy:
- Performance profiling
- Query optimization
- Caching implementation
- Benchmark validation

### Refactoring
```bash
/impl "Refactor authentication middleware"
```

Safe refactoring approach:
- Preserve existing functionality
- Improve code structure
- Maintain test coverage
- Update documentation

## Best Practices

### 1. Start with Specifications
```bash
# Better: Use existing specification
/impl feat-notifications-001

# Good: Let planner create specification first
/impl "Add push notifications"
```

### 2. Provide Clear Context
```bash
# Good context
/impl "Add rate limiting to API endpoints using Redis, supporting 1000 requests per minute per user"

# Insufficient context
/impl "add rate limiting"
```

### 3. Consider Existing Patterns
The implementer automatically:
- Follows existing code patterns
- Uses established libraries
- Maintains architectural consistency
- Preserves existing interfaces

### 4. Iterative Implementation
For complex features:
```bash
/impl "User authentication - Phase 1: Basic login"
/impl "User authentication - Phase 2: Password reset"
/impl "User authentication - Phase 3: OAuth providers"
```

## Troubleshooting

### Implementation Failures
If implementation fails:
1. Review error messages for specific issues
2. Check if dependencies are missing
3. Verify specification requirements are clear
4. Use debugger agent for complex issues

### Test Failures
When tests fail:
1. QA agent provides detailed failure analysis
2. Implementer fixes failing tests
3. Additional test scenarios added if needed

### Code Quality Issues
If review finds problems:
1. Specific improvement recommendations provided
2. Code automatically updated to meet standards
3. Additional documentation added if needed

## Monitoring Implementation

### Progress Tracking
```bash
quaestor status feat-auth-001    # Check implementation progress
quaestor agents status           # See active agent work
```

### Quality Metrics
- Code coverage percentage
- Cyclomatic complexity scores
- Security vulnerability counts
- Performance benchmark results

## Next Steps

- Learn about the [/review Command](review.md) for code quality validation
- Explore [Specification-Driven Development](../specs/workflow.md)
- Understand [Agent Collaboration](../agents/overview.md)
- Read about [Code Quality Standards](../advanced/architecture.md)