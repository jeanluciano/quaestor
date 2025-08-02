# /debug Command

The `/debug` command provides intelligent troubleshooting and bug fixing capabilities using specialized debugging agents. It focuses on root cause analysis and systematic problem resolution with multi-agent collaboration.

## Overview

The debug command employs multiple specialized agents:
- **QA Agent**: Test failure analysis and fix implementation
- **Security Agent**: Vulnerability assessment and security fixes
- **Implementer Agent**: Performance profiling and optimization
- **Architect Agent**: Design flaw identification and structural improvements

Debug helps with:
- Root cause analysis of issues
- Systematic bug fixing
- Performance optimization
- Test failure resolution
- Security vulnerability fixes

## Usage

### Basic Debugging
```bash
/debug "test failures in auth module"
```

Investigates and fixes test failures:
- Analyzes failing tests and error messages
- Identifies root causes
- Implements fixes
- Creates/updates tests to prevent regression

### Performance Debugging
```bash
/debug "performance bottleneck in API"
```

Profiles and optimizes performance issues:
- Identifies slow operations and bottlenecks
- Analyzes algorithm complexity
- Implements optimizations
- Provides before/after metrics

### Error-Specific Debugging
```bash
/debug --error "TypeError: undefined is not a function"
```

Focuses on specific error resolution:
- Analyzes stack traces and error patterns
- Identifies the source of the error
- Implements targeted fixes
- Adds preventive measures

## Debugging Workflow

### Phase 1: Issue Understanding 🔍
```bash
/debug "authentication failing randomly"
```

**Problem Classification:**
- Runtime errors: exceptions, crashes
- Test failures: unit, integration, e2e
- Performance: slow queries, memory leaks
- Logic bugs: incorrect behavior
- Security: vulnerabilities, exposures

**Reproduction Strategy:**
1. Capture error messages, stack traces, logs
2. Create minimal reproduction case
3. Document steps to reproduce
4. Identify environment factors

### Phase 2: Multi-Agent Analysis 🧪

The debug command automatically routes issues to appropriate agents:

#### QA Agent (Test Issues)
```bash
/debug "integration tests failing after database changes"
```

Handles:
- Test failure analysis and root cause identification
- Test fix implementation and improvement
- Coverage analysis and edge case identification
- Test suite optimization

#### Security Agent (Security Issues)
```bash
/debug "potential SQL injection vulnerability"
```

Handles:
- Vulnerability assessment and impact analysis
- Security fix implementation (input validation, sanitization)
- Authentication and authorization debugging
- Security test creation

#### Implementer Agent (Performance Issues)
```bash
/debug "API response times too slow"
```

Handles:
- Performance profiling and bottleneck identification
- Algorithm optimization and efficiency improvements
- Memory leak detection and resolution
- Code optimization implementation

#### Architect Agent (Design Issues)
```bash
/debug "circular dependency breaking the build"
```

Handles:
- Design flaw identification and analysis
- Structural improvements and refactoring
- Dependency issue resolution
- Architecture pattern violation fixes

### Phase 3: Systematic Fixing 🔧

**Fix Implementation Priority:**
1. **Stop the bleeding**: Immediate mitigation of critical issues
2. **Root cause**: Address underlying problems
3. **Prevention**: Add guards, validation, and safeguards
4. **Testing**: Ensure fixes work and add regression tests
5. **Documentation**: Update relevant documentation

**Common Fix Patterns:**
```python
# Null checks and validation
if user is None:
    raise ValueError("User cannot be None")

# Type safety improvements
def process_data(data: List[Dict[str, Any]]) -> ProcessedData:
    # Implementation with proper type hints

# Race condition fixes with synchronization
async with self._lock:
    # Critical section code

# SQL injection prevention
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Phase 4: Verification & Prevention ✅

**Testing Strategy:**
- **Reproduction test**: Captures the original bug
- **Fix verification**: Ensures the solution works
- **Regression tests**: Prevents future occurrences
- **Edge cases**: Tests related scenarios

**Quality Gates:**
- All tests passing
- No new issues introduced
- Performance within acceptable bounds
- Security validated

## Debugging Modes

### Quick Debug (~5 minutes)
```bash
/debug --quick "simple null pointer exception"
```
- Single issue focus with direct fix attempt
- Basic verification with existing tests
- Uses single agent for straightforward issues

### Standard Debug (~10 minutes)
```bash
/debug "user login occasionally fails"
```
- Root cause analysis with systematic investigation
- Proper fix implementation with testing
- Uses 1-2 agents depending on complexity

### Deep Debug (~20 minutes)
```bash
/debug --deep "intermittent data corruption"
```
- Comprehensive investigation of complex issues
- Multiple related fixes and improvements
- Multi-agent team collaboration
- Extensive testing and validation

### Performance Debug (~30 minutes)
```bash
/debug --profile "database queries are extremely slow"
```
- Full performance profiling and analysis
- Bottleneck identification and optimization
- Before/after performance metrics
- Comprehensive performance testing

## Advanced Debugging Features

### Interactive Debugging
```bash
# Add strategic logging
/debug "Add logging to user authentication flow"

