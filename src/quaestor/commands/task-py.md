---
allowed-tools: all
description: Execute production-quality implementation with strict standards
---

# TASK COMMAND - MANDATORY COMPLIANCE REQUIRED
<!-- META:command:task -->
<!-- META:version:3.0 -->
<!-- META:ai-optimized:true -->

## ⚡ IMMEDIATE ACTION REQUIRED ⚡

**TASK ASSIGNMENT:** $ARGUMENTS

**YOU MUST:** Begin with research phase. No exceptions.

## IRON-CLAD EXECUTION SEQUENCE

<!-- DATA:workflow-sequence:START -->
```yaml
mandatory_workflow:
  deviation_tolerance: ZERO
  enforcement: IMMEDIATE
  
phases:
  - phase: RESEARCH
    order: 1
    action: "Analyze codebase exhaustively"
    required_output: "I'll research the codebase and create a plan before implementing."
    minimum_duration: "THOROUGH - no rushing allowed"
    
  - phase: PLAN
    order: 2
    action: "Present detailed implementation strategy"
    required_output: "Here's my implementation plan: [DETAILED PLAN]"
    approval: "MANDATORY before proceeding"
    
  - phase: IMPLEMENT
    order: 3
    action: "Execute with continuous validation"
    validation_frequency: "EVERY 3 EDITS"
    checkpoint_enforcement: "AUTOMATIC"

required_responses:
  task_start: "I'll research the codebase and create a plan before implementing."
  complex_architecture: "I need to ultrathink through this architecture."
  multi_component: "I'll spawn agents to handle different components in parallel."
  found_issues: "Stopping to fix linting issues before continuing."
  completion: "All checks pass. Implementation complete."
```
<!-- DATA:workflow-sequence:END -->

## ABSOLUTE REQUIREMENTS - NO DEVIATION

### Python Code Standards - ENFORCE IMMEDIATELY

<!-- DATA:linting-requirements:START -->
```yaml
linting_enforcement:
  status: "LAW"
  tool: "uv run ruff check"
  formatter: "uv run ruff format"
  frequency: "AFTER EVERY EDIT"
  tolerance: "ZERO WARNINGS"
  action_on_failure: "STOP AND FIX IMMEDIATELY"
  
python_mandates:
  type_hints: "MANDATORY for ALL functions"
  docstrings: "REQUIRED for ALL public APIs"
  imports: "ABSOLUTE imports only - no relative imports"
  error_handling: "EXPLICIT - no bare except:"
  file_operations: "pathlib ONLY - no os.path"
  testing: "pytest with >90% coverage"
  async: "asyncio for concurrency - no threading unless justified"

forbidden_patterns:
  - "except:"  # Bare except
  - "import *"  # Star imports
  - "eval("  # Dynamic execution
  - "exec("  # Dynamic execution
  - "globals()["  # Global manipulation
  - "type("  # Use isinstance instead
  - "== True"  # Redundant boolean comparison
  - "!= None"  # Use 'is not None'
```
<!-- DATA:linting-requirements:END -->

### Reality Enforcement Checkpoints

<!-- DATA:checkpoint-rules:START -->
```yaml
mandatory_checkpoints:
  - trigger: "every_3_edits"
    actions:
      - "uv run ruff check"
      - "uv run ruff format"
    failure_response: "HALT ALL WORK"
    
  - trigger: "function_complete"
    actions:
      - "uv run pytest -xvs"
    failure_response: "FIX BEFORE PROCEEDING"
    
  - trigger: "before_completion_claim"
    actions:
      - "uv run ruff check"
      - "uv run pytest"
      - "uv run mypy"
    requirement: "ALL MUST PASS"
```
<!-- DATA:checkpoint-rules:END -->

## FEATURE IMPLEMENTATION RULES

<!-- DATA:evolution-rules:START -->
```yaml
replacement_policy:
  approach: "COMPLETE REPLACEMENT"
  old_code: "DELETE IMMEDIATELY"
  compatibility_layers: "FORBIDDEN"
  migration_helpers: "FORBIDDEN"
  versioned_functions: "FORBIDDEN"
  parallel_implementations: "FORBIDDEN"

forbidden_patterns:
  - "processDataV2"  # NO versioning
  - "process_data_new"  # NO 'new' suffix
  - "TODO: migrate later"  # NO deferral
  - "if use_new_method:"  # NO feature flags
  - "@deprecated"  # NO deprecation - just delete
```
<!-- DATA:evolution-rules:END -->

