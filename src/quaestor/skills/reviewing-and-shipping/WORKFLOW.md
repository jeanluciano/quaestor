# Review and Ship - Complete 5-Phase Workflow

This file describes the detailed workflow for comprehensive code review, validation, auto-fixing, commit generation, and PR creation.

## Workflow Overview: Validate → Fix → Commit → Review → Ship

```yaml
Phase 1: Comprehensive Validation (🔍)
  - Multi-domain quality checks
  - Security vulnerability scanning
  - Test coverage analysis
  - Documentation completeness
  - Quality gate enforcement

Phase 2: Intelligent Auto-Fixing (⚡)
  - Simple issue direct fixes
  - Complex issue agent delegation
  - Parallel fix execution
  - Validation after fixes

Phase 3: Smart Commit Generation (📝)
  - Change analysis and grouping
  - Commit classification
  - Conventional commit format
  - Specification integration

Phase 4: Multi-Agent Review (🤖)
  - Code quality review
  - Security review
  - Test coverage review
  - Architecture review (if needed)
  - Consolidated review summary

Phase 5: PR Creation & Shipping (🚀)
  - PR title and description generation
  - Quality metrics inclusion
  - Review insights integration
  - Automation setup (labels, reviewers)
  - Specification archiving
```

---

## Phase 1: Comprehensive Validation 🔍

### Pre-Validation: Workflow Coordinator Check

**FIRST, use the workflow-coordinator agent to validate workflow state before review.**

```yaml
Workflow Coordinator Validates:
  - Implementation phase completed
  - All tasks in specification done
  - Tests passing before review
  - Ready for review/completion phase
  - No blocking issues remaining

If Not Ready:
  - Report incomplete work
  - Guide user to complete implementation
  - Do NOT proceed to validation
```

### Multi-Domain Quality Checks

**Parallel Validation Across All Domains:**

```yaml
Code Quality:
  Tools:
    Python: ruff check ., mypy .
    Rust: cargo clippy -- -D warnings
    JavaScript/TypeScript: eslint ., tsc --noEmit
    Go: golangci-lint run

  Checks:
    - Linting errors (must be zero)
    - Formatting issues (auto-fixable)
    - Code complexity (cyclomatic, cognitive)
    - Best practices compliance
    - Type safety (if applicable)

  Agent: refactorer (for complex issues)

Security:
  Tools:
    Python: bandit, safety check
    JavaScript: npm audit, snyk
    Rust: cargo audit
    Go: gosec

  Checks:
    - Known CVEs in dependencies
    - Hardcoded secrets or credentials
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Insecure authentication patterns
    - Weak encryption usage

  Agent: security (for vulnerabilities)

Testing:
  Tools:
    Python: pytest --cov
    Rust: cargo test
    JavaScript: npm test -- --coverage
    Go: go test -cover

  Checks:
    - All tests passing (no failures)
    - Test coverage ≥80% (threshold)
    - Edge cases covered
    - Mock usage appropriate
    - Performance within bounds

  Agent: qa (for test failures)

Documentation:
  Checks:
    - API documentation complete
    - Function/method docstrings present
    - README up to date
    - Examples working and clear
    - CHANGELOG updated (if applicable)
    - Architecture docs current

  Agent: implementer (for doc gaps)

Build & Deployment:
  Checks:
    - Build successful (no errors)
    - No broken imports/exports
    - Dependencies properly declared
    - Configuration valid
    - Environment variables documented
```

### Quality Gate Requirements

**Must Pass (Blocking):**

```yaml
Critical Gates:
  - ✅ Zero linting errors (warnings OK with justification)
  - ✅ All tests passing (no skipped tests without reason)
  - ✅ Security scan clean (no critical/high vulnerabilities)
  - ✅ Type checking valid (if applicable to language)
  - ✅ Build successful (compiles/runs without errors)
  - ✅ No hardcoded secrets or credentials
```

**Should Pass (Warnings):**