# State inspection
/debug "Show variable state in payment processing"

# Focused test execution
/debug "Run only the failing auth tests"

# Performance profiling
/debug "Profile the slow database operations"
```

### AI-Powered Fix Suggestions
The debug command provides intelligent recommendations:
- Similar issue patterns from the codebase
- Common fix approaches for the error type
- Best practices for the specific technology
- Library solutions and tools

### Debugging Artifacts
Generated during debug sessions:
- **Debug logs**: Detailed execution traces
- **Performance profiles**: Timing and resource usage
- **Test cases**: Reproduction and regression tests
- **Fix documentation**: Explanation of changes made

## Integration with Other Commands

### From Other Commands
```bash
# When implementation hits an error
/impl "user registration system" 
# → encounters error → automatically suggests /debug

# When research finds problematic patterns
/research "authentication security issues"
# → finds vulnerabilities → can transition to /debug

# When review identifies failing tests
/review pull-request-branch
# → finds test failures → suggests /debug
```

### To Other Commands
```bash
# After debugging completes successfully
/debug "fix authentication bug" 
# → bug resolved → can continue with /impl

# After all issues are resolved
/debug "resolve all test failures"
# → tests passing → ready for /review
```

## Common Debugging Scenarios

### Test Failure Resolution
```bash
/debug "authentication tests failing after API changes"
```

Process:
1. Run failing tests in isolation
2. Analyze error messages and stack traces
3. Identify changes that broke the tests
4. Fix implementation or update test expectations
5. Verify all tests pass

### Performance Issue Resolution
```bash
/debug "user dashboard loading takes 10+ seconds"
```

Process:
1. Profile page loading and identify bottlenecks
2. Analyze database queries and API calls
3. Identify N+1 queries or inefficient operations
4. Implement caching, query optimization, or lazy loading
5. Measure and verify performance improvements

### Security Issue Resolution
```bash
/debug "user input not being sanitized properly"
```

Process:
1. Identify vulnerability type (XSS, SQL injection, etc.)
2. Trace user input flow through the application
3. Implement proper validation and sanitization
4. Add security tests to prevent regression
5. Audit similar code paths for related issues

### Logic Bug Resolution
```bash
/debug "shopping cart total calculation incorrect"
```

Process:
1. Create test case that reproduces the incorrect calculation
2. Trace through calculation logic step by step
3. Identify the specific calculation error
4. Fix the logic and verify with edge cases
5. Add comprehensive tests for calculation scenarios

## Best Practices

### 1. Reproduce First
```bash
# Good: Clear reproduction case
/debug "User login fails when email contains '+' character"

# Less effective: Vague description
/debug "login doesn't work sometimes"
```

### 2. Provide Context
```bash
# Good: Includes relevant context
/debug "After upgrading to Node.js 18, JWT validation throws 'algorithm not supported' error"

# Less helpful: Missing context
/debug "JWT error"
```

### 3. Use Appropriate Mode
```bash
# Simple issues: Quick mode
/debug --quick "typo causing undefined variable error"

# Complex issues: Deep mode
/debug --deep "race condition in concurrent user registration"

# Performance issues: Profile mode
/debug --profile "memory usage growing over time"
```

### 4. Follow Up with Testing
After debugging, ensure comprehensive testing:
- Add regression tests for the fixed bug
- Test edge cases and boundary conditions
- Verify no new issues were introduced
- Update integration tests if needed

## Troubleshooting Debug Command

### When Debug Gets Stuck
If debugging isn't making progress:
1. Try a different debugging mode (--quick vs --deep)
2. Provide more specific error details
3. Use multiple agents: `/debug --agents=qa,security "complex auth issue"`
4. Break down complex issues into smaller parts

### When Fixes Don't Work
If implemented fixes don't resolve the issue:
1. Verify the reproduction case is accurate
2. Check if multiple issues are interacting
3. Use deeper debugging mode for more thorough analysis
4. Consider architectural issues that might need the architect agent

### When Performance Issues Persist
If performance debugging doesn't improve speed:
1. Profile with different tools and approaches
2. Check if the bottleneck is in external dependencies
3. Consider scaling issues vs. algorithmic issues
4. Use the architect agent for structural performance problems

## Next Steps

- Learn about the [/impl Command](impl.md) for implementing fixes
- Explore [Agent Collaboration](../agents/overview.md)
- Understand [QA Agent](../agents/qa.md) for testing strategies
- Read about [Security Agent](../agents/security.md) for security debugging