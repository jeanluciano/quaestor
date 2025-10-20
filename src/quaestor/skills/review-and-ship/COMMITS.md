# Intelligent Commit Generation

This file describes strategies for analyzing changes and generating high-quality, atomic commits.

## Commit Generation Overview

```yaml
Commit Generation Process:
  1. Change Analysis: Understand what changed and why
  2. Change Grouping: Group related changes logically
  3. Commit Classification: Determine commit type
  4. Scope Extraction: Extract scope from context
  5. Message Generation: Create clear, conventional messages
  6. Specification Integration: Link to specifications
  7. Commit Creation: Create atomic commits

Goals:
  - Atomic: One logical change per commit
  - Clear: Easy to understand what changed
  - Conventional: Follow conventional commit format
  - Traceable: Link to specifications and context
```

---

## Change Analysis

### Understanding Changes

**Discovery Phase:**

```bash
# Get all changed files
git status --short
git diff --stat

# Analyze uncommitted changes
git diff
git diff --cached  # Staged changes

# Compare with main branch
git diff main...HEAD

# Get file-level changes
git diff --name-only
git diff --name-status  # Include status (A/M/D)
```

**Change Classification:**

```yaml
Change Types:
  Added (A): New files created
  Modified (M): Existing files changed
  Deleted (D): Files removed
  Renamed (R): Files renamed/moved
  Copied (C): Files copied

Example Output:
  A  src/auth/jwt.py           # New JWT module
  M  src/auth/service.py       # Modified auth service
  A  tests/test_jwt.py         # New tests
  M  docs/api.md               # Updated docs
  M  README.md                 # Updated readme
```

### Change Grouping Strategy

**Group by Module:**

```yaml
Module-Based Grouping:
  Group 1 - Auth Module:
    - src/auth/jwt.py (new)
    - src/auth/service.py (modified)
    - tests/test_jwt.py (new)

  Group 2 - Documentation:
    - docs/api.md (modified)
    - README.md (modified)

Result: 2 commits (module, docs)
```

**Group by Feature:**

```yaml
Feature-Based Grouping:
  Group 1 - JWT Implementation:
    - src/auth/jwt.py (new)
    - src/auth/service.py (modified - added JWT calls)

  Group 2 - JWT Tests:
    - tests/test_jwt.py (new)

  Group 3 - JWT Documentation:
    - docs/api.md (modified - JWT endpoints)
    - README.md (modified - JWT setup)

Result: 3 commits (impl, test, docs)
```

**Group by Type:**

```yaml
Type-Based Grouping:
  Group 1 - Feature Changes:
    - src/auth/jwt.py (new feature)
    - src/auth/service.py (feature addition)

  Group 2 - Test Changes:
    - tests/test_jwt.py (tests for feature)

  Group 3 - Documentation Changes:
    - docs/api.md (document feature)
    - README.md (document feature)

Result: 3 commits (feat, test, docs)
```

### Recommended Grouping Approach

**Hybrid Strategy (Recommended):**

```yaml
Strategy: Feature-based with Test Inclusion

Rule: Include tests with implementation
  - Implementation + its tests = one commit
  - Documentation = separate commit
  - Refactoring = separate commit

Example:
  Commit 1: feat(auth): implement JWT generation
    - src/auth/jwt.py (JWT generation code)
    - tests/test_jwt.py (JWT generation tests)

  Commit 2: feat(auth): implement JWT validation
    - src/auth/jwt.py (JWT validation code)
    - tests/test_jwt.py (JWT validation tests)

  Commit 3: docs(auth): document JWT implementation
    - docs/api.md (JWT API documentation)
    - README.md (JWT setup instructions)

Benefits:
  - Atomic: Each commit is a complete logical change
  - Testable: Tests included with implementation
  - Clear: Easy to understand what each commit does
  - Revertable: Can revert entire feature cleanly
```

---

## Commit Classification

### Conventional Commit Types

**Type Definitions:**

