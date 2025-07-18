# Quaestor Test Suite

This directory contains the simplified test suite for Quaestor, focusing on core functionality.

## Test Organization

### Core Unit Tests
- `test_command_processor.py` - Tests for command configuration processing
- `test_command_config.py` - Tests for configuration loading and merging
- `test_automation_base.py` - Tests for automation/hook functionality
- `test_init_integration.py` - Integration tests for the init command

### End-to-End Tests
- `e2e/test_basic_workflow.py` - Basic workflow tests
- `e2e/test_command_execution.py` - Command execution scenarios

### Shared Fixtures
- `conftest.py` - Common test fixtures and utilities

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_command_processor.py

# Run with coverage
uv run pytest --cov=quaestor --cov-report=term-missing

# Run only unit tests (exclude e2e)
uv run pytest tests/ -k "not e2e"
```

## Test Philosophy

We maintain a simplified test suite that focuses on:
1. **Core functionality** - Command processing, configuration, automation
2. **User-facing commands** - Init, configure, update
3. **Critical paths** - Workflows that users depend on

We avoid:
- Testing unimplemented features
- Overly complex test infrastructure
- Performance benchmarking (until post-1.0)
- Cross-platform matrix testing (CI handles basic coverage)