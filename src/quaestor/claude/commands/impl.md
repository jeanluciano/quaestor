---
allowed-tools: [Read, Write, Edit, MultiEdit, Bash, Glob, Grep, TodoWrite, Task]
description: "Execute production-quality implementation with specification-driven orchestration"

agent-strategy:
  multi_file_changes: "Use the researcher agent to map dependencies"
  system_design: "Use the architect agent to design the solution"
  security_features: "Use the security agent to review implementation"
  test_creation: "Use the qa agent to ensure quality coverage"
---

# /impl - Intelligent Implementation Command

## Purpose
Execute production-quality features with auto-detected language standards, intelligent tool orchestration, and specification integration.

## Auto-Intelligence

### Project Detection
- **Language**: Auto-detect → Python|Rust|JS|Generic standards
- **Scope**: Assess changes → Single-file|Multi-file|System-wide
- **Context**: Identify task requirements → architecture|security|testing|refactoring

### Execution Strategy
- **System-wide**: Comprehensive planning with multiple agent coordination
- **Feature Development**: Iterative implementation with testing  
- **Bug Fixes**: Focused resolution with validation

## Execution

**FIRST, use the workflow-coordinator agent to validate workflow state and coordinate the implementation phase.**

The workflow-coordinator will:
- Verify planning phase has been completed (specification exists)
- Check for active specifications in .quaestor/specs/active/
- Ensure prerequisites are met (research done, plan approved)
- Coordinate the transition from planning to implementation

Then follow the coordinator's guidance to:
- **Use the implementer agent to** build features according to the specification
- **Use the architect agent to** design system architecture when needed
- **Use the security agent to** review auth, encryption, or access control implementation
- **Use the qa agent to** create comprehensive tests alongside implementation
- **Use the refactorer agent to** ensure consistency across multiple files

## Workflow: Research → Plan → Implement → Validate

### Phase 1: Discovery & Research 🔍
**No Arguments?** → Check `.quaestor/spec/active/` for in-progress specifications

**Specification Integration:**
```yaml
🎯 Context Check:
- Scan: .quaestor/spec/draft/*.yaml for matching spec
- Move: draft spec → active/ folder (if space available)
- Update: spec status → "in_progress"
- Track: implementation in spec phases
```

**Research Protocol:**
- Analyze codebase patterns & conventions
- Identify dependencies & integration points
- Determine required agents based on task requirements

### Phase 2: Planning & Approval 📋
**Present detailed implementation strategy:**
- Architecture decisions & trade-offs
- File changes & new components required
- Quality gates & validation approach
- Risk assessment & mitigation

**MANDATORY: Get approval before proceeding**

### Phase 3: Implementation ⚡
**Claude Code Sub-agent Orchestration:**
- **Multi-file operations** → Use the researcher agent to map dependencies, then use the implementer agent to execute changes
- **System refactoring** → Use the architect agent to design the solution, then use the refactorer agent to implement consistently
- **Test creation** → Use the qa agent to create comprehensive test coverage
- **Security implementation** → Use the security agent to review and validate sensitive code
- **Documentation updates** → Use the implementer agent to update docs alongside code

**Task-Based Agent Selection:**
Select agents based on specific task requirements:
- **System architecture changes** → Use the architect agent to design, then use the implementer agent to build
- **Security-sensitive features** → Use the security agent to define requirements, then use the implementer agent to build securely
- **Multi-file refactoring** → Use the researcher agent to analyze impact, then use the refactorer agent to update consistently
- **Quality assurance** → Use the qa agent to create tests and validate implementation

**Quality Cycle** (every 3 edits):
```
Execute → Validate → Fix (if ❌) → Continue
```

### Phase 4: Validation & Completion ✅
**Language-Specific Standards:**

**Python:** `ruff check . && ruff format . && pytest`
**Rust:** `cargo clippy -- -D warnings && cargo fmt && cargo test`  
**JS/TS:** `npx eslint . --fix && npx prettier --write . && npm test`
**Generic:** Syntax + error handling + documentation + tests

**Completion Criteria:**
- ✅ All tests passing
- ✅ Zero linting errors  
- ✅ Type checking clean (if applicable)
- ✅ Documentation complete
- ✅ Specification status updated

## Task Management & Agent Coordination

**Code Quality Checkpoints:**
- Function exceeds 50 lines → Use the refactorer agent to break into smaller functions
- Nesting depth exceeds 3 → Use the refactorer agent to simplify logic
- Circular dependencies detected → Use the architect agent to review design
- Performance implications unclear → Use the implementer agent to add measurements

**Agent Chaining for Complex Tasks:**
- **Large-scale changes** → Chain agents: Use the researcher agent to analyze, then use the architect agent to design, then use the implementer agent to build
- **Cross-domain features** → Parallel coordination: Use multiple specialized agents concurrently
- **Security-critical paths** → Sequential validation: Use the implementer agent to build, then use the security agent to audit, then use the qa agent to test

**Example Agent Chains:**
```yaml
Authentication Feature:
  1. Use the architect agent to design the auth flow
  2. Use the security agent to define security requirements
  3. Use the implementer agent to build the feature
  4. Use the qa agent to create security tests
  
API Refactoring:
  1. Use the researcher agent to map all API endpoints
  2. Use the architect agent to design the new structure
  3. Use the refactorer agent to update consistently
  4. Use the qa agent to validate backwards compatibility
```

## Specification Integration

**Auto-Update Protocol:**
```yaml
Pre-Implementation:
  - Check: .quaestor/spec/draft/ for matching spec ID
  - Move: spec from draft/ → active/ (max 3 active)
  - Declare: "Working on Spec: [ID] - [Title]"
  - Update: phase status in spec file

Post-Implementation:
  - Update: phase status → "completed"
  - Track: acceptance criteria completion
  - Move: spec to completed/ when all phases done
  - Create: git commit with spec reference
```

## Specification Discovery (No Arguments)
```yaml
Discovery Protocol:
  1. Check: .quaestor/spec/active/*.yaml (current work)
  2. If empty: Check .quaestor/spec/draft/*.yaml (available work)
  3. Match: spec ID from command argument
  4. Output: "Found spec: [ID] - [Title]" OR "No matching specification"
```

## Quality Gates by Language

### Python Standards
```yaml
Validation:
  - ruff: check . --fix
  - format: ruff format .
  - tests: pytest -v
  - types: mypy . --ignore-missing-imports
Required:
  - Comprehensive docstrings
  - Type hints everywhere  
  - 80%+ test coverage
```

### Rust Standards  
```yaml
Validation:
  - clippy: cargo clippy -- -D warnings
  - format: cargo fmt
  - tests: cargo test
  - check: cargo check
Required:
  - Comprehensive documentation
  - Result<T,E> error handling
  - No unwrap() in production
```

### JavaScript/TypeScript Standards
```yaml
Validation:
  - lint: npx eslint . --fix
  - format: npx prettier --write .
  - tests: npm test
  - types: npx tsc --noEmit
Required:
  - Proper async/await patterns
  - Comprehensive JSDoc
  - Error boundaries (React)
```

## Final Response Protocol
**Implementation complete. All quality gates passed. Specification status updated. Ready for review.**

---
*Command with orchestration for Claude integration and execution efficiency*