```yaml
feat: New feature for the user
  When:
    - Adding new functionality
    - New API endpoints
    - New user-facing features
    - New capabilities

  Examples:
    - "feat(auth): implement JWT authentication"
    - "feat(api): add user profile endpoint"
    - "feat(payments): integrate Stripe checkout"
    - "feat(search): add full-text search"

fix: Bug fix for the user
  When:
    - Fixing broken functionality
    - Correcting errors
    - Resolving issues
    - Patching vulnerabilities

  Examples:
    - "fix(auth): prevent token expiry race condition"
    - "fix(api): handle null response in user endpoint"
    - "fix(validation): correct email regex pattern"
    - "fix(db): resolve connection timeout issue"

docs: Documentation changes only
  When:
    - Updating documentation
    - Adding code comments
    - README changes
    - API documentation
    - Examples and guides

  Examples:
    - "docs(api): update OpenAPI specifications"
    - "docs(readme): add installation instructions"
    - "docs(auth): document OAuth flow"
    - "docs: add contributing guidelines"

refactor: Code change that neither fixes nor adds feature
  When:
    - Restructuring code
    - Improving code quality
    - No behavior change
    - Performance optimization (internal)

  Examples:
    - "refactor(parser): simplify token extraction"
    - "refactor(utils): extract common validation logic"
    - "refactor(auth): improve session management structure"
    - "refactor: apply DRY principle to reducers"

test: Adding or updating tests
  When:
    - Adding missing tests
    - Improving test coverage
    - Fixing failing tests
    - Adding test utilities

  Examples:
    - "test(auth): add coverage for edge cases"
    - "test(api): add integration tests for user endpoints"
    - "test(utils): add unit tests for validators"
    - "test: increase coverage to 85%"

perf: Performance improvements
  When:
    - Optimizing performance
    - Reducing load times
    - Improving efficiency
    - User-visible performance gains

  Examples:
    - "perf(query): optimize database query for large datasets"
    - "perf(render): add memoization to reduce re-renders"
    - "perf(cache): implement Redis caching layer"
    - "perf(api): reduce response time by 40%"

style: Code style changes (formatting, naming)
  When:
    - Formatting changes
    - Whitespace fixes
    - Naming improvements
    - No code logic change

  Examples:
    - "style(auth): apply consistent naming conventions"
    - "style: format code with prettier"
    - "style(api): fix indentation"
    - "style: remove trailing whitespace"

chore: Maintenance tasks (dependencies, config)
  When:
    - Dependency updates
    - Configuration changes
    - Build script updates
    - Tool configuration

  Examples:
    - "chore(deps): update dependencies to latest versions"
    - "chore(config): update linting rules"
    - "chore: update CI/CD pipeline"
    - "chore(deps): bump axios from 0.21.0 to 0.21.1"

build: Build system or external dependency changes
  When:
    - Build configuration changes
    - Build tool updates
    - Compilation changes

  Examples:
    - "build: update webpack configuration"
    - "build(docker): optimize Docker image size"
    - "build: add source maps for production"

ci: CI/CD configuration changes
  When:
    - CI pipeline changes
    - GitHub Actions updates
    - Deployment config changes

  Examples:
    - "ci: add automated testing to PR workflow"
    - "ci: update deployment pipeline"
    - "ci(github): add code coverage reporting"

revert: Reverting a previous commit
  When:
    - Rolling back changes
    - Undoing a commit

  Examples:
    - "revert: revert 'feat(auth): implement JWT'"
    - "revert: undo performance optimization"
```

### Type Selection Algorithm

**Decision Tree:**

```yaml
Is this a new feature for users?
  Yes → feat

Does this fix a bug or error?
  Yes → fix

Does this change documentation only?
  Yes → docs

Does this add or improve tests only?
  Yes → test

Does this improve performance (user-visible)?
  Yes → perf

Does this restructure code without behavior change?
  Yes → refactor

Does this change only formatting/style?
  Yes → style

Does this update dependencies or config?
  Yes → chore

Does this change build system?
  Yes → build

Does this change CI/CD?
  Yes → ci
```

---

## Scope Extraction

### Determining Scope

**From File Paths:**

