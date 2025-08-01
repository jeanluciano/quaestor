# Implementer Agent

The Implementer agent is a feature development and code writing specialist focused on creating production-quality code. It excels at translating specifications and designs into working implementations while following best practices and established patterns.

## Core Capabilities

### Code Implementation
- Writes clean, maintainable production code
- Implements features according to specifications
- Creates new components and modules
- Follows established coding patterns
- Handles error cases comprehensively

### Pattern Application
- Applies appropriate design patterns
- Follows framework conventions
- Implements SOLID principles
- Uses dependency injection
- Creates reusable abstractions

### Quality Focus
- Writes self-documenting code
- Includes comprehensive error handling
- Validates inputs thoroughly
- Implements logging appropriately
- Considers performance implications

### Language Expertise
- Python: Type hints, async/await, decorators
- JavaScript/TypeScript: Modern ES6+, promises, types
- Rust: Ownership, error handling, traits
- Go: Goroutines, channels, interfaces
- And more based on project needs

## When to Use

The Implementer agent excels at:
- **Feature implementation** from specifications
- **Algorithm development** and optimization
- **API endpoint creation** with proper validation
- **Data model implementation** with relationships
- **Integration development** with external services
- **Utility function creation** and helpers

## Implementation Process

### Phase 1: Understanding
```yaml
analyze:
  - Review specification or requirements
  - Understand existing code patterns
  - Identify dependencies and interfaces
  - Plan implementation approach
  - Consider edge cases and errors
```

### Phase 2: Implementation
```yaml
implement:
  - Write core functionality first
  - Add comprehensive error handling
  - Implement input validation
  - Include appropriate logging
  - Follow coding standards
```

### Phase 3: Polish
```yaml
polish:
  - Add documentation/comments
  - Optimize performance if needed
  - Ensure consistent code style
  - Review error messages
  - Verify specification compliance
```

## Code Quality Standards

### Clean Code Principles
```python
# Bad
def calc(x, y, z):
    return x * 0.1 + y * 0.2 + z * 0.7

# Good
def calculate_weighted_score(
    homework_score: float,
    quiz_score: float,
    exam_score: float
) -> float:
    """Calculate final grade using weighted averages.
    
    Args:
        homework_score: Score for homework (0-100)
        quiz_score: Score for quizzes (0-100)
        exam_score: Score for exam (0-100)
        
    Returns:
        Weighted average score (0-100)
    """
    HOMEWORK_WEIGHT = 0.1
    QUIZ_WEIGHT = 0.2
    EXAM_WEIGHT = 0.7
    
    return (
        homework_score * HOMEWORK_WEIGHT +
        quiz_score * QUIZ_WEIGHT +
        exam_score * EXAM_WEIGHT
    )
```

### Error Handling
```python
# Bad
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Good
def get_user(user_id: int) -> Optional[User]:
    """Retrieve user by ID with proper error handling."""
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")
    
    try:
        user = db.query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        if not user:
            logger.warning(f"User not found: {user_id}")
            return None
            
        return User.from_db_record(user)
        
    except DatabaseError as e:
        logger.error(f"Database error retrieving user {user_id}: {e}")
        raise ServiceError("Unable to retrieve user") from e
```

### Input Validation
```typescript
// Bad
function createUser(data: any) {
    return db.users.create(data);
}

// Good
interface CreateUserInput {
    email: string;
    password: string;
    name?: string;
}

function createUser(input: CreateUserInput): Promise<User> {
    // Validate email
    if (!isValidEmail(input.email)) {
        throw new ValidationError('Invalid email format');
    }
    
    // Validate password
    if (input.password.length < 8) {
        throw new ValidationError('Password must be at least 8 characters');
    }
    
    // Sanitize optional fields
    const userData = {
        email: input.email.toLowerCase().trim(),
        passwordHash: await hashPassword(input.password),
        name: input.name?.trim() || null,
        createdAt: new Date()
    };
    
    return db.users.create(userData);
}
```

## Common Implementation Patterns

### Repository Pattern
```python
class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self, db: Database):
        self._db = db
    
    async def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        query = "SELECT * FROM users WHERE id = %s"
        result = await self._db.fetch_one(query, user_id)
        return User(**result) if result else None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        query = "SELECT * FROM users WHERE email = %s"
        result = await self._db.fetch_one(query, email.lower())
        return User(**result) if result else None
    
    async def create(self, user_data: CreateUserDTO) -> User:
        """Create new user."""
        query = """
            INSERT INTO users (email, password_hash, name)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        result = await self._db.fetch_one(
            query,
            user_data.email,
            user_data.password_hash,
            user_data.name
        )
        return User(**result)
```

