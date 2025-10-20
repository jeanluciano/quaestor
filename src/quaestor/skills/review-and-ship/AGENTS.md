# Multi-Agent Review Strategies

This file describes how to coordinate multiple specialized agents for comprehensive code review and quality assurance.

## Agent Overview

### Available Agents for Review

```yaml
workflow-coordinator:
  role: "Pre-review validation and workflow state management"
  use_first: true
  validates:
    - Implementation phase completed
    - All specification tasks done
    - Tests passing before review
    - Ready for review/completion phase
  coordinates: "Transition from implementation to review"
  criticality: MANDATORY

refactorer:
  role: "Code quality and style review"
  specializes:
    - Code readability and clarity
    - SOLID principles compliance
    - Design pattern usage
    - Code smell detection
    - Complexity reduction
  focus: "Making code maintainable and clean"

security:
  role: "Security vulnerability review"
  specializes:
    - Authentication/authorization review
    - Input validation checking
    - Vulnerability scanning
    - Encryption implementation
    - Security best practices
  focus: "Making code secure"

qa:
  role: "Test quality and coverage review"
  specializes:
    - Test coverage analysis
    - Test quality assessment
    - Edge case identification
    - Mock appropriateness
    - Performance testing
  focus: "Making code well-tested"

implementer:
  role: "Documentation and feature completeness"
  specializes:
    - Documentation completeness
    - API documentation review
    - Code comment quality
    - Example code validation
    - Feature implementation gaps
  focus: "Making code documented and complete"

architect:
  role: "Architecture and design review"
  specializes:
    - Component boundary validation
    - Dependency direction checking
    - Abstraction level assessment
    - Scalability evaluation
    - Design pattern application
  focus: "Making code architecturally sound"
  when_needed: "Major changes, new components, refactoring"
```

---

## Agent Selection Rules

### MANDATORY: Workflow Coordinator First

**Always Start with workflow-coordinator:**

```yaml
Pre-Review Protocol:
  1. ALWAYS use workflow-coordinator agent first
  2. workflow-coordinator validates:
     - Implementation phase is complete
     - All tasks in specification are done
     - Tests are passing
     - No blocking issues remain
  3. If validation fails:
     - Do NOT proceed to review
     - Report incomplete work to user
     - Guide user to complete implementation
  4. If validation passes:
     - Proceed to multi-agent review

NEVER skip workflow-coordinator validation!
```

### Task-Based Agent Selection

**Use this matrix to determine which agents to invoke:**

```yaml
Authentication/Authorization Feature:
  agents:
    - security: Security requirements and review (primary)
    - refactorer: Code quality and structure
    - qa: Security and integration testing
    - implementer: Documentation completeness
  reason: Security-critical feature needs security focus

API Development:
  agents:
    - refactorer: Code structure and patterns (primary)
    - implementer: API documentation
    - qa: API testing and validation
  reason: API quality and documentation critical

Performance Optimization:
  agents:
    - refactorer: Code efficiency review (primary)
    - qa: Performance testing validation
    - architect: Architecture implications (if major)
  reason: Performance changes need quality + testing

Security Fix:
  agents:
    - security: Security fix validation (primary)
    - qa: Security test coverage
    - implementer: Security documentation
  reason: Security fixes need security expert review

Refactoring:
  agents:
    - refactorer: Code quality improvements (primary)
    - architect: Design pattern compliance (if structural)
    - qa: No regression validation
  reason: Refactoring needs quality focus + safety

Bug Fix:
  agents:
    - refactorer: Code quality of fix (primary)
    - qa: Regression test addition
  reason: Simple bug fixes need basic review

Documentation Update:
  agents:
    - implementer: Documentation quality (primary)
  reason: Documentation changes need content review only

New Feature (Standard):
  agents:
    - refactorer: Code quality and structure
    - security: Security implications
    - qa: Test coverage and quality
    - implementer: Documentation completeness
  reason: Standard features need comprehensive review

Major System Change:
  agents:
    - architect: Architecture validation (primary)
    - refactorer: Code quality review
    - security: Security implications
    - qa: Comprehensive testing
    - implementer: Documentation update
  reason: Major changes need all-hands review
```

---

## Agent Coordination Patterns

### Pattern 1: Parallel Review (Standard)

**When to Use:** Most feature reviews where agents can work independently.

```yaml
Parallel Review Pattern:
  Spawn 4 agents simultaneously:
    - refactorer: Review code quality
    - security: Review security
    - qa: Review testing
    - implementer: Review documentation

  Each agent focuses on their domain independently

  Wait for all agents to complete

  Consolidate results into unified review summary

Advantages:
  - Fast (all reviews happen simultaneously)
  - Comprehensive (all domains covered)
  - Independent (no agent blocking others)

Time: ~5-10 minutes
```