```yaml
Path Analysis:
  src/auth/jwt.py → scope: auth
  src/api/users.py → scope: api
  src/api/posts.py → scope: api
  src/utils/validation.py → scope: utils
  src/database/migrations/ → scope: database
  tests/test_auth.py → scope: auth (test relates to auth)
  docs/api.md → scope: api (docs relate to api)
  README.md → scope: none (project-level)

Rules:
  - Use first directory after src/ as scope
  - For tests, use what they're testing
  - For docs, use what they're documenting
  - For project-level, omit scope
```

**From Specification:**

```yaml
Specification-Based Scope:
  Spec ID: spec-feature-auth-001
    → scope: auth

  Spec ID: spec-refactor-api-endpoints
    → scope: api

  Spec Title: "User Profile Management"
    → scope: profile

  Spec Title: "Payment Integration"
    → scope: payments
```

**From Change Context:**

```yaml
Context-Based Scope:
  User authentication changes → auth
  API endpoint changes → api
  Database changes → database or db
  UI component changes → ui or components
  Utility function changes → utils
  Configuration changes → config
  Testing changes → test (or omit)
```

### Multiple Scopes

**Handling Multiple Scopes:**

```yaml
Option 1: Separate Commits (Recommended)
  Changes in auth/ and api/
  → Commit 1: feat(auth): implement JWT
  → Commit 2: feat(api): add JWT middleware

Option 2: Multiple Scopes
  Changes in auth/ and api/
  → Commit: feat(auth,api): implement JWT authentication

Option 3: Broader Scope
  Changes in auth/ and api/ (tightly coupled)
  → Commit: feat: implement JWT authentication

Recommendation:
  - Prefer separate commits (Option 1) for clarity
  - Use multiple scopes if changes must be together
  - Use no scope for system-wide changes
```

---

## Message Generation

### Conventional Commit Format

**Format Structure:**

```yaml
Format: type(scope): description

[optional body]

[optional footer]

Rules:
  - type: lowercase (feat, fix, docs, etc.)
  - scope: lowercase, optional, in parentheses
  - description: lowercase, imperative mood, no period
  - body: optional, explain "why" not "what"
  - footer: optional, breaking changes, references

Examples:
  feat(auth): implement JWT refresh tokens
  fix(api): handle null response in user endpoint
  docs(readme): add installation instructions
  refactor(parser): simplify token extraction logic
```

### Description Guidelines

**Good Descriptions:**

```yaml
Characteristics:
  - Imperative mood: "add" not "added" or "adds"
  - Lowercase: "implement feature" not "Implement Feature"
  - Concise: Under 72 characters
  - Clear: Describes what changed
  - No period: "add feature" not "add feature."

Examples:
  ✅ "implement JWT refresh tokens"
  ✅ "handle null response in user endpoint"
  ✅ "add coverage for edge cases"
  ✅ "update OpenAPI specifications"
  ✅ "simplify token extraction logic"

  ❌ "added JWT stuff"
  ❌ "Fixed a bug."
  ❌ "Update"
  ❌ "Implemented the JWT refresh token functionality for better security"
  ❌ "auth changes"
```

### Body Content

**When to Include Body:**

```yaml
Include Body When:
  - Need to explain "why" the change was made
  - Breaking changes need explanation
  - Complex changes need context
  - Alternatives were considered
  - Specification provides context

Omit Body When:
  - Description is self-explanatory
  - Simple, straightforward change
  - No additional context needed
```

**Body Examples:**

```yaml
Example 1: With Context
  feat(auth): implement JWT refresh tokens

  Adds refresh token rotation for improved security.
  Access tokens expire after 15 minutes, refresh tokens after 7 days.

  This approach prevents token theft and improves security posture
  while maintaining good user experience.

  Implements spec-feature-auth-001 phase 2.

Example 2: Breaking Change
  feat(api): change user endpoint response format

  BREAKING CHANGE: User endpoint now returns nested profile object
  instead of flat structure.

  Old format: { id, name, email, bio }
  New format: { id, profile: { name, email, bio } }

  This improves consistency with other endpoints and supports
  future profile expansion.

Example 3: Bug Fix Context
  fix(auth): prevent token expiry race condition

  Users were occasionally logged out unexpectedly when token refresh
  happened simultaneously with API calls. Added mutex to ensure only
  one refresh happens at a time.

  Fixes issue reported in user feedback.
```

