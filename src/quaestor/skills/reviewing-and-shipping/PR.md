# PR Creation and Shipping

This file describes strategies for creating comprehensive pull requests with rich context, automation, and team collaboration features.

## PR Creation Overview

```yaml
PR Creation Process:
  1. Title Generation: Clear, concise, conventional format
  2. Description Assembly: Comprehensive PR description
  3. Quality Metrics: Include validation results
  4. Review Insights: Add multi-agent review summary
  5. Automation Setup: Labels, reviewers, projects
  6. Specification Integration: Link and archive specs
  7. PR Creation: Use GitHub CLI for creation

Goals:
  - Clear: Easy to understand what changed and why
  - Comprehensive: All relevant context included
  - Reviewable: Makes reviewer's job easier
  - Traceable: Links to specifications and issues
  - Automated: Reduces manual setup work
```

---

## PR Title Generation

### Title Strategy

**From Specification:**

```yaml
Specification-Based Title:
  Spec: "spec-feature-auth-001: JWT Authentication System"
  Title: "feat: JWT Authentication System"

  Spec: "spec-fix-api-null-handling: Fix Null Response Handling"
  Title: "fix(api): Handle null response in user endpoint"

  Spec: "spec-refactor-auth-module: Refactor Authentication Module"
  Title: "refactor(auth): Simplify authentication logic"

Rules:
  - Extract type from spec or changes
  - Extract scope if clear
  - Use spec title or summary
  - Keep under 72 characters
```

**From Primary Commit:**

```yaml
Commit-Based Title:
  Primary Commit: "feat(auth): implement JWT refresh tokens"
  Title: "feat(auth): Implement JWT refresh tokens"

  Primary Commit: "fix(api): handle timeout in user fetch"
  Title: "fix(api): Handle timeout in user fetch"

Rules:
  - Use primary/first commit message
  - Capitalize first word of description
  - Keep type and scope from commit
```

**From Changes Summary:**

```yaml
Change-Based Title:
  Multiple features in auth: "feat(auth): Authentication enhancements"
  Single fix in API: "fix(api): Correct user endpoint errors"
  Documentation updates: "docs: Update authentication documentation"
  Refactoring work: "refactor: Code quality improvements"

Rules:
  - Summarize primary change type
  - Use most relevant scope
  - Keep description general but clear
```

### Title Format

**Standard Format:**

```yaml
Format: type(scope): Description

Components:
  type: feat, fix, docs, refactor, test, perf, etc.
  scope: Optional, module or area affected
  description: Clear, concise summary (50-72 chars)

Examples:
  ✅ "feat: JWT Authentication System"
  ✅ "feat(auth): Add JWT refresh token support"
  ✅ "fix(api): Handle null user responses"
  ✅ "docs(api): Update authentication documentation"
  ✅ "refactor(auth): Simplify token validation logic"

  ❌ "Authentication stuff" (no type)
  ❌ "feat: implemented the complete JWT authentication system with refresh tokens and session management" (too long)
  ❌ "Fixed bugs." (vague)
  ❌ "FEAT: JWT AUTH" (wrong case)
```

---

## PR Description Generation

### Description Template

**Comprehensive Template:**

```markdown
## Summary
[What was done and why - 2-3 sentences from specification or changes]

[Specification reference if applicable]

## Changes

### [Type Category 1]
- [Change 1 with commit link]
- [Change 2 with commit link]

### [Type Category 2]
- [Change 1 with commit link]
- [Change 2 with commit link]

## Quality Report

**Tests:** [Status]
- [Test metrics]

**Security:** [Status]
- [Security metrics]

**Code Quality:** [Status]
- [Quality metrics]

**Performance:** [Status]
- [Performance metrics]

## Review Insights

### [Agent 1 Name]
✅ **Strengths:**
- [Strength 1]
- [Strength 2]

⚠️ **Suggestions:**
- [Suggestion 1]

### [Agent 2 Name]
[Similar format]

### Overall Assessment
[Overall review recommendation]

## Checklist
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security reviewed
- [ ] No breaking changes
- [ ] Specification completed
```

### Section Details

**Summary Section:**

