# /research Command

The `/research` command uses specialized research agents to deeply explore and understand your codebase. It provides comprehensive analysis of patterns, dependencies, architecture, and implementation details to inform development decisions.

## Overview

The research command employs the specialized **Researcher** agent which provides:
- **Pattern analysis**: Discovery of recurring code patterns and their usage
- **Architectural exploration**: Deep system architecture understanding
- **Dependency mapping**: Impact assessment and relationship analysis

Research helps with:
- Understanding existing code patterns
- Finding implementation examples
- Mapping system dependencies
- Identifying architectural decisions
- Discovering hidden connections

## Usage

### Basic Code Research
```bash
/research "How is user authentication currently implemented?"
```

Provides comprehensive analysis:
- Authentication patterns and mechanisms
- Related code files and components
- Security implementations
- Integration points with other systems

### Pattern Discovery
```bash
/research "Find all database access patterns"
```

Returns:
- Repository implementations
- ORM usage patterns
- Database connection management
- Query optimization techniques
- Transaction handling approaches

### Dependency Analysis
```bash
/research "What components depend on the user service?"
```

Maps:
- Direct dependencies and imports
- Service call relationships
- Data flow connections
- Event/message dependencies
- Configuration dependencies

## Research Types

### 1. Pattern Analysis
Identifies recurring code patterns and their usage:

```bash
/research --type=patterns "error handling"
```

**Output Example:**
```markdown
## Error Handling Patterns Found

### Pattern 1: Service Layer Exceptions
- **Files**: 12 services use this pattern
- **Implementation**: Custom exception classes with error codes
- **Usage**: `raise UserNotFoundError(user_id, code='USER_404')`

### Pattern 2: API Error Responses
- **Files**: All API endpoints in `routes/` directory
- **Implementation**: Centralized error handler middleware
- **Usage**: Automatic conversion of exceptions to HTTP responses

### Pattern 3: Logging Integration
- **Files**: Throughout codebase via logger injection
- **Implementation**: Structured logging with correlation IDs
- **Usage**: `logger.error("Operation failed", extra={"user_id": user_id})`
```

### 2. Architecture Exploration
Maps system architecture and component relationships:

```bash
/research --type=architecture "authentication system"
```

**Output Example:**
```markdown
## Authentication System Architecture

### Core Components
```
┌─────────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│  Auth Service   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │  Token Manager  │       │  User Provider  │
          └─────────────────┘       └─────────────────┘
```

### Integration Points
- **JWT Middleware**: Validates tokens on all protected routes
- **Session Store**: Redis-backed session management
- **User Database**: PostgreSQL user accounts table
- **External Auth**: OAuth2 providers (Google, GitHub)
```

### 3. Usage Discovery
Finds how specific components or functions are used:

```bash
/research --type=usage "EmailService.send_notification"
```

**Output Example:**
```markdown
## EmailService.send_notification Usage Analysis

### Direct Callers (8 locations)
1. **UserRegistrationHandler** - Welcome emails
2. **PasswordResetService** - Reset instructions
3. **NotificationProcessor** - System alerts
4. **OrderService** - Order confirmations

### Notification Types
- `welcome`: New user registration (avg 50/day)
- `password_reset`: Password reset requests (avg 20/day)
- `order_confirm`: Order confirmations (avg 200/day)
- `system_alert`: Critical system notifications (avg 5/day)

### Dependencies
- Requires: SMTP configuration
- Templates: Located in `templates/email/`
- Queue: Uses Celery for async processing
```

### 4. Impact Assessment
Analyzes the impact of potential changes:

```bash
/research --impact "changing User model schema"
```

**Output Example:**
```markdown
## Impact Analysis: User Model Schema Changes

### Direct Impact (High Risk)
- **Database migrations**: Requires schema migration
- **Serializers**: 6 API serializers need updates
- **Forms**: 4 web forms require field changes

### Indirect Impact (Medium Risk)
- **Cached data**: User data cached in Redis
- **External APIs**: User data exported to analytics
- **Background jobs**: 3 jobs process user data

### Testing Requirements
- Unit tests: 23 tests need updates
- Integration tests: 8 API tests affected
- End-to-end tests: User registration flow

### Rollback Strategy
- Database migration rollback plan needed
- Cache invalidation strategy required
- API versioning considerations
```

## Advanced Research Options

### `--depth`
Control research thoroughness:
```bash
/research --depth=shallow "basic authentication flow"  # Quick overview
/research --depth=deep "authentication system"         # Comprehensive analysis
```

### `--format`
Specify output format:
```bash
/research --format=json "API endpoints"        # Machine-readable output
/research --format=diagram "system architecture"  # Visual diagrams
/research --format=report "security analysis"     # Detailed report
```