```yaml
Quality Gates:
  - ⚠️ Test coverage >80% (can proceed with plan)
  - ⚠️ Documentation complete (can fix in review)
  - ⚠️ No TODO comments in critical paths
  - ⚠️ Code complexity within bounds
  - ⚠️ Performance benchmarks met
```

### Validation Output

**Quality Report Generation:**

```yaml
Quality Validation Report:

  Code Quality:
    Status: ✅ PASS
    Details:
      - Linting: 0 errors, 2 warnings (acceptable)
      - Type checking: Clean
      - Complexity: Average 3.2 (target: <5)

  Security:
    Status: ✅ PASS
    Details:
      - Vulnerabilities: 0 critical, 0 high, 1 low
      - Secrets check: Clean
      - Auth patterns: Secure

  Testing:
    Status: ✅ PASS
    Details:
      - Tests: 42 passed, 0 failed
      - Coverage: 87% (target: 80%)
      - Edge cases: Well covered

  Documentation:
    Status: ⚠️ WARNING
    Details:
      - API docs: Complete
      - Code comments: 3 functions missing docstrings
      - README: Up to date

  Build:
    Status: ✅ PASS
    Details:
      - Build time: 12.3s
      - Bundle size: 1.2MB
      - No errors or warnings

Overall Status: ✅ READY FOR FIXES
  - 2 critical issues → auto-fix
  - 3 documentation gaps → agent fix
```

---

## Phase 2: Intelligent Auto-Fixing ⚡

### Fix Classification

**Categorize Issues by Complexity:**

```yaml
Simple Issues (Direct Fix):
  - Formatting errors (prettier, rustfmt, black)
  - Import sorting (isort, organize imports)
  - Trailing whitespace cleanup
  - Simple type annotations (obvious types)
  - Missing semicolons or commas
  - Unused imports removal

  Strategy: Auto-fix immediately with tools

Complex Issues (Agent Delegation):
  - Test failures → qa agent
  - Security vulnerabilities → security agent
  - Performance regressions → implementer agent
  - Documentation gaps → implementer agent
  - Architecture concerns → architect agent
  - Code quality issues → refactorer agent

  Strategy: Delegate to specialized agent
```

### Simple Fix Execution

**Direct Auto-Fixing:**

```bash
# Python
ruff check . --fix              # Auto-fix linting
ruff format .                   # Format code
isort .                        # Sort imports

# JavaScript/TypeScript
npx prettier --write .         # Format code
npx eslint . --fix             # Fix linting

# Rust
cargo fmt                      # Format code
cargo clippy --fix             # Fix clippy warnings

# Go
gofmt -w .                     # Format code
go mod tidy                    # Clean dependencies
```

**Verification After Simple Fixes:**

```yaml
After Auto-Fix:
  1. Re-run validation tools
  2. Verify no new issues introduced
  3. Run quick test suite
  4. Report fixes applied
```

### Complex Fix Orchestration

**Agent Delegation Strategy:**

```yaml
Test Failures:
  Use the qa agent to:
    - Analyze failing tests
    - Identify root causes
    - Fix test implementation or code
    - Add missing test cases
    - Verify all tests pass

Security Vulnerabilities:
  Use the security agent to:
    - Review vulnerability details
    - Assess severity and impact
    - Implement secure fixes
    - Add security tests
    - Verify vulnerability resolved

Performance Issues:
  Use the implementer agent to:
    - Profile performance bottlenecks
    - Implement optimizations
    - Add performance tests
    - Verify no regressions

Documentation Gaps:
  Use the implementer agent to:
    - Add missing docstrings
    - Update API documentation
    - Add code examples
    - Update README if needed

Code Quality Issues:
  Use the refactorer agent to:
    - Refactor complex functions
    - Reduce code duplication
    - Improve naming consistency
    - Simplify logic flow
```

### Parallel Fix Execution

**Coordinate Multiple Agents:**

