---
name: Review and Ship
description: Comprehensive review, validation, commit generation, and PR creation with multi-agent orchestration. Use after implementation to validate quality and ship changes.
allowed-tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, TodoWrite, Task]
---

# Review and Ship

I help you perform comprehensive code review, automatically fix issues, generate organized commits, and create pull requests with rich context and multi-agent validation.

## When to Use Me

- User says "review my changes", "create a PR", "ship this feature"
- After completing implementation (implementation-workflow finished)
- Need comprehensive quality validation
- Want intelligent commit generation from changes
- Ready to create PR with rich context
- Need multi-agent code review

## Supporting Files

This skill uses several supporting files for detailed workflows:

- **@WORKFLOW.md** - 5-phase review process (Validate → Fix → Commit → Review → Ship)
- **@AGENTS.md** - Multi-agent review strategies and coordination
- **@MODES.md** - Different review modes (full, quick, commit-only, validate-only, PR-only, analysis)
- **@COMMITS.md** - Intelligent commit generation and organization strategies
- **@PR.md** - PR creation with rich context and automation

## My Process

I follow a structured 5-phase workflow to ensure quality and completeness:

### Phase 1: Comprehensive Validation 🔍

**Multi-Domain Quality Checks:**
- **Code Quality**: Linting, formatting, complexity, patterns
- **Security**: Vulnerability scan, input validation, auth patterns, secrets check
- **Testing**: Coverage, test quality, edge cases, performance
- **Documentation**: API docs, code comments, README, examples

**Quality Gate Requirements:**
- ✅ Zero linting errors
- ✅ All tests passing
- ✅ Security scan clean
- ✅ Type checking valid
- ✅ Build successful

**See @WORKFLOW.md Phase 1 for complete validation process**

### Phase 2: Intelligent Auto-Fixing ⚡

**Agent-Driven Fixes:**
- **Simple Issues**: Formatting, import sorting, trailing spaces (direct fix)
- **Complex Issues**: Test failures, security vulnerabilities, performance (agent delegation)
- **Parallel Execution**: Multiple agents for different domains

**Fix Strategy:**
- Use qa agent for test failures
- Use security agent for vulnerabilities
- Use implementer agent for documentation gaps
- Use refactorer agent for code quality issues

**See @AGENTS.md for agent coordination strategies**

### Phase 3: Smart Commit Generation 📝

**Intelligent Commit Organization:**
- Group related changes by module/feature
- Classify as feat|fix|docs|refactor|test|perf
- Extract scope from file paths
- Generate conventional commit messages

**Commit Strategy:**
- One logical change per commit (atomic)
- Include tests with implementation
- Keep refactoring separate
- Link to specifications

**See @COMMITS.md for commit generation details**

### Phase 4: Multi-Agent Review 🤖

**Comprehensive Code Review:**
- **refactorer agent**: Code quality, readability, SOLID principles
- **security agent**: Input validation, auth flows, data exposure
- **qa agent**: Test coverage, edge cases, mocks
- **architect agent** (if needed): Component boundaries, dependencies

**Review Output:**
- ✅ Strengths identified
- ⚠️ Suggestions provided
- 🚨 Required fixes (if any)

**See @AGENTS.md for multi-agent review patterns**

### Phase 5: PR Creation & Shipping 🚀

**Intelligent PR Assembly:**
- **Title**: From specifications or changes
- **Description**: Summary, changes, quality report, review insights, checklist
- **Automation**: Labels, reviewers, projects, CI/CD triggers

**PR Content:**
- Quality metrics (tests, coverage, security)
- Multi-agent review summary
- Organized changes by type
- Links to commits and specifications

**See @PR.md for PR creation details**

## Review Modes

**I support multiple review modes:**

**Full Review** (default):
```
"Review my changes"
# Runs all 5 phases: Validate → Fix → Commit → Review → Ship
```

**Quick Review**:
```
"Quick review for small changes"
# Basic validation, fast commits, simplified PR
```

**Commit-Only**:
```
"Generate commits from my changes"
# Smart commit generation without PR creation
```

**Validate-Only**:
```
"Validate and fix quality issues"
# Run quality checks and auto-fix issues
```

**PR-Only**:
```
"Create PR from existing commits"
# Skip validation/commits, just create PR
```

**Deep Analysis**:
```
"Analyze code quality"
# Comprehensive metrics and insights
```

**See @MODES.md for complete mode details**

## Auto-Intelligence

### Mode Detection
- No args → Full review pipeline
- Detect based on context and user intent
- Optimize for common workflows

### Agent Orchestration
**Parallel Review:**
- refactorer: Code quality and style
- security: Vulnerability scanning
- qa: Test coverage and quality
- implementer: Documentation completeness

**Sequential Workflow:**
1. Validate: Run all quality checks
2. Fix: Auto-fix all issues
3. Commit: Generate organized commits
4. Review: Final multi-agent review
5. Ship: Create PR with insights

**See @AGENTS.md for orchestration details**

## Specification Integration

**Pre-Review:**
- Check `.quaestor/specs/active/` for in-progress work
- Verify all tasks completed
- Ensure acceptance criteria met

**Post-Review:**
- Update specification status → completed
- Move spec from active/ → completed/
- Include spec summary in PR
- Link PR to specification

**Archive Specification:**
```
"Archive completed specification spec-feature-001"
# Moves spec to completed/, updates status, generates summary
```

## Quality Gates

**Must Pass Before Shipping:**
- ✅ All tests passing
- ✅ Zero linting errors
- ✅ Security scan clean
- ✅ Type checking valid
- ✅ Build successful

**Should Pass (Warnings):**
- ⚠️ Test coverage >80%
- ⚠️ Documentation complete
- ⚠️ No TODOs in critical paths

**See @WORKFLOW.md for language-specific quality gates**

## Agent Coordination

**I coordinate with workflow-coordinator first!**

The workflow-coordinator validates:
- Implementation phase completed
- All spec tasks done
- Tests passing
- Ready for review phase

Then I coordinate:
- **refactorer** - Code quality and style review
- **security** - Security vulnerability scanning
- **qa** - Test coverage and quality validation
- **implementer** - Documentation completeness check
- **architect** (if needed) - Architecture review

**See @AGENTS.md for complete agent coordination patterns**

## Success Criteria

- ✅ workflow-coordinator validates implementation complete
- ✅ All quality gates passed (linting, tests, security, types, build)
- ✅ Issues automatically fixed or documented
- ✅ Commits properly organized and generated
- ✅ Multi-agent review complete with insights
- ✅ PR created with rich context
- ✅ Specification updated and archived (if complete)
- ✅ Ready for team review

## Final Response

When review is complete:
```
✅ Review Complete

Quality Gates: All passed
- Tests: 42 passed, 0 failed
- Linting: Clean
- Security: No vulnerabilities
- Type checking: Valid
- Build: Successful

Commits: 3 commits created
- feat(auth): implement JWT refresh tokens
- test(auth): add coverage for edge cases
- docs(auth): update API documentation

PR: Created #123
Title: "feat: User Authentication System"
URL: https://github.com/user/repo/pull/123

Specification: spec-feature-001 moved to completed/

Ready for team review!
```

**See @WORKFLOW.md for complete workflow and @PR.md for PR details**

---

*Comprehensive review with multi-agent validation, auto-fixing, intelligent commits, and rich PR creation*
