# {{ project_name }} Development Rules

## Project Configuration

### Language Environment
- **Project Type**: {{ project_type }}
- **Primary Language**: {{ language_display_name }}{% if primary_language != "unknown" %} ({{ primary_language }}){% endif %}
- **Configuration Version**: {{ config_system_version }}
{% if strict_mode %}- **Mode**: Strict (enforced due to project complexity)
{% else %}- **Mode**: Standard
{% endif %}

## Code Quality Standards

### Linting and Formatting
- **Linter**: `{{ lint_command }}`
- **Formatter**: `{{ format_command }}`
- **Code Formatter**: {{ code_formatter }}
- **Quick Check**: `{{ quick_check_command }}`
- **Full Validation**: `{{ full_check_command }}`

### Testing Requirements
- **Test Runner**: `{{ test_command }}`
- **Coverage**: `{{ coverage_command }}`
- **Coverage Threshold**: {{ coverage_threshold_percent }}
- **Testing Framework**: {{ testing_framework }}
- **Coverage Target**: Maintain >80% test coverage
- **Quality**: Use pytest with fixtures and parameterization

{% if type_checking_enabled %}### Type Checking
- **Type Checker**: `{{ type_check_command }}`
- **Type Safety**: Required
{% endif %}

### Security and Performance
{% if has_security_scanner == "true" %}- **Security Scanner**: `{{ security_scan_command }}`
- **Security Scanning**: Enabled ({{ security_scanner }})
{% else %}- **Security Scanner**: Configure security scanning tools
{% endif %}{% if has_profiler == "true" %}- **Profiler**: `{{ profile_command }}`
{% endif %}- **Performance Target**: {{ performance_budget }}

## Development Commands

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

## Code Style Guidelines

- **Language**: {{ language_display_name }}{% if primary_language != "unknown" %} ({{ primary_language }}){% endif %}
- **Formatting**: {{ code_formatter }}
- **Linting**: {{ lint_command }}
- **Testing**: {{ testing_framework }}
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

## Architecture Patterns

- **Dependency Injection**: Use for testability and modularity
- **Plugin Architecture**: Extensible hook and agent systems
- **Template Processing**: Dynamic content generation with context awareness
- **Configuration Management**: Layered configuration with validation

## Development Workflow

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

### Testing Approach
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage**: Maintain >80% test coverage
- **Quality**: Use pytest with fixtures and parameterization

## Language-Specific Conventions

### Code Organization
- **File Structure**: {{ file_organization }}
- **Naming Convention**: {{ naming_convention }}
- **Dependency Management**: {{ dependency_management }}

### Development Tools
- **Build Tool**: {{ build_tool }}
- **Package Manager**: {{ package_manager }}
{% if language_server %}- **Language Server**: {{ language_server }}
{% endif %}{% if virtual_env %}- **Environment Management**: {{ virtual_env }}
{% endif %}

### Error Handling Pattern
```{{ primary_language }}
{{ error_handling_pattern }}
```

## Common Patterns

- **Error Handling**: Use Result types for operation outcomes
- **Logging**: Structured logging with appropriate levels
- **Configuration**: Layered config with validation
- **Testing**: Unit, integration, and E2E test strategies
- **Documentation**: Auto-generated with manual curation

## Performance Guidelines

- **Database**: Use connection pooling and query optimization
- **Memory**: Proper resource cleanup and monitoring
- **Caching**: Strategic caching with invalidation
- **Async**: Non-blocking operations where appropriate
- **Monitoring**: Metrics, tracing, and alerting

## Security Considerations

- **Input Validation**: Sanitize all external inputs
- **Authentication**: Proper session management
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Audit Logging**: Track security-relevant operations

## Debugging Workflow

1. **Reproduce**: Create minimal reproduction case
2. **Isolate**: Use divide-and-conquer approach
3. **Log Analysis**: Check logs for error patterns
4. **Testing**: Write failing test first
5. **Fix**: Implement minimal fix
6. **Verify**: Ensure fix doesn't break other functionality

## Code Review Checklist

- [ ] Follows established patterns and conventions
- [ ] Comprehensive error handling implemented
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Tests cover edge cases
- [ ] Documentation updated
- [ ] Backward compatibility maintained

## Integration Points

- **CI/CD**: Automated testing and deployment
- **Monitoring**: Health checks and metrics
- **Documentation**: Auto-generated API docs
- **Dependencies**: Regular security updates
- **Backup**: Data backup and recovery procedures

## Quality Thresholds

### Metrics
- **Test Coverage**: {{ coverage_threshold_percent }}
- **Code Duplication**: d{{ max_duplication }}
- **Technical Debt**: d{{ max_debt_hours }}
- **Bug Density**: d{{ max_bugs_per_kloc }} per KLOC
- **Performance**: {{ performance_budget }}

### Current Status
- **Coverage**: {{ current_coverage }}
- **Duplication**: {{ current_duplication }}
- **Tech Debt**: {{ current_debt }}
- **Bug Density**: {{ current_bug_density }}
{% if main_config_available %}- **Configuration**: Advanced (layered configuration system)
{% else %}- **Configuration**: Basic (static configuration)
{% endif %}

## Automation Rules

### Hook Configuration
- **Enforcement Level**: {{ rule_enforcement }}
- **Pre-edit Validation**: `{{ pre_edit_script }}`
- **Post-edit Processing**: `{{ post_edit_script }}`

### CI/CD Pipeline
{{ ci_pipeline_config }}

## Project Standards

### Build and Deployment
- **Max Build Time**: {{ max_build_time }}
- **Bundle Size Limit**: {{ max_bundle_size }}
- **Memory Threshold**: {{ memory_threshold }}

### Monitoring and Debugging
- **Logging**: {{ logging_config }}
- **Monitoring**: {{ monitoring_setup }}
- **Debug Mode**: {{ debug_configuration }}

### Reliability
- **Retry Strategy**: {{ retry_configuration }}
- **Fallback Behavior**: {{ fallback_behavior }}

---

*This project uses {{ language_display_name }} with Quaestor v{{ config_system_version }}*
*Project: {{ project_name }} ({{ project_type }})*
{% if strict_mode %}*Strict Mode: Enabled due to project complexity*{% endif %}