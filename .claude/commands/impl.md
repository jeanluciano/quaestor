---
allowed-tools: [Read, Write, Edit, MultiEdit, Bash, Glob, Grep, TodoWrite, Task]
description: "Execute production-quality implementation with specification-driven orchestration"
performance-profile: "complex"
complexity-threshold: 0.7
auto-activation: ["auto-persona", "specification-integration", "quality-gates"]
intelligence-features: ["project-detection", "parallel-execution", "context-awareness"]
agent-strategy:
  complexity > 0.7: [architect, implementer]
  security_keywords: [security, qa]
  multi_file: [researcher, refactorer]
  testing_required: [qa, implementer]
---

# /impl - Intelligent Implementation Command

## Purpose
Execute production-quality features with auto-detected language standards, intelligent tool orchestration, and specification integration.

## Usage
```
/impl "implement user authentication system"
/impl [description] [--strategy systematic|agile|focused] [--parallel]
```

## Auto-Intelligence

### Project Detection
- **Language**: Auto-detect → Python|Rust|JS|Generic standards
- **Complexity**: Assess scope → Single|Multi-file|System-wide
- **Persona**: Activate based on keywords → architect|frontend|backend|security

### Execution Strategy
- **Systematic**: Complex architecture (>0.7 complexity)
- **Agile**: Feature development (0.3-0.7 complexity)  
- **Focused**: Bug fixes (<0.3 complexity)

## Execution

**Use the implementer agent to build features according to the specification.**

For complex implementations:
- **Use the architect agent** for system design decisions (complexity > 0.7)
- **Use the security agent** when implementing auth, encryption, or access control
- **Use the qa agent** to create tests alongside implementation
- **Use the refactorer agent** for multi-file changes requiring consistency

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
- Assess complexity → tool selection strategy

### Phase 2: Planning & Approval 📋
**Present detailed implementation strategy:**
- Architecture decisions & trade-offs
- File changes & new components required
- Quality gates & validation approach
- Risk assessment & mitigation

**MANDATORY: Get approval before proceeding**

### Phase 3: Implementation ⚡
**Intelligent Orchestration with Quaestor Agents:**
- **Multi-file ops** → Spawn @researcher and @implementer agents in parallel
- **Complex refactoring** → @architect designs, then @refactorer executes
- **Test writing** → @qa agent handles test creation and coverage
- **Security concerns** → @security agent reviews sensitive code
- **Documentation** → @documenter updates docs concurrently

**Automatic Agent Selection:**
Based on task analysis, Quaestor automatically spawns specialized agents:
- High complexity (>0.7) → architect + implementer collaboration
- Security keywords detected → security agent joins the team
- Multiple files affected → researcher maps dependencies first
- Tests needed → qa agent ensures quality coverage

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

## Complexity Management

**Auto-Stop Triggers:**
- Function >50 lines → refactor prompt
- Nesting depth >3 → simplification required
- Circular dependencies → architecture review
- Performance implications unclear → measurement required

**Intelligent Delegation:**
- **>7 directories** → `--parallel-dirs` auto-enabled
- **>50 files** → Multi-agent file delegation
- **Multiple domains** → Specialized agent per domain

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