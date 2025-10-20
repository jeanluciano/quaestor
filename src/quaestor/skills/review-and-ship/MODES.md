# Review Modes - Different Review Strategies

This file describes the different review modes available and when to use each one.

## Mode Overview

```yaml
Available Modes:
  full: Complete 5-phase review pipeline (default)
  quick: Fast review for small changes
  commit-only: Generate commits without PR
  validate-only: Quality checks and fixes only
  pr-only: Create PR from existing commits
  analysis: Deep code quality analysis
  archive-spec: Move completed spec to completed/

Mode Selection:
  - Auto-detect based on context
  - User specifies with flags
  - Optimize for common workflows
```

---

## Full Review Mode (Default)

### Overview

```yaml
Full Review Mode:
  phases: [Validate, Fix, Commit, Review, Ship]
  time: 15-30 minutes
  coverage: Comprehensive
  output: Complete PR with rich context

When to Use:
  - Completed feature ready to ship
  - Major changes need thorough review
  - Want comprehensive quality validation
  - Need multi-agent review insights
  - Creating important PR

When NOT to Use:
  - Small quick fixes (use quick mode)
  - Just need commits (use commit-only)
  - Already have commits (use pr-only)
  - Just checking quality (use validate-only)
```

### Workflow

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
  - refactorer: Code quality review
  - security: Security review
  - qa: Test coverage review
  - implementer: Documentation review
  - architect: Architecture review (if needed)
  - Consolidated review summary

Phase 5: PR Creation & Shipping (🚀)
  - PR title and description generation
  - Quality metrics inclusion
  - Review insights integration
  - Automation setup
  - Specification archiving
```

### Example Usage

```bash
# Command-based
/review

# Conversation-based
"Review my changes and create a PR"
"Ready to ship this feature"
"Comprehensive review of authentication implementation"
```

### Expected Output

```yaml
Output Components:
  1. Quality Validation Report:
     - All quality gates status
     - Issues found and fixed
     - Metrics (coverage, linting, etc.)

  2. Generated Commits:
     - List of commits created
     - Conventional commit format
     - Specification references

  3. Multi-Agent Review Summary:
     - Code quality insights
     - Security assessment
     - Test coverage analysis
     - Documentation completeness
     - Overall recommendation

  4. PR Details:
     - PR number and URL
     - Title and description preview
     - Automation applied (labels, reviewers)
     - Specification archive status

Time: ~15-30 minutes
```

---

## Quick Review Mode

### Overview

```yaml
Quick Review Mode:
  phases: [Basic Validate, Auto-Fix, Simple Commit, Single Review, Basic PR]
  time: 3-5 minutes
  coverage: Essential checks only
  output: Simple PR with basic context

When to Use:
  - Small changes (1-3 files)
  - Documentation updates
  - Minor bug fixes
  - Quick hotfixes
  - Low-risk changes

When NOT to Use:
  - Major features (use full review)
  - Security changes (use full review)
  - Complex refactoring (use full review)
  - Need detailed analysis (use analysis mode)
```

### Workflow

```yaml
Phase 1: Basic Validation (🔍)
  - Linting check only
  - Quick test run
  - No deep analysis
  - Skip: Security scan, coverage analysis

Phase 2: Auto-Fix Only (⚡)
  - Formatting fixes
  - Linting auto-fixes
  - Skip: Agent delegation
  - Skip: Complex fixes

Phase 3: Simple Commit (📝)
  - One commit for all changes
  - Basic conventional format
  - Skip: Intelligent grouping
  - Skip: Complex classification

Phase 4: Single Agent Review (🤖)
  - Use refactorer agent only
  - Quick code quality check
  - Skip: Security, QA, implementer reviews
  - Skip: Consolidated summary

Phase 5: Basic PR (🚀)
  - Simple title and description
  - Basic quality metrics
  - Skip: Detailed review insights
  - Skip: Complex automation