### Footer Content

**Footer Types:**

```yaml
Breaking Changes:
  BREAKING CHANGE: Description of breaking change

  Example:
    feat(api): redesign authentication endpoints

    BREAKING CHANGE: /auth/login endpoint now requires email instead of username

Issue References:
  Closes #123
  Fixes #456
  Resolves #789

  Example:
    fix(api): handle timeout in user fetch

    Fixes #123

Specification References:
  Spec: spec-feature-auth-001

  Example:
    feat(auth): implement JWT tokens

    Implements spec-feature-auth-001 phase 2

Multiple Footers:
  Example:
    feat(api): add rate limiting

    BREAKING CHANGE: API now returns 429 status when rate limit exceeded
    Closes #234
    Spec: spec-feature-api-ratelimit
```

---

## Atomic Commit Strategy

### Principles of Atomic Commits

```yaml
Atomic Commit Principles:
  1. Single Logical Change: One commit = one complete change
  2. Independently Revertable: Can undo without breaking things
  3. Includes Tests: Tests for the change included
  4. Passes Tests: All tests pass after commit
  5. Clear Purpose: Easy to understand what and why

Benefits:
  - Easy to review: Focused, clear changes
  - Easy to revert: No tangled dependencies
  - Clear history: Understandable git log
  - Better debugging: git bisect works well
  - Selective cherry-pick: Can pick specific changes
```

### Good Atomic Commits

**Examples:**

```yaml
Example 1: Feature with Tests
  Commit: feat(auth): implement JWT generation
  Files:
    - src/auth/jwt.py (add generateToken function)
    - tests/test_jwt.py (add tests for generateToken)

  Why Atomic:
    - One logical change: JWT generation
    - Includes tests
    - Can be reverted cleanly
    - Tests pass

Example 2: Bug Fix with Test
  Commit: fix(api): handle null user in response
  Files:
    - src/api/users.py (add null check)
    - tests/test_users.py (add test for null case)

  Why Atomic:
    - One logical change: null handling
    - Includes regression test
    - Can be reverted
    - Tests pass

Example 3: Documentation Update
  Commit: docs(api): document authentication endpoints
  Files:
    - docs/api.md (add auth section)
    - README.md (add auth setup)

  Why Atomic:
    - One logical change: auth documentation
    - Related docs together
    - Can be reverted
    - No code changes to break

Example 4: Refactoring
  Commit: refactor(auth): extract UserValidator class
  Files:
    - src/auth/service.py (extract validation)
    - src/auth/validator.py (new validator class)
    - tests/test_validator.py (update tests)

  Why Atomic:
    - One logical change: extract validator
    - No behavior change
    - Tests updated
    - Tests pass
```

### Bad Non-Atomic Commits

**Anti-Patterns:**

```yaml
Example 1: Too Many Changes
  Commit: feat: add authentication and fix bugs and update docs
  Files:
    - src/auth/ (new auth system)
    - src/api/users.py (unrelated bug fix)
    - src/database/ (schema change)
    - docs/ (documentation)
    - tests/ (various tests)

  Why Bad:
    - Multiple unrelated changes
    - Can't revert one without affecting others
    - Hard to review
    - Unclear purpose

  Fix: Split into 4-5 commits:
    - feat(auth): implement authentication system
    - fix(api): correct user endpoint bug
    - feat(database): add user roles schema
    - test(auth): add authentication tests
    - docs(auth): document authentication

Example 2: Incomplete Change
  Commit: feat(auth): implement JWT (WIP)
  Files:
    - src/auth/jwt.py (incomplete implementation)
    - Tests don't pass

  Why Bad:
    - Not complete
    - Tests failing
    - Not in working state
    - "WIP" in commit message

  Fix: Complete implementation before committing

Example 3: Mixed Concerns
  Commit: update code
  Files:
    - src/auth/jwt.py (feature addition)
    - src/api/users.py (formatting)
    - README.md (typo fix)

  Why Bad:
    - Unrelated changes
    - Vague commit message
    - Hard to understand purpose

  Fix: Split into 3 commits:
    - feat(auth): add JWT token refresh
    - style(api): format users endpoint
    - docs(readme): fix typo in setup section
```

