# Python Quality Standards

**Load this file when:** Implementing features in Python projects

## Validation Commands

```bash
# Linting
ruff check . --fix

# Formatting
ruff format .

# Tests
pytest -v

# Type Checking
mypy . --ignore-missing-imports

# Coverage
pytest --cov --cov-report=html

# Full Validation Pipeline
ruff check . && ruff format . && mypy . && pytest
```

## Required Standards

```yaml
Code Style:
  - Line length: 120 characters (configurable)
  - Imports: Sorted with isort style
  - Docstrings: Google or NumPy style
  - Type hints: Everywhere (functions, methods, variables)

Testing:
  - Framework: pytest
  - Coverage: >= 80%
  - Test files: test_*.py or *_test.py
  - Fixtures: Prefer pytest fixtures over setup/teardown
  - Assertions: Use pytest assertions, not unittest

Documentation:
  - All modules: Docstring with purpose
  - All classes: Docstring with attributes
  - All functions: Docstring with args, returns, raises
  - Complex logic: Inline comments for clarity

Error Handling:
  - Use specific exceptions (not bare except)
  - Custom exceptions for domain errors
  - Proper exception chaining
  - Clean resource management (context managers)
```

## Quality Checklist

**Before Declaring Complete:**
- [ ] All functions have type hints
- [ ] All functions have docstrings (Google/NumPy style)
- [ ] No linting errors (`ruff check .`)
- [ ] Code formatted consistently (`ruff format .`)
- [ ] Type checking passes (`mypy .`)
- [ ] All tests pass (`pytest`)
- [ ] Test coverage >= 80%
- [ ] No bare except clauses
- [ ] Proper exception handling
- [ ] Resources properly managed

## Example Quality Pattern

```python
from typing import Optional
from pathlib import Path

def load_config(config_path: Path) -> dict[str, any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dictionary containing configuration values

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid YAML
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    try:
        with config_path.open() as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_path}") from e
```

---

*Python-specific quality standards for production-ready code*
