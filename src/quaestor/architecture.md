<!-- META:document:architecture -->
<!-- META:version:2.0 -->
<!-- META:ai-optimized:true -->

# {{ project_name }} Architecture

## 1. PROJECT CONFIGURATION

### Environment
- **Project Type**: {{ project_type }}
- **Primary Language**: {{ language_display_name }}{% if primary_language != "unknown" %} ({{ primary_language }}){% endif %}
- **Configuration Version**: {{ config_system_version }}
{% if strict_mode %}- **Mode**: Strict (enforced due to project complexity)
{% else %}- **Mode**: Standard
{% endif %}

### Development Tools
- **Build Tool**: {{ build_tool }}
- **Package Manager**: {{ package_manager }}
{% if language_server %}- **Language Server**: {{ language_server }}
{% endif %}{% if virtual_env %}- **Environment Management**: {{ virtual_env }}
{% endif %}- **Dependency Management**: {{ dependency_management }}

## 2. ARCHITECTURE OVERVIEW

### Selected Pattern
```yaml
pattern:
  selected: "[Your architecture pattern: MVC, DDD, Microservices, etc.]"
  description: "Brief description of why this pattern was chosen"
```

**For detailed architecture pattern examples (MVC, DDD, Microservices, Clean Architecture), use the `architecture-patterns` skill**

### Core Components

```yaml
components:
  - name: "[Component Name]"
    responsibility: "[Description]"
    key_files:
      - "[path/to/files]"

  - name: "[Component Name]"
    responsibility: "[Description]"
    key_files:
      - "[path/to/files]"
```

### Code Organization

```yaml
structure:
  - path: "src/"
    contains:
      - path: "[layer/module]/"
        description: "[Description]"

  - path: "tests/"
    contains:
      - path: "unit/"
      - path: "integration/"
      - path: "e2e/"
```

## 3. CODE QUALITY STANDARDS

### Linting and Formatting
- **Linter**: `{{ lint_command }}`
- **Formatter**: `{{ format_command }}`
- **Code Formatter**: {{ code_formatter }}
- **Quick Check**: `{{ quick_check_command }}`
- **Full Validation**: `{{ full_check_command }}`

**For detailed code quality patterns and review checklists, use the `code-quality` skill**

### Testing Requirements
- **Test Runner**: `{{ test_command }}`
- **Coverage**: `{{ coverage_command }}`
- **Coverage Threshold**: {{ coverage_threshold_percent }}
- **Testing Framework**: {{ testing_framework }}
- **Coverage Target**: Maintain >80% test coverage

**For comprehensive testing strategies and patterns, use the `testing-strategy` skill**

{% if type_checking_enabled %}### Type Checking
- **Type Checker**: `{{ type_check_command }}`
- **Type Safety**: Required
{% endif %}

### Code Style Guidelines
- **Language**: {{ language_display_name }}
- **Formatting**: {{ code_formatter }}
- **Documentation**: {{ documentation_style }}
- **Error Handling**: Comprehensive exception handling with proper logging
- **File Organization**: {{ file_organization }}
- **Naming Convention**: {{ naming_convention }}

### Documentation Style
{{ documentation_style }}

**Example Format:**
```{{ primary_language }}
{{ doc_style_example }}
```

### Error Handling Pattern
```{{ primary_language }}
{{ error_handling_pattern }}
```

## 4. DEVELOPMENT WORKFLOW

### Quick Start Commands

```bash
# Quick validation
{{ quick_check_command }}

# Full validation suite
{{ full_check_command }}

# Testing and coverage
{{ test_command }}
{{ coverage_command }}

{% if type_checking_enabled %}# Type checking
{{ type_check_command }}
{% endif %}
{% if has_security_scanner == "true" %}# Security scanning
{{ security_scan_command }}
{% endif %}
```

### Git and Commits
- **Commit Prefix**: `{{ commit_prefix }}`
- **Pre-commit Hooks**: `{{ precommit_install_command }}`
- **Branch Strategy**: {{ branch_rules }}
- **Atomic Commits**: Each completed task gets its own commit

### Development Lifecycle
1. **Setup**: {{ precommit_install_command }}
2. **Development**: Follow {{ file_organization }}
3. **Quality Check**: {{ quick_check_command }}
4. **Testing**: {{ test_command }}
5. **Commit**: Use "{{ commit_prefix }}: description" format