### `--scope`
Limit research scope:
```bash
/research --scope=backend "user management"    # Backend code only
/research --scope=frontend "authentication"    # Frontend code only
/research --scope=database "data relationships" # Database schema only
```

## Research Workflows

### 1. New Feature Planning
Before implementing new features:

```bash
/research "similar features in codebase"
/research "integration patterns for new service"
/research "testing strategies used in project"
```

### 2. Bug Investigation
When investigating issues:

```bash
/research "error handling in payment processing"
/research "logging patterns for debugging"
/research "transaction boundaries in order system"
```

### 3. Refactoring Preparation
Before major refactoring:

```bash
/research --impact "extracting authentication service"
/research "current service boundaries"
/research "shared utilities and their usage"
```

### 4. Onboarding Support
For new team members:

```bash
/research "project architecture overview"
/research "coding conventions and patterns"
/research "deployment and configuration setup"
```

## Integration with Other Commands

### Research → Plan → Implement
```bash
/research "existing user profile features"     # Understand current state
/plan "enhanced user profile with avatars"     # Plan improvements
/impl spec-user-profile-002                    # Implement changes
```

### Research → Review
```bash
/research "security patterns in auth system"   # Understand security approach
/review --security auth-service.py            # Apply security review
```

## Research Output Examples

### Code Pattern Analysis
```python
# Research finds this pattern repeated across services:
class BaseService:
    def __init__(self, db: Database, logger: Logger):
        self.db = db
        self.logger = logger
    
    async def execute_with_transaction(self, operation):
        async with self.db.transaction():
            try:
                return await operation()
            except Exception as e:
                self.logger.error(f"Operation failed: {e}")
                raise ServiceError(f"Operation failed") from e
```

### Dependency Mapping
```yaml
# Service dependency graph
UserService:
  depends_on:
    - DatabaseConnection
    - EmailService
    - CacheManager
  used_by:
    - AuthenticationController
    - UserProfileController
    - AdminUserController
  
EmailService:
  depends_on:
    - SMTPConfig
    - TemplateEngine
  used_by:
    - UserService
    - NotificationService
    - OrderService
```

### Architecture Insights
```markdown
## Current Authentication Architecture

### Strengths
- ✅ JWT-based stateless authentication
- ✅ Centralized token validation
- ✅ Role-based access control
- ✅ Refresh token rotation

### Weaknesses
- ⚠️ Token revocation requires database lookup
- ⚠️ No distributed session management
- ⚠️ Limited audit logging

### Recommendations
1. Implement Redis-based token blacklist
2. Add distributed session store
3. Enhance audit logging with correlation IDs
```

## Best Practices

### 1. Start Broad, Then Focus
```bash
# Start with high-level overview
/research "system architecture"

# Then dive into specific areas
/research "authentication implementation details"
```

### 2. Use Research for Decision Making
```bash
# Before choosing implementation approach
/research "existing async processing patterns"
/research "message queue implementations in use"
```

### 3. Regular Architecture Reviews
```bash
# Periodic architecture analysis
/research --type=architecture "service boundaries"
/research --type=dependencies "tight coupling analysis"
```

### 4. Document Findings
Research outputs can be saved and shared:
```bash
/research "API design patterns" > docs/architecture/api-patterns.md
```

## Tips for Effective Research

### 1. Be Specific in Queries
```bash
# Good: Specific and actionable
/research "Redis caching patterns for user data"

# Too broad: May return unfocused results
/research "caching"
```

### 2. Use Research Before Major Changes
Always research before:
- Adding new dependencies
- Changing core interfaces
- Implementing new patterns
- Major refactoring efforts

### 3. Combine with Other Tools
```bash
# Research + external documentation
/research "OAuth2 implementation" && open docs/auth/oauth2.md

# Research + code review
/research "error handling patterns" && /review --focus=errors src/services/
```

## Common Research Scenarios

### Understanding Legacy Code
```bash
/research "deprecated authentication methods"
/research "migration path from session to JWT"
```

### Security Analysis
```bash
/research "input validation patterns"
/research "security middleware implementations"
```

### Performance Investigation
```bash
/research "database query optimization techniques"
/research "caching strategies for user data"
```

### Testing Strategy
```bash
/research "unit testing patterns for async code"
/research "integration test setup and teardown"
```

## Next Steps

- Learn about the [/review Command](review.md) for code quality analysis
- Explore [Architecture Documentation](../advanced/architecture.md)
- Understand [Specification-Driven Development](../specs/overview.md)
- Read about [Agent Collaboration](../agents/overview.md)