---

## Specification Integration

### Linking Commits to Specifications

**Specification References:**

```yaml
In Commit Message Body:
  feat(auth): implement JWT refresh tokens

  Implements spec-feature-auth-001 phase 2: Token Management

In Commit Message Footer:
  feat(auth): implement JWT validation

  Spec: spec-feature-auth-001

In Both:
  feat(auth): implement session management

  Adds session storage with Redis for scalability.
  Users can maintain sessions across devices.

  Implements spec-feature-auth-001 phase 3
  Spec: spec-feature-auth-001
```

### Tracking Implementation Progress

**Update Specification File:**

```yaml
After Each Commit:
  1. Update specification file
  2. Mark completed phases/tasks
  3. Add commit reference
  4. Update completion evidence

Example Specification Update:
  ## Implementation Progress

  ### Phase 1: JWT Generation ✅
  - Status: Completed
  - Commit: abc123 "feat(auth): implement JWT generation"
  - Date: 2025-10-19

  ### Phase 2: JWT Validation ✅
  - Status: Completed
  - Commit: def456 "feat(auth): implement JWT validation"
  - Date: 2025-10-19

  ### Phase 3: Session Management 🚧
  - Status: In Progress
  - Commit: -
  - Date: -
```

### Commit Hash References

**In Specification:**

```yaml
Track Commits in Spec:
  ## Commits
  - abc123: feat(auth): implement JWT generation
  - def456: feat(auth): implement JWT validation
  - ghi789: test(auth): add comprehensive JWT tests
  - jkl012: docs(auth): document JWT implementation

Benefits:
  - Traceability: Link spec to implementation
  - Evidence: Show what was completed
  - Review: Easy to find relevant code
  - History: Track implementation timeline
```

---

## Commit Generation Examples

### Example 1: Authentication Feature

**Changes:**
```yaml
Modified Files:
  - src/auth/jwt.py (new file - 120 lines)
  - src/auth/service.py (modified - added JWT integration)
  - tests/test_jwt.py (new file - 80 lines)
  - tests/test_auth_service.py (modified - added JWT tests)
  - docs/api.md (modified - documented JWT endpoints)
  - README.md (modified - added JWT setup)
```

**Generated Commits:**

```yaml
Commit 1: feat(auth): implement JWT generation and signing
  Files:
    - src/auth/jwt.py (JWT generation, signing)
    - tests/test_jwt.py (generation tests)

  Message:
    feat(auth): implement JWT generation and signing

    Adds JWT token generation with HS256 signing algorithm.
    Tokens include user ID, expiry, and custom claims.

    Implements spec-feature-auth-001 phase 1

Commit 2: feat(auth): implement JWT validation and verification
  Files:
    - src/auth/jwt.py (JWT validation, verification)
    - tests/test_jwt.py (validation tests)

  Message:
    feat(auth): implement JWT validation and verification

    Adds JWT token validation including expiry check,
    signature verification, and claim extraction.

    Implements spec-feature-auth-001 phase 2

Commit 3: feat(auth): integrate JWT into authentication service
  Files:
    - src/auth/service.py (JWT integration)
    - tests/test_auth_service.py (integration tests)

  Message:
    feat(auth): integrate JWT into authentication service

    Updates authentication service to use JWT tokens
    for user sessions. Replaces session-based auth.

    Implements spec-feature-auth-001 phase 3

Commit 4: docs(auth): document JWT authentication
  Files:
    - docs/api.md (JWT API documentation)
    - README.md (JWT setup instructions)

  Message:
    docs(auth): document JWT authentication

    Adds documentation for JWT authentication including:
    - API endpoints for token generation
    - Token format and claims
    - Setup instructions

    Spec: spec-feature-auth-001
```

### Example 2: Bug Fix

**Changes:**
```yaml
Modified Files:
  - src/api/users.py (null check added)
  - tests/test_users.py (regression test added)
```

**Generated Commit:**

