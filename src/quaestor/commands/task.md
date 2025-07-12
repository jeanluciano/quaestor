---
allowed-tools: all
description: Execute production-quality implementation with auto-detected language standards
---

# TASK COMMAND - MANDATORY COMPLIANCE REQUIRED
<!-- META:command:task -->
<!-- META:version:4.0 -->
<!-- META:ai-optimized:true -->
<!-- META:auto-detect:true -->

## ⚡ IMMEDIATE ACTION REQUIRED ⚡

**TASK ASSIGNMENT:** $ARGUMENTS

<!-- IF NO ARGUMENTS PROVIDED -->
{% if not ARGUMENTS or ARGUMENTS == "" %}
**NO TASK SPECIFIED - CHECKING FOR NEXT TASK:**
1. First, check .quaestor/MEMORY.md for pending tasks or next logical step
2. Look for sections like "next_task:", "pending:", "TODO:", or incomplete items
3. If found, announce the task and proceed with it
4. If no pending tasks found, ask the user what they'd like to work on

Example response:
"I'll check MEMORY.md for the next task... Found pending task: 'implement user authentication'. Starting research phase for this task."
{% endif %}

**YOU MUST:** Begin with milestone awareness phase. No exceptions.

## 📋 MILESTONE AWARENESS PHASE (MANDATORY)

**BEFORE STARTING ANY WORK:**