```

### Example Usage

```bash
# Command-based
/review --quick

# Conversation-based
"Quick review for this small fix"
"Fast review, just need to ship docs"
"Simple review for typo fixes"
```

### Expected Output

```yaml
Output Components:
  1. Basic Validation:
     - Tests: ✅ Passed
     - Linting: ✅ Clean

  2. Single Commit:
     - "fix(api): correct typo in error message"

  3. Quick Review:
     - Code quality: ✅ Good
     - No major issues found

  4. Simple PR:
     - PR #124 created
     - Basic description
     - Ready for merge

Time: ~3-5 minutes
```

---

## Commit-Only Mode

### Overview

```yaml
Commit-Only Mode:
  phases: [Basic Validate, Auto-Fix, Smart Commit]
  time: 5-10 minutes
  coverage: Commit generation focused
  output: Organized commits, no PR

When to Use:
  - Want organized commits but not ready for PR
  - Working on long-running branch
  - Need to commit progress
  - Plan to create PR later
  - Want conventional commits without review

When NOT to Use:
  - Ready to ship (use full review)
  - Need quality validation (use validate-only)
  - Already have commits (no need)
```

### Workflow

```yaml
Phase 1: Basic Validation (🔍)
  - Run linting
  - Run tests
  - Basic quality checks
  - Ensure changes compile/run

Phase 2: Simple Auto-Fixing (⚡)
  - Format code
  - Fix simple linting issues
  - Skip: Complex agent fixes

Phase 3: Smart Commit Generation (📝)
  - Analyze all changes
  - Group related changes
  - Classify by type
  - Generate conventional commits
  - Include specification references

Phases Skipped:
  - Multi-agent review
  - PR creation
```

### Example Usage

```bash
# Command-based
/review --commit-only

# Conversation-based
"Generate commits from my changes"
"Create organized commits but don't make PR yet"
"I want proper commits but I'm not done with the feature"
```

### Expected Output

```yaml
Output Components:
  1. Validation Status:
     - Tests: ✅ Passed
     - Linting: ✅ Clean (auto-fixed)

  2. Generated Commits:
     - 3 commits created:
       • "feat(auth): implement JWT generation"
       • "test(auth): add JWT generation tests"
       • "docs(auth): document JWT implementation"

  3. Summary:
     - Commits created and pushed
     - No PR created (as requested)
     - Ready to continue work or create PR later

Time: ~5-10 minutes
```

---

## Validate-Only Mode

### Overview

```yaml
Validate-Only Mode:
  phases: [Comprehensive Validate, Auto-Fix]
  time: 5-10 minutes
  coverage: Quality checks and fixes
  output: Validation report with fixes

When to Use:
  - Check code quality before committing
  - Want to fix issues without committing
  - Unsure if ready for review
  - Need quality metrics
  - Want to ensure quality gates pass

When NOT to Use:
  - Ready to commit (use commit-only)
  - Ready to ship (use full review)
  - Just need PR (use pr-only)
```

### Workflow

```yaml
Phase 1: Comprehensive Validation (🔍)
  - Multi-domain quality checks
  - Security vulnerability scanning
  - Test coverage analysis
  - Documentation completeness
  - Build validation

Phase 2: Intelligent Auto-Fixing (⚡)
  - Simple issue direct fixes
  - Complex issue agent delegation
  - Parallel fix execution
  - Re-validation after fixes

Phases Skipped:
  - Commit generation
  - Multi-agent review
  - PR creation
```

### Example Usage

```bash
# Command-based
/review --validate-only