```yaml
Independent Issues (Parallel):
  Spawn simultaneously:
    - qa agent: Fix test failures in auth module
    - implementer agent: Add docs to API module
    - refactorer agent: Simplify parser logic

  Wait for all completions

  Validate combined result:
    - No conflicts introduced
    - All fixes applied successfully
    - Quality gates now passing

Dependent Issues (Sequential):
  Step 1: Use security agent to fix vulnerability
  Step 2: Use qa agent to add security tests
  Step 3: Use implementer agent to document fix
```

### Fix Verification

**Post-Fix Validation:**

```yaml
Verification Steps:
  1. Re-run all quality checks:
     - Linting: Should be clean
     - Tests: Should all pass
     - Security: Should be clean
     - Type checking: Should be valid

  2. Verify no regressions:
     - Run full test suite
     - Check no new issues introduced
     - Validate fixes don't break other areas

  3. Document changes:
     - Track what was fixed
     - Note any manual interventions
     - Update fix summary
```

### Fix Report

**Generate Fix Summary:**

```yaml
Auto-Fix Summary:

Simple Fixes Applied:
  - Formatting: 47 files formatted
  - Imports: 12 files sorted
  - Linting: 8 auto-fixable issues resolved

Agent Fixes Applied:
  - qa agent: Fixed 3 test failures in auth module
  - implementer agent: Added docstrings to 5 functions
  - security agent: Updated password hashing algorithm

Remaining Issues: 0

Validation Status: ✅ All quality gates passing
```

---

## Phase 3: Smart Commit Generation 📝

### Change Analysis

**Analyze Uncommitted Changes:**

```bash
# Get all changes
git status --short
git diff --stat

# Analyze by type
git diff --name-only | sort
```

**Group Related Changes:**

```yaml
Grouping Strategy:
  By Module:
    - auth/ changes → one commit
    - api/ changes → one commit
    - utils/ changes → one commit

  By Feature:
    - Feature implementation → one commit
    - Tests for feature → include in same commit
    - Documentation → separate commit if extensive

  By Type:
    - Refactoring → separate commit
    - Bug fixes → separate commit
    - Feature additions → one per feature
```

### Commit Classification

**Conventional Commit Types:**

```yaml
feat: New feature for the user
  Examples:
    - "feat(auth): implement JWT refresh tokens"
    - "feat(api): add user profile endpoint"
    - "feat(payments): integrate Stripe checkout"

fix: Bug fix for the user
  Examples:
    - "fix(api): handle null response in user endpoint"
    - "fix(auth): prevent token expiry race condition"
    - "fix(validation): correct email regex pattern"

docs: Documentation changes
  Examples:
    - "docs(api): update OpenAPI specifications"
    - "docs(readme): add installation instructions"
    - "docs(auth): document OAuth flow"

refactor: Code change that neither fixes nor adds feature
  Examples:
    - "refactor(parser): simplify token extraction"
    - "refactor(utils): extract common validation logic"
    - "refactor(auth): improve session management structure"

test: Adding or updating tests
  Examples:
    - "test(auth): add coverage for edge cases"
    - "test(api): add integration tests for user endpoints"
    - "test(utils): add unit tests for validators"

perf: Performance improvements
  Examples:
    - "perf(query): optimize database query for large datasets"
    - "perf(render): add memoization to reduce re-renders"
    - "perf(cache): implement Redis caching layer"

style: Code style changes (formatting, naming)
  Examples:
    - "style(auth): apply consistent naming conventions"
    - "style: format code with prettier"

chore: Maintenance tasks (dependencies, config)
  Examples:
    - "chore(deps): update dependencies to latest versions"
    - "chore(config): update linting rules"
```

### Scope Extraction

**Determine Commit Scope:**

```yaml
From File Paths:
  src/auth/jwt.py → scope: auth
  src/api/users.py → scope: api
  src/utils/validation.py → scope: utils
  tests/test_auth.py → scope: auth (test relates to auth)

From Specification:
  Spec: "spec-feature-auth-001"
  → scope: auth

Multiple Scopes:
  Changes in auth/ and api/
  → Option 1: Two commits (auth, api)
  → Option 2: One commit with scope: auth,api
  → Prefer: Separate commits for clarity
```

