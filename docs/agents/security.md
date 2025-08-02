# Security Agent

The Security Agent specializes in identifying vulnerabilities, implementing security best practices, and ensuring secure coding patterns throughout the development lifecycle. It provides comprehensive security analysis and automated security testing.

## Overview

The Security Agent excels at:
- **Vulnerability Detection**: Identifying security flaws and potential attack vectors
- **Security Implementation**: Writing secure code with proper validation and sanitization
- **Compliance Checking**: Ensuring adherence to security standards and best practices
- **Threat Modeling**: Analyzing security risks and attack scenarios
- **Security Testing**: Creating comprehensive security test suites

## When to Use the Security Agent

### 🔒 Security Reviews
```bash
# Before releasing new features
/security-review "user authentication system"
/security-review "payment processing endpoint"
/security-review "file upload functionality"
```

### 🛡️ Vulnerability Assessment
```bash
# Regular security audits
/security-audit "check for SQL injection vulnerabilities"
/security-audit "analyze input validation patterns"
/security-audit "review authentication mechanisms"
```

### 🔐 Secure Implementation
```bash
# When implementing security-critical features
/impl --security "OAuth2 authentication flow"
/impl --security "password reset with token validation"
/impl --security "API rate limiting and abuse prevention"
```

## Security Capabilities

### Vulnerability Detection

The Security Agent identifies common security vulnerabilities:

```python
# Example Vulnerability Analysis
@security_agent.scan_vulnerabilities()
def identify_security_issues():
    """
    Detects issues like:
    - SQL injection in database queries
    - XSS vulnerabilities in user input handling
    - CSRF token missing in state-changing operations
    - Insecure password storage mechanisms
    - Exposed sensitive data in logs or responses
    """
    return {
        "critical": ["SQL injection in user search", "Hardcoded API keys"],
        "high": ["Missing CSRF protection", "Weak password policies"],
        "medium": ["Information disclosure in errors", "Missing security headers"],
        "low": ["Verbose error messages", "Missing rate limiting"]
    }
```

### Security Implementation Patterns

Implements secure coding patterns and best practices:

```python
# Secure Authentication Implementation
class SecureAuthService:
    """Security Agent implemented authentication with best practices."""
    
    def __init__(self, password_hasher, token_manager, rate_limiter):
        self.password_hasher = password_hasher  # bcrypt with salt rounds >= 12
        self.token_manager = token_manager      # JWT with proper expiration
        self.rate_limiter = rate_limiter        # Prevent brute force attacks
    
    async def authenticate_user(self, email: str, password: str, client_ip: str) -> AuthResult:
        """Secure user authentication with comprehensive protection."""
        
        # Rate limiting to prevent brute force
        if not await self.rate_limiter.check_limit(client_ip, "auth_attempts"):
            raise AuthenticationError("Too many attempts. Try again later.")
        
        # Input validation and sanitization
        email = self._validate_and_sanitize_email(email)
        if not self._validate_password_strength(password):
            raise AuthenticationError("Invalid credentials")
        
        # Secure user lookup with constant-time comparison
        user = await self._secure_user_lookup(email)
        if not user or not self._verify_password_constant_time(password, user.password_hash):
            # Log failed attempt without revealing whether user exists
            await self._log_failed_attempt(email, client_ip)
            raise AuthenticationError("Invalid credentials")
        
        # Generate secure tokens
        access_token = self.token_manager.create_access_token(
            user_id=user.id,
            expires_in=timedelta(hours=1)  # Short-lived access tokens
        )
        refresh_token = self.token_manager.create_refresh_token(
            user_id=user.id,
            expires_in=timedelta(days=30)  # Longer-lived refresh tokens
        )
        
        # Log successful authentication
        await self._log_successful_auth(user.id, client_ip)
        
        return AuthResult(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token
        )
```

### Input Validation and Sanitization

Comprehensive input protection patterns:

```python
# Security Agent Input Validation Framework
class SecureInputValidator:
    """Comprehensive input validation with security focus."""
    
    @staticmethod
    def validate_user_input(data: dict, schema: ValidationSchema) -> dict:
        """Validate and sanitize user input against schema."""
        
        validated_data = {}
        
        for field_name, field_schema in schema.fields.items():
            raw_value = data.get(field_name)
            
            # Required field validation
            if field_schema.required and raw_value is None:
                raise ValidationError(f"{field_name} is required")
            
            if raw_value is not None:
                # Type validation
                validated_value = field_schema.validate_type(raw_value)
                
                # Length validation
                if hasattr(field_schema, 'max_length'):
                    if len(str(validated_value)) > field_schema.max_length:
                        raise ValidationError(f"{field_name} exceeds maximum length")
                
                # Pattern validation (regex)
                if hasattr(field_schema, 'pattern'):
                    if not re.match(field_schema.pattern, str(validated_value)):
                        raise ValidationError(f"{field_name} format is invalid")
                
                # XSS prevention
                if field_schema.sanitize_html:
                    validated_value = bleach.clean(
                        validated_value,
                        tags=field_schema.allowed_tags or [],
                        attributes=field_schema.allowed_attributes or {}
                    )
                
                # SQL injection prevention
                if field_schema.escape_sql:
                    validated_value = sqlalchemy.text(":value").params(value=validated_value)
                
                validated_data[field_name] = validated_value
        
        return validated_data
```