# Conversation-based
"Check if my code passes quality gates"
"Validate and fix issues but don't commit"
"Make sure my changes are good quality"
```

### Expected Output

```yaml
Output Components:
  1. Initial Validation Report:
     Code Quality: ⚠️ 3 issues
       - 2 formatting issues
       - 1 unused import

     Security: ✅ Clean
       - No vulnerabilities

     Testing: ✅ Passed
       - Coverage: 87%

     Documentation: ⚠️ 1 issue
       - 1 missing docstring

  2. Auto-Fix Results:
     - Formatted 2 files
     - Removed unused import
     - Added missing docstring

  3. Final Validation:
     Code Quality: ✅ Clean
     Security: ✅ Clean
     Testing: ✅ Passed
     Documentation: ✅ Complete

  Status: ✅ All quality gates passing
  Ready to commit when you're ready

Time: ~5-10 minutes
```

---

## PR-Only Mode

### Overview

```yaml
PR-Only Mode:
  phases: [Multi-Agent Review, PR Creation]
  time: 10-15 minutes
  coverage: Review and PR only
  output: PR with review insights

When to Use:
  - Commits already created manually
  - Just need PR creation
  - Want review insights without re-validation
  - Already validated and fixed issues
  - Ready to ship existing commits

When NOT to Use:
  - No commits yet (use commit-only or full)
  - Need quality validation (use validate-only)
  - Need fixes (use full review)
```

### Workflow

```yaml
Phase 1: Verify Commits (✓)
  - Check commits exist
  - Analyze commit history
  - Extract PR context

Phase 2: Multi-Agent Review (🤖)
  - refactorer: Code quality review
  - security: Security review
  - qa: Test coverage review
  - implementer: Documentation review
  - Consolidated review summary

Phase 3: PR Creation (🚀)
  - Extract title from commits
  - Generate comprehensive description
  - Include review insights
  - Setup automation (labels, reviewers)
  - Archive specification

Phases Skipped:
  - Validation
  - Auto-fixing
  - Commit generation
```

### Example Usage

```bash
# Command-based
/review --pr-only

# Conversation-based
"Create PR from my existing commits"
"I already committed, just need the PR"
"Make a PR with review insights"
```

### Expected Output

```yaml
Output Components:
  1. Commit Analysis:
     - Found 3 commits:
       • "feat(auth): implement JWT generation"
       • "test(auth): add JWT tests"
       • "docs(auth): document JWT"

  2. Multi-Agent Review:
     - Code quality: ✅ Excellent
     - Security: ✅ Secure
     - Testing: ✅ Well-tested
     - Documentation: ✅ Complete

  3. PR Created:
     - PR #125: "feat: JWT Authentication"
     - URL: https://github.com/user/repo/pull/125
     - Labels: enhancement, security
     - Reviewers: @security-team
     - Specification: spec-feature-auth-001 archived

Time: ~10-15 minutes
```

---

## Deep Analysis Mode

### Overview

```yaml
Deep Analysis Mode:
  phases: [Comprehensive Validate, Extended Review]
  time: 20-30 minutes
  coverage: In-depth analysis and metrics
  output: Detailed quality report

When to Use:
  - Need comprehensive quality insights
  - Want to understand technical debt
  - Planning refactoring
  - Assessing code health
  - Before major release

When NOT to Use:
  - Just need quick check (use validate-only)
  - Ready to ship (use full review)
  - Simple changes (use quick mode)
```

### Workflow

```yaml
Phase 1: Comprehensive Validation (🔍)
  - All standard quality checks
  - Plus: Complexity analysis
  - Plus: Technical debt assessment
  - Plus: Performance profiling
  - Plus: Architecture health

Phase 2: Extended Multi-Agent Review (🤖)
  - All agents review (refactorer, security, qa, implementer, architect)
  - Plus: Detailed metrics collection
  - Plus: Historical comparison
  - Plus: Trend analysis
  - Plus: Actionable recommendations

Phase 3: Analysis Report Generation (📊)
  - Code quality trends
  - Security posture
  - Test coverage evolution
  - Documentation completeness
  - Architecture health score
  - Technical debt quantification
  - Refactoring opportunities
  - Performance bottlenecks

Phases Skipped:
  - Commit generation
  - PR creation
```

### Example Usage

```bash
# Command-based
/review --analysis

