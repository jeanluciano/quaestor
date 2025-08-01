# QA Agent

The QA (Quality Assurance) agent specializes in testing strategies, test implementation, and quality validation. It ensures code reliability through comprehensive test coverage, edge case identification, and quality metrics enforcement.

## Core Capabilities

### Test Design
- Creates comprehensive test strategies
- Identifies edge cases and boundary conditions
- Designs test scenarios from specifications
- Implements behavior-driven development (BDD)
- Creates property-based tests

### Test Implementation
- Writes unit tests with high coverage
- Creates integration tests
- Implements end-to-end tests
- Develops performance benchmarks
- Creates test fixtures and mocks

### Quality Analysis
- Measures and improves test coverage
- Identifies untested code paths
- Detects potential bugs through testing
- Validates error handling
- Ensures specification compliance

### Framework Expertise
- Python: pytest, unittest, mock
- JavaScript: Jest, Mocha, Cypress
- Rust: built-in testing, proptest
- Go: testing package, testify
- General: BDD, TDD, property-based testing

## When to Use

The QA agent excels at:
- **Test creation** for new features
- **Coverage improvement** for existing code
- **Edge case discovery** and testing
- **Test refactoring** and organization
- **Performance testing** and benchmarking
- **Test strategy planning** for complex features

## Testing Philosophy

### Test Pyramid
```
         /\
        /  \    E2E Tests (Few)
       /    \   - Critical user journeys
      /------\  - Full system integration
     /        \ 
    /          \  Integration Tests (Some)
   /            \ - Component interactions
  /              \- API contract tests
 /----------------\
/                  \ Unit Tests (Many)
/                    \- Individual functions
----------------------- Fast, isolated, specific
```

### Testing Principles
1. **Fast**: Tests should run quickly
2. **Isolated**: Tests shouldn't depend on each other
3. **Repeatable**: Same result every time
4. **Self-Validating**: Pass or fail clearly
5. **Thorough**: Cover happy path and edge cases

## Test Implementation Examples

### Unit Tests
```python
# Testing a user service
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from services.user_service import UserService
from models.user import User
from exceptions import ValidationError, DuplicateError


class TestUserService:
    """Test suite for UserService."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create service instance with mock repo."""
        return UserService(repository=mock_repo)
    
    def test_create_user_success(self, service, mock_repo):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        expected_user = User(id=1, **user_data)
        mock_repo.find_by_email.return_value = None
        mock_repo.create.return_value = expected_user
        
        # Act
        result = service.create_user(**user_data)
        
        # Assert
        assert result.id == 1
        assert result.email == user_data["email"]
        mock_repo.find_by_email.assert_called_once_with(user_data["email"])
        mock_repo.create.assert_called_once()
    
    def test_create_user_duplicate_email(self, service, mock_repo):
        """Test user creation with duplicate email."""
        # Arrange
        existing_user = User(id=1, email="test@example.com")
        mock_repo.find_by_email.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(DuplicateError) as exc:
            service.create_user(
                email="test@example.com",
                password="SecurePass123!",
                name="Test User"
            )
        
        assert "Email already exists" in str(exc.value)
        mock_repo.create.assert_not_called()
    
    @pytest.mark.parametrize("password,error_message", [
        ("short", "Password must be at least 8 characters"),
        ("no-uppercase", "Password must contain uppercase letter"),
        ("NO-LOWERCASE", "Password must contain lowercase letter"),
        ("NoSpecial123", "Password must contain special character"),
    ])
    def test_create_user_invalid_password(
        self, service, mock_repo, password, error_message
    ):
        """Test password validation."""
        with pytest.raises(ValidationError) as exc:
            service.create_user(
                email="test@example.com",
                password=password,
                name="Test User"
            )
        
        assert error_message in str(exc.value)
```