1. **Check Active Milestones:**
   - Read all .quaestor/milestones/*/README.md files
   - Find tasks.yaml files with status: "in_progress" or "active"
   - Identify which phase/task/subtask relates to this work

2. **Declare Your Work Context:**
   - Announce: "Working on: [Phase] > [Task] > [Subtask]"
   - Example: "Working on: Phase 1 > vector_store > Create VectorStore abstraction"
   - If no match found, declare: "New work not in existing milestones"

3. **Update Task Status:**
   - If starting a new task, update status to "in_progress"
   - If continuing existing work, confirm current status
   - Document any changes to the original plan

**MILESTONE DECLARATION TEMPLATE:**
```
🎯 MILESTONE CONTEXT:
- Phase: [Phase Name]
- Task ID: [task_id]
- Task Name: [Task Name]
- Subtask: [Current Subtask] ([X/Y] completed)
- Progress: [X]%
- File: .quaestor/milestones/[phase]/tasks.yaml
```

**IF NO MILESTONE MATCH:**
Ask the user if this work should:
1. Be added to existing milestone
2. Create new task in current phase
3. Proceed as standalone work

**MILESTONE AUTO-DETECTION:**
1. Scan .quaestor/milestones/ for keywords in task names
2. Match argument keywords to task descriptions
3. Identify related subtasks
4. Suggest milestone context to user

**EXAMPLE:**
Task: "implement vector store"
Detected: Phase 1 > vector_store task
Subtasks: ["Create VectorStore abstraction (ABC)", "Implement InMemoryVectorDB", ...]
Suggestion: "This appears to relate to Phase 1 vector_store task. Shall I work on the next incomplete subtask?"

## AUTO-DETECTION PHASE

<!-- DATA:detection-rules:START -->
```yaml
project_detection:
  order: 0
  action: "Detect project type from files"
  checks:
    - if_exists: ["pyproject.toml", "requirements.txt", "setup.py", "*.py"]
      then: "PYTHON_MODE"
    - if_exists: ["Cargo.toml", "*.rs"]
      then: "RUST_MODE"
    - if_exists: ["package.json", "*.js", "*.ts", "*.jsx", "*.tsx"]
      then: "JAVASCRIPT_MODE"
    - else: "GENERIC_MODE"
```
<!-- DATA:detection-rules:END -->

## IRON-CLAD EXECUTION SEQUENCE

<!-- DATA:workflow-sequence:START -->
```yaml
mandatory_workflow:
  deviation_tolerance: ZERO
  enforcement: IMMEDIATE
  
phases:
  - phase: TASK_DISCOVERY
    order: 0
    action: "Find next task if none specified"
    only_if: "No arguments provided"
    steps:
      - "Read .quaestor/MEMORY.md"
      - "Look for: next_task, pending items, incomplete milestones"
      - "Check current_milestone progress"
      - "Find TODOs or unfinished features"
    required_output: "Found task: [describe task] OR No pending tasks found"
    
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
  found_issues: "Stopping to fix issues before continuing."
  completion: "All checks pass. Implementation complete."
```
<!-- DATA:workflow-sequence:END -->

## LANGUAGE-SPECIFIC QUALITY STANDARDS

### PYTHON MODE
<!-- DATA:python-standards:START -->
```yaml
quality_gates:
  - tool: "ruff"
    command: "ruff check . --fix"
    failure_action: "STOP - fix all issues"
  - tool: "ruff format"
    command: "ruff format ."
    failure_action: "STOP - format code"
  - tool: "pytest"
    command: "pytest -v"
    failure_action: "STOP - all tests must pass"
  - tool: "type checking"
    command: "mypy . --ignore-missing-imports"
    failure_action: "FIX - add type hints"

validation_commands:
  before_commit:
    - "ruff check ."
    - "ruff format --check ."
    - "pytest"
  after_major_change:
    - "pytest -v"
    - "ruff check . --statistics"

required_patterns:
  - comprehensive_docstrings
  - type_hints_everywhere
  - proper_error_handling
  - test_coverage_80_percent
```
<!-- DATA:python-standards:END -->

### RUST MODE
<!-- DATA:rust-standards:START -->
```yaml
quality_gates:
  - tool: "cargo clippy"
    command: "cargo clippy -- -D warnings"
    failure_action: "STOP - fix all clippy warnings"
  - tool: "cargo fmt"
    command: "cargo fmt"
    failure_action: "STOP - format code"
  - tool: "cargo test"
    command: "cargo test"
    failure_action: "STOP - all tests must pass"
  - tool: "cargo check"
    command: "cargo check"
    failure_action: "STOP - code must compile"

validation_commands:
  before_commit:
    - "cargo fmt -- --check"
    - "cargo clippy -- -D warnings"
    - "cargo test"
  after_major_change:
    - "cargo test --all"
    - "cargo bench"

required_patterns:
  - comprehensive_documentation
  - proper_error_handling_with_result
  - safe_rust_patterns
  - no_unwrap_in_production
  - test_coverage_80_percent
```
<!-- DATA:rust-standards:END -->

### JAVASCRIPT/TYPESCRIPT MODE
<!-- DATA:javascript-standards:START -->
```yaml
quality_gates:
  - tool: "eslint"
    command: "npx eslint . --fix"
    failure_action: "STOP - fix all issues"
  - tool: "prettier"
    command: "npx prettier --write ."
    failure_action: "STOP - format code"
  - tool: "tests"
    command: "npm test"
    failure_action: "STOP - all tests must pass"
  - tool: "type checking"
    command: "npx tsc --noEmit"
    failure_action: "FIX - resolve type errors"

validation_commands:
  before_commit:
    - "npx eslint ."
    - "npx prettier --check ."
    - "npm test"
  after_major_change:
    - "npm test -- --coverage"
    - "npm run build"

required_patterns:
  - proper_async_await
  - error_boundaries
  - comprehensive_jsdoc
  - test_coverage_80_percent
```
<!-- DATA:javascript-standards:END -->

### GENERIC MODE
<!-- DATA:generic-standards:START -->
```yaml
quality_gates:
  - check: "syntax_validity"
    action: "Ensure code compiles/runs"
  - check: "error_handling"
    action: "Add proper error handling"
  - check: "documentation"
    action: "Add clear comments and docs"
  - check: "tests"
    action: "Write comprehensive tests"

required_patterns:
  - clear_variable_names
  - modular_design
  - proper_error_handling
  - comprehensive_documentation
```
<!-- DATA:generic-standards:END -->

## MANDATORY AGENT USAGE

**SPAWN AGENTS FOR:**
- Multi-file operations
- Test writing while implementing
- Complex refactoring
- Performance optimization
- Documentation updates

## COMPLEXITY MANAGEMENT

**IMMEDIATELY STOP AND ASK WHEN:**
- Function exceeds 50 lines
- Nesting depth > 3
- Circular dependencies detected
- Multiple valid approaches exist
- Performance implications unclear

## VALIDATION CYCLE

<!-- DATA:validation-cycle:START -->
```yaml
continuous_validation:
  frequency: "EVERY 3 EDITS"
  checks:
    - syntax_valid: "MANDATORY"
    - tests_pass: "MANDATORY"
    - linting_clean: "MANDATORY"
    - types_correct: "MANDATORY"
  
  on_failure:
    action: "STOP IMMEDIATELY"
    fix: "RESOLVE BEFORE CONTINUING"
    report: "EXPLAIN ISSUE AND FIX"
```
<!-- DATA:validation-cycle:END -->

## CHECKPOINT REQUIREMENTS

**MANDATORY STOPS:**
1. After research phase - present findings
2. After plan creation - get approval
3. Every 3 file edits - run validation
4. Before declaring complete - full test suite

## COMPLETION CRITERIA

**BEFORE MARKING COMPLETE:**
- [ ] All tests passing
- [ ] Zero linting errors
- [ ] Type checking passes (if applicable)
- [ ] Documentation complete
- [ ] Error handling comprehensive
- [ ] Performance acceptable

## 📊 POST-COMPLETION MILESTONE UPDATE (MANDATORY)

**AFTER COMPLETING IMPLEMENTATION:**

1. **Update Milestone Files:**
   ```bash
   # Update .quaestor/milestones/[phase]/tasks.yaml
   # Mark completed subtasks with "# COMPLETED"
   # Update progress percentage
   # Add timestamped notes
   ```

2. **Update MEMORY.md:**
   ```markdown
   ### YYYY-MM-DD
   - **COMPLETED**: [Task Name] ([Phase] - [task_id], subtask [X/Y])
     - Implementation: [brief description]
     - Files created: [list key files]
     - Tests added: [count and brief description]
     - Status: [X]% complete
     - Next: [what's next in this task]
   ```

3. **Verification Checklist:**
   - [ ] Milestone task status updated
   - [ ] Subtasks marked complete with "# COMPLETED"
   - [ ] Progress percentage updated
   - [ ] MEMORY.md progress log added
   - [ ] Notes added with timestamp
   - [ ] Next steps identified

**COMPLIANCE CHECK:**
If you cannot complete the milestone updates, explain why and ask for guidance.

**FINAL RESPONSE:** "Task complete. All quality gates passed. Milestone tracking updated. Ready for review."