---
allowed-tools: [Read, Edit, MultiEdit, Bash, Grep, Glob, TodoWrite, Task]
description: "Comprehensive review, validation, commit generation, and PR creation with multi-agent orchestration"
performance-profile: "complex"
complexity-threshold: 0.6
auto-activation: ["quality-validation", "commit-generation", "pr-creation", "final-review"]
intelligence-features: ["multi-agent-review", "auto-fixing", "smart-commits", "quality-analysis"]
agent-strategy:
  code_quality: refactorer
  security_review: security
  test_coverage: qa
  documentation: implementer
  final_check: [qa, security]
---

# /review - Comprehensive Review & Ship

## Purpose
Final quality validation, intelligent commit generation, and PR creation. Combines thorough code review, automated fixes, commit organization, and shipping preparation with multi-agent expertise.

## Usage
```
/review                    # Full review, fix issues, generate commits, create PR
/review --commit-only      # Generate commits from recent changes
/review --validate-only    # Run all quality checks and fix issues
/review --pr-only         # Create PR from existing commits
/review --analysis        # Deep code quality analysis
/review --quick           # Fast review for small changes
```

## Auto-Intelligence

### Multi-Mode Review
```yaml
Mode Detection:
  - No args → Full review pipeline
  - --commit-only → Smart commit generation
  - --validate-only → Quality fixing focus
  - --pr-only → PR creation from commits
  - --analysis → Deep quality insights
```

### Agent Orchestration
```yaml
Parallel Review:
  - refactorer: Code quality and style
  - security: Vulnerability scanning
  - qa: Test coverage and quality
  - implementer: Documentation completeness
  
Sequential Workflow:
  1. Validate: Run all quality checks
  2. Fix: Auto-fix all issues
  3. Commit: Generate organized commits
  4. Review: Final multi-agent review
  5. Ship: Create PR with insights
```

## Workflow: Validate → Fix → Commit → Review → Ship

### Phase 1: Comprehensive Validation 🔍
**Multi-Domain Quality Checks:**
```yaml
Parallel Validation (All Agents):
  Code Quality:
    - Linting: ruff, eslint, clippy
    - Formatting: prettier, rustfmt
    - Complexity: cyclomatic, cognitive
    - Patterns: best practices compliance
    
  Security:
    - Vulnerability scan: known CVEs
    - Input validation: sanitization
    - Auth patterns: secure flows
    - Secrets: no hardcoded keys
    
  Testing:
    - Coverage: minimum thresholds
    - Test quality: assertions, mocks
    - Edge cases: boundary testing
    - Performance: no regressions
    
  Documentation:
    - API docs: completeness
    - Code comments: clarity
    - README: up to date
    - Examples: working code
```

**Quality Gate Requirements:**
```yaml
Must Pass:
  - ✅ Zero linting errors
  - ✅ All tests passing
  - ✅ Security scan clean
  - ✅ Type checking valid
  - ✅ Build successful
  
Should Pass:
  - ⚠️ Test coverage >80%
  - ⚠️ Documentation complete
  - ⚠️ No TODOs in critical paths
```

### Phase 2: Intelligent Auto-Fixing ⚡
**Agent-Driven Fixes:**
```yaml
Fix Strategy:
  Simple Issues (Direct Fix):
    - Formatting: auto-format all files
    - Import sorting: organize imports
    - Trailing spaces: clean up
    - Simple type annotations: add obvious types
    
  Complex Issues (Agent Delegation):
    - Test failures → qa agent
    - Security vulnerabilities → security agent
    - Performance issues → implementer agent
    - Documentation gaps → implementer agent
    
  Parallel Execution:
    - Spawn multiple agents for different domains
    - Coordinate fixes to avoid conflicts
    - Verify fixes don't break other areas
```