**Example: New Feature Review**

```yaml
Review Authentication Feature:

Spawn in Parallel:
  Use the refactorer agent to:
    - Review code structure and organization
    - Check SOLID principles compliance
    - Identify code smells
    - Suggest improvements

  Use the security agent to:
    - Review authentication logic
    - Check password hashing
    - Validate token handling
    - Identify security risks

  Use the qa agent to:
    - Analyze test coverage
    - Check edge case handling
    - Validate test quality
    - Identify missing tests

  Use the implementer agent to:
    - Review API documentation
    - Check code comments
    - Validate examples
    - Identify doc gaps

Wait for All Completions

Consolidate:
  - Combine all agent findings
  - Identify common themes
  - Prioritize issues
  - Generate unified review summary
```

### Pattern 2: Sequential Review with Validation

**When to Use:** Critical features where one review informs the next.

```yaml
Sequential Review Pattern:
  Step 1: First agent reviews
    → Wait for completion
    → Analyze findings

  Step 2: Second agent reviews (builds on first)
    → Wait for completion
    → Analyze findings

  Step 3: Third agent reviews (builds on previous)
    → Wait for completion
    → Final analysis

Advantages:
  - Each review informs the next
  - Can adjust focus based on findings
  - Deeper analysis possible

Time: ~15-20 minutes
```

**Example: Security-Critical Feature Review**

```yaml
Review Security Feature:

Step 1: Use the security agent to:
  - Deep security analysis
  - Identify vulnerabilities
  - Define security requirements
  - Assess risk level

  Output: Security requirements document + vulnerability report

Step 2: Use the refactorer agent to:
  - Review code with security context
  - Check if vulnerabilities addressed
  - Ensure secure coding patterns
  - Validate security requirements met

  Context: Security agent's findings
  Output: Code quality + security compliance report

Step 3: Use the qa agent to:
  - Review tests with security focus
  - Ensure vulnerabilities tested
  - Check security edge cases
  - Validate security test coverage

  Context: Security requirements + code review
  Output: Test coverage + security testing report

Step 4: Use the implementer agent to:
  - Document security implementation
  - Document security tests
  - Add security examples
  - Document threat model

  Context: All previous reviews
  Output: Documentation completeness report
```

### Pattern 3: Iterative Review with Fixing

**When to Use:** When issues are expected and fixes needed during review.

```yaml
Iterative Review Pattern:
  Loop:
    1. Agent reviews and identifies issues
    2. Same agent (or another) fixes issues
    3. Re-validate fixed issues
    4. If new issues: repeat
    5. If clean: proceed to next agent

Advantages:
  - Issues fixed during review
  - Continuous improvement
  - Final review is clean

Time: ~20-30 minutes (depends on issues)
```

**Example: Refactoring Review with Fixes**

```yaml
Review Refactored Code:

Iteration 1 - Code Quality:
  Use the refactorer agent to:
    - Review code structure
    - Identify 3 issues:
      • Function too long (85 lines)
      • Duplicate code in 2 places
      • Complex nested conditionals

  Use the refactorer agent to:
    - Break long function into 4 smaller ones
    - Extract duplicate code to shared utility
    - Flatten nested conditionals

  Validate: All issues fixed ✅

Iteration 2 - Testing:
  Use the qa agent to:
    - Review test coverage
    - Identify 2 issues:
      • New functions not tested
      • Edge case missing

  Use the qa agent to:
    - Add tests for new functions
    - Add edge case test

  Validate: Coverage now 89% ✅

Iteration 3 - Documentation:
  Use the implementer agent to:
    - Review documentation
    - Identify 1 issue:
      • Refactored functions missing docstrings

  Use the implementer agent to:
    - Add docstrings to all new functions
    - Update examples

  Validate: All documented ✅

Final: All issues addressed, ready to ship
```

### Pattern 4: Focused Review (Subset)

**When to Use:** Small changes or specific review needs.

```yaml
Focused Review Pattern:
  Select 1-2 agents based on change type:
    - Bug fix → refactorer + qa
    - Docs update → implementer only
    - Security fix → security + qa
    - Performance → refactorer + qa

  Only review relevant aspects

  Skip unnecessary reviews

Advantages:
  - Fast (minimal agents)
  - Focused (relevant only)
  - Efficient (no wasted effort)

Time: ~3-5 minutes
```

**Example: Bug Fix Review**