### Commit Message Generation

**Template Format:**

```yaml
Format: type(scope): description

[optional body]

[optional footer]
```

**Generation Algorithm:**

```yaml
Step 1: Classify Changes
  - Analyze file diffs
  - Determine primary type (feat, fix, docs, etc.)
  - Extract scope from file paths

Step 2: Generate Description
  - Summarize what changed (imperative mood)
  - Keep under 72 characters
  - Focus on "what" not "how"

  Examples:
    ✅ "implement JWT refresh tokens"
    ✅ "handle null response in user endpoint"
    ❌ "added some JWT code"
    ❌ "fixed a bug"

Step 3: Add Body (if needed)
  - Explain "why" the change was made
  - Describe implications or context
  - Reference specification or issue

  Example:
    "feat(auth): implement JWT refresh tokens

    Adds refresh token rotation for better security.
    Tokens expire after 15 minutes, refresh after 7 days.

    Implements spec-feature-auth-001 phase 2."

Step 4: Add Footer (if applicable)
  - Breaking changes: BREAKING CHANGE: description
  - Issue references: Closes #123
  - Specification: Spec: spec-feature-auth-001
```

### Atomic Commit Strategy

**One Logical Change Per Commit:**

```yaml
Good Atomic Commits:

Commit 1: feat(auth): implement JWT generation
  - src/auth/jwt.py (JWT generation logic)
  - tests/test_jwt.py (JWT generation tests)

Commit 2: feat(auth): implement JWT validation
  - src/auth/jwt.py (JWT validation logic)
  - tests/test_jwt.py (JWT validation tests)

Commit 3: docs(auth): document JWT implementation
  - docs/auth.md (JWT documentation)
  - README.md (update authentication section)

Bad Non-Atomic Commits:

Commit 1: "lots of changes"
  - src/auth/jwt.py (generation AND validation)
  - src/api/users.py (unrelated API changes)
  - docs/auth.md (documentation)
  - tests/test_jwt.py (tests)
  - README.md (readme update)

  Problem: Too many unrelated changes in one commit
```

### Specification Integration

**Link Commits to Specifications:**

```yaml
Commit Message with Spec Reference:
  feat(auth): implement JWT refresh tokens

  Implements spec-feature-auth-001 phase 2: Token Management

  - Add refresh token generation
  - Implement token rotation
  - Add token expiry validation

  Spec: spec-feature-auth-001

Track Progress:
  - Update specification file
  - Mark phase as completed
  - Add commit hash reference
  - Update completion evidence
```

### Commit Generation Output

**Generated Commits Summary:**

```yaml
Generated 3 Commits:

1. feat(auth): implement JWT refresh tokens
   Files: src/auth/jwt.py, tests/test_jwt.py
   Spec: spec-feature-auth-001 phase 2

2. test(auth): add security tests for token rotation
   Files: tests/security/test_token_rotation.py
   Spec: spec-feature-auth-001 phase 3

3. docs(auth): document JWT implementation
   Files: docs/auth.md, README.md
   Spec: spec-feature-auth-001 phase 4

All commits follow conventional commit format.
All commits are atomic and focused.
Ready for push and PR creation.
```

**See @COMMITS.md for detailed commit generation strategies**

---

## Phase 4: Multi-Agent Review 🤖

### Review Coordination

**Parallel Multi-Agent Review:**

```yaml
Review Strategy:
  Spawn 4 agents in parallel:
    - refactorer: Code quality review
    - security: Security review
    - qa: Test coverage review
    - architect: Architecture review (if needed)

  Each agent focuses on their domain

  Wait for all reviews to complete

  Consolidate into unified review summary
```

### Code Quality Review (refactorer)

**Focus Areas:**

