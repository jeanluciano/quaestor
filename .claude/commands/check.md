---
allowed-tools: [Read, Bash, Glob, Grep, Edit, MultiEdit, Task]
description: "Comprehensive quality validation with intelligent error fixing"
performance-profile: "optimization"
complexity-threshold: 0.4
auto-activation: ["parallel-fixing", "error-categorization", "quality-gates"]
intelligence-features: ["auto-fix-suggestions", "parallel-agents", "validation-cycles"]
---

# /check - Intelligent Quality Validation

## Purpose
Verify code quality, run tests, fix all issues, and ensure production readiness with zero tolerance for errors.

## Usage
```
/check
/check --parallel --fix-all
/check --focus [linting|testing|security|performance]
```

## 🚨 Critical Rule: FIX ALL ISSUES
**This is a FIXING task, not a reporting task!**

## Auto-Intelligence

### Error Categorization & Auto-Fix
- **Linting**: Auto-format + rule fixes
- **Tests**: Parallel test fixing by domain
- **Types**: Add missing annotations
- **Security**: Apply security patterns

### Parallel Agent Strategy
```yaml
Agent Distribution:
  - lint_agent: Format + linting issues
  - test_agent: Test failures + coverage
  - type_agent: Type checking + annotations  
  - security_agent: Vulnerability fixes
```

## Execution: Validate → Fix → Verify

### Phase 1: Pre-Flight Check 🛑
**MANDATORY: Re-read @./CLAUDE.md & @.quaestor/MEMORY.md**
- Verify current work context
- Check for premature completion declarations

### Phase 2: Comprehensive Analysis 🔍
**Auto-detect project type → apply language standards:**

**Python:** `ruff check . && ruff format . && pytest`
**Rust:** `cargo clippy && cargo fmt && cargo test`
**JS/TS:** `eslint . && prettier . && npm test`
**Generic:** Manual validation for syntax + tests + docs

### Phase 3: Intelligent Issue Resolution ⚡

**Parallel Fixing Strategy:**
```yaml
When Issues Found:
  1. Categorize: linting|tests|types|security
  2. Spawn: dedicated agents per category  
  3. Execute: fixes in parallel
  4. Validate: re-run checks
  5. Repeat: until ALL ✅ GREEN
```

**Example Agent Coordination:**
```
"Found 15 linting issues, 3 test failures, 5 type errors.
Spawning 3 agents:
- Agent 1: Fix all linting issues  
- Agent 2: Resolve test failures
- Agent 3: Add missing type annotations
Working in parallel..."
```

### Phase 4: Quality Gates ✅

**Universal Standards:**
- ✅ Zero linting warnings
- ✅ All tests passing
- ✅ Type checking clean (if applicable)
- ✅ Build succeeds
- ✅ Security scan clean

**Quality Checklists:**
```yaml
Code Hygiene:
  - No commented-out code
  - No debug print statements  
  - No placeholder implementations
  - Dependencies actually used
  - Consistent formatting

Security Audit:
  - Input validation on external data
  - No hardcoded secrets
  - Proper error handling
  - Rate limiting where appropriate

Performance:
  - No obvious N+1 queries
  - No unnecessary allocations in hot paths
  - Connection pooling configured
  - Efficient algorithms used
```

## Validation Cycle (Every Check)
```
Execute → Validate → Fix (if ❌) → Re-validate → ✅ Complete
```

## Error Response Protocol

**No Excuses Allowed:**
- ❌ "It's just stylistic" → Fix it
- ❌ "Most issues are minor" → Fix ALL
- ❌ "Good enough" → Must be perfect
- ❌ "Linter is pedantic" → Linter is right

**Fix-First Mentality:**
```yaml
Issue Detection → Immediate Fix Attempt → Agent Spawn (if needed) → Validation
```

## Failure Recovery

**Auto-Escalation:**
1. **Simple fixes** → Direct resolution
2. **Complex issues** → Spawn specialized agents
3. **Multi-domain** → Parallel agent coordination
4. **Blocked** → Request user guidance (last resort)

## Language-Specific Validation

### Python Excellence
```yaml
Commands:
  - format: "ruff format ."
  - check: "ruff check . --fix"  
  - test: "pytest -v"
  - type: "mypy . --ignore-missing-imports"
Standards:
  - Comprehensive docstrings
  - Type hints everywhere
  - 80%+ test coverage
```

### Rust Excellence
```yaml
Commands:
  - clippy: "cargo clippy -- -D warnings"
  - format: "cargo fmt"
  - test: "cargo test"
  - check: "cargo check"
Standards:
  - Comprehensive documentation
  - Result<T,E> error handling
  - No unwrap() in production
```

### JavaScript/TypeScript Excellence
```yaml
Commands:
  - lint: "npx eslint . --fix"
  - format: "npx prettier --write ."
  - test: "npm test"
  - type: "npx tsc --noEmit"
Standards:
  - Proper async/await patterns
  - Error boundaries (React)
  - Comprehensive JSDoc
```

## Completion Criteria
**Code is ready ONLY when:**
- ✅ ALL linters pass with zero warnings
- ✅ ALL tests pass successfully  
- ✅ Type checking clean
- ✅ Build succeeds without errors
- ✅ Security validation complete
- ✅ Performance acceptable

## Final Protocol
**Keep working until EVERYTHING shows ✅ GREEN**

**Success Response:**
"All quality gates passed. Zero errors, zero warnings. Code ready for production."

---
*Intelligent validation with zero-tolerance error fixing for production readiness*