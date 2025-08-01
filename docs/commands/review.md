# /review Command

The `/review` command provides comprehensive code review using specialized reviewer agents that focus on quality, security, performance, and architectural consistency. It performs deep analysis beyond basic linting to ensure production-ready code.

## Overview

The review process employs multiple specialized agents:
- **Reviewer**: General code quality and best practices
- **Security**: Security vulnerability detection and secure coding practices
- **Performance**: Performance analysis and optimization recommendations
- **Architect**: Architectural consistency and design pattern validation

Reviews cover:
- Code quality and maintainability
- Security vulnerabilities and risks
- Performance bottlenecks and optimizations
- Architectural consistency
- Test coverage and quality
- Documentation completeness

## Usage

### Review Specific Files
```bash
/review src/auth/service.py
```

Performs comprehensive analysis:
- Code quality assessment
- Security vulnerability scan
- Performance optimization opportunities
- Best practice compliance
- Documentation review

### Review by Specification
```bash
/review feat-auth-001
```

Reviews all files related to a specification:
- Implementation completeness
- Requirement fulfillment
- Test coverage adequacy
- Documentation accuracy

### Full Project Review
```bash
/review --all
```

Comprehensive project-wide review:
- Architectural consistency
- Cross-cutting concerns
- Integration patterns
- Overall code quality metrics

## Review Types

### 1. Quality Review
Focuses on code quality and maintainability:

```bash
/review --type=quality src/services/
```

**Analysis Areas:**
- Code complexity and readability
- Naming conventions
- Function and class design
- Error handling patterns
- Code duplication
- Maintainability metrics

**Example Output:**
```markdown
## Code Quality Review: UserService

### Issues Found

#### High Priority
- **Method Complexity**: `process_user_registration()` has cyclomatic complexity of 12 (max 10)
  - **File**: src/services/user_service.py:45
  - **Recommendation**: Extract validation logic into separate methods

#### Medium Priority  
- **Long Method**: `validate_user_data()` has 58 lines (max 50)
  - **File**: src/services/user_service.py:103
  - **Recommendation**: Split into focused validation methods

### Positive Patterns
- ✅ Consistent error handling with custom exceptions
- ✅ Proper dependency injection pattern
- ✅ Clear separation of concerns
```

### 2. Security Review
Identifies security vulnerabilities and risks:

```bash
/review --type=security src/api/
```

**Analysis Areas:**
- Input validation and sanitization
- Authentication and authorization
- Data exposure risks
- Injection vulnerabilities
- Cryptographic practices
- Secure coding patterns

**Example Output:**
```markdown
## Security Review: Authentication API

### Critical Issues
- **SQL Injection Risk**: Raw SQL query construction detected
  - **File**: src/api/auth.py:67
  - **Code**: `f"SELECT * FROM users WHERE email = '{email}'"`
  - **Fix**: Use parameterized queries

### High Priority
- **Hardcoded Secret**: API key found in source code
  - **File**: src/config/settings.py:23
  - **Recommendation**: Move to environment variables

### Best Practices Applied
- ✅ Password hashing with bcrypt
- ✅ JWT token expiration implemented
- ✅ Rate limiting on authentication endpoints
```

### 3. Performance Review
Analyzes performance characteristics and optimization opportunities:

```bash
/review --type=performance src/data/
```

**Analysis Areas:**
- Database query efficiency
- Memory usage patterns
- Algorithmic complexity
- Caching opportunities
- Resource utilization
- Scalability considerations

**Example Output:**
```markdown
## Performance Review: Data Access Layer

### Performance Issues
- **N+1 Query Problem**: User loading triggers multiple queries
  - **File**: src/data/repositories.py:89
  - **Impact**: O(n) database calls for n users
  - **Solution**: Use eager loading or batch queries

- **Missing Index**: Slow query on user_email column
  - **Query**: `SELECT * FROM users WHERE email = ?`
  - **Recommendation**: Add index on email column

### Optimization Opportunities
- **Caching**: User profile data accessed frequently
  - **Recommendation**: Implement Redis caching with 1-hour TTL
  - **Expected Impact**: 70% reduction in database queries

### Efficient Patterns Found
- ✅ Connection pooling configured properly
- ✅ Bulk operations for large datasets
- ✅ Pagination implemented for list endpoints
```

### 4. Architecture Review
Validates architectural consistency and design patterns:

```bash
/review --type=architecture src/
```

**Analysis Areas:**
- Design pattern compliance
- Separation of concerns
- Dependency management
- Interface consistency
- Layer boundaries
- SOLID principles

**Example Output:**
```markdown
## Architecture Review: Service Layer

### Architecture Violations
- **Tight Coupling**: UserService directly imports EmailService
  - **File**: src/services/user_service.py:5
  - **Issue**: Violates dependency inversion principle
  - **Solution**: Use dependency injection

- **Layer Violation**: Service calling controller method
  - **File**: src/services/payment_service.py:78
  - **Issue**: Business logic calling presentation layer
  - **Solution**: Extract shared logic to utility

### Design Patterns Applied
- ✅ Repository pattern for data access
- ✅ Factory pattern for service creation
- ✅ Observer pattern for event handling
```

## Review Scopes

### File-Level Review
```bash
/review src/auth/handlers.py
```

Detailed analysis of a single file:
- Function-level quality assessment
- Security vulnerability scanning
- Performance bottleneck identification
- Documentation completeness

### Module-Level Review
```bash
/review src/auth/
```