## QUALITY GATES - ALL MUST PASS

<!-- DATA:completion-standards:START -->
```yaml
definition_of_done:
  linting:
    command: "uv run ruff check"
    requirement: "ZERO warnings, ZERO errors"
    
  formatting:
    command: "uv run ruff format --check"
    requirement: "No changes needed"
    
  tests:
    command: "uv run pytest -xvs"
    requirement: "100% pass rate"
    coverage: ">90% for business logic"
    
  type_checking:
    command: "uv run mypy"
    requirement: "No type errors"
    
  functionality:
    requirement: "Works end-to-end"
    validation: "Manual verification required"

banned_phrases:
  - "TODO"
  - "FIXME"
  - "HACK"
  - "good enough"
  - "will refactor later"
  - "temporary solution"
  - "quick fix"
  - "works for now"
```
<!-- DATA:completion-standards:END -->

## IMPLEMENTATION METHODOLOGY

<!-- WORKFLOW:implementation:START -->
```yaml
execution_steps:
  - step: 1
    action: "Research codebase patterns"
    tools: ["Grep", "Glob", "Task agents"]
    output: "Pattern analysis complete"
    
  - step: 2
    action: "Design complete solution"
    requirement: "No partial implementations"
    validation: "Architecture review"
    
  - step: 3
    action: "Implement with validation"
    checkpoints: "Every 3 edits"
    linting: "Continuous"
    
  - step: 4
    action: "Test thoroughly"
    coverage: "Business logic >90%"
    edge_cases: "All handled"
```
<!-- WORKFLOW:implementation:END -->

## ANTI-PROCRASTINATION ENFORCEMENT

<!-- DATA:forbidden-excuses:START -->
```yaml
procrastination_triggers:
  "I'll fix the linting later": "NO. Fix now."
  "Let me just get it working": "NO. Quality from start."
  "The tests can wait": "NO. Test-driven development."
  "This is mostly working": "NO. Fully working only."
  "I'll clean it up after": "NO. Clean as you go."
```
<!-- DATA:forbidden-excuses:END -->

## FINAL VALIDATION CHECKLIST

<!-- DATA:completion-checklist:START -->
```yaml
all_items_must_be_true:
  research_thorough: "Deep codebase analysis completed"
  plan_approved: "Implementation plan reviewed and approved"
  linting_perfect: "ruff check reports ZERO issues"
  tests_complete: "All tests pass with required coverage"
  types_correct: "mypy passes without errors"
  feature_working: "End-to-end functionality verified"
  old_code_removed: "No legacy code remains"
  docs_written: "All required docstrings present"
  no_todos: "Zero TODOs or FIXMEs in code"
  
enforcement: "INCOMPLETE = CONTINUE WORKING"
```
<!-- DATA:completion-checklist:END -->

## POST-COMPLETION HOOKS

<!-- DATA:workflow-hooks:START -->
```yaml
automatic_actions:
  on_task_complete:
    trigger: "All checklist items pass"
    actions:
      - update_todo_status: "Mark as completed"
      - update_memory: "Sync progress to MEMORY.md"
      - run_milestone_commit: "Auto-commit if enabled"
    
  milestone_commit_hook:
    enabled: true
    conditions:
      - "Task marked complete"
      - "All quality checks pass"
      - "Changes saved to files"
    command: "/quaestor:milestone-commit"
    message: "Task completed - triggering milestone commit"
  
  workflow_integration:
    with_claude_md: "Follow workflow_hooks configuration"
    automatic_pr: "When milestone complete"
    quality_gates: "Enforced before commit"
```
<!-- DATA:workflow-hooks:END -->

**BEGIN IMMEDIATELY WITH RESEARCH PHASE.**

**NO EXCUSES. NO SHORTCUTS. PRODUCTION QUALITY ONLY.**