---
allowed-tools: all
description: Verify code quality, run tests, and ensure production readiness
---

<!-- META:command:check -->
<!-- META:version:2.0 -->
<!-- META:ai-optimized:true -->

<!-- SECTION:check:critical-requirement:START -->
# 🚨🚨🚨 CRITICAL REQUIREMENT: FIX ALL ERRORS! 🚨🚨🚨

**THIS IS NOT A REPORTING TASK - THIS IS A FIXING TASK!**
<!-- SECTION:check:critical-requirement:END -->

<!-- SECTION:check:mandatory-actions:START -->
## MANDATORY ACTIONS

<!-- DATA:check-requirements:START -->
```yaml
when_running_check:
  1_identify: "all errors, warnings, and issues"
  2_fix: "EVERY SINGLE ONE - not just report them!"
  3_use_agents: 
    strategy: "MULTIPLE AGENTS in parallel"
    distribution:
      - agent: "linting_fixer"
        target: "linting issues"
      - agent: "test_fixer"
        target: "test failures"
      - agent: "module_fixer"
        target: "different files/modules"
    required_statement: "I'll spawn multiple agents to fix all these issues in parallel"
  4_completion_criteria:
    - "✅ ALL linters pass with ZERO warnings"
    - "✅ ALL tests pass"
    - "✅ Build succeeds"
    - "✅ EVERYTHING is GREEN"
```
<!-- DATA:check-requirements:END -->
<!-- SECTION:check:mandatory-actions:END -->

<!-- SECTION:check:forbidden-behaviors:START -->
## FORBIDDEN BEHAVIORS

<!-- DATA:forbidden-responses:START -->
```yaml
forbidden:
  - response: "Here are the issues I found"
    instead: "FIX THEM!"
  - response: "The linter reports these problems"
    instead: "RESOLVE THEM!"
  - response: "Tests are failing because..."
    instead: "MAKE THEM PASS!"
  - response: "Stopping after listing issues"
    instead: "KEEP WORKING!"
```
<!-- DATA:forbidden-responses:END -->
<!-- SECTION:check:forbidden-behaviors:END -->

<!-- SECTION:check:mandatory-workflow:START -->
## MANDATORY WORKFLOW

<!-- WORKFLOW:check-fix-cycle:START -->
```yaml
workflow:
  - step: 1
    action: "Run checks"
    result: "Find issues"
  - step: 2
    action: "IMMEDIATELY spawn agents to fix ALL issues"
  - step: 3
    action: "Re-run checks"
    result: "Find remaining issues"
  - step: 4
    action: "Fix those too"
  - step: 5
    action: "REPEAT until EVERYTHING passes"

completion_state:
  - "All linters pass with zero warnings"
  - "All tests pass successfully"
  - "All builds complete without errors"
  - "Everything shows green/passing status"
```
<!-- WORKFLOW:check-fix-cycle:END -->
<!-- SECTION:check:mandatory-workflow:END -->

<!-- SECTION:check:pre-flight:START -->
## 🛑 **MANDATORY PRE-FLIGHT CHECK** 🛑

<!-- DATA:pre-flight-steps:START -->
```yaml
steps:
  1: 
    action: "Re-read @./CLAUDE.md RIGHT NOW"
  2:
    action: "Check Active Work section in @.quaestor/MEMORY.md"
  3:
    action: "Verify you're not declaring 'done' prematurely"
```
<!-- DATA:pre-flight-steps:END -->

Execute comprehensive quality checks with ZERO tolerance for excuses.
<!-- SECTION:check:pre-flight:END -->

<!-- SECTION:check:forbidden-excuses:START -->
## FORBIDDEN EXCUSE PATTERNS

<!-- DATA:excuse-patterns:START -->
```yaml
forbidden_excuses:
  - excuse: "This is just stylistic"
    reality: "it's a requirement"
  - excuse: "Most remaining issues are minor"
    reality: "ALL issues must be fixed"
  - excuse: "This can be addressed later"
    reality: "fix it now"
  - excuse: "It's good enough"
    reality: "it must be perfect"
  - excuse: "The linter is being pedantic"
    reality: "the linter is right"
```
<!-- DATA:excuse-patterns:END -->
<!-- SECTION:check:forbidden-excuses:END -->

<!-- SECTION:check:verification-protocol:START -->
## Universal Quality Verification Protocol

Let me **ultrathink** about validating this codebase against our exceptional standards.

<!-- SECTION:check:step0-linting:START -->
### Step 0: Linting Status Check

<!-- DATA:linting-check:START -->
```yaml
commands:
  format: "uv run ruff format"
  check: "uv run ruff check"
requirements:
  - "If ANY issues exist, they MUST be fixed before proceeding"
```
<!-- DATA:linting-check:END -->
<!-- SECTION:check:step0-linting:END -->

<!-- SECTION:check:step1-analysis:START -->
### Step 1: Pre-Check Analysis

<!-- DATA:pre-check-tasks:START -->
```yaml
tasks:
  - "Review recent changes to understand scope"
  - "Identify which tests should be affected"
  - "Check for any outstanding TODOs or temporary code"
```
<!-- DATA:pre-check-tasks:END -->
<!-- SECTION:check:step1-analysis:END -->

<!-- SECTION:check:step2-linting:START -->
### Step 2: Language-Agnostic Linting