### Service Layer
```typescript
class AuthenticationService {
    constructor(
        private userRepo: UserRepository,
        private tokenService: TokenService,
        private emailService: EmailService
    ) {}
    
    async login(email: string, password: string): Promise<AuthResult> {
        // Find user
        const user = await this.userRepo.findByEmail(email);
        if (!user) {
            throw new AuthenticationError('Invalid credentials');
        }
        
        // Verify password
        const isValid = await verifyPassword(password, user.passwordHash);
        if (!isValid) {
            throw new AuthenticationError('Invalid credentials');
        }
        
        // Generate tokens
        const accessToken = this.tokenService.generateAccessToken(user);
        const refreshToken = this.tokenService.generateRefreshToken(user);
        
        // Store refresh token
        await this.tokenService.storeRefreshToken(user.id, refreshToken);
        
        return {
            user: user.toPublicJSON(),
            accessToken,
            refreshToken
        };
    }
}
```

## Framework-Specific Patterns

### React Components
```typescript
interface UserProfileProps {
    userId: string;
    onUpdate?: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ 
    userId, 
    onUpdate 
}) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    
    useEffect(() => {
        const fetchUser = async () => {
            try {
                setLoading(true);
                const userData = await api.users.get(userId);
                setUser(userData);
            } catch (err) {
                setError(err as Error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchUser();
    }, [userId]);
    
    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} />;
    if (!user) return <NotFound />;
    
    return (
        <div className="user-profile">
            <h2>{user.name}</h2>
            <p>{user.email}</p>
            {onUpdate && (
                <EditButton onClick={() => onUpdate(user)} />
            )}
        </div>
    );
};
```

### Django Views
```python
class UserViewSet(viewsets.ModelViewSet):
    """API endpoints for user management."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(organization=user.organization)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password."""
        user = self.get_object()
        
        # Check permissions
        if not request.user.can_reset_password(user):
            raise PermissionDenied("Cannot reset this user's password")
        
        # Generate reset token
        token = PasswordResetToken.objects.create(user=user)
        
        # Send email
        send_password_reset_email.delay(user.email, token.token)
        
        return Response(
            {"message": "Password reset email sent"},
            status=status.HTTP_200_OK
        )
```

## Best Practices

### Code Organization
1. **Single Responsibility**: Each function/class does one thing
2. **Meaningful Names**: Clear, descriptive naming
3. **Consistent Style**: Follow project conventions
4. **Proper Abstractions**: Don't over-engineer
5. **Test-Friendly**: Design for testability

### Performance Considerations
- Profile before optimizing
- Use appropriate data structures
- Minimize database queries
- Cache expensive operations
- Consider async where beneficial

### Security Practices
- Never trust user input
- Use parameterized queries
- Hash passwords properly
- Validate permissions
- Log security events

## Integration with Other Agents

### From Architect
Receives design specifications and implements them faithfully while:
- Following prescribed patterns
- Using specified technologies
- Maintaining architectural boundaries
- Implementing defined interfaces

### To QA
Provides code that is:
- Testable with clear interfaces
- Documented for test scenarios
- Includes test fixtures/mocks
- Has comprehensive error cases

### With Debugger
When issues arise:
- Adds detailed logging
- Implements fixes systematically
- Preserves existing behavior
- Improves error messages

## Configuration

Customize implementer behavior:

```json
{
  "agent_preferences": {
    "implementer": {
      "code_style": "verbose",
      "error_handling": "comprehensive",
      "documentation": "detailed",
      "performance_focus": false
    }
  }
}
```

## Common Tasks

### API Endpoint Implementation
1. Define route and method
2. Validate input parameters
3. Implement business logic
4. Handle errors gracefully
5. Return appropriate response
6. Add logging and monitoring

### Database Model Creation
1. Define schema/model
2. Add validations
3. Create migrations
4. Implement relationships
5. Add indexes for performance
6. Create repository methods

### Service Integration
1. Define service interface
2. Implement client/SDK
3. Add retry logic
4. Handle timeouts
5. Log requests/responses
6. Add circuit breaker if needed

## Next Steps

- Learn about the [QA Agent](qa.md) for testing your code
- Explore the [Refactorer Agent](refactorer.md) for improvements
- Understand [Code Quality Standards](../advanced/code-quality.md)
- Read about the [/impl Command](../commands/impl.md)