```yaml
Review Bug Fix:

Use the refactorer agent to:
  - Review fix code quality
  - Check if fix is clean
  - Ensure no new issues introduced
  - Validate fix approach

Use the qa agent to:
  - Verify regression test added
  - Check test quality
  - Ensure bug scenario covered
  - Validate no other tests broken

Skip:
  - security (not security-related)
  - implementer (no doc changes)
  - architect (no design changes)

Result: Fast, focused review in ~5 minutes
```

---

## Review Aspect Coordination

### Code Quality Review (refactorer)

**Review Focus:**

```yaml
Readability:
  - Variable/function names clear
  - Code organization logical
  - Comments appropriate
  - Formatting consistent

Design:
  - DRY principle applied
  - SOLID principles followed
  - Abstractions appropriate
  - Patterns used correctly

Maintainability:
  - Functions focused and small
  - Complexity low
  - Dependencies minimal
  - No code smells

Consistency:
  - Follows codebase conventions
  - Naming patterns consistent
  - Error handling uniform
  - Style guide compliance
```

**Review Output Format:**

```yaml
Code Quality Review by refactorer:

✅ Strengths:
  • Clean separation of concerns in auth module
  • Consistent error handling with custom exceptions
  • Good use of dependency injection pattern
  • Function sizes appropriate (avg 25 lines)

⚠️ Suggestions:
  • Consider extracting UserValidator to separate class
  • Could simplify nested conditionals in authenticate()
  • Opportunity to cache user lookups for performance
  • Some variable names could be more descriptive (e.g., 'data' → 'user_data')

🚨 Required Fixes:
  • None

Complexity Metrics:
  • Average cyclomatic complexity: 3.2 (target: <5) ✅
  • Max function length: 42 lines (target: <50) ✅
  • Duplicate code: 0.8% (target: <2%) ✅
```

### Security Review (security)

**Review Focus:**

```yaml
Authentication:
  - Password storage secure (hashing)
  - Token validation robust
  - Session management safe
  - MFA properly implemented

Authorization:
  - Permission checks present
  - RBAC correctly implemented
  - Resource ownership validated
  - No privilege escalation

Input Validation:
  - All inputs sanitized
  - SQL injection prevented
  - XSS prevented
  - CSRF protection active

Data Protection:
  - Sensitive data encrypted
  - Secure communication (HTTPS)
  - No secrets in code
  - PII handling compliant

Vulnerabilities:
  - No known CVEs in deps
  - No hardcoded credentials
  - No insecure algorithms
  - No information leakage
```

**Review Output Format:**

```yaml
Security Review by security:

✅ Strengths:
  • Password hashing uses bcrypt with cost 12 (recommended)
  • JWT validation includes expiry, signature, and issuer checks
  • Input sanitization comprehensive across all endpoints
  • No hardcoded secrets or credentials found

⚠️ Suggestions:
  • Consider adding rate limiting to login endpoint (prevent brute force)
  • Add logging for failed authentication attempts (security monitoring)
  • Consider implementing password complexity requirements
  • Could add request signing for critical API operations

🚨 Required Fixes:
  • None - all critical security measures in place

Vulnerability Scan:
  • Dependencies: 0 critical, 0 high, 1 low (acceptable)
  • Code: No security vulnerabilities detected
  • Secrets: No hardcoded secrets found
```

### Test Coverage Review (qa)

**Review Focus:**

```yaml
Coverage Metrics:
  - Overall coverage ≥80%
  - Critical paths 100%
  - Edge cases covered
  - Error paths tested

Test Quality:
  - Assertions meaningful
  - Test names descriptive
  - Tests isolated
  - No flaky tests
  - Mocks appropriate

Test Types:
  - Unit tests for logic
  - Integration for flows
  - E2E for critical paths
  - Performance if needed

Test Organization:
  - Clear structure
  - Good fixtures
  - Helper functions
  - Easy to maintain
```

**Review Output Format:**

```yaml
Test Coverage Review by qa:

✅ Strengths:
  • Coverage at 87% (target: 80%) - exceeds requirement ✅
  • Critical auth paths 100% covered
  • Good edge case coverage (token expiry, invalid tokens, etc.)
  • Test names clear and descriptive
  • Tests properly isolated with fixtures

⚠️ Suggestions:
  • Could add tests for token refresh edge cases (concurrent requests)
  • Consider adding load tests for auth endpoints (performance validation)
  • Some assertions could be more specific (e.g., check exact error message)
  • Could add property-based tests for token generation

🚨 Required Fixes:
  • None

Coverage Breakdown:
  • src/auth/jwt.py: 92% (23/25 lines)
  • src/auth/service.py: 85% (34/40 lines)
  • src/auth/validators.py: 100% (15/15 lines)

Test Counts:
  • Unit tests: 38 passed
  • Integration tests: 12 passed
  • Security tests: 8 passed
  • Total: 58 tests, 0 failures
```