### Integration Tests
```javascript
// Testing API endpoints
const request = require('supertest');
const app = require('../app');
const { sequelize, User } = require('../models');
const { generateToken } = require('../utils/auth');

describe('User API Integration Tests', () => {
    let authToken;
    let testUser;
    
    beforeAll(async () => {
        // Setup database
        await sequelize.sync({ force: true });
    });
    
    beforeEach(async () => {
        // Create test user
        testUser = await User.create({
            email: 'test@example.com',
            password: 'TestPass123!',
            name: 'Test User'
        });
        
        // Generate auth token
        authToken = generateToken(testUser);
    });
    
    afterEach(async () => {
        // Clean up
        await User.destroy({ where: {} });
    });
    
    afterAll(async () => {
        await sequelize.close();
    });
    
    describe('GET /api/users/:id', () => {
        test('should return user when authenticated', async () => {
            const response = await request(app)
                .get(`/api/users/${testUser.id}`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);
            
            expect(response.body).toMatchObject({
                id: testUser.id,
                email: testUser.email,
                name: testUser.name
            });
            expect(response.body.password).toBeUndefined();
        });
        
        test('should return 401 when not authenticated', async () => {
            await request(app)
                .get(`/api/users/${testUser.id}`)
                .expect(401);
        });
        
        test('should return 404 for non-existent user', async () => {
            await request(app)
                .get('/api/users/99999')
                .set('Authorization', `Bearer ${authToken}`)
                .expect(404);
        });
    });
    
    describe('POST /api/users', () => {
        test('should create user with valid data', async () => {
            const newUser = {
                email: 'new@example.com',
                password: 'NewPass123!',
                name: 'New User'
            };
            
            const response = await request(app)
                .post('/api/users')
                .send(newUser)
                .expect(201);
            
            expect(response.body).toHaveProperty('id');
            expect(response.body.email).toBe(newUser.email);
            
            // Verify user was created
            const dbUser = await User.findOne({ 
                where: { email: newUser.email } 
            });
            expect(dbUser).toBeTruthy();
        });
        
        test('should validate required fields', async () => {
            const response = await request(app)
                .post('/api/users')
                .send({ email: 'test@example.com' })
                .expect(400);
            
            expect(response.body.errors).toContainEqual(
                expect.objectContaining({
                    field: 'password',
                    message: expect.any(String)
                })
            );
        });
    });
});
```

### End-to-End Tests
```typescript
// Using Cypress for E2E testing
describe('User Registration Flow', () => {
    beforeEach(() => {
        cy.visit('/register');
    });
    
    it('should register new user successfully', () => {
        // Fill registration form
        cy.get('[data-cy=email-input]').type('newuser@example.com');
        cy.get('[data-cy=password-input]').type('SecurePass123!');
        cy.get('[data-cy=confirm-password-input]').type('SecurePass123!');
        cy.get('[data-cy=name-input]').type('New User');
        
        // Submit form
        cy.get('[data-cy=register-button]').click();
        
        // Verify success
        cy.url().should('include', '/dashboard');
        cy.contains('Welcome, New User').should('be.visible');
        
        // Verify user can log out and log back in
        cy.get('[data-cy=logout-button]').click();
        cy.visit('/login');
        cy.get('[data-cy=email-input]').type('newuser@example.com');
        cy.get('[data-cy=password-input]').type('SecurePass123!');
        cy.get('[data-cy=login-button]').click();
        
        cy.url().should('include', '/dashboard');
    });
    
    it('should show validation errors', () => {
        // Try to submit empty form
        cy.get('[data-cy=register-button]').click();
        
        // Check validation messages
        cy.contains('Email is required').should('be.visible');
        cy.contains('Password is required').should('be.visible');
        
        // Test invalid email
        cy.get('[data-cy=email-input]').type('invalid-email');
        cy.get('[data-cy=register-button]').click();
        cy.contains('Invalid email format').should('be.visible');
        
        // Test password mismatch
        cy.get('[data-cy=email-input]').clear().type('test@example.com');
        cy.get('[data-cy=password-input]').type('Password123!');
        cy.get('[data-cy=confirm-password-input]').type('Different123!');
        cy.get('[data-cy=register-button]').click();
        cy.contains('Passwords do not match').should('be.visible');
    });
    
    it('should handle duplicate email', () => {
        // Create user first
        cy.task('createUser', {
            email: 'existing@example.com',
            password: 'Password123!'
        });
        
        // Try to register with same email
        cy.get('[data-cy=email-input]').type('existing@example.com');
        cy.get('[data-cy=password-input]').type('Password123!');
        cy.get('[data-cy=confirm-password-input]').type('Password123!');
        cy.get('[data-cy=register-button]').click();
        
        cy.contains('Email already registered').should('be.visible');
    });
});
```