# Conversation-based
"Deep analysis of code quality"
"Comprehensive quality report"
"Assess codebase health"
```

### Expected Output

```yaml
Output Components:
  1. Quality Metrics:
     Code Quality:
       - Overall score: 8.5/10
       - Complexity: 3.2 avg (↓ from 3.8)
       - Duplication: 1.2% (↓ from 2.1%)
       - Maintainability: 85/100

     Security:
       - Security score: 9/10
       - Vulnerabilities: 0 critical, 1 low
       - Auth patterns: Excellent
       - Data protection: Strong

     Testing:
       - Coverage: 87% (↑ from 82%)
       - Test quality: 8/10
       - Edge cases: Well covered
       - Performance: No regressions

     Documentation:
       - Completeness: 92%
       - API docs: 100%
       - Code comments: 88%
       - Examples: 3 provided

  2. Trends:
     - Code quality improving ↑
     - Test coverage growing ↑
     - Complexity decreasing ↓
     - Tech debt reducing ↓

  3. Recommendations:
     Refactoring Opportunities:
       - Extract UserValidator class (medium priority)
       - Simplify authenticate() method (low priority)
       - Consider caching layer (enhancement)

     Performance Optimizations:
       - Add database query caching
       - Optimize token validation path

     Security Hardening:
       - Add rate limiting to auth endpoints
       - Implement request signing

     Technical Debt:
       - Total: ~3 days of work
       - High priority: 1 day
       - Medium: 1.5 days
       - Low: 0.5 days

Time: ~20-30 minutes
```

---

## Specification Archiving Mode

### Overview

```yaml
Specification Archiving Mode:
  phases: [Verify Completion, Move Spec, Generate Summary]
  time: 2-3 minutes
  coverage: Specification management
  output: Archived spec with completion summary

When to Use:
  - Specification work complete
  - All tasks and acceptance criteria met
  - PR merged (or ready to merge)
  - Want to archive completed work
  - Clean up active specifications

When NOT to Use:
  - Specification not complete
  - PR not created yet (use full review)
  - Still working on tasks
```

### Workflow

```yaml
Phase 1: Verify Completion (✓)
  - Check all tasks completed
  - Verify acceptance criteria met
  - Confirm quality gates passed
  - Check PR exists (if applicable)

Phase 2: Move Specification (📁)
  - From: .quaestor/specs/active/<spec-id>.md
  - To: .quaestor/specs/completed/<spec-id>.md
  - Update status → "completed"
  - Add completion_date
  - Link PR URL

Phase 3: Generate Archive Summary (📝)
  - What was delivered
  - Key decisions made
  - Lessons learned
  - Performance metrics
  - Completion evidence
```

### Example Usage

```bash
# Command-based
/review --archive-spec spec-feature-auth-001

