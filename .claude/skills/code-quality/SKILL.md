---
name: Code Quality
description: Code quality standards, linting, formatting, and review checklists. Use when setting up quality tools, conducting code reviews, or enforcing coding standards.
---

# Code Quality

## Purpose
Provides code quality standards, linting and formatting guidelines, and comprehensive code review checklists.

## When to Use
- Setting up linting and formatting tools
- Conducting code reviews
- Establishing coding standards
- Improving code maintainability
- Refactoring existing code
- Onboarding new team members

## Code Quality Principles

### Core Principles
- **Readability**: Code should be easy to understand
- **Maintainability**: Code should be easy to modify
- **Testability**: Code should be easy to test
- **Simplicity**: Favor simple solutions over complex ones
- **Consistency**: Follow established patterns and conventions

### SOLID Principles
```yaml
solid:
  S - Single Responsibility:
    description: "A class should have one reason to change"
    benefit: "Easier to understand and maintain"

  O - Open/Closed:
    description: "Open for extension, closed for modification"
    benefit: "Add features without changing existing code"

  L - Liskov Substitution:
    description: "Subtypes must be substitutable for base types"
    benefit: "Predictable inheritance hierarchies"

  I - Interface Segregation:
    description: "Many specific interfaces over one general"
    benefit: "Clients don't depend on unused methods"

  D - Dependency Inversion:
    description: "Depend on abstractions, not concretions"
    benefit: "Loose coupling, easier testing"
```

### DRY, KISS, YAGNI
```yaml
principles:
  DRY:
    name: "Don't Repeat Yourself"
    description: "Avoid code duplication"
    tip: "Extract common logic into reusable functions"

  KISS:
    name: "Keep It Simple, Stupid"
    description: "Favor simple solutions"
    tip: "Choose clarity over cleverness"

  YAGNI:
    name: "You Aren't Gonna Need It"
    description: "Don't add functionality until needed"
    tip: "Solve current problems, not hypothetical ones"
```

## Linting and Formatting

### Python
```yaml
python_tools:
  formatter:
    tool: "black"
    command: "black ."
    config: "pyproject.toml"

  linter:
    tool: "ruff"
    command: "ruff check ."
    config: "pyproject.toml"

  type_checker:
    tool: "mypy"
    command: "mypy src/"
    config: "mypy.ini"

  import_sorter:
    tool: "isort"
    command: "isort ."
    config: "pyproject.toml"
```

### JavaScript/TypeScript
```yaml
javascript_tools:
  formatter:
    tool: "prettier"
    command: "prettier --write ."
    config: ".prettierrc"

  linter:
    tool: "eslint"
    command: "eslint ."
    config: ".eslintrc"

  type_checker:
    tool: "typescript"
    command: "tsc --noEmit"
    config: "tsconfig.json"
```

### Configuration Example (Python)
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

## Code Review Checklist

### Functionality
- [ ] Code meets requirements
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] Business logic correct
- [ ] No regressions introduced

### Code Quality
- [ ] Follows established patterns
- [ ] No code duplication
- [ ] Appropriate abstraction level
- [ ] Functions are focused (single responsibility)
- [ ] Variables have descriptive names
- [ ] Code is self-documenting

### Architecture
- [ ] Fits into existing architecture
- [ ] No circular dependencies
- [ ] Proper separation of concerns
- [ ] Follows dependency injection
- [ ] Loose coupling maintained
- [ ] High cohesion achieved

### Testing
- [ ] Unit tests included
- [ ] Integration tests where needed
- [ ] Tests cover edge cases
- [ ] All tests pass
- [ ] Coverage targets met
- [ ] No flaky tests

### Security
- [ ] Input validation/sanitization
- [ ] No security vulnerabilities
- [ ] Sensitive data protected
- [ ] Authentication/authorization correct
- [ ] Dependencies up to date
- [ ] No hardcoded secrets

### Performance
- [ ] No obvious performance issues
- [ ] Database queries optimized
- [ ] Proper caching implemented
- [ ] No memory leaks
- [ ] Acceptable response times
- [ ] Scalability considered

### Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README updated if needed
- [ ] Comments add value
- [ ] No outdated comments
- [ ] Breaking changes noted

### Maintainability
- [ ] Code is readable
- [ ] Easy to modify
- [ ] Easy to test
- [ ] No magic numbers
- [ ] Configuration externalized
- [ ] Backward compatibility considered

## Complexity Management