```yaml
Summary Guidelines:
  - 2-3 sentences explaining what and why
  - Link to specification if exists
  - Mention key implementation details
  - Highlight user impact if applicable

Good Summary:
  "Implements JWT-based authentication with refresh token rotation for
  improved security and scalability. Replaces session-based authentication
  with stateless JWT tokens while maintaining backwards compatibility.

  Implements specification: spec-feature-auth-001"

Bad Summary:
  "Added JWT stuff to the auth module."
```

**Changes Section:**

```yaml
Changes Organization:
  Group by Type:
    - Features
    - Bug Fixes
    - Tests
    - Documentation
    - Refactoring
    - Performance

  Include:
    - Commit hash (short)
    - Commit message
    - Link to commit

Example:
  ### Features
  - feat(auth): implement JWT generation ([abc123])
  - feat(auth): add refresh token rotation ([def456])

  ### Tests
  - test(auth): add comprehensive JWT test suite ([ghi789])
  - test(security): add token rotation tests ([jkl012])

  ### Documentation
  - docs(auth): document JWT implementation ([mno345])
```

**Quality Report Section:**

```yaml
Quality Metrics to Include:

Tests:
  - Total test count
  - Pass/fail status
  - Coverage percentage
  - Coverage change from baseline

Security:
  - Vulnerability count by severity
  - Security measures implemented
  - Security scan results

Code Quality:
  - Linting status
  - Type checking status
  - Complexity metrics
  - Code smell count

Performance:
  - Key metrics (response time, etc.)
  - Change from baseline
  - Benchmark results if applicable

Example:
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
```

**Review Insights Section:**

```yaml
Agent Review Summary:
  For each agent that reviewed:
    - Agent name/role
    - Top 3 strengths identified
    - Top 2-3 suggestions
    - Required fixes (if any)

  Overall Assessment:
    - Ready to ship / Needs work / Blocked
    - Critical issues count
    - Nice-to-have suggestions count

Example:
  ### Code Quality (refactorer)
  ✅ **Strengths:**
  - Clean separation of concerns
  - Consistent error handling
  - Good use of dependency injection

  ⚠️ **Suggestions:**
  - Consider extracting UserValidator class
  - Could cache user lookups

  ### Security (security)
  ✅ **Strengths:**
  - Robust JWT validation
  - Secure password hashing
  - Comprehensive input sanitization

  ⚠️ **Suggestions:**
  - Add rate limiting to login endpoint

  ### Overall Assessment
  ✅ **Ready to ship** - All quality gates passed, no blocking issues.
  8 nice-to-have suggestions for future iteration.
```

**Checklist Section:**

```yaml
Standard Checklist:
  - [ ] Tests added/updated
  - [ ] All tests passing
  - [ ] Documentation updated
  - [ ] Security reviewed
  - [ ] No breaking changes
  - [ ] Specification completed

Custom Checklist Items:
  - [ ] Database migrations included
  - [ ] API docs updated
  - [ ] Breaking changes documented
  - [ ] Performance benchmarks run
  - [ ] Accessibility checked
  - [ ] Mobile responsive

Auto-Check:
  - [x] Tests added/updated (auto-checked if tests in commits)
  - [x] All tests passing (auto-checked from validation)
  - [x] Documentation updated (auto-checked if docs in commits)
```

---

## Complete PR Description Examples

### Example 1: Feature PR

