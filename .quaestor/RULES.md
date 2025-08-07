# quaestor Development Rules

## Project Configuration

### Language Environment
- **Project Type**: python
- **Primary Language**: Python (python)
- **Configuration Version**: 2.0
- **Mode**: Strict (enforced due to project complexity)
{% else %}- **Mode**: Standard


## Code Quality Standards

### Linting and Formatting
- **Linter**: `ruff check .`
- **Formatter**: `ruff format .`
- **Code Formatter**: Ruff for fast Python formatting
- **Quick Check**: `ruff check . && pytest -x`
- **Full Validation**: `ruff check . && ruff format --check . && mypy . && pytest`

### Testing Requirements
- **Test Runner**: `pytest`
- **Coverage**: `pytest --cov`
- **Coverage Threshold**: 80%
- **Testing Framework**: pytest with fixtures and parameterization
- **Coverage Target**: Maintain >80% test coverage
- **Quality**: Use pytest with fixtures and parameterization

### Type Checking
- **Type Checker**: `mypy .`
- **Type Safety**: Required


### Security and Performance
- **Security Scanner**: `bandit -r src/`
- **Security Scanning**: Enabled (bandit -r src/)
{% else %}- **Security Scanner**: Configure security scanning tools
- **Profiler**: `python -m cProfile`
- **Performance Target**: 200ms

## Development Commands

```bash
# Quick validation
ruff check . && pytest -x

# Full validation suite
ruff check . && ruff format --check . && mypy . && pytest

# Testing and coverage
pytest
pytest --cov

# Type checking
mypy .

# Security scanning
bandit -r src/

```

## Code Style Guidelines

- **Language**: Python (python)
- **Formatting**: Ruff for fast Python formatting
- **Linting**: ruff check .
- **Testing**: pytest with fixtures and parameterization
- **Documentation**: Python standard
- **Error Handling**: Comprehensive exception handling with proper logging
- **File Organization**: Package structure with __init__.py, src/ layout recommended
- **Naming Convention**: snake_case for functions/variables, PascalCase for classes

### Documentation Style
Python standard

**Example Format:**
```python
def example_function(param: str) -> str:
    """
    Brief description of what the function does.

    Args:
        param: Description of the parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param is invalid
    """
    pass

```

## Architecture Patterns

- **Dependency Injection**: Use for testability and modularity
- **Plugin Architecture**: Extensible hook and agent systems
- **Template Processing**: Dynamic content generation with context awareness
- **Configuration Management**: Layered configuration with validation

## Development Workflow

### Git and Commits
- **Commit Prefix**: `feat`
- **Pre-commit Hooks**: `pre-commit install`
- **Branch Strategy**: Feature branches with PR workflow
- **Atomic Commits**: Each completed task gets its own commit

### Development Lifecycle
1. **Setup**: pre-commit install
2. **Development**: Follow Package structure with __init__.py, src/ layout recommended
3. **Quality Check**: ruff check . && pytest -x
4. **Testing**: pytest
5. **Commit**: Use "feat: description" format

### Testing Approach
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows
- **Coverage**: Maintain >80% test coverage
- **Quality**: Use pytest with fixtures and parameterization

## Language-Specific Conventions

### Code Organization
- **File Structure**: Package structure with __init__.py, src/ layout recommended
- **Naming Convention**: snake_case for functions/variables, PascalCase for classes
- **Dependency Management**: pip with requirements.txt or Poetry/pipenv for advanced needs

### Development Tools
- **Build Tool**: setuptools/pip, Poetry, or PDM for packaging
- **Package Manager**: pip (PyPI), conda for scientific computing


### Error Handling Pattern
```python
try:
    result = hook.run(input_data)
    return result
except TimeoutError:
    logger.warning("Hook execution timed out, using fallback")
    return fallback_result()
except Exception as e:
    logger.error(f"Hook execution failed: {e}")
    return safe_default()
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
- **Test Coverage**: 80%
- **Code Duplication**: d5%
- **Technical Debt**: d40h
- **Bug Density**: d1 per KLOC
- **Performance**: 200ms

### Current Status
- **Coverage**: Run 'quaestor status' to see current metrics
- **Duplication**: Run 'quaestor status' to see current metrics
- **Tech Debt**: Run 'quaestor status' to see current metrics
- **Bug Density**: Run 'quaestor status' to see current metrics
- **Configuration**: Advanced (layered configuration system)
{% else %}- **Configuration**: Basic (static configuration)


## Automation Rules

### Hook Configuration
- **Enforcement Level**: learning
- **Pre-edit Validation**: `ruff check .`
- **Post-edit Processing**: `ruff format .`

### CI/CD Pipeline
# Python CI/CD Configuration
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint with ruff
        run: ruff check .
      - name: Test with pytest
        run: pytest --cov


## Project Standards

### Build and Deployment
- **Max Build Time**: 5min
- **Bundle Size Limit**: 5MB
- **Memory Threshold**: 512MB

### Monitoring and Debugging
- **Logging**: Structured JSON logging
- **Monitoring**: Track execution time and success rate
- **Debug Mode**: Enable with DEBUG=1 environment variable

### Reliability
- **Retry Strategy**: 3 attempts with exponential backoff
- **Fallback Behavior**: Graceful degradation on failures

---

*This project uses Python with Quaestor v2.0*
*Project: quaestor (python)*
*Strict Mode: Enabled due to project complexity*