```yaml
Readability:
  - Clear variable/function names
  - Appropriate code comments
  - Logical code organization
  - Consistent formatting

Design Principles:
  - DRY (Don't Repeat Yourself)
  - SOLID principles applied
  - Appropriate abstractions
  - Design patterns usage

Code Smells:
  - Long functions (>50 lines)
  - Deep nesting (>3 levels)
  - Large classes (>500 lines)
  - Duplicate code blocks
  - Magic numbers/strings

Review Output:
  ✅ Strengths:
    - Clean separation of concerns in auth module
    - Good use of dependency injection
    - Consistent error handling patterns

  ⚠️ Suggestions:
    - Consider extracting UserValidator to separate class
    - Could simplify nested conditionals in authenticate()
    - Opportunity to cache user lookups

  🚨 Required Fixes:
    - None
```

### Security Review (security)

**Focus Areas:**

```yaml
Authentication:
  - Secure password storage (hashing)
  - Token validation robust
  - Session management secure
  - MFA implementation correct

Authorization:
  - Permission checks in place
  - Role-based access control correct
  - Resource ownership validated
  - No privilege escalation paths

Input Validation:
  - All inputs sanitized
  - SQL injection prevented
  - XSS vulnerabilities blocked
  - CSRF protection in place

Data Protection:
  - Sensitive data encrypted
  - Secure communication (HTTPS)
  - No secrets in code/logs
  - PII handling compliant

Review Output:
  ✅ Strengths:
    - Password hashing uses bcrypt with appropriate cost
    - JWT validation includes expiry and signature checks
    - Input sanitization comprehensive

  ⚠️ Suggestions:
    - Consider adding rate limiting to login endpoint
    - Could add additional logging for failed auth attempts

  🚨 Required Fixes:
    - None - all critical security measures in place
```

### Test Coverage Review (qa)

**Focus Areas:**

```yaml
Coverage Analysis:
  - Overall coverage ≥80%
  - Critical paths 100% covered
  - Edge cases tested
  - Error handling tested

Test Quality:
  - Assertions meaningful
  - Test names descriptive
  - Mocks used appropriately
  - Tests isolated and independent

Test Types:
  - Unit tests for logic
  - Integration tests for flows
  - E2E tests for critical paths
  - Performance tests if applicable

Review Output:
  ✅ Strengths:
    - Coverage at 87% (target: 80%)
    - Critical auth paths fully tested
    - Good edge case coverage
    - Test names clear and descriptive

  ⚠️ Suggestions:
    - Could add tests for token expiry edge cases
    - Consider adding load tests for auth endpoints

  🚨 Required Fixes:
    - None
```

### Architecture Review (architect - if needed)

**When to Include Architect Review:**

```yaml
Trigger Architect Review When:
  - Major architectural changes
  - New system components added
  - Cross-module dependencies changed
  - Performance-critical features
  - Database schema modifications
```

**Focus Areas:**

```yaml
Component Boundaries:
  - Separation of concerns clear
  - Dependencies point in correct direction
  - No circular dependencies
  - Proper abstraction layers

Scalability:
  - Design supports horizontal scaling
  - Database queries optimized
  - Caching strategy appropriate
  - No obvious bottlenecks

Maintainability:
  - Code organized logically
  - Easy to extend and modify
  - Technical debt minimal
  - Documentation adequate

Review Output:
  ✅ Strengths:
    - Clean layered architecture maintained
    - Auth module well isolated
    - Easy to swap JWT implementation if needed

  ⚠️ Suggestions:
    - Consider event-driven approach for audit logging
    - Could abstract session storage for flexibility

  🚨 Required Fixes:
    - None
```

### Consolidated Review Summary

**Unified Review Report:**

