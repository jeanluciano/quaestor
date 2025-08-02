# Reviewer Agent

The Reviewer Agent specializes in comprehensive code quality assessment, ensuring adherence to best practices, and maintaining consistent coding standards across the project. It provides detailed analysis beyond basic linting to ensure production-ready code.

## Overview

The Reviewer Agent excels at:
- **Code Quality Assessment**: Evaluating maintainability, readability, and design patterns
- **Security Reviews**: Identifying security vulnerabilities and enforcing secure coding practices  
- **Performance Analysis**: Finding performance bottlenecks and optimization opportunities
- **Architecture Validation**: Ensuring consistency with established architectural patterns
- **Best Practices Enforcement**: Maintaining coding standards and team conventions

## When to Use the Reviewer Agent

### 🔍 Pre-Merge Reviews
```bash
# Before merging pull requests
/review --comprehensive feature-branch
/review --security payment-processing-changes
/review --performance database-optimization-branch
```

### 📋 Code Quality Audits
```bash
# Regular quality assessments
/review --quality src/services/
/review --architecture src/
/review --standards new-feature-implementation
```

### 🎯 Specification Compliance
```bash
# Verify implementation matches specifications
/review --spec spec-auth-001 src/auth/
/review --requirements user-registration-feature
```

## Review Capabilities

### Code Quality Analysis

The Reviewer Agent evaluates multiple quality dimensions:

```python
# Example Quality Assessment
@reviewer_agent.assess_quality()
def analyze_code_quality(file_path: str) -> QualityReport:
    """
    Comprehensive quality analysis covering:
    - Complexity metrics (cyclomatic, cognitive)
    - Maintainability index and technical debt
    - Code duplication and pattern consistency
    - Documentation coverage and clarity
    - Error handling completeness
    """
    return QualityReport(
        complexity_score=7.2,        # Target: < 10
        maintainability=82,          # Target: > 80
        duplication_rate=3.1,        # Target: < 5%
        documentation_coverage=89,   # Target: > 85%
        error_handling_score=95      # Target: > 90%
    )
```

### Security Review Analysis

Comprehensive security assessment with actionable recommendations:

```python
# Security Review Output Example
@reviewer_agent.security_review()
def perform_security_analysis() -> SecurityReviewReport:
    """
    Security-focused code review including:
    - Input validation and sanitization patterns
    - Authentication and authorization implementation
    - Data handling and privacy protection
    - Cryptographic usage and key management
    - Error handling and information disclosure
    """
    return SecurityReviewReport(
        critical_issues=[
            SecurityIssue(
                severity="CRITICAL",
                file="src/auth/login.py:45",
                issue="SQL injection vulnerability in user lookup",
                recommendation="Use parameterized queries with SQLAlchemy",
                example_fix="user = session.query(User).filter(User.email == email).first()"
            )
        ],
        high_priority=[
            SecurityIssue(
                severity="HIGH", 
                file="src/api/users.py:123",
                issue="Missing input validation on user registration",
                recommendation="Add comprehensive input validation and sanitization",
                example_fix="validated_data = UserRegistrationSchema().load(request_data)"
            )
        ],
        recommendations=[
            "Implement rate limiting on authentication endpoints",
            "Add CSRF protection to state-changing operations",
            "Enable security headers (HSTS, CSP, X-Frame-Options)"
        ]
    )
```

### Performance Review Analysis

Identifies performance issues and optimization opportunities:

```python
# Performance Review Example
@reviewer_agent.performance_review()
def analyze_performance() -> PerformanceReviewReport:
    """
    Performance-focused analysis including:
    - Algorithm complexity and efficiency
    - Database query optimization opportunities
    - Memory usage patterns and potential leaks
    - Caching strategies and effectiveness
    - Resource utilization and bottlenecks
    """
    return PerformanceReviewReport(
        bottlenecks=[
            PerformanceIssue(
                severity="HIGH",
                file="src/services/user_service.py:89",
                issue="N+1 query problem in user profile loading",
                impact="O(n) database calls for n users",
                recommendation="Use eager loading or batch queries",
                example_fix="users = session.query(User).options(joinedload(User.profile)).all()"
            )
        ],
        optimizations=[
            OptimizationOpportunity(
                file="src/api/search.py:156",
                issue="Inefficient list comprehension with multiple iterations",
                current_complexity="O(n²)",
                optimized_complexity="O(n)",
                recommendation="Use single pass with dictionary lookup"
            )
        ],
        caching_opportunities=[
            "User profile data accessed frequently - implement Redis caching",
            "Product catalog rarely changes - add application-level caching",
            "Search results could benefit from query result caching"
        ]
    )
```

