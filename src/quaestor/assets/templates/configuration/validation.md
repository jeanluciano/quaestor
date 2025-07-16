# VALIDATION.md - Quality Gates and Validation Rules

<!-- QUAESTOR:version:1.0 -->

## Overview

This document defines the quality gates, validation rules, and checks that must pass before any implementation is considered complete. These validations ensure code quality, security, and maintainability.

## Quality Gate Configuration

<!-- DATA:quality-gates:START -->
```yaml
quality_gates:
  pre_implementation:
    - research_completed: mandatory
    - plan_approved: mandatory
    - dependencies_checked: mandatory
  
  during_implementation:
    - syntax_valid: mandatory
    - type_checking: {{ "mandatory" if type_checking else "optional" }}
    - security_scan: on_sensitive_files
    - performance_check: on_critical_paths
  
  post_implementation:
    - all_tests_pass: mandatory
    - linting_clean: mandatory
    - documentation_complete: mandatory
    - code_coverage: {{ "">=" + coverage_threshold|string + "%" if coverage_threshold else "optional" }}
```
<!-- DATA:quality-gates:END -->

## Validation Checkpoints

### 1. Pre-Implementation Validation

<!-- VALIDATION:pre-implementation:START -->
**Before writing any code, validate:**

- [ ] **Requirements Clear**: All requirements are understood and documented
- [ ] **Architecture Reviewed**: Solution aligns with architecture principles
- [ ] **Dependencies Available**: All required dependencies are accessible
- [ ] **Breaking Changes**: Impact on existing functionality assessed
- [ ] **Security Implications**: Security review completed for sensitive features
<!-- VALIDATION:pre-implementation:END -->

### 2. Code Quality Validation

<!-- VALIDATION:code-quality:START -->
**During implementation, continuously check:**

#### Syntax and Style
```bash
# Syntax validation
{{ lint_command }}

# Code formatting
{{ format_command }}

# Type checking (if applicable)
{{ type_check_command if type_check_command else "# No type checking configured" }}
```

#### Complexity Metrics
- **Function Length**: < 50 lines (warning), < 100 lines (error)
- **Cyclomatic Complexity**: < 10 (preferred), < 15 (maximum)
- **Nesting Depth**: < 4 levels
- **File Length**: < 500 lines (warning), < 1000 lines (error)
<!-- VALIDATION:code-quality:END -->

### 3. Security Validation

<!-- VALIDATION:security:START -->
**Security checks required for:**

- [ ] **Input Validation**: All user inputs sanitized
- [ ] **Authentication**: Proper auth checks in place
- [ ] **Authorization**: Permission checks implemented
- [ ] **Secrets Management**: No hardcoded secrets or credentials
- [ ] **SQL Injection**: Parameterized queries used
- [ ] **XSS Prevention**: Output properly escaped
- [ ] **CSRF Protection**: Tokens implemented where needed

**Automated Security Scan:**
```bash
# Run security scanner
{{ security_scan_command if security_scan_command else "# Configure security scanner" }}
```
<!-- VALIDATION:security:END -->

### 4. Testing Validation

<!-- VALIDATION:testing:START -->
**Test coverage requirements:**

```yaml
test_requirements:
  unit_tests:
    coverage: {{ coverage_threshold|string + "%" if coverage_threshold else "80%" }}
    required: true
  integration_tests:
    coverage: "Critical paths"
    required: true
  e2e_tests:
    coverage: "User workflows"
    required: {{ "true" if project_type == "web" else "false" }}
```

**Run tests:**
```bash
# Run all tests
{{ test_command }}

# Run with coverage
{{ coverage_command if coverage_command else test_command + " --coverage" }}

# Run specific test file
{{ test_command }} path/to/test_file
```
<!-- VALIDATION:testing:END -->

### 5. Performance Validation

<!-- VALIDATION:performance:START -->
**Performance checks for critical paths:**

- [ ] **Response Time**: < {{ performance_target_ms if performance_target_ms else "200" }}ms for API endpoints
- [ ] **Memory Usage**: No memory leaks detected
- [ ] **Database Queries**: N+1 queries eliminated
- [ ] **Caching**: Appropriate caching implemented
- [ ] **Async Operations**: Long-running tasks made asynchronous

**Performance profiling:**
```bash
# Profile performance
{{ profile_command if profile_command else "# Configure profiler" }}
```
<!-- VALIDATION:performance:END -->

### 6. Documentation Validation

<!-- VALIDATION:documentation:START -->
**Documentation requirements:**

- [ ] **Code Comments**: Complex logic explained
- [ ] **Function/Method Docs**: All public APIs documented
- [ ] **README Updated**: New features documented
- [ ] **API Documentation**: OpenAPI/Swagger specs updated
- [ ] **Architecture Docs**: Significant changes documented
- [ ] **Migration Guide**: Breaking changes documented

**Documentation style:**
```{{ primary_language }}
{{ doc_style_example if doc_style_example else """def example_function(param: str) -> str:
    '''
    Brief description of what the function does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param is invalid
    '''
    pass""" }}
```
<!-- VALIDATION:documentation:END -->

## Validation Automation

### Continuous Validation

<!-- AUTOMATION:continuous:START -->
```yaml
continuous_validation:
  on_save:
    - syntax_check
    - format_check
  
  on_commit:
    - lint_check
    - test_suite
    - security_scan
  
  on_pr:
    - full_test_suite
    - coverage_report
    - performance_tests
    - documentation_check
```
<!-- AUTOMATION:continuous:END -->

### Validation Scripts

<!-- SCRIPTS:validation:START -->
**Quick validation:**
```bash
# Run all quick checks
{{ quick_check_command if quick_check_command else "make check" }}
```

**Full validation:**
```bash
# Run comprehensive validation
{{ full_check_command if full_check_command else "make validate" }}
```

**Pre-commit validation:**
```bash
# Install pre-commit hooks
{{ precommit_install_command if precommit_install_command else "pre-commit install" }}
```
<!-- SCRIPTS:validation:END -->

## Validation Exceptions

### When to Skip Validation

<!-- EXCEPTIONS:when-to-skip:START -->
Validation may be temporarily skipped ONLY when:

1. **Prototyping**: Clearly marked experimental code
2. **Emergency Fixes**: With documented follow-up ticket
3. **External Dependencies**: Beyond project control

**Required for exceptions:**
- Management approval
- Documented justification
- Remediation timeline
- Risk assessment
<!-- EXCEPTIONS:when-to-skip:END -->

### Technical Debt Tracking

<!-- DEBT:tracking:START -->
When validation is skipped:

```{{ primary_language }}
# TODO(VALIDATION-SKIP): [Ticket-ID] Temporary skip because [reason]
# Remediation: [What needs to be done]
# Target date: [When it will be fixed]
```
<!-- DEBT:tracking:END -->

## Validation Results

### Success Criteria

<!-- CRITERIA:success:START -->
✅ **Implementation is complete when:**
- All quality gates pass
- No critical security issues
- Test coverage meets threshold
- Documentation is complete
- Performance targets met
- Code review approved
<!-- CRITERIA:success:END -->

### Failure Handling

<!-- CRITERIA:failure:START -->
❌ **When validation fails:**
1. Stop current work
2. Fix validation issues
3. Re-run validation suite
4. Document any remaining issues
5. Get approval for exceptions
<!-- CRITERIA:failure:END -->

## Custom Validation Rules

<!-- CUSTOM:rules:START -->
<!-- Add project-specific validation rules here -->




<!-- CUSTOM:rules:END -->

Remember: Quality gates exist to ensure excellence, not to slow progress. Automate everything possible.