Comprehensive module analysis:
- Inter-component relationships
- Module cohesion and coupling
- Interface consistency
- Shared pattern compliance

### Feature-Level Review
```bash
/review --feature user-authentication
```

End-to-end feature review:
- Complete user journey analysis
- Cross-cutting concern validation
- Integration point verification
- Test coverage assessment

## Advanced Review Options

### `--focus`
Concentrate on specific aspects:
```bash
/review --focus=security,performance src/api/
```

### `--severity`
Filter by issue severity:
```bash
/review --severity=high src/           # Only high-priority issues
/review --severity=all src/            # All issues including minor
```

### `--format`
Control output format:
```bash
/review --format=json src/auth.py      # Machine-readable
/review --format=sarif src/            # SARIF format for tools
/review --format=report src/           # Detailed report
```

### `--baseline`
Compare against baseline:
```bash
/review --baseline=main src/           # Compare with main branch
/review --baseline=v1.0.0 src/         # Compare with specific version
```

## Integration Patterns

### Pre-Commit Review
```bash
# Review only changed files
/review --changed

# Review staged files
/review --staged
```

### CI/CD Integration
```bash
# Generate review reports for CI
/review --format=junit-xml --output=reports/review.xml src/

# Fail CI on critical issues
/review --fail-on=critical src/
```

### Code Review Workflow
```bash
# Before creating PR
/review --comprehensive src/

# Review specific PR changes
/review --pr=123

# Post-implementation review
/review feat-payments-001
```

## Review Quality Gates

### Code Quality Gates
- **Complexity**: Cyclomatic complexity < 10
- **Coverage**: Line coverage > 80%
- **Duplication**: Code duplication < 5%
- **Maintainability**: Maintainability index > 70

### Security Gates
- **Vulnerabilities**: Zero critical/high security issues
- **Dependencies**: No known vulnerable dependencies
- **Secrets**: No hardcoded secrets or credentials
- **Compliance**: OWASP Top 10 compliance

### Performance Gates
- **Response Time**: API endpoints < 200ms average
- **Memory**: Memory usage within expected bounds
- **Database**: Query efficiency within thresholds
- **Scalability**: Load testing passes requirements

## Common Review Scenarios

### Pre-Deployment Review
```bash
/review --comprehensive --type=security,performance src/
```

Complete production readiness check:
- Security vulnerability assessment
- Performance bottleneck analysis
- Code quality validation
- Documentation completeness

### Legacy Code Review
```bash
/review --focus=maintainability,security legacy/
```

Assessment of legacy systems:
- Technical debt identification
- Security risk assessment
- Modernization opportunities
- Refactoring priorities

### New Feature Review
```bash
/review feat-notifications-001
```

Feature implementation validation:
- Requirements fulfillment
- Integration point verification
- Test coverage adequacy
- Performance impact assessment

### Dependency Update Review
```bash
/review --dependencies --security
```

Third-party dependency assessment:
- Security vulnerability scan
- License compliance check
- Breaking change analysis
- Update impact assessment

## Best Practices

### 1. Regular Review Cycles
```bash
# Weekly architecture review
/review --type=architecture --scope=services

# Daily security scan
/review --type=security --changed

# Monthly comprehensive review
/review --all --comprehensive
```

### 2. Automated Review Integration
```bash
# Git hooks for pre-commit review
#!/bin/bash
quaestor review --changed --fail-on=high

# CI pipeline review step
script: quaestor review --format=junit-xml src/
```

### 3. Review-Driven Development
```bash
# Review early and often
/research existing-patterns    # Understand current state
/plan new-feature             # Plan implementation
/impl spec-001                # Implement feature
/review spec-001              # Review implementation
```

### 4. Team Review Standards
Establish consistent review criteria:
- Quality gates and thresholds
- Security requirements
- Performance benchmarks
- Documentation standards

## Review Reporting

### Summary Reports
```bash
/review --summary src/
```

High-level overview:
- Overall quality score
- Issue distribution by severity
- Trend analysis over time
- Improvement recommendations

### Detailed Reports
```bash
/review --detailed --output=reports/review.html src/
```

Comprehensive analysis:
- File-by-file breakdown
- Issue categorization
- Code examples and fixes
- Metrics and visualizations

### Compliance Reports
```bash
/review --compliance=pci-dss src/payments/
```

Regulatory compliance assessment:
- Standard-specific requirements
- Compliance gap analysis
- Remediation recommendations
- Audit trail documentation

## Tips for Effective Reviews

### 1. Focus Reviews Appropriately
```bash
# For new features
/review --type=quality,security feat-001

# For performance-critical code
/review --type=performance --focus=database src/queries/

# For public APIs
/review --type=security,architecture src/api/
```

### 2. Use Progressive Review
```bash
# Start with high-level issues
/review --severity=critical,high src/

# Then address medium priority
/review --severity=medium src/

# Finally polish with minor issues
/review --severity=low src/
```

### 3. Review Context Matters
- **New code**: Focus on quality and architecture
- **Bug fixes**: Emphasize security and testing
- **Performance updates**: Prioritize performance analysis
- **Legacy updates**: Balance maintainability with risk

## Next Steps

- Learn about [Code Quality Standards](../advanced/architecture.md)
- Explore [Security Best Practices](../advanced/security.md)
- Understand [Performance Optimization](../advanced/performance.md)
- Read about [Agent Collaboration](../agents/overview.md)