# Conversation-based
"Archive completed specification spec-feature-auth-001"
"Move spec-feature-auth-001 to completed"
"Mark authentication spec as complete"
```

### Expected Output

```yaml
Output Components:
  1. Verification:
     ✅ All tasks completed (8/8)
     ✅ Acceptance criteria met (5/5)
     ✅ Quality gates passed
     ✅ PR exists (#123)

  2. Archive Action:
     Moved: spec-feature-auth-001.md
     From: .quaestor/specs/active/
     To: .quaestor/specs/completed/
     Status: completed
     Completion Date: 2025-10-19

  3. Completion Summary:
     Delivered:
       - JWT authentication with refresh tokens
       - Comprehensive test suite (87% coverage)
       - API documentation
       - Security review passed

     Key Decisions:
       - JWT over sessions for scalability
       - bcrypt cost factor 12 for security
       - Refresh token rotation every 7 days

     Lessons Learned:
       - Token expiry edge cases need careful testing
       - Rate limiting should be in initial design

     Metrics:
       - Timeline: 3 days (estimated: 5 days) ✅
       - Quality: All gates passed ✅
       - Tests: 58 tests, 87% coverage ✅
       - Security: 0 vulnerabilities ✅

     Links:
       - PR: #123
       - Commits: abc123, def456, ghi789

Time: ~2-3 minutes
```

---

## Mode Comparison Matrix

```yaml
Feature Comparison:

                    Full  Quick  Commit  Validate  PR  Analysis  Archive
Validation           ✅    ⚡     ⚡      ✅       ❌    ✅       ✅
Auto-Fixing          ✅    ⚡     ⚡      ✅       ❌    ❌       ❌
Commit Generation    ✅    ⚡     ✅      ❌       ❌    ❌       ❌
Multi-Agent Review   ✅    ⚡     ❌      ❌       ✅    ✅✅     ❌
PR Creation          ✅    ⚡     ❌      ❌       ✅    ❌       ❌
Deep Analysis        ❌    ❌     ❌      ❌       ❌    ✅       ❌
Spec Archiving       ✅    ❌     ❌      ❌       ✅    ❌       ✅

Legend:
  ✅ = Full feature
  ⚡ = Simplified version
  ✅✅ = Extended version
  ❌ = Not included

Time Comparison:

Mode          Time            Best For
────────────  ──────────────  ────────────────────────────
Full          15-30 min       Complete feature shipping
Quick         3-5 min         Small changes, hotfixes
Commit        5-10 min        Progress commits
Validate      5-10 min        Quality check before commit
PR            10-15 min       PR from existing commits
Analysis      20-30 min       Deep quality insights
Archive       2-3 min         Spec completion tracking
```

---

## Mode Selection Guidelines

### Decision Tree

```yaml
Choose Mode Based on Situation:

Do you have uncommitted changes?
  No → Do you want a PR?
    Yes → Use: pr-only
    No → Use: analysis (for insights)
  Yes → Are you ready to ship?
    Yes → Use: full (comprehensive review + PR)
    No → Do you want to commit?
      Yes → Use: commit-only (commits without PR)
      No → Do you need quality check?
        Yes → Use: validate-only (check + fix)
        No → Continue working

Is this a small change (<5 files)?
  Yes → Use: quick (fast review)
  No → Use: full (comprehensive review)

Do you need detailed metrics?
  Yes → Use: analysis (deep insights)
  No → Use: appropriate mode above

Is specification complete?
  Yes → Use: archive-spec (after PR merged)
  No → Continue implementation
```

### Situational Recommendations

```yaml
Situation → Recommended Mode:

"I finished the feature and want to ship"
  → full: Complete review, commits, PR

"Quick typo fix in docs"
  → quick: Fast review and simple PR

"I want to save progress but not done"
  → commit-only: Organized commits, no PR

"Is my code good quality?"
  → validate-only: Check and fix issues

"I already committed, need PR"
  → pr-only: Review and PR creation

"How healthy is this codebase?"
  → analysis: Comprehensive metrics

"Feature done, PR merged"
  → archive-spec: Move spec to completed/

"Working on experimental feature"
  → commit-only: Save progress commits

"About to start refactoring"
  → analysis: Understand current state

"Hotfix for production"
  → quick: Fast review and ship
```

---

## Combining Modes

### Sequential Mode Usage

```yaml
Common Workflows:

Development → Validation → Commit → Review → Ship:
  1. During development: validate-only (check quality)
  2. End of day: commit-only (save progress)
  3. Feature complete: full (review and PR)
  4. After merge: archive-spec (archive spec)

Before Refactoring → During → After:
  1. Before: analysis (understand current state)
  2. During: validate-only (ensure quality)
  3. After: full (review refactoring + PR)

Long Feature → Progress → Ship:
  1. Daily: commit-only (save progress)
  2. Weekly: validate-only (quality check)
  3. Done: full (comprehensive review + PR)
  4. Merged: archive-spec (archive spec)
```

---

*Comprehensive review mode documentation with clear guidelines for when to use each mode*