## Review Types

### Comprehensive Review
```bash
/review --comprehensive src/
```

**Analysis Scope:**
- Code quality metrics and maintainability
- Security vulnerabilities and best practices
- Performance bottlenecks and optimization opportunities
- Architecture consistency and design patterns
- Documentation completeness and clarity

### Focused Reviews

#### Security-Focused Review
```bash
/review --security src/auth/
```
- Input validation and sanitization
- Authentication and authorization mechanisms
- Cryptographic implementations
- Data protection and privacy compliance

#### Performance-Focused Review
```bash
/review --performance src/api/
```
- Algorithm efficiency and complexity analysis
- Database query optimization
- Memory usage and potential leaks
- Caching strategies and resource utilization

#### Architecture Review
```bash
/review --architecture src/services/
```
- Design pattern consistency
- Component boundaries and coupling
- Dependency management and injection
- SOLID principles adherence

## Review Standards and Guidelines

### Code Quality Standards
```yaml
Quality_Thresholds:
  complexity:
    cyclomatic: 10      # Maximum cyclomatic complexity per function
    cognitive: 15       # Maximum cognitive complexity per function
  
  maintainability:
    index: 80           # Minimum maintainability index
    duplication: 5      # Maximum code duplication percentage
  
  documentation:
    coverage: 85        # Minimum documentation coverage
    public_api: 100     # All public APIs must be documented
  
  testing:
    coverage: 80        # Minimum test coverage
    assertion_ratio: 3  # Minimum assertions per test function
```

### Security Standards
```yaml
Security_Requirements:
  input_validation:
    - All user inputs must be validated and sanitized
    - Use schema-based validation for complex data
    - Apply principle of least privilege for access control
  
  authentication:
    - Use secure password hashing (bcrypt, scrypt, or Argon2)
    - Implement proper session management
    - Add rate limiting to prevent brute force attacks
  
  data_protection:
    - Encrypt sensitive data at rest and in transit
    - Use parameterized queries to prevent SQL injection
    - Implement proper error handling without information disclosure
```

### Performance Standards
```yaml
Performance_Requirements:
  response_times:
    api_endpoints: 200ms    # Average response time target
    database_queries: 50ms  # Maximum query execution time
    page_loads: 2s          # Maximum page load time
  
  resource_usage:
    memory_growth: 5%       # Maximum memory growth per hour
    cpu_utilization: 70%    # Maximum sustained CPU usage
    database_connections: 80% # Maximum connection pool usage
  
  scalability:
    concurrent_users: 1000  # Target concurrent user capacity
    throughput: 500rps      # Requests per second target
    availability: 99.9%     # Uptime requirement
```

## Review Output Examples

### Code Quality Report
```markdown
## Code Quality Review: UserService

### Quality Metrics
- **Maintainability Index**: 78/100 (Target: >80) ⚠️
- **Cyclomatic Complexity**: Average 8.3 (Target: <10) ✅
- **Code Duplication**: 6.2% (Target: <5%) ⚠️
- **Documentation Coverage**: 92% (Target: >85%) ✅

### Issues Found

#### High Priority
- **Method Complexity**: `process_user_registration()` has cyclomatic complexity of 12
  - **Location**: src/services/user_service.py:45
  - **Recommendation**: Extract validation logic into separate methods
  - **Example**: Create `_validate_user_data()` and `_check_duplicate_email()` methods

#### Medium Priority
- **Code Duplication**: Similar validation logic in 3 different methods
  - **Locations**: Lines 78, 123, 167 in user_service.py
  - **Recommendation**: Extract common validation into a shared utility method
  - **Impact**: Reduces maintenance burden and ensures consistency

### Positive Patterns
✅ Consistent error handling with custom exceptions  
✅ Proper dependency injection pattern  
✅ Clear separation of concerns between layers  
✅ Comprehensive input validation on public methods
```