```markdown
## Summary
Implements JWT-based authentication with refresh token rotation for improved security and scalability. Replaces session-based authentication with stateless JWT tokens while maintaining backwards compatibility during migration period.

Implements specification: spec-feature-auth-001

## Changes

### Features
- feat(auth): implement JWT generation and validation ([abc123](link))
- feat(auth): add refresh token rotation mechanism ([def456](link))
- feat(auth): integrate JWT into authentication service ([ghi789](link))

### Tests
- test(auth): add comprehensive JWT test suite ([jkl012](link))
- test(security): add token rotation security tests ([mno345](link))

### Documentation
- docs(auth): document JWT implementation and API ([pqr678](link))
- docs(readme): add JWT setup instructions ([stu901](link))

## Quality Report

**Tests:** ✅ All passing
- 58 tests passed, 0 failed
- 87% coverage (+12% from baseline)
- Added 16 new tests for JWT functionality

**Security:** ✅ No vulnerabilities
- 0 critical, 0 high, 0 medium, 1 low (acceptable)
- bcrypt password hashing with cost factor 12
- JWT signature validation with HS256
- Token expiry validation implemented
- No hardcoded secrets or credentials

**Code Quality:** ✅ Clean
- 0 linting errors, 2 warnings (acceptable)
- Type checking: Valid (mypy clean)
- Complexity: Average 3.2 (target: <5)
- Duplication: 0.8% (target: <2%)

**Performance:** ✅ No regressions
- Auth endpoint: 45ms (baseline: 42ms, +7%)
- Token generation: 12ms average
- Token validation: 3ms average
- Build time: 12.3s (baseline: 11.8s)

## Review Insights

### Code Quality (refactorer)
✅ **Strengths:**
- Clean separation of concerns in auth module
- Consistent error handling with custom exceptions
- Good use of dependency injection pattern
- Function sizes appropriate (avg 25 lines)

⚠️ **Suggestions:**
- Consider extracting UserValidator to separate class
- Could simplify nested conditionals in authenticate()
- Opportunity to cache user lookups for performance

### Security (security)
✅ **Strengths:**
- Robust bcrypt password hashing (cost 12)
- Comprehensive JWT validation (expiry, signature, issuer)
- Input sanitization across all endpoints
- No hardcoded secrets found

⚠️ **Suggestions:**
- Add rate limiting to prevent brute force attacks
- Add logging for failed authentication attempts
- Consider implementing password complexity requirements

### Testing (qa)
✅ **Strengths:**
- Excellent coverage at 87% (exceeds 80% target)
- All critical auth paths fully tested
- Good edge case coverage (token expiry, invalid tokens)
- Test names clear and descriptive

⚠️ **Suggestions:**
- Could add tests for concurrent token refresh scenarios
- Consider adding load tests for auth endpoints

### Documentation (implementer)
✅ **Strengths:**
- Complete API documentation with OpenAPI specs
- Clear docstrings on all public functions
- README updated with JWT setup instructions
- Working examples provided

⚠️ **Suggestions:**
- Could add architecture diagram for auth flow
- More code examples for token refresh flow would help

### Overall Assessment
✅ **READY TO SHIP** - All quality gates passed, no blocking issues.
8 nice-to-have suggestions identified for future iteration.

## Checklist
- [x] Tests added/updated
- [x] All tests passing
- [x] Documentation updated
- [x] Security reviewed
- [x] No breaking changes
- [x] Specification completed

## Migration Notes
For deployment, clear all existing sessions. Users will need to re-authenticate.
Old session tokens will gracefully expire over 24 hours.
```

### Example 2: Bug Fix PR

```markdown
## Summary
Fixes API endpoint returning 500 error when user data contains null values. Now properly handles null responses with 404 status and clear error message.

Fixes issue #234

## Changes

### Bug Fixes
- fix(api): handle null user in response ([abc123](link))

### Tests
- test(api): add regression test for null user ([def456](link))

## Quality Report

**Tests:** ✅ All passing
- 45 tests passed, 0 failed
- Coverage: 85% (unchanged)
- Added 1 regression test

**Security:** ✅ No vulnerabilities
- No security implications

**Code Quality:** ✅ Clean
- 0 linting errors
- Type checking: Valid

**Performance:** ✅ Improved
- Error handling: 15ms (was: N/A due to crash)

## Review Insights

### Code Quality (refactorer)
✅ **Strengths:**
- Clean null check implementation
- Appropriate error handling
- Good test coverage for fix

⚠️ **Suggestions:**
- None

### Testing (qa)
✅ **Strengths:**
- Regression test prevents recurrence
- Test covers edge case well

⚠️ **Suggestions:**
- None

### Overall Assessment
✅ **READY TO MERGE** - Clean fix with proper test coverage.

## Checklist
- [x] Tests added/updated
- [x] All tests passing
- [x] Documentation updated (N/A for bug fix)
- [x] Security reviewed
- [x] No breaking changes
- [x] Regression test added

## Impact
Low-risk change. Only affects error handling path.
```