### Cyclomatic Complexity
```yaml
complexity_limits:
  function:
    max_complexity: 10
    action_if_exceeded: "Refactor into smaller functions"

  class:
    max_methods: 15
    action_if_exceeded: "Split into multiple classes"

  file:
    max_lines: 500
    action_if_exceeded: "Split into multiple files"
```

### Nesting Depth
```python
# Bad: Deep nesting
def process_data(data):
    if data:
        if data.is_valid():
            if data.has_permission():
                if data.is_active():
                    # Do something
                    pass

# Good: Early returns
def process_data(data):
    if not data:
        return

    if not data.is_valid():
        return

    if not data.has_permission():
        return

    if not data.is_active():
        return

    # Do something
```

### Function Length
```yaml
function_length:
  ideal: "< 20 lines"
  maximum: "< 50 lines"
  action_if_exceeded: |
    - Extract helper functions
    - Simplify logic
    - Remove duplication
```

## Naming Conventions

### General Guidelines
```yaml
naming:
  variables:
    style: "snake_case"
    example: "user_email"
    rules:
      - Descriptive names
      - Avoid abbreviations
      - No single letters (except i, j in loops)

  functions:
    style: "snake_case"
    example: "calculate_total_price"
    rules:
      - Verb + noun
      - Describe action
      - Clear intent

  classes:
    style: "PascalCase"
    example: "UserManager"
    rules:
      - Noun or noun phrase
      - Singular form
      - Meaningful name

  constants:
    style: "UPPER_SNAKE_CASE"
    example: "MAX_RETRY_ATTEMPTS"
    rules:
      - All caps
      - Descriptive
      - Group related constants
```

### Avoid Bad Names
```python
# Bad
def fn(x, y):
    tmp = x + y
    data = tmp * 2
    return data

# Good
def calculate_doubled_sum(first_number, second_number):
    sum_result = first_number + second_number
    doubled_result = sum_result * 2
    return doubled_result
```

## Common Code Smells

### Long Method
**Problem**: Method does too much
**Solution**: Extract smaller, focused methods

### Large Class
**Problem**: Class has too many responsibilities
**Solution**: Split into multiple classes (Single Responsibility)

### Duplicate Code
**Problem**: Same logic in multiple places
**Solution**: Extract to shared function/class

### Feature Envy
**Problem**: Method uses another class more than its own
**Solution**: Move method to the other class

### Data Clumps
**Problem**: Same group of data appears together
**Solution**: Create a class to represent the group

### Long Parameter List
**Problem**: Too many function parameters
**Solution**: Use parameter object or builder pattern

### Primitive Obsession
**Problem**: Using primitives instead of small objects
**Solution**: Create value objects

## Refactoring Techniques

### Extract Method
```python
# Before
def process_order(order):
    # Validate order
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Invalid total")

    # Calculate shipping
    shipping = 0
    if order.total < 50:
        shipping = 10

    # Apply discount
    discount = 0
    if order.total > 100:
        discount = order.total * 0.1

    return order.total + shipping - discount

# After
def process_order(order):
    validate_order(order)
    shipping = calculate_shipping(order)
    discount = calculate_discount(order)
    return order.total + shipping - discount

def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Invalid total")

def calculate_shipping(order):
    return 10 if order.total < 50 else 0

def calculate_discount(order):
    return order.total * 0.1 if order.total > 100 else 0
```

### Replace Magic Numbers
```python
# Before
def apply_discount(price):
    if price > 100:
        return price * 0.9
    return price

# After
DISCOUNT_THRESHOLD = 100
DISCOUNT_RATE = 0.1

def apply_discount(price):
    if price > DISCOUNT_THRESHOLD:
        return price * (1 - DISCOUNT_RATE)
    return price
```

### Introduce Parameter Object
```python
# Before
def create_user(name, email, age, address, phone):
    pass

# After
@dataclass
class UserData:
    name: str
    email: str
    age: int
    address: str
    phone: str

def create_user(user_data: UserData):
    pass
```

## Code Quality Metrics

### Tracking Metrics
```yaml
metrics:
  coverage:
    target: ">80%"
    tool: "coverage.py / jest"

  duplication:
    target: "<5%"
    tool: "jscpd / pylint"

  complexity:
    target: "<10 per function"
    tool: "radon / eslint"

  maintainability_index:
    target: ">65"
    tool: "radon / CodeClimate"

  technical_debt:
    target: "<8 hours"
    tool: "SonarQube"
```

## Pre-commit Hooks

### Setup Example
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

---
*Use this skill when enforcing code quality standards and conducting code reviews*