```yaml
Commit: fix(api): handle null user in response

  Files:
    - src/api/users.py (add null check)
    - tests/test_users.py (add regression test)

  Message:
    fix(api): handle null user in response

    API was returning 500 error when user not found.
    Now returns 404 with proper error message.

    Added regression test to prevent future occurrence.

    Fixes #234
```

### Example 3: Refactoring

**Changes:**
```yaml
Modified Files:
  - src/auth/service.py (extract validator)
  - src/auth/validator.py (new validator class)
  - tests/test_validator.py (validator tests)
  - tests/test_auth_service.py (update to use validator)
```

**Generated Commits:**

```yaml
Commit 1: refactor(auth): extract UserValidator class
  Files:
    - src/auth/validator.py (new validator class)
    - tests/test_validator.py (validator tests)

  Message:
    refactor(auth): extract UserValidator class

    Extracts user validation logic into separate class
    for better separation of concerns and testability.

    No behavior change.

Commit 2: refactor(auth): use UserValidator in auth service
  Files:
    - src/auth/service.py (use new validator)
    - tests/test_auth_service.py (update tests)

  Message:
    refactor(auth): use UserValidator in auth service

    Updates auth service to use new UserValidator class.
    Removes duplicate validation logic.

    No behavior change.
```

---

## Git Best Practices

### Commit Workflow

```bash
# 1. Review changes
git status
git diff

# 2. Stage related changes
git add src/auth/jwt.py tests/test_jwt.py

# 3. Create commit with message
git commit -m "feat(auth): implement JWT generation" \
           -m "Adds JWT token generation with HS256 signing."

# 4. Repeat for next logical group
git add src/auth/service.py tests/test_auth_service.py
git commit -m "feat(auth): integrate JWT into auth service"

# 5. Push when ready
git push
```

### Interactive Staging

```bash
# Stage specific hunks interactively
git add -p src/auth/service.py

# This allows selecting specific changes within a file
# Useful when file has multiple unrelated changes
```

### Amending Commits

```bash
# Add forgotten file to last commit
git add tests/test_missing.py
git commit --amend --no-edit

# Change last commit message
git commit --amend -m "feat(auth): implement JWT tokens"

# WARNING: Only amend commits not yet pushed!
```

### Commit Message Validation

```bash
# Use commitlint to validate messages
npm install -g @commitlint/cli @commitlint/config-conventional

# Validate commit message
echo "feat(auth): add JWT" | commitlint

# Set up git hook
# In .git/hooks/commit-msg
#!/bin/sh
npx commitlint --edit $1
```

---

## Common Commit Scenarios

### Scenario 1: Feature with Multiple Components

```yaml
Situation: Authentication feature with JWT, session, and docs

Strategy: Separate by component
  Commit 1: feat(auth): implement JWT token management
  Commit 2: feat(auth): add session storage with Redis
  Commit 3: test(auth): add authentication test suite
  Commit 4: docs(auth): document authentication system

Why: Each component is independent and atomic
```

### Scenario 2: Bug Fix Affecting Multiple Areas

```yaml
Situation: Null handling bug in API and database layer

Strategy: Single commit if tightly coupled
  Commit: fix: handle null values in user data

  Files:
    - src/api/users.py (null check)
    - src/database/queries.py (null handling)
    - tests/test_users.py (regression tests)

Why: Changes are interdependent, must be together
```

### Scenario 3: Large Refactoring

```yaml
Situation: Refactor entire authentication module

Strategy: Multiple small commits
  Commit 1: refactor(auth): extract UserValidator
  Commit 2: refactor(auth): extract TokenManager
  Commit 3: refactor(auth): simplify AuthService
  Commit 4: refactor(auth): update tests for new structure

Why: Easier to review, revert if needed, understand changes
```

### Scenario 4: Dependency Update

```yaml
Situation: Update dependencies and fix breaking changes

Strategy: Separate commits
  Commit 1: chore(deps): update axios to v1.0
  Commit 2: fix(api): update API calls for axios v1.0

Why: Dependency update separate from code changes
```

---

*Comprehensive guide to intelligent commit generation with conventional commits and atomic strategy*