---

## Quality Metrics Inclusion

### Test Metrics

```yaml
Test Metrics to Include:
  - Total test count (passed/failed)
  - Test coverage percentage
  - Coverage change from baseline
  - New tests added count
  - Test types (unit/integration/e2e)

Example:
  **Tests:** ✅ All passing
  - Total: 58 passed, 0 failed
  - Coverage: 87% (+12% from baseline)
  - New tests: 16 added
  - Breakdown:
    • Unit tests: 42 passed
    • Integration tests: 12 passed
    • Security tests: 4 passed
```

### Security Metrics

```yaml
Security Metrics to Include:
  - Vulnerability scan results (by severity)
  - Security measures implemented
  - Secrets scan results
  - Dependency vulnerabilities

Example:
  **Security:** ✅ No vulnerabilities
  - Vulnerabilities: 0 critical, 0 high, 0 medium, 1 low
  - Secrets scan: Clean (no hardcoded secrets)
  - Dependencies: All up to date
  - Security measures:
    • bcrypt password hashing (cost: 12)
    • JWT signature validation
    • Input sanitization
    • HTTPS enforcement
```

### Code Quality Metrics

```yaml
Code Quality Metrics to Include:
  - Linting results
  - Type checking results
  - Complexity metrics
  - Code duplication

Example:
  **Code Quality:** ✅ Clean
  - Linting: 0 errors, 2 warnings (acceptable)
  - Type checking: Valid (mypy clean)
  - Complexity: Average 3.2 (target: <5)
  - Duplication: 0.8% (target: <2%)
  - Maintainability: 85/100
```

### Performance Metrics

```yaml
Performance Metrics to Include:
  - Key endpoint response times
  - Change from baseline
  - Build time
  - Bundle size (if applicable)

Example:
  **Performance:** ✅ No regressions
  - Auth endpoint: 45ms (baseline: 42ms, +7%)
  - Token generation: 12ms average
  - Token validation: 3ms average
  - Build time: 12.3s (baseline: 11.8s, +4%)
  - No performance regressions detected
```

---

## Automation Setup

### Auto-Detection Strategy

```yaml
Labels Auto-Detection:
  From Changes:
    - src/auth/ changes → "security", "backend"
    - src/api/ changes → "api", "backend"
    - src/ui/ changes → "frontend", "ui"
    - docs/ changes → "documentation"
    - tests/ changes → "testing"

  From Type:
    - feat commits → "enhancement"
    - fix commits → "bug"
    - refactor commits → "refactoring"
    - perf commits → "performance"
    - docs commits → "documentation"

  From Specification:
    - spec-feature-* → "enhancement"
    - spec-fix-* → "bug"
    - spec-security-* → "security"

Reviewers Auto-Detection:
  From CODEOWNERS:
    - src/auth/ → @security-team
    - src/api/ → @backend-team
    - src/ui/ → @frontend-team
    - docs/ → @documentation-team

  From Git History:
    - Recent contributors to changed files
    - Original authors of modified code

  From Team Structure:
    - Tech lead always added
    - Domain experts for specific areas

Projects Auto-Detection:
  From Specification:
    - Spec linked to project → Add PR to project
    - Spec milestone → Link PR to milestone

Assignees:
  - Author of PR (auto-assigned)
  - Specification owner (if different)
```

### GitHub CLI Commands

**Creating PR with Automation:**

```bash
# Basic PR creation
gh pr create \
  --title "feat: JWT Authentication System" \
  --body-file pr_description.md

# PR with full automation
gh pr create \
  --title "feat: JWT Authentication System" \
  --body-file pr_description.md \
  --label "enhancement,security,backend" \
  --reviewer "@security-team,@backend-team,@tech-lead" \
  --assignee "@me" \
  --milestone "v1.2.0" \
  --project "Authentication System"

# PR with base branch
gh pr create \
  --title "feat: JWT Authentication" \
  --body-file pr_description.md \
  --base main \
  --head feature/jwt-auth

# Draft PR
gh pr create \
  --title "feat: JWT Authentication (WIP)" \
  --body-file pr_description.md \
  --draft
```