### Phase 3: Smart Commit Generation 📝
**Intelligent Commit Organization:**
```yaml
Change Analysis:
  - Group: related changes by module/feature
  - Classify: feat|fix|docs|refactor|test|perf
  - Extract: scope from file paths
  - Generate: conventional commit messages

Commit Strategy:
  Atomic Commits:
    - One logical change per commit
    - Include tests with implementation
    - Keep refactoring separate
    
  Message Generation:
    Template: "type(scope): description"
    
    Examples:
    - "feat(auth): implement JWT refresh tokens"
    - "fix(api): handle null response in user endpoint"
    - "test(auth): add coverage for edge cases"
    - "docs(api): update OpenAPI specifications"

TODO Integration:
  - Link commits to completed TODOs
  - Update specification status
  - Track completion evidence
```

### Phase 4: Multi-Agent Review 🤖
**Comprehensive Code Review:**
```yaml
Review Aspects:
  Code Quality (refactorer):
    - Readability and clarity
    - DRY principle compliance
    - SOLID principles
    - Design patterns usage
    
  Security (security):
    - Input validation
    - Authentication flows
    - Data exposure risks
    - Dependency vulnerabilities
    
  Testing (qa):
    - Test coverage adequacy
    - Edge case handling
    - Mock appropriateness
    - Performance benchmarks
    
  Architecture (architect):
    - Component boundaries
    - Dependency directions
    - Abstraction levels
    - Future extensibility

Review Output:
  📊 Review Summary
  
  ✅ Strengths:
  • Clean architecture in auth module
  • Comprehensive test coverage (87%)
  • Good error handling patterns
  
  ⚠️ Suggestions:
  • Consider caching in user service
  • Add rate limiting to API endpoints
  • Refactor large processor function
  
  🚨 Required Fixes:
  • None - all critical issues resolved
```

### Phase 5: PR Creation & Shipping 🚀
**Intelligent PR Assembly:**
```yaml
PR Content Generation:
  Title: 
    - Extract from specifications or changes
    - Follow team conventions
    - Include ticket numbers if found
    
  Description:
    ## Summary
    [Auto-generated from specifications/changes]
    
    ## Changes
    [Organized by type with commit links]
    
    ## Quality Report
    - Tests: ✅ All passing (count)
    - Coverage: 📊 87% (+3%)
    - Security: 🔒 No vulnerabilities
    - Performance: ⚡ No regressions
    
    ## Review Insights
    [Multi-agent review summary]
    
    ## Checklist
    - [x] Tests added/updated
    - [x] Documentation updated
    - [x] Security reviewed
    - [x] No breaking changes

Automation:
  - Labels: auto-detect from changes
  - Reviewers: from CODEOWNERS + history
  - Projects: link to specifications
  - CI/CD: trigger workflows
```

## Advanced Features

### Deep Analysis Mode (--analysis)
```yaml
Comprehensive Metrics:
  - Code complexity trends
  - Technical debt quantification
  - Performance bottlenecks
  - Security risk assessment
  - Architecture health score
  
Actionable Insights:
  - Refactoring opportunities
  - Performance optimizations
  - Security hardening needs
  - Test coverage gaps
```

### Quick Review Mode (--quick)
```yaml
For Small Changes:
  - Basic validation only
  - Fast commit generation
  - Simplified PR description
  - Single agent review
  Time: ~5 minutes
```

### Commit-Only Mode (--commit-only)
```yaml
Smart Commits:
  - Analyze uncommitted changes
  - Generate atomic commits
  - Follow conventions
  - Update tracking
  No PR creation
```

## Integration with Workflow

### From Other Commands
```yaml
Task → Review:
  - "Implementation complete"
  - All changes ready for review
  
Debug → Review:
  - "All issues fixed"
  - Ready for final validation
  
Plan → Review:
  - "Project phase complete"
  - Time to ship
```

### Handoff Context
```yaml
Context Preservation:
  - Task completions
  - Fixed issues
  - Architecture decisions
  - Performance metrics
```

## Success Criteria
- ✅ All quality gates passed
- ✅ Issues automatically fixed
- ✅ Commits properly organized
- ✅ Multi-agent review complete
- ✅ PR created with rich context
- ✅ Ready for team review

---
*Comprehensive review pipeline with multi-agent validation, auto-fixing, and intelligent shipping*