<!-- DATA:linting-commands:START -->
```yaml
python:
  format: "uv run ruff format"
  check: "uv run ruff check"
other_languages:
  action: "Manual linter runs for other languages if needed"

universal_requirements:
  - "ZERO warnings across ALL linters"
  - "ZERO disabled linter rules without documented justification"
  - "ZERO 'nolint' or suppression comments without explanation"
  - "ZERO formatting issues (all code must be auto-formatted)"
```
<!-- DATA:linting-commands:END -->
<!-- SECTION:check:step2-linting:END -->


<!-- SECTION:check:step3-testing:START -->
### Step 3: Test Verification

<!-- DATA:test-requirements:START -->
```yaml
command: "uv run pytest"
ensure:
  - "ALL tests pass without flakiness"
  - "Test coverage is meaningful (not just high numbers)"
  - "Table-driven tests for complex logic"
  - "No skipped tests without justification"
  - "Benchmarks exist for performance-critical paths"
  - "Tests actually test behavior, not implementation details"
```
<!-- DATA:test-requirements:END -->
<!-- SECTION:check:step3-testing:END -->

<!-- SECTION:check:quality-checklists:START -->
## Quality Checklists

<!-- DATA:code-hygiene-checklist:START -->
```yaml
code_hygiene:
  - "[ ] All exported symbols have godoc comments"
  - "[ ] No commented-out code blocks"
  - "[ ] No debugging print statements"
  - "[ ] No placeholder implementations"
  - "[ ] Consistent formatting (gofmt/goimports)"
  - "[ ] Dependencies are actually used"
  - "[ ] No circular dependencies"
```
<!-- DATA:code-hygiene-checklist:END -->

<!-- DATA:security-checklist:START -->
```yaml
security_audit:
  - "[ ] Input validation on all external data"
  - "[ ] SQL queries use prepared statements"
  - "[ ] Crypto operations use crypto/rand"
  - "[ ] No hardcoded secrets or credentials"
  - "[ ] Proper permission checks"
  - "[ ] Rate limiting where appropriate"
```
<!-- DATA:security-checklist:END -->

<!-- DATA:performance-checklist:START -->
```yaml
performance:
  - "[ ] No obvious N+1 queries"
  - "[ ] Appropriate use of pointers vs values"
  - "[ ] Buffered channels where beneficial"
  - "[ ] Connection pooling configured"
  - "[ ] No unnecessary allocations in hot paths"
  - "[ ] No busy-wait loops consuming CPU"
  - "[ ] Channels used for efficient goroutine coordination"
```
<!-- DATA:performance-checklist:END -->
<!-- SECTION:check:quality-checklists:END -->

<!-- SECTION:check:failure-protocol:START -->
## Failure Response Protocol

<!-- WORKFLOW:issue-fixing:START -->
```yaml
when_issues_found:
  1_spawn_agents:
    example: |
      "I found 15 linting issues and 3 test failures. I'll spawn agents to fix these:
      - Agent 1: Fix linting issues in files A, B, C
      - Agent 2: Fix linting issues in files D, E, F  
      - Agent 3: Fix the failing tests
      Let me tackle all of these in parallel..."
  
  2_fix_everything:
    rule: "Address EVERY issue, no matter how 'minor'"
  
  3_verify:
    action: "Re-run all checks after fixes"
  
  4_repeat:
    condition: "If new issues found"
    action: "spawn more agents and fix those too"
  
  5_no_stopping:
    rule: "Keep working until ALL checks show ✅ GREEN"
  
  6_no_excuses:
    invalid_excuses:
      - excuse: "It's just formatting"
        action: "Auto-format it NOW"
      - excuse: "It's a false positive"
        action: "Prove it or fix it NOW"
      - excuse: "It works fine"
        action: "Working isn't enough, fix it NOW"
      - excuse: "Other code does this"
        action: "Fix that too NOW"
  
  7_escalate:
    when: "Only if truly blocked after attempting fixes"
```
<!-- WORKFLOW:issue-fixing:END -->
<!-- SECTION:check:failure-protocol:END -->

<!-- SECTION:check:final-verification:START -->
## Final Verification

<!-- DATA:ready-criteria:START -->
```yaml
code_is_ready_when:
  - "✓ uv run ruff check: PASSES with zero warnings"
  - "✓ uv run pytest: PASSES all tests"
  - "✓ go test -race: NO race conditions"
  - "✓ All checklist items verified"
  - "✓ Feature works end-to-end in realistic scenarios"
  - "✓ Error paths tested and handle gracefully"
```
<!-- DATA:ready-criteria:END -->
<!-- SECTION:check:final-verification:END -->

<!-- SECTION:check:final-commitment:START -->
## Final Commitment

<!-- DATA:commitment:START -->
```yaml
i_will:
  - "✅ Run all checks to identify issues"
  - "✅ SPAWN MULTIPLE AGENTS to fix issues in parallel"
  - "✅ Keep working until EVERYTHING passes"
  - "✅ Not stop until all checks show passing status"

i_will_not:
  - "❌ Just report issues without fixing them"
  - "❌ Skip any checks"
  - "❌ Rationalize away issues"
  - "❌ Declare 'good enough'"
  - "❌ Stop at 'mostly passing'"
  - "❌ Stop working while ANY issues remain"
```
<!-- DATA:commitment:END -->

**REMEMBER: This is a FIXING task, not a reporting task!**

The code is ready ONLY when every single check shows ✅ GREEN.

**Executing comprehensive validation and FIXING ALL ISSUES NOW...**
<!-- SECTION:check:final-commitment:END -->