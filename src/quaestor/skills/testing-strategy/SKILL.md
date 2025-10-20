---
name: Testing Strategy
description: Comprehensive testing patterns, coverage requirements, and test frameworks. Use when implementing tests, setting up test infrastructure, or defining testing standards for projects.
---

# Testing Strategy

## Purpose
Provides testing best practices, patterns, and guidelines for comprehensive test coverage across unit, integration, and end-to-end testing.

## When to Use
- Setting up testing infrastructure
- Implementing test coverage
- Defining testing standards
- Writing unit, integration, or E2E tests
- Improving test quality
- Debugging test failures

## Testing Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /____\     - User workflows
     /      \    - Full system tests
    / Integr.\
   /  ation   \  Integration Tests (Some)
  /____________\ - Component interactions
 /              \
/  Unit  Tests  \ Unit Tests (Many)
/________________\ - Individual functions
                   - Pure logic
```

## Testing Levels

### Unit Tests
**Purpose**: Test individual components in isolation

**Characteristics:**
- Fast execution (< 10ms per test)
- No external dependencies
- Focused on single function/method
- High code coverage target (>80%)

**When to Write:**
- For all business logic
- For utility functions
- For data transformations
- For validation logic

**Example Structure:**
```python
def test_user_validation():
    # Arrange
    user = User(email="test@example.com", age=25)

    # Act
    result = validate_user(user)

    # Assert
    assert result.is_valid
    assert len(result.errors) == 0
```

### Integration Tests
**Purpose**: Test component interactions

**Characteristics:**
- Medium execution time
- Tests multiple components together
- May use test databases
- Verify integration points

**When to Write:**
- For API endpoints
- For database operations
- For external service integrations
- For message queue handlers

**Example Structure:**
```python
def test_user_creation_workflow():
    # Setup
    db = setup_test_database()

    # Act
    response = api_client.post('/users', data=user_data)
    user = db.query(User).filter_by(email=user_data['email']).first()

    # Assert
    assert response.status_code == 201
    assert user is not None
    assert user.email == user_data['email']
```

### End-to-End Tests
**Purpose**: Test complete user workflows

**Characteristics:**
- Slow execution
- Tests full system
- Simulates real user behavior
- Fewer in number

**When to Write:**
- For critical user paths
- For key business workflows
- For regression prevention
- For deployment validation

## Testing Best Practices

### General Principles
- ✅ Write tests before or during development (TDD)
- ✅ Tests should be independent
- ✅ Tests should be deterministic (no flaky tests)
- ✅ Use descriptive test names
- ✅ Follow AAA pattern (Arrange, Act, Assert)
- ✅ Keep tests simple and focused
- ✅ Mock external dependencies in unit tests

### Test Organization
```yaml
test_structure:
  tests/:
    - unit/
      - test_models.py
      - test_services.py
      - test_utils.py

    - integration/
      - test_api.py
      - test_database.py
      - test_workflows.py

    - e2e/
      - test_user_journey.py
      - test_checkout_flow.py

    - fixtures/
      - data/
      - mocks/

    - conftest.py  # Shared fixtures
```

## Coverage Requirements

### Coverage Targets
```yaml
coverage_goals:
  overall: ">80%"
  unit_tests: ">90%"
  integration_tests: ">70%"

  critical_paths:
    authentication: "100%"
    payment_processing: "100%"
    data_security: "100%"

  acceptable_lower:
    ui_components: ">60%"
    configuration: ">50%"
```

### What to Test
- ✅ Business logic
- ✅ Edge cases
- ✅ Error conditions
- ✅ Input validation
- ✅ State transitions
- ✅ Integration points

### What NOT to Test
- ❌ Third-party library code
- ❌ Framework internals
- ❌ Simple getters/setters
- ❌ Configuration files
- ❌ Constants

## Testing Patterns

### Test Fixtures
```python
import pytest

@pytest.fixture
def sample_user():
    return User(
        id=1,
        email="test@example.com",
        name="Test User"
    )

@pytest.fixture
def database_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()
```

### Parameterized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    (None, None),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Mocking External Dependencies
```python
from unittest.mock import Mock, patch

def test_fetch_user_data():
    # Mock external API
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'id': 1, 'name': 'Test'}

        result = fetch_user_data(1)

        assert result['name'] == 'Test'
        mock_get.assert_called_once()
```

### Testing Async Code
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result is not None
```

## Test Quality Checklist

### Before Writing Tests
- [ ] Understand the requirement
- [ ] Identify edge cases
- [ ] Determine test level (unit/integration/e2e)
- [ ] Plan test data needs

### While Writing Tests
- [ ] Use descriptive test names
- [ ] Follow AAA pattern
- [ ] Test one thing per test
- [ ] Use fixtures for setup
- [ ] Mock external dependencies

### After Writing Tests
- [ ] All tests pass
- [ ] Coverage targets met
- [ ] No flaky tests
- [ ] Tests run quickly
- [ ] Tests are maintainable

## Testing Commands

### Python (pytest)
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run tests matching pattern
pytest -k "test_user"

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto

# Run only failed tests
pytest --lf
```

### JavaScript (Jest)
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- user.test.js
```

## Common Testing Anti-Patterns

### Testing Implementation Details
```python
# Bad: Testing internal implementation
def test_user_creation():
    user = User()
    user._internal_method()  # Testing private method
    assert user._state == "initialized"

# Good: Testing behavior
def test_user_creation():
    user = User()
    assert user.is_active()
```

### Flaky Tests
```python
# Bad: Time-dependent test
def test_timestamp():
    result = generate_timestamp()
    assert result == "2025-01-15 10:30:00"  # Will fail at different times

# Good: Test relative to current time
def test_timestamp():
    result = generate_timestamp()
    now = datetime.now()
    assert abs((result - now).total_seconds()) < 1
```

### Overly Complex Tests
```python
# Bad: Testing too much
def test_entire_workflow():
    user = create_user()
    order = create_order(user)
    payment = process_payment(order)
    shipment = ship_order(order)
    # Too many steps, hard to debug

# Good: Test each step separately
def test_create_user():
    user = create_user()
    assert user.id is not None

def test_create_order():
    order = create_order(test_user)
    assert order.user_id == test_user.id
```

## Test Data Management

### Test Database Setup
```python
@pytest.fixture(scope="session")
def database():
    """Create test database once per session"""
    db = create_test_db()
    yield db
    db.drop_all()

@pytest.fixture(scope="function")
def db_session(database):
    """Create clean session for each test"""
    session = database.create_session()
    yield session
    session.rollback()
```

### Test Data Builders
```python
class UserBuilder:
    def __init__(self):
        self.user = User(
            email="default@example.com",
            name="Default User"
        )

    def with_email(self, email):
        self.user.email = email
        return self

    def with_role(self, role):
        self.user.role = role
        return self

    def build(self):
        return self.user

# Usage
user = UserBuilder().with_email("admin@example.com").with_role("admin").build()
```

## CI/CD Integration

### GitHub Actions Example
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run tests
      run: pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
```

---
*Use this skill when implementing testing infrastructure and writing comprehensive tests*
