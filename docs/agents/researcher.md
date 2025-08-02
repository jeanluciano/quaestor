# Researcher Agent

The Researcher Agent specializes in deep code analysis, pattern discovery, and system understanding. It provides comprehensive insights into codebases, identifies architectural patterns, and discovers implementation details to inform development decisions.

## Overview

The Researcher Agent excels at:
- **Pattern Discovery**: Finding recurring code patterns and architectural decisions
- **Dependency Analysis**: Mapping system dependencies and relationships
- **Usage Discovery**: Understanding how components are used throughout the system
- **Impact Assessment**: Analyzing the effects of potential changes
- **Knowledge Extraction**: Extracting insights from existing code and documentation

## When to Use the Researcher Agent

### 🔍 Before Implementation
```bash
# Understanding existing patterns before adding new features
/research "authentication patterns in the codebase"
/research "database access layer implementation"
/research "error handling strategies used"
```

### 🧭 System Understanding
```bash
# Getting oriented in a new or complex codebase
/research "overall system architecture"  
/research "service boundaries and communication"
/research "data flow through the application"
```

### 📊 Impact Analysis
```bash
# Before making significant changes
/research --impact "changing user model schema"
/research "components that depend on auth service"
/research "files that would be affected by API changes"
```

## Research Capabilities

### Code Pattern Analysis

The Researcher Agent identifies and analyzes recurring patterns:

```python
# Pattern Discovery Example
@researcher.analyze_patterns("error handling")
def find_error_patterns():
    """
    Discovers patterns like:
    - Service layer exception handling
    - API error response formatting  
    - Logging and monitoring integration
    - User-facing error messages
    """
    return {
        "service_exceptions": "Custom exception classes with error codes",
        "api_responses": "Centralized error handler middleware", 
        "logging": "Structured logging with correlation IDs",
        "user_messages": "Internationalized error messages"
    }
```

### Dependency Mapping

Comprehensive analysis of system relationships:

```yaml
# Dependency Analysis Output
UserService:
  depends_on:
    - DatabaseConnection: "Required for user data access"
    - EmailService: "For user notifications"
    - CacheManager: "For session and profile caching"
    - AuthTokenManager: "For JWT token operations"
  
  used_by:
    - AuthenticationController: "Login/logout operations"
    - UserProfileController: "Profile management"
    - AdminUserController: "User administration"
    - NotificationService: "User-specific notifications"
    
  integration_points:
    - REST_API: "/api/users/* endpoints"
    - Database: "users, user_profiles, user_sessions tables"
    - Events: "UserCreated, UserUpdated, UserDeleted events"
    - Cache: "user:{id} cache keys"
```

### Usage Analysis

Understanding how components are actually used:

```python
# Usage Analysis Example
@researcher.analyze_usage("EmailService.send_notification")
def analyze_email_usage():
    """
    Returns detailed usage information:
    - Call frequency and patterns
    - Parameter variations
    - Error handling approaches
    - Performance characteristics
    """
    return {
        "call_frequency": "~300 calls/day average",
        "primary_callers": [
            "UserRegistrationHandler: welcome emails",
            "PasswordResetService: reset instructions", 
            "OrderService: order confirmations",
            "NotificationProcessor: system alerts"
        ],
        "common_parameters": {
            "template_types": ["welcome", "password_reset", "order_confirm"],
            "languages": ["en", "es", "fr"],
            "priorities": ["normal", "high"]
        },
        "error_patterns": "Retry logic with exponential backoff"
    }
```

### Architecture Discovery

Identifying architectural patterns and decisions:

```yaml
# Architecture Analysis Output
Architecture_Patterns:
  Overall_Style: "Layered Architecture with Service Layer"
  
  Layers:
    Presentation: 
      - "REST API controllers in /api"
      - "Request/response DTOs"
      - "Input validation middleware"
    
    Business:
      - "Service classes in /services"
      - "Domain models in /models" 
      - "Business rule validation"
    
    Data:
      - "Repository pattern implementation"
      - "Database entities with ORM"
      - "Data access abstractions"
  
  Cross_Cutting:
    - "Dependency injection container"
    - "Centralized logging and monitoring"
    - "Configuration management"
    - "Error handling and recovery"
    
  Design_Patterns:
    - "Repository: Data access abstraction"
    - "Service Layer: Business logic encapsulation"
    - "Factory: Object creation"
    - "Observer: Event handling"
```

## Research Types

### Pattern Research
```bash
/research --type=patterns "caching implementation"
```

**Analysis Focus:**
- Identifies all caching patterns in the codebase
- Documents cache key strategies and TTL policies
- Maps cache invalidation approaches
- Finds performance optimization techniques

### Architectural Research
```bash
/research --type=architecture "microservices communication"
```

**Analysis Focus:**
- Maps service-to-service communication patterns
- Identifies API contracts and data formats
- Documents error handling and retry strategies
- Analyzes service discovery and load balancing

### Security Research
```bash
/research --type=security "authentication and authorization"
```

**Analysis Focus:**
- Maps authentication flows and token handling
- Identifies authorization patterns and role management
- Documents security validation and sanitization
- Finds potential security vulnerabilities

### Performance Research
```bash  
/research --type=performance "database query optimization"
```

**Analysis Focus:**
- Identifies slow queries and N+1 problems
- Maps database access patterns and connection usage
- Documents caching strategies and hit rates
- Analyzes algorithmic complexity and bottlenecks

## Research Output Examples