```yaml
📊 Multi-Agent Review Summary

Code Quality (refactorer): ✅ EXCELLENT
  Strengths:
    • Clean architecture and separation of concerns
    • Consistent code style and naming
    • Good use of design patterns

  Suggestions:
    • Consider extracting UserValidator class
    • Simplify nested conditionals in authenticate()

Security (security): ✅ SECURE
  Strengths:
    • Robust authentication implementation
    • Comprehensive input validation
    • Secure password hashing with bcrypt

  Suggestions:
    • Add rate limiting to login endpoint
    • Add logging for failed auth attempts

Testing (qa): ✅ WELL-TESTED
  Strengths:
    • 87% coverage (target: 80%)
    • Critical paths fully tested
    • Good edge case coverage

  Suggestions:
    • Add tests for token expiry edge cases
    • Consider load tests for auth endpoints

Architecture (architect): ✅ SOLID
  Strengths:
    • Clean layered architecture
    • Well-isolated auth module
    • Easy to extend and modify

  Suggestions:
    • Consider event-driven audit logging
    • Abstract session storage for flexibility

Overall Assessment: ✅ READY TO SHIP
  - All critical requirements met
  - No blocking issues
  - Quality standards exceeded
  - Ready for team review
```

**See @AGENTS.md for agent coordination details**

---

## Phase 5: PR Creation & Shipping 🚀

### PR Title Generation

**Title Strategy:**

```yaml
From Specification:
  Spec: "spec-feature-auth-001: JWT Authentication System"
  → Title: "feat: JWT Authentication System"

From Primary Commit:
  Commit: "feat(auth): implement JWT refresh tokens"
  → Title: "feat(auth): Implement JWT refresh tokens"

From Changes Summary:
  Multiple features: "feat: User Authentication Enhancements"
  Single fix: "fix(api): Handle null user responses"

Format:
  - Start with type: feat, fix, docs, etc.
  - Include scope in parentheses (optional)
  - Capitalize first word of description
  - No period at end
  - Keep under 72 characters
```

### PR Description Generation

**Template Structure:**

```markdown
## Summary
[What was done and why - 2-3 sentences from specification]

## Changes
[Organized list of changes by type with commit links]

## Quality Report
[Metrics from Phase 1 validation]

## Review Insights
[Summary from Phase 4 multi-agent review]

## Checklist
[Standard PR checklist items]
```

**Generated Example:**

```markdown
## Summary
Implements JWT-based authentication with refresh token rotation for improved security and scalability. Replaces session-based authentication with stateless JWT tokens while maintaining backwards compatibility during migration.

Implements specification: spec-feature-auth-001

## Changes

### Features
- feat(auth): implement JWT generation and validation ([abc123])
- feat(auth): add refresh token rotation ([def456])

### Tests
- test(auth): add comprehensive JWT test suite ([ghi789])
- test(security): add token rotation security tests ([jkl012])

### Documentation
- docs(auth): document JWT implementation and API ([mno345])

## Quality Report

**Tests:** ✅ All passing
- 42 tests passed, 0 failed
- 87% coverage (+12% from baseline)

**Security:** ✅ No vulnerabilities
- 0 critical, 0 high, 0 medium
- bcrypt password hashing implemented
- Token validation comprehensive

**Code Quality:** ✅ Clean
- 0 linting errors
- Type checking: Valid
- Complexity: Average 3.2 (target: <5)

**Performance:** ✅ No regressions
- Auth endpoint: 45ms (baseline: 42ms)
- Build time: 12.3s (baseline: 11.8s)

## Review Insights

### Code Quality (refactorer)
✅ **Strengths:**
- Clean separation of concerns in auth module
- Consistent error handling patterns
- Good use of dependency injection

⚠️ **Suggestions:**
- Consider extracting UserValidator class
- Could cache user lookups for performance

### Security (security)
✅ **Strengths:**
- Robust JWT validation with expiry checks
- Secure password hashing (bcrypt cost: 12)
- Comprehensive input sanitization

⚠️ **Suggestions:**
- Add rate limiting to login endpoint
- Add logging for failed auth attempts

### Testing (qa)
✅ **Strengths:**
- Excellent coverage at 87%
- Critical auth paths fully tested
- Good edge case coverage

⚠️ **Suggestions:**
- Add tests for token expiry edge cases

### Overall Assessment
✅ **Ready to ship** - All quality gates passed, no blocking issues.

## Checklist
- [x] Tests added/updated
- [x] All tests passing
- [x] Documentation updated
- [x] Security reviewed
- [x] No breaking changes
- [x] Specification completed
```

