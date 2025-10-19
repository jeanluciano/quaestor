---
allowed-tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, TodoWrite, Task]
description: "Interactive debugging and troubleshooting with specialized agent assistance"
agent-strategy:
  test_failures: qa
  security_issues: security
  performance: implementer
  architecture: architect
  general: [qa, implementer]
---

# /debug - Intelligent Troubleshooting & Fixing

ARGUMENTS: $ERROR_OR_ISSUE

## Purpose
Investigate issues, fix bugs, optimize performance, and troubleshoot problems with specialized debugging agents. Focuses on root cause analysis and systematic problem resolution.

## Usage
```
/debug "test failures in auth module"
/debug "performance bottleneck in API"
/debug --error "TypeError: undefined is not a function"
/debug --profile "slow database queries"
```

## Auto-Intelligence

### Agent-Driven Debugging
```yaml
Error Classification:
  - Test failures → qa agent
  - Security vulnerabilities → security agent
  - Performance issues → implementer agent
  - Design problems → architect agent
  - Unknown/mixed → multiple agents

Debugging Strategy:
  simple_fix: single agent
  complex_issue: agent team
  systematic_failure: sequential agents
  performance: profiling + optimization
```

### Root Cause Analysis
- **Error parsing**: Stack trace analysis, error pattern recognition
- **Impact assessment**: Affected files, downstream effects
- **Fix strategies**: Quick fix vs. proper solution
- **Verification**: Automated test creation/running

## Workflow: Reproduce → Analyze → Fix → Verify

### Phase 1: Issue Understanding 🔍
**Problem Classification:**
```yaml
Issue Types:
  - Runtime errors: exceptions, crashes
  - Test failures: unit, integration, e2e
  - Performance: slow queries, memory leaks
  - Logic bugs: incorrect behavior
  - Security: vulnerabilities, exposures
```

**Reproduction Strategy:**
```yaml
Steps:
  1. Capture: error message, stack trace, logs
  2. Isolate: minimal reproduction case
  3. Document: steps to reproduce
  4. Environment: dependencies, versions
```

### Phase 2: Multi-Agent Analysis 🧪
**Agent Specialization:**
```yaml
QA Agent:
  - Test failure analysis
  - Test fix implementation
  - Coverage improvement
  - Edge case identification

Security Agent:
  - Vulnerability assessment
  - Security fix implementation
  - Input validation
  - Auth flow debugging

Implementer Agent:
  - Performance profiling
  - Algorithm optimization
  - Memory leak detection
  - Code fix implementation

Architect Agent:
  - Design flaw identification
  - Structural improvements
  - Dependency issues
  - Pattern violations
```

**Debugging Techniques:**
```yaml
Interactive Debugging:
  - Strategic logging: Add debug statements
  - Binary search: Isolate problem area
  - State inspection: Variable values
  - Flow tracing: Execution path

Performance Profiling:
  - Time measurement: Identify slow operations
  - Memory profiling: Leak detection
  - Query analysis: Database optimization
  - Algorithm complexity: Big-O analysis
```

### Phase 3: Systematic Fixing 🔧
**Fix Implementation:**
```yaml
Fix Priority:
  1. Stop the bleeding: Immediate mitigation
  2. Root cause: Address underlying issue
  3. Prevention: Add guards/validation
  4. Testing: Ensure fix works
  5. Documentation: Update as needed
```

**Fix Patterns:**
```yaml
Common Fixes:
  - Null checks: Add proper validation
  - Type safety: Fix type mismatches
  - Race conditions: Add synchronization
  - Memory leaks: Proper cleanup
  - SQL injection: Parameterized queries
  - XSS: Input sanitization
```

### Phase 4: Verification & Prevention ✅
**Testing Strategy:**
```yaml
Test Creation:
  - Reproduction test: Captures the bug
  - Fix verification: Ensures solution works
  - Regression tests: Prevents recurrence
  - Edge cases: Related scenarios

Quality Gates:
  - All tests passing
  - No new issues introduced
  - Performance acceptable
  - Security validated
```

## Debug Session Example
```
🔍 Debug Session: Authentication Test Failures

🚨 Issue Identified:
- Type: Test failures (3 tests)
- Module: auth/test_login.py
- Error: "JWT token validation failing"

🤖 Spawning QA agent for test analysis...

📊 Root Cause Analysis:
- Token expiry time changed in config
- Tests using hardcoded timestamps
- Mismatch causes validation failure

🔧 Fix Implementation:
1. Update test fixtures to use dynamic timestamps
2. Add test helper for token generation
3. Update affected test cases

✅ Verification:
- All auth tests now passing
- Added 2 new edge case tests
- No regression in other modules

💡 Prevention:
- Created test utility for token handling
- Added comment warning about timestamps
- Updated test documentation
```

## Debugging Modes

### Quick Debug (~5 min)
- Single issue focus
- Direct fix attempt
- Basic verification
- Single agent

### Standard Debug (~10 min)
- Root cause analysis
- Proper fix implementation
- Test creation
- 1-2 agents

### Deep Debug (~20 min)
- Systematic investigation
- Multiple related fixes
- Comprehensive testing
- Multi-agent team

### Performance Debug (~30 min)
- Full profiling
- Bottleneck identification
- Optimization implementation
- Before/after metrics

## Advanced Features

### Interactive Debugging
```yaml
Commands:
  - "Add logging here"
  - "Show variable state"
  - "Run this test only"
  - "Profile this function"
```

### Fix Suggestions
```yaml
AI-Powered Recommendations:
  - Similar issue patterns
  - Common fix approaches
  - Best practices
  - Library solutions
```

### Debugging Artifacts
```yaml
Generated:
  - Debug logs
  - Performance profiles
  - Test cases
  - Fix documentation
```

## Integration with Workflow

### From Other Commands
```yaml
Task → Debug:
  - "Implementation hit an error"
  - Context passed to debug agent

Research → Debug:
  - "Found problematic patterns"
  - Focus debugging on issues

Review → Debug:
  - "Tests failing in PR"
  - Fix before merge
```

### To Other Commands
```yaml
Debug → Task:
  - "Bug fixed, continue implementation"
  - Clean slate for progress

Debug → Review:
  - "All issues resolved"
  - Ready for final review
```

## Success Criteria
- ✅ Issue reproduced and understood
- ✅ Root cause identified
- ✅ Fix implemented and verified
- ✅ Tests added/updated
- ✅ No regressions introduced
- ✅ Performance acceptable
- ✅ Documentation updated

## Common Debugging Patterns

### Test Failure Debugging
```yaml
Process:
  1. Run failing test in isolation
  2. Add debug output
  3. Identify assertion failure
  4. Fix implementation or test
  5. Verify all tests pass
```

### Performance Debugging
```yaml
Process:
  1. Profile code execution
  2. Identify bottlenecks
  3. Analyze algorithm complexity
  4. Implement optimization
  5. Measure improvement
```

### Security Debugging
```yaml
Process:
  1. Identify vulnerability type
  2. Trace attack vector
  3. Implement protection
  4. Add security tests
  5. Audit similar code
```

---
*Interactive debugging with specialized agents for systematic problem resolution*