### Documentation Review (implementer)

**Review Focus:**

```yaml
API Documentation:
  - All endpoints documented
  - Parameters described
  - Responses documented
  - Examples provided

Code Documentation:
  - Functions have docstrings
  - Complex logic explained
  - Public APIs documented
  - Types annotated

Project Documentation:
  - README up to date
  - Setup instructions clear
  - Architecture documented
  - Examples working

Completeness:
  - No missing docs
  - Accurate and current
  - Easy to understand
  - Maintained with code
```

**Review Output Format:**

```yaml
Documentation Review by implementer:

✅ Strengths:
  • API documentation complete with OpenAPI specs
  • All public functions have clear docstrings
  • README updated with authentication section
  • Examples provided and tested

⚠️ Suggestions:
  • Could add more code examples for token refresh flow
  • Consider adding architecture diagram for auth flow
  • Some docstrings could include example usage
  • Could document error codes more explicitly

🚨 Required Fixes:
  • None

Documentation Coverage:
  • Public functions: 100% (all documented)
  • API endpoints: 100% (all in OpenAPI)
  • README: Up to date ✅
  • Examples: 3 working examples included
```

### Architecture Review (architect)

**When to Invoke:**

```yaml
Trigger Architecture Review:
  - New system components added
  - Major refactoring done
  - Cross-module dependencies changed
  - Database schema modified
  - API contract changes
  - Performance-critical features

Skip for:
  - Small bug fixes
  - Documentation updates
  - Minor refactoring
  - Single-file changes
```

**Review Focus:**

```yaml
Component Boundaries:
  - Clear separation of concerns
  - Dependencies flow correctly
  - No circular dependencies
  - Proper abstraction layers

Scalability:
  - Horizontal scaling supported
  - No obvious bottlenecks
  - Database queries optimized
  - Caching appropriate

Maintainability:
  - Easy to extend
  - Easy to test
  - Low coupling
  - High cohesion

Future-Proofing:
  - Flexible design
  - Easy to modify
  - Minimal technical debt
  - Clear upgrade path
```

**Review Output Format:**

```yaml
Architecture Review by architect:

✅ Strengths:
  • Clean layered architecture maintained
  • Auth module well-isolated from other concerns
  • JWT implementation abstracted (easy to swap if needed)
  • Good use of dependency injection for testability

⚠️ Suggestions:
  • Consider event-driven approach for audit logging (scalability)
  • Could abstract session storage interface (flexibility)
  • May want to add caching layer for user lookups (performance)
  • Consider adding rate limiting at architecture level

🚨 Required Fixes:
  • None

Architecture Health:
  • Coupling: Low ✅
  • Cohesion: High ✅
  • Complexity: Manageable ✅
  • Scalability: Good ✅
  • Technical debt: Low ✅
```

---

## Review Consolidation

### Collecting Agent Reviews

**Consolidation Strategy:**

```yaml
Step 1: Collect All Reviews
  - Wait for all agents to complete
  - Gather all review outputs
  - Organize by agent

Step 2: Identify Common Themes
  - Issues mentioned by multiple agents
  - Conflicting suggestions (rare)
  - Critical vs nice-to-have

Step 3: Prioritize Findings
  - 🚨 Required Fixes (blocking)
  - ⚠️ Suggestions (improvements)
  - ✅ Strengths (positive feedback)

Step 4: Generate Unified Summary
  - Overall assessment
  - Critical issues (if any)
  - Key improvements suggested
  - Ready-to-ship decision
```

### Unified Review Summary Template

```yaml
📊 Multi-Agent Review Summary

Code Quality (refactorer): ✅ EXCELLENT
  Strengths: [Top 3 strengths]
  Suggestions: [Top 2-3 suggestions]

Security (security): ✅ SECURE
  Strengths: [Top 3 strengths]
  Suggestions: [Top 2-3 suggestions]

Testing (qa): ✅ WELL-TESTED
  Strengths: [Coverage metrics + top strengths]
  Suggestions: [Top 2-3 suggestions]

Documentation (implementer): ✅ COMPLETE
  Strengths: [Documentation coverage]
  Suggestions: [Top 2-3 suggestions]

Architecture (architect): ✅ SOLID (if included)
  Strengths: [Architecture assessment]
  Suggestions: [Top 2-3 suggestions]

Overall Assessment: ✅ READY TO SHIP
  Critical Issues: [Count] (must be 0 to ship)
  Suggestions: [Count] (nice-to-have improvements)
  Quality Score: [Excellent/Good/Needs Work]

Recommendation: [Ship / Fix Critical Issues / Consider Suggestions]
```