### Automation Setup

**GitHub PR Automation:**

```bash
# Create PR with gh CLI
gh pr create \
  --title "feat: JWT Authentication System" \
  --body "$(cat pr_description.md)" \
  --label "enhancement,security" \
  --reviewer "@security,@backend-team" \
  --assignee "@me" \
  --milestone "v1.2.0"
```

**Auto-Detection:**

```yaml
Labels:
  From changes:
    - src/auth/ changes → "security", "backend"
    - docs/ changes → "documentation"
    - tests/ changes → "testing"
  From type:
    - feat commits → "enhancement"
    - fix commits → "bug"
    - refactor commits → "refactoring"

Reviewers:
  From CODEOWNERS:
    - src/auth/ → @security-team
    - src/api/ → @backend-team
  From git history:
    - Recent contributors to changed files

Projects:
  From specification:
    - Spec linked to project → Add PR to project

Milestone:
  From specification:
    - Spec target version → Add PR to milestone
```

### Specification Archiving

**Move Completed Specification:**

```yaml
Archive Process:
  1. Verify Completion:
     - All spec tasks completed
     - All acceptance criteria met
     - Quality gates passed
     - PR created and linked

  2. Move Specification:
     From: .quaestor/specs/active/spec-feature-auth-001.md
     To: .quaestor/specs/completed/spec-feature-auth-001.md

  3. Update Metadata:
     - status: "in_progress" → "completed"
     - completion_date: "2025-10-19"
     - pr_url: "https://github.com/user/repo/pull/123"

  4. Generate Archive Summary:
     - What was delivered
     - Key decisions made
     - Lessons learned
     - Performance metrics
```

**Archive Summary Template:**

```yaml
Specification Archived: spec-feature-auth-001

Completion Summary:
  - Delivered: JWT authentication with refresh tokens
  - Quality: 87% test coverage, 0 security vulnerabilities
  - Timeline: Completed in 3 days (estimated: 5 days)
  - PR: #123 (created, awaiting review)

Key Decisions:
  - Chose JWT over sessions for scalability
  - Implemented refresh token rotation for security
  - Used bcrypt with cost factor 12 for password hashing

Lessons Learned:
  - Token expiry edge cases require careful testing
  - Rate limiting should be included in initial design

Performance Metrics:
  - Auth endpoint: 45ms average response time
  - 87% test coverage achieved
  - 0 security vulnerabilities found
```

### Shipping Checklist

**Final Pre-Ship Validation:**

```yaml
Before Creating PR:
  - ✅ All commits pushed to branch
  - ✅ Branch up to date with main
  - ✅ All quality gates passed
  - ✅ Multi-agent review complete
  - ✅ Specification updated/archived
  - ✅ PR description generated

PR Created:
  - ✅ Title follows conventions
  - ✅ Description comprehensive
  - ✅ Labels auto-applied
  - ✅ Reviewers assigned
  - ✅ CI/CD triggered

Ready for Team Review:
  - ✅ All automated checks passing
  - ✅ PR linked to specification
  - ✅ Quality report included
  - ✅ Review insights shared
```

**See @PR.md for complete PR creation details**

---

## Error Handling & Recovery

### Validation Failures

**Quality Gate Failures:**

```yaml
Linting Errors:
  1. Attempt auto-fix: ruff check --fix, eslint --fix
  2. If persist: Use refactorer agent to fix
  3. Re-validate: Ensure clean
  4. If still failing: Report to user for manual fix

Test Failures:
  1. Analyze: Identify failing tests
  2. Use qa agent: Fix test or implementation
  3. Re-run: Verify all pass
  4. If persist: Detailed report to user

Security Vulnerabilities:
  1. Use security agent: Review and fix
  2. Update dependencies if needed
  3. Re-scan: Verify clean
  4. If critical unfixable: Block PR creation, report to user
```

### Fix Failures

**Agent Fix Issues:**