### Security Testing Implementation

Automated security test generation:

```python
# Security Test Suite Generation
class SecurityTestGenerator:
    """Generates comprehensive security tests."""
    
    def generate_auth_security_tests(self, auth_endpoint: str) -> List[SecurityTest]:
        """Generate authentication security tests."""
        
        return [
            # Brute force protection tests
            SecurityTest(
                name="test_brute_force_protection",
                description="Verify rate limiting prevents brute force attacks",
                test_function=self._test_brute_force_protection,
                endpoint=auth_endpoint
            ),
            
            # SQL injection tests
            SecurityTest(
                name="test_sql_injection_protection", 
                description="Verify protection against SQL injection in auth",
                test_function=self._test_sql_injection_protection,
                endpoint=auth_endpoint,
                payloads=["' OR '1'='1", "'; DROP TABLE users; --"]
            ),
            
            # XSS protection tests
            SecurityTest(
                name="test_xss_protection",
                description="Verify XSS protection in user input",
                test_function=self._test_xss_protection,
                endpoint=auth_endpoint,
                payloads=["<script>alert('xss')</script>", "javascript:alert('xss')"]
            ),
            
            # CSRF protection tests
            SecurityTest(
                name="test_csrf_protection",
                description="Verify CSRF token requirement",
                test_function=self._test_csrf_protection,
                endpoint=auth_endpoint
            )
        ]
```

## Security Analysis Types

### Vulnerability Scanning
```bash
/security-scan --type=vulnerabilities "payment processing"
```

**Analysis Focus:**
- OWASP Top 10 vulnerability patterns
- Input validation and output encoding issues
- Authentication and session management flaws
- Access control and authorization problems

### Code Security Review
```bash  
/security-review --type=code "user registration system"
```

**Analysis Focus:**
- Secure coding pattern compliance
- Cryptographic implementations
- Error handling and information disclosure
- Logging and monitoring security considerations

### Infrastructure Security
```bash
/security-audit --type=infrastructure "deployment configuration"
```

**Analysis Focus:**
- Container and deployment security
- Network security and communication encryption
- Environment variable and secrets management
- Database and storage security configuration

### Compliance Assessment
```bash
/security-compliance --standard=PCI-DSS "payment system"
```

**Analysis Focus:**
- Regulatory compliance requirements (PCI-DSS, GDPR, HIPAA)
- Industry-specific security standards
- Data protection and privacy requirements
- Audit trail and monitoring requirements

## Security Best Practices Implementation

### Authentication Security
```python
# Secure Password Handling
class SecurePasswordManager:
    """Security Agent password management with best practices."""
    
    def __init__(self):
        self.min_length = 12
        self.require_complexity = True
        self.hash_rounds = 12  # bcrypt cost factor
    
    def hash_password(self, password: str) -> str:
        """Hash password with secure parameters."""
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        # Use bcrypt with appropriate cost factor
        salt = bcrypt.gensalt(rounds=self.hash_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password with constant-time comparison."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except ValueError:
            # Invalid hash format
            return False
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements."""
        if len(password) < self.min_length:
            return False
        
        if self.require_complexity:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password) 
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            return all([has_upper, has_lower, has_digit, has_special])
        
        return True
```

### API Security Implementation
```python
# Secure API Framework
class SecureAPIFramework:
    """Security Agent API security implementation."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.input_validator = SecureInputValidator()
        self.token_manager = JWTTokenManager()
    
    def secure_endpoint(self, 
                       endpoint_func,
                       requires_auth: bool = True,
                       rate_limit: str = "100/hour",
                       input_schema: ValidationSchema = None):
        """Decorator for securing API endpoints."""
        
        def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            
            # Rate limiting
            if not self.rate_limiter.check_limit(request.client.host, rate_limit):
                raise HTTPException(429, "Rate limit exceeded")
            
            # Authentication
            if requires_auth:
                token = self._extract_auth_token(request)
                user = self.token_manager.validate_token(token)
                kwargs['current_user'] = user
            
            # Input validation
            if input_schema and request.method in ['POST', 'PUT', 'PATCH']:
                validated_data = self.input_validator.validate_user_input(
                    await request.json(),
                    input_schema
                )
                kwargs['validated_data'] = validated_data
            
            # Execute endpoint
            response = endpoint_func(*args, **kwargs)
            
            # Security headers
            response.headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY', 
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
            })
            
            return response
        
        return wrapper
```