### Example Consolidated Review

```yaml
📊 Multi-Agent Review Summary

Code Quality (refactorer): ✅ EXCELLENT
  Strengths:
    • Clean architecture with excellent separation of concerns
    • Consistent code style and naming conventions
    • Low complexity (avg 3.2, target <5)

  Suggestions:
    • Consider extracting UserValidator class
    • Simplify nested conditionals in authenticate()

Security (security): ✅ SECURE
  Strengths:
    • Robust bcrypt password hashing (cost 12)
    • Comprehensive JWT validation
    • No hardcoded secrets or credentials

  Suggestions:
    • Add rate limiting to prevent brute force
    • Add security event logging

Testing (qa): ✅ WELL-TESTED
  Strengths:
    • 87% coverage (exceeds 80% target)
    • All critical paths fully tested
    • Good edge case coverage

  Suggestions:
    • Add tests for concurrent token refresh
    • Consider load testing auth endpoints

Documentation (implementer): ✅ COMPLETE
  Strengths:
    • All APIs documented with OpenAPI
    • Clear docstrings on all functions
    • README updated with examples

  Suggestions:
    • Add architecture diagram
    • More code examples for token flow

Overall Assessment: ✅ READY TO SHIP
  Critical Issues: 0
  Suggestions: 8 nice-to-have improvements
  Quality Score: Excellent

Recommendation: SHIP - All quality gates passed. Consider addressing suggestions in future iteration.
```

---

## Agent Communication Best Practices

### Clear Context Handoff

**When Chaining Agents:**

```yaml
Good Context Handoff:
  Use the security agent to review authentication
    → Output: Security review with 3 suggestions

  Use the implementer agent to document security measures
    Context: Security review identified token expiry, hashing, validation
    Task: Document these security features in API docs

Bad Context Handoff:
  Use the security agent to review authentication
  Use the implementer agent to add docs
    Problem: implementer doesn't know what security found
```

### Explicit Review Boundaries

**Define What Each Agent Reviews:**

```yaml
Good Boundary Definition:
  Use the refactorer agent to review code quality:
    - Focus: Code structure, naming, patterns
    - Scope: src/auth/ directory only
    - Exclude: Security aspects (security agent will cover)

Bad Boundary Definition:
  Use the refactorer agent to review the code
    Problem: Unclear scope and focus
```

### Validation After Each Review

**Always Validate Agent Output:**

```yaml
Review Validation:
  After agent completes:
    1. Check review is comprehensive
    2. Verify findings are actionable
    3. Ensure no critical issues missed
    4. Validate suggestions are reasonable

  If issues:
    - Re-prompt agent with clarifications
    - Use different agent for second opinion
    - Escalate to user if uncertain
```

---

## Quality Checkpoint Triggers

### Automatic Agent Invocation

**Based on Code Metrics:**

```yaml
High Complexity Detected:
  If cyclomatic complexity >10:
    → Use the refactorer agent to:
      - Analyze complex functions
      - Suggest simplifications
      - Break into smaller functions

Security Patterns Found:
  If authentication/encryption code:
    → Use the security agent to:
      - Review security implementation
      - Validate secure patterns
      - Check for vulnerabilities

Low Test Coverage:
  If coverage <80%:
    → Use the qa agent to:
      - Identify untested code
      - Suggest test cases
      - Improve coverage

Missing Documentation:
  If docstring coverage <90%:
    → Use the implementer agent to:
      - Identify missing docs
      - Generate docstrings
      - Add examples

Circular Dependencies:
  If circular deps detected:
    → Use the architect agent to:
      - Analyze dependency structure
      - Suggest refactoring
      - Break circular references
```

---

## Multi-Agent Review Best Practices

### DO:

```yaml
✅ Best Practices:
  - ALWAYS use workflow-coordinator first
  - Use parallel reviews for speed when possible
  - Provide clear context to each agent
  - Validate each agent's output
  - Consolidate findings into unified summary
  - Focus agents on their expertise areas
  - Skip unnecessary agents for simple changes
  - Use sequential review for critical features
```

### DON'T:

```yaml
❌ Anti-Patterns:
  - Skip workflow-coordinator validation
  - Use all agents for every review (overkill)
  - Let agents review outside their expertise
  - Forget to consolidate findings
  - Accept reviews without validation
  - Chain agents without clear handoff
  - Run sequential when parallel would work
  - Use parallel when sequential needed
```

---

*Comprehensive multi-agent review strategies for quality assurance and code validation*