### Security Review Report
```markdown
## Security Review: Authentication System

### Critical Issues
🚨 **SQL Injection Risk** (Line 67)
- **Issue**: Raw SQL query construction detected
- **Code**: `f"SELECT * FROM users WHERE email = '{email}'"`
- **Fix**: Use parameterized queries
- **Example**: `session.query(User).filter(User.email == email).first()`

### High Priority Issues  
⚠️ **Missing Rate Limiting** (auth endpoints)
- **Impact**: Vulnerable to brute force attacks
- **Recommendation**: Implement rate limiting (5 attempts per 15 minutes)
- **Example**: Use Flask-Limiter or similar middleware

⚠️ **Weak Password Policy** (registration)
- **Current**: Minimum 6 characters
- **Recommended**: Minimum 12 characters with complexity requirements
- **Implementation**: Update validation schema and user interface

### Security Best Practices Applied
✅ Password hashing with bcrypt (cost factor 12)  
✅ JWT tokens with proper expiration (1 hour)  
✅ HTTPS enforcement in production  
✅ Input sanitization on user registration
```

### Performance Review Report
```markdown
## Performance Review: API Endpoints

### Performance Issues

#### Critical
🔴 **N+1 Query Problem** (Line 89)
- **Location**: src/services/user_service.py:89
- **Issue**: Loading users triggers O(n) additional queries for profiles
- **Current**: 1 + N database calls for N users
- **Solution**: Use eager loading with `joinedload(User.profile)`
- **Expected Impact**: 95% reduction in database queries

#### High Priority
🟡 **Inefficient Sorting Algorithm** (Line 156)
- **Location**: src/api/search.py:156
- **Issue**: Bubble sort implementation for large datasets
- **Current Complexity**: O(n²)
- **Solution**: Use built-in `sorted()` or implement quicksort
- **Expected Impact**: 80% improvement for datasets >100 items

### Optimization Opportunities
💡 **Caching Strategy**: User profile data accessed frequently  
💡 **Database Indexing**: Add composite index on (user_id, created_at)  
💡 **Response Compression**: Enable gzip compression for API responses
```

## Integration with Other Agents

### Review → Debug
```bash
/review --comprehensive feature-branch    # Identify issues
/debug "fix performance issues in user service"  # Address findings
```

### Review → Security
```bash
/review --security auth-system           # Find security issues
/security-fix "implement missing input validation"  # Apply security fixes
```

### Review → QA  
```bash
/review --quality new-feature            # Assess quality
/test --coverage "improve test coverage for low-coverage areas"  # Enhance testing
```

## Best Practices

### 1. Regular Review Cycles
```bash
# Pre-commit reviews
/review --quick src/modified-files

# Pre-merge reviews  
/review --comprehensive feature-branch

# Periodic quality audits
/review --architecture --performance src/
```

### 2. Incremental Improvements
Focus on improving quality gradually:
- Address critical issues first
- Set achievable quality targets
- Track quality metrics over time
- Celebrate quality improvements

### 3. Team Standards Alignment
```bash
# Establish team coding standards
/review --standards --generate-guidelines

# Ensure consistency across the team
/review --consistency src/
```

### 4. Automated Quality Gates
Integrate reviews into CI/CD pipeline:
- Fail builds on critical security issues
- Require minimum quality thresholds
- Generate quality reports for stakeholders
- Track quality trends over time

## Common Review Scenarios

### Pre-Release Quality Assurance
```bash
/review --comprehensive --security --performance src/
```
Complete production readiness assessment covering all quality dimensions.

### Legacy Code Assessment
```bash
/review --maintainability --technical-debt legacy/
```
Evaluate legacy systems for modernization and refactoring opportunities.

### New Feature Validation
```bash
/review --spec spec-user-profiles-001 src/profiles/
```
Verify new feature implementation matches specifications and quality standards.

### Security Audit
```bash
/review --security --compliance src/
```
Comprehensive security assessment for compliance and vulnerability management.

## Next Steps

- Learn about [QA Agent](qa.md) for testing and quality assurance
- Explore [Security Agent](security.md) for security-focused reviews
- Understand [Debug Agent](debug.md) for fixing identified issues
- Read about [Code Quality Standards](../advanced/quality.md)