```yaml
Agent Unable to Fix:
  1. Document: What agent attempted
  2. Report: Detailed error information
  3. Guide: Suggest manual intervention
  4. Offer: Alternative approaches

Conflicting Fixes:
  1. Detect: Conflicts between agent fixes
  2. Analyze: Determine priority
  3. Resolve: Apply fixes sequentially
  4. Validate: Ensure no regressions
```

### Commit Generation Issues

**Commit Creation Problems:**

```yaml
No Changes to Commit:
  - Report: "No uncommitted changes found"
  - Guide: User to make changes first

Commit Conflicts:
  - Detect: Merge conflicts with main
  - Report: Conflict details
  - Guide: User to resolve manually

Invalid Commit Message:
  - Validate: Conventional commit format
  - Fix: Regenerate with correct format
  - Apply: Create commit with valid message
```

### PR Creation Failures

**GitHub PR Issues:**

```yaml
Branch Already Has PR:
  - Detect: Existing PR for branch
  - Report: Link to existing PR
  - Offer: Update existing PR instead

Authentication Failure:
  - Check: gh auth status
  - Guide: User to authenticate
  - Retry: After authentication

Network/API Error:
  - Retry: Up to 3 attempts
  - Report: If persistent failure
  - Save: PR description for manual creation
```

---

## Mode-Specific Workflows

### Full Review Mode (Default)

**All 5 Phases:**

```yaml
Full Review Workflow:
  Phase 1: Comprehensive Validation ✅
  Phase 2: Intelligent Auto-Fixing ✅
  Phase 3: Smart Commit Generation ✅
  Phase 4: Multi-Agent Review ✅
  Phase 5: PR Creation & Shipping ✅

Time: ~15-30 minutes (depends on codebase size)
Use When: Ready to ship completed feature
```

### Quick Review Mode

**Streamlined Process:**

```yaml
Quick Review Workflow:
  Phase 1: Basic Validation (tests + linting only)
  Phase 2: Auto-Fix Only (no agent delegation)
  Phase 3: Simple Commit (one commit for all changes)
  Phase 4: Single Agent Review (refactorer only)
  Phase 5: Basic PR (simple description)

Time: ~5 minutes
Use When: Small changes, hotfixes, documentation updates
```

### Commit-Only Mode

**Skip PR Creation:**

```yaml
Commit-Only Workflow:
  Phase 1: Basic Validation ✅
  Phase 2: Simple Auto-Fixing ✅
  Phase 3: Smart Commit Generation ✅
  Phase 4: Skip
  Phase 5: Skip

Time: ~5-10 minutes
Use When: Want commits but not ready for PR
```

### Validate-Only Mode

**Focus on Quality:**

```yaml
Validate-Only Workflow:
  Phase 1: Comprehensive Validation ✅
  Phase 2: Intelligent Auto-Fixing ✅
  Phase 3: Skip
  Phase 4: Skip
  Phase 5: Skip

Time: ~5-10 minutes
Use When: Want to check quality before committing
```

### PR-Only Mode

**From Existing Commits:**

```yaml
PR-Only Workflow:
  Phase 1: Skip (assume validated)
  Phase 2: Skip (assume fixed)
  Phase 3: Skip (commits exist)
  Phase 4: Multi-Agent Review ✅
  Phase 5: PR Creation & Shipping ✅

Time: ~10-15 minutes
Use When: Commits already created, ready for PR
```

### Deep Analysis Mode

**Comprehensive Insights:**

```yaml
Analysis Workflow:
  Phase 1: Comprehensive Validation ✅
  Phase 2: Skip (analysis only)
  Phase 3: Skip
  Phase 4: Extended Multi-Agent Review ✅
    - All agents review
    - Detailed metrics collection
    - Architecture health assessment
    - Technical debt analysis
  Phase 5: Skip

Time: ~20-30 minutes
Use When: Need detailed code quality insights
```

**See @MODES.md for complete mode details**

---

*Comprehensive 5-phase review workflow with multi-agent orchestration, auto-fixing, and intelligent shipping*