**Updating Existing PR:**

```bash
# Update PR description
gh pr edit 123 --body-file updated_description.md

# Add labels
gh pr edit 123 --add-label "security,backend"

# Add reviewers
gh pr edit 123 --add-reviewer "@security-team"

# Mark ready for review (remove draft status)
gh pr ready 123
```

**Checking PR Status:**

```bash
# Check PR status
gh pr view 123

# Check PR checks (CI/CD)
gh pr checks 123

# List PRs
gh pr list --author "@me"
```

---

## Specification Integration

### Linking Specifications

**In PR Description:**

```yaml
Specification Reference:
  Format: "Implements specification: spec-feature-auth-001"

  Full Example:
    ## Summary
    Implements JWT-based authentication system.

    Implements specification: spec-feature-auth-001

  Multiple Specs:
    Implements specifications:
    - spec-feature-auth-001 (JWT implementation)
    - spec-feature-session-002 (Session management)
```

**Automatic Linking:**

```yaml
GitHub Auto-Linking:
  - GitHub auto-links spec IDs to issues/files
  - Use: "Implements spec-feature-auth-001"
  - GitHub creates clickable link if spec is issue

Custom Linking:
  - Link to spec file in repo
  - Format: [spec-feature-auth-001](.quaestor/specs/active/spec-feature-auth-001.md)
```

### Specification Archiving

**Archive Process:**

```yaml
When to Archive:
  - PR created and ready for merge
  - All spec tasks completed
  - Acceptance criteria met
  - Quality gates passed

Archive Steps:
  1. Verify Completion:
     - Check all tasks marked complete
     - Verify acceptance criteria met
     - Confirm quality gates passed

  2. Move Specification:
     From: .quaestor/specs/active/spec-feature-auth-001.md
     To: .quaestor/specs/completed/spec-feature-auth-001.md

  3. Update Metadata:
     - status: "completed"
     - completion_date: "2025-10-19"
     - pr_url: "https://github.com/user/repo/pull/123"
     - pr_number: 123

  4. Generate Summary:
     - What was delivered
     - Key decisions made
     - Lessons learned
     - Performance metrics
```

**Archive in PR Description:**

```yaml
Include Archive Status:
  ## Specification Status
  ✅ **Specification Completed and Archived**
  - Specification: spec-feature-auth-001
  - Status: Moved to completed/
  - Completion Date: 2025-10-19
  - All acceptance criteria met
```

---

## Team Collaboration Features

### CODEOWNERS Integration

**CODEOWNERS File:**

```yaml
# .github/CODEOWNERS
# Auth module
/src/auth/ @security-team @backend-team

# API endpoints
/src/api/ @backend-team

# Frontend
/src/ui/ @frontend-team

# Documentation
/docs/ @documentation-team

# Tests
/tests/ @qa-team

# Config
*.config.js @devops-team
```

**Auto-Assignment:**

```yaml
When PR Created:
  - GitHub auto-requests reviews from CODEOWNERS
  - Based on files changed in PR
  - Example: PR changes src/auth/ → @security-team auto-requested
```

### Review Request Strategy

```yaml
Review Request Tiers:

Required Reviewers:
  - CODEOWNERS for changed files (auto-requested)
  - Tech lead (always)
  - Domain expert (if specialized area)

Optional Reviewers:
  - Recent contributors to changed files
  - Team members in same area
  - Original code authors

Example:
  Required:
    - @security-team (CODEOWNERS for src/auth/)
    - @tech-lead (always required)

  Optional:
    - @john (recent auth contributor)
    - @jane (original auth author)
```

### PR Labels Strategy

```yaml
Label Categories:

Type Labels:
  - enhancement: New features
  - bug: Bug fixes
  - documentation: Docs only
  - refactoring: Code improvements
  - performance: Performance improvements

Area Labels:
  - backend: Backend changes
  - frontend: Frontend changes
  - api: API changes
  - security: Security-related
  - database: Database changes

Status Labels:
  - work-in-progress: Not ready for review
  - ready-for-review: Ready for review
  - needs-changes: Changes requested
  - approved: Approved by reviewers

Priority Labels:
  - priority:high: High priority
  - priority:medium: Medium priority
  - priority:low: Low priority

Example PR Labels:
  - enhancement, security, backend, ready-for-review, priority:high
```