### Data Protection Implementation
```python
# Secure Data Handling
class SecureDataManager:
    """Security Agent data protection implementation."""
    
    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)
        self.pii_fields = {'email', 'phone', 'ssn', 'address'}
    
    def encrypt_sensitive_data(self, data: dict) -> dict:
        """Encrypt PII and sensitive data fields."""
        encrypted_data = data.copy()
        
        for field_name, field_value in data.items():
            if self._is_sensitive_field(field_name):
                if field_value is not None:
                    encrypted_value = self.fernet.encrypt(
                        str(field_value).encode('utf-8')
                    )
                    encrypted_data[field_name] = encrypted_value.decode('utf-8')
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, encrypted_data: dict) -> dict:
        """Decrypt PII and sensitive data fields."""
        decrypted_data = encrypted_data.copy()
        
        for field_name, field_value in encrypted_data.items():
            if self._is_sensitive_field(field_name):
                if field_value is not None:
                    try:
                        decrypted_value = self.fernet.decrypt(
                            field_value.encode('utf-8')
                        )
                        decrypted_data[field_name] = decrypted_value.decode('utf-8')
                    except InvalidToken:
                        # Handle decryption errors gracefully
                        decrypted_data[field_name] = None
        
        return decrypted_data
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Determine if field contains sensitive data."""
        return (field_name.lower() in self.pii_fields or 
                'password' in field_name.lower() or
                'secret' in field_name.lower() or
                'token' in field_name.lower())
```

## Security Testing Strategies

### Automated Security Testing
```python
# Security Test Suite
class SecurityTestSuite:
    """Comprehensive automated security testing."""
    
    def run_security_tests(self, target_url: str) -> SecurityTestReport:
        """Run complete security test suite."""
        
        test_results = []
        
        # Authentication tests
        test_results.extend(self._test_authentication_security(target_url))
        
        # Input validation tests
        test_results.extend(self._test_input_validation(target_url))
        
        # Authorization tests  
        test_results.extend(self._test_authorization(target_url))
        
        # Session management tests
        test_results.extend(self._test_session_management(target_url))
        
        # Infrastructure tests
        test_results.extend(self._test_infrastructure_security(target_url))
        
        return SecurityTestReport(
            target=target_url,
            tests_run=len(test_results),
            vulnerabilities_found=len([t for t in test_results if not t.passed]),
            results=test_results
        )
```

### Penetration Testing Framework
```python
# Automated Penetration Testing
class SecurityPenetrationTester:
    """Automated penetration testing capabilities."""
    
    def test_authentication_bypass(self, auth_endpoint: str) -> List[SecurityFinding]:
        """Test for authentication bypass vulnerabilities."""
        findings = []
        
        # Test SQL injection in authentication
        sql_payloads = [
            "admin'--",
            "' OR '1'='1'--",
            "' UNION SELECT 1,1,1--"
        ]
        
        for payload in sql_payloads:
            result = self._test_auth_with_payload(auth_endpoint, payload)
            if result.bypassed_auth:
                findings.append(SecurityFinding(
                    severity="CRITICAL",
                    title="SQL Injection Authentication Bypass",
                    description=f"Authentication can be bypassed using SQL injection payload: {payload}",
                    recommendation="Use parameterized queries and input validation"
                ))
        
        return findings
```

## Integration with Other Agents

### Security → Review
```bash
/security-audit "payment processing system"    # Identify security issues
/review --security payment-service.py         # Apply security-focused code review
```

### Security → Debug
```bash
/security-scan "authentication vulnerabilities"  # Find security issues
/debug --security "fix SQL injection in login"   # Debug and fix security issues
```

### Security → Implementation
```bash
/impl --security "secure file upload with validation"  # Implement with security focus
/security-test "file upload endpoint"                  # Test the implementation
```

## Common Security Scenarios

### API Security Hardening
```bash
/security-review "REST API endpoints"
/security-implement "rate limiting and input validation"
/security-test "API security controls"
```

### Authentication System Security
```bash
/security-audit "user authentication flow"
/security-implement "secure password reset mechanism"
/security-test "authentication security controls"
```

### Data Protection Implementation
```bash
/security-review "user data handling"
/security-implement "PII encryption and data masking"
/security-test "data protection controls"
```

## Best Practices

### 1. Security by Design
Always consider security from the beginning:
```bash
# Good: Security considerations from the start
/plan --security "user registration with secure defaults"

# Less ideal: Adding security as an afterthought
/impl "user registration" && /security-review "user registration"
```

### 2. Defense in Depth
Implement multiple layers of security:
- Input validation at multiple layers
- Authentication AND authorization
- Encryption in transit AND at rest
- Monitoring AND alerting

### 3. Regular Security Audits
```bash
# Schedule regular security reviews
/security-audit --comprehensive "entire application"
/security-test --regression "all security controls"
```

### 4. Stay Updated
Keep security knowledge current:
- Monitor OWASP Top 10 updates
- Follow security advisories for dependencies
- Implement security patches promptly
- Review and update security tests regularly

## Next Steps

- Learn about [QA Agent](qa.md) for security testing integration
- Explore [Reviewer Agent](reviewer.md) for security code reviews  
- Understand [Debug Agent](debug.md) for security issue resolution
- Read about [Compliance Standards](../advanced/compliance.md)