### Property-Based Tests
```python
# Using hypothesis for property-based testing
from hypothesis import given, strategies as st
from hypothesis import assume
import string

from utils.validators import validate_email, validate_password


class TestValidators:
    """Property-based tests for validators."""
    
    @given(st.text())
    def test_email_validation_properties(self, email):
        """Test email validation properties."""
        result = validate_email(email)
        
        # If valid, must contain @ and .
        if result:
            assert '@' in email
            assert '.' in email.split('@')[1]
            assert len(email) >= 3
        
        # If invalid, must be missing requirements
        if not result:
            assume(email)  # Skip empty strings
            conditions = [
                '@' not in email,
                '.' not in email.split('@')[-1] if '@' in email else True,
                email.startswith('@'),
                email.endswith('@'),
                '..' in email,
            ]
            assert any(conditions)
    
    @given(st.text(
        alphabet=string.ascii_letters + string.digits + string.punctuation,
        min_size=1,
        max_size=100
    ))
    def test_password_validation_properties(self, password):
        """Test password validation properties."""
        result = validate_password(password)
        
        if result:
            # Valid passwords must meet all criteria
            assert len(password) >= 8
            assert any(c.isupper() for c in password)
            assert any(c.islower() for c in password)
            assert any(c.isdigit() for c in password)
            assert any(c in string.punctuation for c in password)
        else:
            # Invalid passwords must fail at least one criterion
            conditions = [
                len(password) < 8,
                not any(c.isupper() for c in password),
                not any(c.islower() for c in password),
                not any(c.isdigit() for c in password),
                not any(c in string.punctuation for c in password),
            ]
            assert any(conditions)
```

## Test Strategies

### Coverage Goals
- **Line Coverage**: Minimum 80%
- **Branch Coverage**: All conditional paths
- **Edge Cases**: Boundary conditions
- **Error Paths**: All error scenarios
- **Integration Points**: External dependencies

### Test Organization
```
tests/
├── unit/
│   ├── services/
│   ├── models/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
├── e2e/
│   ├── user_flows/
│   └── admin_flows/
├── fixtures/
├── mocks/
└── conftest.py
```

### Performance Testing
```python
import pytest
import time
from statistics import mean, stdev


def test_search_performance(large_dataset):
    """Test search performance with large dataset."""
    search_times = []
    
    # Warm up
    for _ in range(5):
        search_service.search("test")
    
    # Measure
    for _ in range(100):
        start = time.perf_counter()
        results = search_service.search("test query")
        end = time.perf_counter()
        search_times.append(end - start)
    
    # Assert performance requirements
    avg_time = mean(search_times)
    std_dev = stdev(search_times)
    
    assert avg_time < 0.1  # 100ms average
    assert max(search_times) < 0.5  # 500ms max
    assert std_dev < 0.05  # Consistent performance
```

## Best Practices

### Test Writing Guidelines
1. **Descriptive Names**: Test names should explain what they test
2. **Arrange-Act-Assert**: Clear test structure
3. **One Assertion**: Focus on one thing per test
4. **Independent Tests**: No shared state
5. **Fast Execution**: Mock external dependencies

### Mock Best Practices
- Mock at boundaries (database, API, filesystem)
- Don't mock what you own
- Verify mock interactions
- Use realistic test data
- Reset mocks between tests

### Test Data Management
- Use factories for test data creation
- Keep test data minimal but realistic
- Use deterministic data when possible
- Clean up after tests
- Consider data privacy in tests

## Integration with Other Agents

### From Implementer
- Receives code to test
- Understands implementation details
- Creates appropriate test cases
- Validates edge cases

### With Debugger
- Provides failing tests for bugs
- Creates regression tests
- Helps reproduce issues
- Validates fixes

### To Reviewer
- Provides coverage reports
- Documents test scenarios
- Shows quality metrics
- Highlights untested code

## Configuration

Customize QA behavior:

```json
{
  "agent_preferences": {
    "qa": {
      "coverage_threshold": 85,
      "test_framework": "pytest",
      "include_property_tests": true,
      "performance_tests": true,
      "mutation_testing": false
    }
  }
}
```

## Testing Checklist

### Unit Test Checklist
- [ ] Happy path tested
- [ ] Error cases covered
- [ ] Boundary conditions tested
- [ ] Null/empty inputs handled
- [ ] Dependencies mocked
- [ ] Assertions are specific

### Integration Test Checklist
- [ ] Component interactions tested
- [ ] Database transactions verified
- [ ] API contracts validated
- [ ] Error propagation tested
- [ ] Cleanup implemented
- [ ] Performance acceptable

### E2E Test Checklist
- [ ] Critical user journeys covered
- [ ] Cross-browser testing done
- [ ] Mobile responsiveness tested
- [ ] Error scenarios handled
- [ ] Performance monitored
- [ ] Accessibility validated

## Next Steps

- Learn about the [Debugger Agent](debugger.md) for fixing issues
- Explore the [Implementer Agent](implementer.md) for code creation
- Understand [Test Strategies](../advanced/testing.md)
- Read about the [/test Command](../commands/test.md)