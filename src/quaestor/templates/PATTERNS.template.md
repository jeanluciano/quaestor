# PATTERNS.md - Implementation Patterns and Best Practices

<!-- QUAESTOR:version:1.0 -->

## Overview

This document contains proven implementation patterns and best practices for working with {{ project_name }}. These patterns have been extracted from successful implementations and should be followed for consistency and quality.

## Core Implementation Patterns

### Error Handling Pattern

<!-- PATTERN:error-handling:START -->
```{{ primary_language }}
# Standard error handling approach
try:
    # Operation that might fail
    result = perform_operation()
except SpecificError as e:
    # Log error with context
    logger.error(f"Operation failed: {e}", extra={"context": context})
    # Graceful recovery or re-raise
    raise OperationError("User-friendly message") from e
```
<!-- PATTERN:error-handling:END -->

### Validation Pattern

<!-- PATTERN:validation:START -->
```{{ primary_language }}
# Input validation before processing
def validate_input(data: Dict[str, Any]) -> ValidationResult:
    errors = []
    
    # Required field validation
    if not data.get("required_field"):
        errors.append("required_field is missing")
    
    # Type validation
    if not isinstance(data.get("number_field"), (int, float)):
        errors.append("number_field must be numeric")
    
    return ValidationResult(valid=not errors, errors=errors)
```
<!-- PATTERN:validation:END -->

### Testing Pattern

<!-- PATTERN:testing:START -->
```{{ primary_language }}
# Standard test structure
class TestFeature:
    def setup_method(self):
        # Setup test data
        self.test_data = create_test_data()
    
    def test_happy_path(self):
        # Test normal operation
        result = feature_function(self.test_data)
        assert result.success
    
    def test_error_case(self):
        # Test error handling
        with pytest.raises(ExpectedError):
            feature_function(invalid_data)
```
<!-- PATTERN:testing:END -->

## Architecture Patterns

### Service Layer Pattern

<!-- PATTERN:service-layer:START -->
- **Separation of Concerns**: Business logic separate from infrastructure
- **Dependency Injection**: Services receive dependencies, don't create them
- **Interface Contracts**: Clear input/output contracts for each service
- **Error Boundaries**: Services handle their own errors gracefully
<!-- PATTERN:service-layer:END -->

### Repository Pattern

<!-- PATTERN:repository:START -->
- **Data Access Abstraction**: Hide database details from business logic
- **Query Methods**: Specific methods for each query type
- **Transaction Management**: Handle transactions at repository level
- **Caching Strategy**: Implement caching within repository when needed
<!-- PATTERN:repository:END -->

## Code Organization Patterns

### Module Structure

<!-- PATTERN:module-structure:START -->
```
module/
├── __init__.py          # Public API exports
├── models.py           # Data models/schemas
├── services.py         # Business logic
├── repository.py       # Data access layer
├── validators.py       # Input validation
├── exceptions.py       # Module-specific exceptions
└── tests/
    ├── test_services.py
    └── test_repository.py
```
<!-- PATTERN:module-structure:END -->

### Import Organization

<!-- PATTERN:imports:START -->
```{{ primary_language }}
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
from sqlalchemy import create_engine

# Local application imports
from app.core import settings
from app.models import User
from app.services import UserService
```
<!-- PATTERN:imports:END -->

## Performance Patterns

### Caching Pattern

<!-- PATTERN:caching:START -->
```{{ primary_language }}
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=128)
def expensive_operation(param: str) -> Result:
    # Expensive computation
    return compute_result(param)

# For time-based caching
cache_store = {}
cache_timestamps = {}

def cached_with_ttl(key: str, ttl_seconds: int = 300):
    if key in cache_store:
        if time.time() - cache_timestamps[key] < ttl_seconds:
            return cache_store[key]
    
    result = compute_result(key)
    cache_store[key] = result
    cache_timestamps[key] = time.time()
    return result
```
<!-- PATTERN:caching:END -->

### Batch Processing Pattern

<!-- PATTERN:batch-processing:START -->
```{{ primary_language }}
def process_in_batches(items: List[Item], batch_size: int = 100):
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
        
        # Progress tracking
        progress = (i + len(batch)) / len(items) * 100
        logger.info(f"Processing: {progress:.1f}% complete")
    
    return results
```
<!-- PATTERN:batch-processing:END -->

## Security Patterns

### Input Sanitization

<!-- PATTERN:input-sanitization:START -->
```{{ primary_language }}
import html
import re

def sanitize_user_input(text: str) -> str:
    # Remove HTML tags
    text = re.sub('<.*?>', '', text)
    
    # Escape special characters
    text = html.escape(text)
    
    # Limit length
    max_length = 1000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()
```
<!-- PATTERN:input-sanitization:END -->

### Authentication Pattern

<!-- PATTERN:authentication:START -->
```{{ primary_language }}
def require_authentication(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        # Check authentication
        if not request.user.is_authenticated:
            raise AuthenticationError("Authentication required")
        
        # Check permissions
        if not has_permission(request.user, func.__name__):
            raise PermissionError("Insufficient permissions")
        
        return func(request, *args, **kwargs)
    return wrapper
```
<!-- PATTERN:authentication:END -->

## Anti-Patterns to Avoid

### ❌ God Object
- Classes that do too much
- Solution: Split into focused, single-responsibility classes

### ❌ Magic Numbers
- Hard-coded values without explanation
- Solution: Use named constants or configuration

### ❌ Catch-All Exception Handling
- `except Exception:` without specific handling
- Solution: Catch specific exceptions and handle appropriately

### ❌ Premature Optimization
- Optimizing before measuring
- Solution: Profile first, optimize bottlenecks only

## Project-Specific Patterns

<!-- PROJECT-PATTERNS:START -->
<!-- Add your project-specific patterns here -->




<!-- PROJECT-PATTERNS:END -->

## Pattern Evolution

As the project evolves, new patterns will emerge. Document them here:

1. **Identify Pattern**: When you notice a repeated solution
2. **Document Pattern**: Add it to the appropriate section
3. **Review Pattern**: Ensure it aligns with architecture principles
4. **Share Pattern**: Discuss with team for adoption

Remember: Patterns are guidelines, not rigid rules. Use judgment for each specific case.