## 5. TESTING STRATEGY

### Testing Approach
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage**: Maintain >80% test coverage

### Test Organization
```yaml
test_structure:
  - "tests/unit/": Individual component tests
  - "tests/integration/": Component interaction tests
  - "tests/e2e/": End-to-end workflow tests
  - "tests/fixtures/": Shared test fixtures and data
```

**For detailed testing patterns, use the `testing-strategy` skill**

## 6. SECURITY & PERFORMANCE

### Security Considerations
{% if has_security_scanner == "true" %}- **Security Scanner**: `{{ security_scan_command }}`
- **Security Scanning**: Enabled ({{ security_scanner }})
{% else %}- **Security Scanner**: Configure security scanning tools
{% endif %}- **Input Validation**: Sanitize all external inputs
- **Authentication**: Proper session management where applicable
- **Data Protection**: Encryption at rest and in transit
- **Audit Logging**: Track security-relevant operations

**For detailed security patterns and OWASP guidelines, use the `security-audit` skill**

### Performance Guidelines
{% if has_profiler == "true" %}- **Profiler**: `{{ profile_command }}`
{% endif %}- **Performance Target**: {{ performance_budget }}
- **Database**: Use connection pooling and query optimization
- **Memory**: Proper resource cleanup and monitoring
- **Caching**: Strategic caching with invalidation
- **Async**: Non-blocking operations where appropriate
- **Monitoring**: Metrics, tracing, and alerting

**For performance optimization techniques, use the `performance-optimization` skill**

## 7. COMMON PATTERNS

### Architecture Patterns
- **Dependency Injection**: Use for testability and modularity
- **Error Handling**: Use Result types for operation outcomes
- **Logging**: Structured logging with appropriate levels
- **Configuration**: Layered config with validation
- **Documentation**: Auto-generated with manual curation

## 8. QUALITY THRESHOLDS

### Metrics
- **Test Coverage**: {{ coverage_threshold_percent }}
- **Code Duplication**: <{{ max_duplication }}
- **Technical Debt**: <{{ max_debt_hours }}
- **Bug Density**: <{{ max_bugs_per_kloc }} per KLOC
- **Performance**: {{ performance_budget }}

### Current Status
- **Coverage**: {{ current_coverage }}
- **Duplication**: {{ current_duplication }}
- **Tech Debt**: {{ current_debt }}
- **Bug Density**: {{ current_bug_density }}
{% if main_config_available %}- **Configuration**: Advanced (layered configuration system)
{% else %}- **Configuration**: Basic (static configuration)
{% endif %}

## 9. INTEGRATION POINTS

### Hook System
The hook system provides automated assistance for development workflows.

**For hook configuration details, see `.claude/settings.json`**

### CI/CD Pipeline
{{ ci_pipeline_config }}

### Monitoring and Debugging
- **Logging**: {{ logging_config }}
- **Monitoring**: {{ monitoring_setup }}
- **Debug Mode**: {{ debug_configuration }}

**For systematic debugging approaches, use the `debugging-workflow` skill**

## 10. PROJECT STANDARDS

### Build and Deployment
- **Max Build Time**: {{ max_build_time }}
- **Bundle Size Limit**: {{ max_bundle_size }}
- **Memory Threshold**: {{ memory_threshold }}

### Reliability
- **Retry Strategy**: {{ retry_configuration }}
- **Fallback Behavior**: {{ fallback_behavior }}

### Automation Rules
- **Enforcement Level**: {{ rule_enforcement }}
- **Pre-edit Validation**: `{{ pre_edit_script }}`
- **Post-edit Processing**: `{{ post_edit_script }}`

---

*Project: {{ project_name }} ({{ project_type }})*
{% if strict_mode %}*Strict Mode: Enabled due to project complexity*{% endif %}

## Available Skills

This project includes specialized skills for common development tasks:
- **security-audit**: Security patterns, vulnerability scanning, OWASP guidelines
- **performance-optimization**: Caching strategies, profiling, optimization techniques
- **testing-strategy**: Test pyramid, coverage requirements, testing patterns
- **code-quality**: Linting, formatting, SOLID principles, code review checklists
- **architecture-patterns**: MVC, DDD, Microservices, Clean Architecture examples
- **debugging-workflow**: Systematic debugging, troubleshooting, root cause analysis

Invoke skills by referencing them when needed for specific tasks.