### PR Projects and Milestones

```yaml
Project Integration:
  - Link PR to project board
  - Auto-move through project stages
  - Track progress visually

Milestone Integration:
  - Link PR to version milestone
  - Track feature completion
  - Plan releases

GitHub CLI:
  # Add to project
  gh pr edit 123 --add-project "Authentication System"

  # Add to milestone
  gh pr edit 123 --milestone "v1.2.0"
```

---

## CI/CD Integration

### Automated Checks

```yaml
PR Checks to Trigger:
  - Linting (eslint, ruff, etc.)
  - Testing (pytest, jest, etc.)
  - Type checking (mypy, tsc, etc.)
  - Security scan (bandit, snyk, etc.)
  - Coverage report (codecov, coveralls)
  - Build verification
  - E2E tests (if applicable)

Status Checks:
  - All checks must pass before merge
  - Display status in PR
  - Block merge if failing
```

**GitHub Actions Workflow:**

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on:
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          npm test
          npm run test:coverage

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Linting
        run: npm run lint

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Security Scan
        run: npm audit
```

### Auto-Merge Configuration

```yaml
Auto-Merge Rules:
  Requirements:
    - All checks passing
    - Required reviews approved
    - No changes requested
    - Up to date with base branch

  Configuration:
    - Enable auto-merge in repo settings
    - Set branch protection rules
    - Require status checks

GitHub CLI:
  # Enable auto-merge
  gh pr merge 123 --auto --squash

  # Merge when ready
  gh pr merge 123 --squash --delete-branch
```

---

## PR Best Practices

### DO:

```yaml
✅ Best Practices:
  - Write clear, descriptive PR titles
  - Include comprehensive description
  - Add all relevant quality metrics
  - Include multi-agent review insights
  - Link to specifications and issues
  - Use appropriate labels
  - Request relevant reviewers
  - Keep PRs focused and atomic
  - Update PR when requirements change
  - Respond to review comments promptly
```

### DON'T:

```yaml
❌ Anti-Patterns:
  - Vague titles: "Fix stuff" or "Updates"
  - Empty descriptions: No context provided
  - Missing quality metrics: No test/coverage info
  - No specification links: Can't trace to requirements
  - Wrong reviewers: Irrelevant team members
  - Massive PRs: Too many changes at once
  - Outdated PRs: Not synced with base branch
  - Ignoring CI failures: Merge with failing tests
  - No response to reviews: Leave comments unaddressed
```

---

## Common PR Scenarios

### Scenario 1: Feature PR

```yaml
Situation: New feature implementation complete

PR Structure:
  - Title: "feat: JWT Authentication System"
  - Description: Full template with all sections
  - Labels: enhancement, security, backend
  - Reviewers: @security-team, @backend-team
  - Milestone: v1.2.0
  - Specification: Linked and archived
```

### Scenario 2: Bug Fix PR

```yaml
Situation: Critical bug fix

PR Structure:
  - Title: "fix(api): Handle null user responses"
  - Description: Simplified template
  - Labels: bug, backend, priority:high
  - Reviewers: @backend-team, @tech-lead
  - Issue: Closes #234
  - Fast-track: Request expedited review
```

### Scenario 3: Documentation PR

```yaml
Situation: Documentation updates only

PR Structure:
  - Title: "docs: Update authentication documentation"
  - Description: Simple description
  - Labels: documentation
  - Reviewers: @documentation-team
  - CI: Only doc checks needed
  - Quick merge: Low risk change
```

### Scenario 4: Large Refactoring PR

```yaml
Situation: Major code refactoring

PR Structure:
  - Title: "refactor: Restructure authentication module"
  - Description: Detailed with migration notes
  - Labels: refactoring, backend, breaking-change
  - Reviewers: @tech-lead, @architect, @backend-team
  - Testing: Comprehensive test coverage required
  - Review: Multiple review rounds expected
```

---

*Comprehensive guide to PR creation with rich context, automation, and team collaboration*
