---
allowed-tools: all
description: Execute production-quality Rust implementation with strict standards
---

# RUST TASK COMMAND - MANDATORY COMPLIANCE REQUIRED
<!-- META:command:task-rust -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->
<!-- META:rust-focused:true -->

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
  found_issues: "Stopping to fix clippy warnings before continuing."
  completion: "All checks pass. Implementation complete."
```
<!-- DATA:workflow-sequence:END -->

## ABSOLUTE REQUIREMENTS - NO DEVIATION

### Rust Code Standards - ENFORCE IMMEDIATELY

<!-- DATA:linting-requirements:START -->
```yaml
linting_enforcement:
  status: "LAW"
  linter: "cargo clippy -- -D warnings"
  formatter: "cargo fmt"
  frequency: "AFTER EVERY EDIT"
  tolerance: "ZERO WARNINGS"
  action_on_failure: "STOP AND FIX IMMEDIATELY"
  
rust_mandates:
  ownership: "EXPLICIT - no unnecessary clones"
  error_handling: "Result<T, E> for ALL fallible operations"
  unsafe_code: "FORBIDDEN unless absolutely necessary with safety comments"
  lifetimes: "EXPLICIT when needed - no elision confusion"
  traits: "Implement standard traits (Debug, Clone, etc.)"
  documentation: "/// for ALL public items"
  testing: "Unit tests for ALL public functions"
  dependencies: "Minimal - justify each one"

forbidden_patterns:
  - "unwrap()"  # Use expect() or proper error handling
  - "panic!"  # Only in truly unrecoverable situations
  - "unsafe {"  # Without safety documentation
  - "clone()"  # Without justification
  - "Box<dyn Error>"  # Use specific error types
  - "use std::*"  # No glob imports
  - "pub use *"  # No re-export globs
  - "#[allow("  # No suppressing warnings
```
<!-- DATA:linting-requirements:END -->

### Reality Enforcement Checkpoints

<!-- DATA:checkpoint-rules:START -->
```yaml
mandatory_checkpoints:
  - trigger: "every_3_edits"
    actions:
      - "cargo fmt --check"
      - "cargo clippy -- -D warnings"
    failure_response: "HALT ALL WORK"
    
  - trigger: "function_complete"
    actions:
      - "cargo test"
      - "cargo check"
    failure_response: "FIX BEFORE PROCEEDING"
    
  - trigger: "before_completion_claim"
    actions:
      - "cargo fmt --check"
      - "cargo clippy -- -D warnings"
      - "cargo test"
      - "cargo doc --no-deps"
      - "cargo audit"
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
  - "process_data_v2"  # NO versioning
  - "process_data_new"  # NO 'new' suffix
  - "// TODO: migrate later"  # NO deferral
  - "if use_new_method"  # NO feature flags
  - "#[deprecated]"  # NO deprecation - just delete
  - "mod old_"  # NO old modules
```
<!-- DATA:evolution-rules:END -->

## RUST-SPECIFIC QUALITY REQUIREMENTS

<!-- DATA:rust-specific-rules:START -->
```yaml
memory_safety:
  ownership: "CLEAR and EXPLICIT"
  borrowing: "MINIMAL - prefer ownership transfer"
  lifetimes: "ANNOTATE when non-obvious"
  unsafe: "DOCUMENT every unsafe block"

error_handling:
  style: "Custom error types with thiserror"
  propagation: "Use ? operator"
  context: "Add context with anyhow/color-eyre"
  panics: "ONLY for programmer errors"

performance:
  allocations: "MINIMIZE - use iterators"
  copies: "AVOID - use references"
  collections: "Choose correct type (Vec, HashMap, etc.)"
  async: "Use tokio for async runtime"

idioms:
  builder_pattern: "For complex structs"
  newtype_pattern: "For type safety"
  iterator_chains: "Prefer over loops"
  pattern_matching: "Exhaustive matches"
```
<!-- DATA:rust-specific-rules:END -->

## QUALITY GATES - ALL MUST PASS

<!-- DATA:completion-standards:START -->
```yaml
definition_of_done:
  formatting:
    command: "cargo fmt --check"
    requirement: "No changes needed"
    
  linting:
    command: "cargo clippy -- -D warnings"
    requirement: "ZERO warnings, ZERO errors"
    
  compilation:
    command: "cargo check --all-features"
    requirement: "Clean compilation"
    
  tests:
    command: "cargo test --all-features"
    requirement: "100% pass rate"
    coverage: "tarpaulin >90% for business logic"
    
  documentation:
    command: "cargo doc --no-deps"
    requirement: "No missing docs warnings"
    
  security:
    command: "cargo audit"
    requirement: "No vulnerabilities"
    
  functionality:
    requirement: "Works end-to-end"
    validation: "Integration tests pass"

banned_phrases:
  - "TODO"
  - "FIXME"
  - "HACK"
  - "good enough"
  - "will refactor later"
  - "temporary solution"
  - "quick fix"
  - "works for now"
  - "unwrap() // safe"
```
<!-- DATA:completion-standards:END -->

## IMPLEMENTATION METHODOLOGY

<!-- WORKFLOW:implementation:START -->
```yaml
execution_steps:
  - step: 1
    action: "Research codebase patterns"
    tools: ["Grep", "Glob", "cargo tree"]
    output: "Module structure understood"
    
  - step: 2
    action: "Design complete solution"
    requirement: "Type-driven development"
    validation: "API design review"
    
  - step: 3
    action: "Implement with validation"
    checkpoints: "Every 3 edits"
    linting: "Continuous clippy checks"
    
  - step: 4
    action: "Test thoroughly"
    levels: ["unit", "integration", "doc tests"]
    edge_cases: "All error paths covered"
```
<!-- WORKFLOW:implementation:END -->

## ANTI-PROCRASTINATION ENFORCEMENT

<!-- DATA:forbidden-excuses:START -->
```yaml
procrastination_triggers:
  "I'll fix the clippy warnings later": "NO. Fix now."
  "Let me just get it compiling": "NO. Quality from start."
  "The tests can wait": "NO. Test-driven development."
  "This mostly works": "NO. Fully working only."
  "I'll handle errors properly later": "NO. Proper error handling now."
  "unwrap() is fine here": "NO. Use expect() with reason."
```
<!-- DATA:forbidden-excuses:END -->

## CARGO.TOML REQUIREMENTS

<!-- DATA:cargo-requirements:START -->
```yaml
dependencies:
  justification: "REQUIRED for each dependency"
  versions: "EXACT versions only"
  features: "MINIMAL feature set"

lints:
  workspace: true
  rust:
    unsafe_code: "warn"
    missing_docs: "warn"
  clippy:
    all: "warn"
    pedantic: "warn"
    nursery: "warn"
    cargo: "warn"
```
<!-- DATA:cargo-requirements:END -->

## FINAL VALIDATION CHECKLIST

<!-- DATA:completion-checklist:START -->
```yaml
all_items_must_be_true:
  research_thorough: "Module structure and traits understood"
  plan_approved: "Implementation plan reviewed and approved"
  formatting_perfect: "cargo fmt reports no changes"
  clippy_clean: "cargo clippy reports ZERO warnings"
  tests_complete: "All tests pass with coverage"
  docs_written: "All public items documented"
  errors_handled: "No unwrap() or panic! without justification"
  unsafe_justified: "All unsafe blocks have safety comments"
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

**RUST DEMANDS PERFECTION. DELIVER IT.**