### Code Pattern Documentation
```markdown
## Authentication Patterns Found

### Pattern 1: JWT Token Management
**Implementation**: Custom TokenManager class
**Usage**: All API endpoints use @auth_required decorator
**Security**: Tokens expire after 24 hours with refresh capability

### Pattern 2: Role-Based Authorization
**Implementation**: Role enum with permission mapping
**Usage**: @requires_role("admin") decorators on sensitive endpoints  
**Security**: Principle of least privilege with role inheritance

### Pattern 3: Password Security
**Implementation**: bcrypt with salt rounds = 12
**Usage**: UserService.hash_password() for all password operations
**Security**: Password strength validation on frontend and backend
```

### Dependency Analysis Report
```yaml
# High-Level Dependencies
External_Dependencies:
  Critical:
    - PostgreSQL: "Primary data storage"
    - Redis: "Caching and session storage"
    - AWS_S3: "File and image storage"
  
  Optional:
    - Stripe: "Payment processing"
    - SendGrid: "Email delivery"
    - Elasticsearch: "Search functionality"

Internal_Dependencies:
  Core_Services:
    - UserService: "Used by 15+ components"
    - AuthService: "Used by all protected endpoints"
    - NotificationService: "Used by 8 components"
  
  Utility_Modules:
    - DatabaseManager: "Used by all services"
    - Logger: "Used throughout application"
    - ConfigManager: "Used by all modules"
```

### Impact Assessment Report
```markdown
## Impact Analysis: Changing User Model Schema

### Direct Impact (High Risk)
- **UserService**: Core service requires updates to all methods
- **AuthenticationController**: Login/logout flows need modification
- **UserRepository**: Database queries and mappings need updates
- **API_Responses**: User data serialization needs changes

### Indirect Impact (Medium Risk) 
- **CacheManager**: User data cached in Redis needs invalidation
- **NotificationService**: User preferences structure may change
- **AuditLogger**: User activity logging format needs updates
- **ReportGenerator**: User analytics queries need modification

### Testing Impact (High Priority)
- **Unit_Tests**: 23 test files need updates for new schema
- **Integration_Tests**: 8 API tests need new assertions
- **E2E_Tests**: User registration/profile flows need updates
- **Performance_Tests**: User data loading benchmarks need updates

### Migration Strategy
1. **Database**: Create migration script with rollback plan
2. **Code**: Update models, services, and controllers incrementally  
3. **Cache**: Clear user caches during deployment
4. **API**: Maintain backward compatibility with versioning
5. **Tests**: Update test fixtures and expectations
```

## Best Practices

### 1. Start Broad, Then Focus
```bash
# Begin with high-level understanding
/research "system architecture overview"

# Then drill down into specific areas
/research "user authentication implementation details"
```

### 2. Use Research for Decision Making
```bash
# Before choosing implementation approach
/research "existing async processing patterns"
/research "message queue implementations in use"

# Then make informed decisions based on findings
```

### 3. Combine Research Types
```bash
# Comprehensive analysis using multiple research types
/research --type=architecture,security "API gateway implementation"
```

### 4. Document and Share Findings
Research outputs can be saved and shared with the team:
```bash
/research "authentication patterns" > docs/architecture/auth-patterns.md
```

## Integration with Other Agents

### Research → Plan → Implement
```bash
/research "existing user management features"     # Understand current state
/plan "enhanced user profiles with social login"  # Plan based on research
/impl spec-user-social-001                       # Implement using insights
```

### Research → Review
```bash
/research "security patterns in payment system"   # Understand security approach
/review --security payment-service.py            # Apply security review based on patterns
```

### Research → Debug
```bash
/research "error handling patterns"              # Understand error handling approach
/debug "inconsistent error responses in API"     # Debug using pattern knowledge
```

## Common Research Scenarios

### New Team Member Onboarding
```bash
/research "project architecture and key patterns"
/research "development workflow and testing strategies"
/research "deployment process and infrastructure"
```

### Before Major Refactoring
```bash
/research --impact "extracting user service to microservice"
/research "current service boundaries and communication"
/research "shared utilities and their usage patterns"
```

### Technology Migration Planning
```bash
/research "current database access patterns"
/research "ORM usage and query complexity"  
/research "transaction boundaries and data consistency"
```

### Performance Investigation
```bash
/research "slow endpoints and their dependencies"
/research "database query patterns and optimization"
/research "caching strategies and hit rates"
```

## Advanced Features

### Cross-Reference Analysis
```python
# Find relationships between different patterns
@researcher.cross_reference()
def analyze_pattern_relationships():
    """
    Identifies how different patterns interact:
    - Authentication + Authorization patterns
    - Caching + Database access patterns
    - Error handling + Logging patterns
    """
```

### Historical Analysis
```python
# Analyze how patterns have evolved
@researcher.historical_analysis()
def track_pattern_evolution():
    """
    Uses git history to understand:
    - How patterns have changed over time
    - Why certain decisions were made
    - Evolution of architectural approaches
    """
```

### Code Quality Insights
```python
# Identify code quality patterns
@researcher.quality_analysis()
def analyze_code_quality():
    """
    Identifies quality patterns:
    - Consistent naming conventions
    - Test coverage patterns
    - Documentation approaches
    - Code complexity trends
    """
```

## Next Steps

- Learn about the [Planner Agent](planner.md) for using research in planning
- Explore [Architect Agent](architect.md) for architectural insights
- Understand [Implementation Agent](implementer.md) for applying research
- Read about [Agent Collaboration](overview.md) for multi-agent workflows