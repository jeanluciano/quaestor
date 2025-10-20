# Implementation Workflow - Complete 4-Phase Process

This file describes the detailed workflow for executing production-quality implementations.

## Workflow Overview: Research → Plan → Implement → Validate

```yaml
Phase 1: Discovery & Research (🔍)
  - Specification discovery and activation
  - Codebase analysis and pattern identification
  - Dependency mapping
  - Agent requirement determination

Phase 2: Planning & Approval (📋)
  - Strategy presentation
  - Architecture decisions
  - Risk assessment
  - MANDATORY user approval

Phase 3: Implementation (⚡)
  - Agent-orchestrated development
  - Quality cycle (every 3 edits)
  - Continuous validation
  - Documentation updates

Phase 4: Validation & Completion (✅)
  - Language-specific quality gates
  - Test execution
  - Specification status update
  - Completion confirmation
```

---

## Phase 1: Discovery & Research 🔍

### Specification Discovery

**No Arguments Provided?**
```yaml
Discovery Protocol:
  1. Check: .quaestor/specs/active/*.md (current work in progress)
  2. If empty: Check .quaestor/specs/draft/*.md (available work)
  3. Match: spec ID from user request
  4. Output: "Found spec: [ID] - [Title]" OR "No matching specification"
```

**Specification Activation:**
```yaml
🎯 Context Check:
  - Scan: .quaestor/specs/draft/*.md for matching spec
  - Validate: Max 3 active specs (enforce limit)
  - Move: draft spec → active/ folder
  - Update: spec status → "in_progress"
  - Track: implementation progress in spec phases
```

### Codebase Research

**Research Protocol:**
1. **Pattern Analysis**
   - Identify existing code conventions
   - Determine file organization patterns
   - Understand naming conventions
   - Map testing strategies

2. **Dependency Mapping**
   - Identify affected modules
   - Map integration points
   - Understand data flow
   - Detect circular dependencies

3. **Agent Determination**
   - Assess task complexity
   - Determine required agent specializations
   - Plan agent coordination strategy
   - Identify potential bottlenecks

**Example Research Output:**
```
🔍 Research Complete:

Specification: spec-feature-001 - User Authentication System
Status: Moved to active/

Codebase Analysis:
- Pattern: Repository pattern with service layer
- Testing: pytest with 75% coverage requirement
- Dependencies: auth module, user module, database layer

Required Agents:
- architect: Design auth flow and session management
- security: Review authentication implementation
- implementer: Build core functionality
- qa: Create comprehensive test suite
```

---

## Phase 2: Clarification & Decision 🤔

### MANDATORY: Ask User to Make Key Decisions

**After research, identify decisions user must make BEFORE planning:**

#### 1. Approach Selection (when 2+ valid options exist)
```
Use AskUserQuestion tool:
- Present 2-3 architectural approaches
- Include pros/cons and trade-offs for each
- Explain complexity and maintenance implications
- Wait for user to choose before proceeding
```

**Example:**
- Approach A: REST API - Simple, widely understood, but less efficient
- Approach B: GraphQL - Flexible queries, but steeper learning curve
- Approach C: gRPC - High performance, but requires protobuf setup

#### 2. Scope Boundaries
```
Ask clarifying questions:
- "Should this also handle [related feature]?"
- "Include [edge case scenario]?"
- "Support [additional requirement]?"
```

**Example:** "Should user authentication also include password reset functionality, or handle that separately?"

#### 3. Priority Trade-offs
```
When trade-offs exist, ask user to decide:
- "Optimize for speed OR memory efficiency?"
- "Prioritize simplicity OR flexibility?"
- "Focus on performance OR maintainability?"
```

**Example:** "This can be implemented for speed (caching, more memory) or simplicity (no cache, easier to maintain). Which priority?"

#### 4. Integration Decisions
```
Clarify connections to existing systems:
- "Integrate with existing [system] OR standalone?"
- "Use [library A] OR [library B]?"
- "Follow [pattern X] OR [pattern Y]?"
```

**Example:** "Should this use the existing Redis cache or create a new in-memory cache?"

**Only proceed to planning after user has made these decisions.**

---

## Phase 3: Planning & Approval 📋

### Present Implementation Strategy

**MANDATORY Components:**

1. **Architecture Decisions**
   - Design approach and rationale
   - Component structure
   - Data flow diagrams (if complex)
   - Integration strategy

2. **File Changes**
   - New files to create
   - Existing files to modify
   - Deletions (if any)
   - Configuration updates

3. **Quality Gates**
   - Testing strategy
   - Validation checkpoints
   - Coverage requirements
   - Performance benchmarks

4. **Risk Assessment**
   - Potential breaking changes
   - Migration requirements
   - Backwards compatibility concerns
   - Mitigation strategies

### Example Planning Output

```markdown
## Implementation Strategy for spec-feature-001

### Architecture Decisions
- Use JWT for stateless authentication
- Implement refresh token rotation
- Store sessions in Redis for scalability
- Use bcrypt for password hashing (cost factor: 12)

**Trade-offs:**
- ✅ Stateless = better scalability
- ⚠️ Redis dependency added
- ✅ Refresh rotation = better security

### File Changes
**New Files:**
- `src/auth/jwt_manager.py` - JWT generation and validation
- `src/auth/session_store.py` - Redis session management
- `tests/test_auth_flow.py` - Authentication flow tests

**Modified Files:**
- `src/auth/service.py` - Add JWT authentication
- `src/config.py` - Add auth configuration
- `requirements.txt` - Add PyJWT, redis dependencies

### Quality Gates
- Unit tests: All auth functions
- Integration tests: Complete auth flow
- Security tests: Token validation, expiry, rotation
- Coverage target: 90% for auth module

### Risk Assessment
- ⚠️ Breaking change: Session format changes
- Migration: Clear existing sessions on deploy
- Backwards compat: Old tokens expire gracefully
- Mitigation: Feature flag for gradual rollout
```

### Get User Approval

**MANDATORY: Wait for explicit approval before proceeding to Phase 3**

Approval phrases:
- "Proceed"
- "Looks good"
- "Go ahead"
- "Approved"
- "Start implementation"

---

## Phase 4: Implementation ⚡

### Agent-Orchestrated Development

**Agent Selection Matrix:**

```yaml
Task Type → Agent Strategy:

System Architecture:
  - Use architect agent to design solution
  - Use implementer agent to build components

Multi-file Changes:
  - Use researcher agent to map dependencies
  - Use refactorer agent to update consistently

Security Features:
  - Use security agent to define requirements
  - Use implementer agent to build securely
  - Use qa agent to create security tests

Test Creation:
  - Use qa agent for comprehensive coverage
  - Use implementer agent for test fixtures

Performance Optimization:
  - Use researcher agent to profile hotspots
  - Use refactorer agent to optimize code
  - Use qa agent to create performance tests
```

### Quality Cycle (Every 3 Edits)

**Continuous Validation:**
```yaml
After Every 3 Code Changes:
  1. Execute: Run relevant tests
  2. Validate: Check linting and type checking
  3. Fix: If ❌, address issues immediately
  4. Continue: Proceed with next changes

Example:
  Edit 1: Create auth/jwt_manager.py
  Edit 2: Add JWT generation method
  Edit 3: Add JWT validation method
  → RUN QUALITY CYCLE
  Execute: pytest tests/test_jwt.py
  Validate: ruff check auth/jwt_manager.py
  Fix: Address any issues
  Continue: Next 3 edits
```

### Implementation Patterns

**Single-File Feature:**
```yaml
Pattern:
  1. Create/modify file
  2. Add documentation
  3. Create tests
  4. Validate quality
  5. Update specification
```

**Multi-File Feature:**
```yaml
Pattern:
  1. Use researcher agent → Map dependencies
  2. Use architect agent → Design components
  3. Use implementer agent → Build core functionality
  4. Use refactorer agent → Ensure consistency
  5. Use qa agent → Create comprehensive tests
  6. Validate quality gates
  7. Update specification
```

**System Refactoring:**
```yaml
Pattern:
  1. Use researcher agent → Analyze impact
  2. Use architect agent → Design new structure
  3. Use refactorer agent → Update all files
  4. Use qa agent → Validate no regressions
  5. Validate quality gates
  6. Update documentation
```

### Code Quality Checkpoints

**Automatic Refactoring Triggers:**
- Function exceeds 50 lines → Use refactorer agent to break into smaller functions
- Nesting depth exceeds 3 → Use refactorer agent to simplify logic
- Circular dependencies detected → Use architect agent to review design
- Duplicate code found → Use refactorer agent to extract common functionality
- Performance implications unclear → Use implementer agent to add measurements

---

## Phase 5: Validation & Completion ✅

### Language-Specific Validation

**Python:**
```bash
ruff check . --fix         # Linting
ruff format .              # Formatting
pytest -v                  # Tests
mypy . --ignore-missing-imports  # Type checking
```

**Rust:**
```bash
cargo clippy -- -D warnings  # Linting
cargo fmt                    # Formatting
cargo test                   # Tests
cargo check                  # Type checking
```

**JavaScript/TypeScript:**
```bash
npx eslint . --fix          # Linting
npx prettier --write .      # Formatting
npm test                    # Tests
npx tsc --noEmit           # Type checking (TS only)
```

**Generic (Any Language):**
- Syntax validation
- Error handling review
- Documentation completeness
- Test coverage assessment

### Completion Criteria

**All Must Pass:**
- ✅ All tests passing (no skipped tests without justification)
- ✅ Zero linting errors (warnings acceptable with comment)
- ✅ Type checking clean (if applicable to language)
- ✅ Documentation complete (functions, classes, modules)
- ✅ Specification status updated (phases marked complete)
- ✅ No unhandled edge cases
- ✅ Performance within acceptable bounds

### Specification Update

**Post-Implementation Protocol:**
```yaml
Update Specification:
  - Mark completed phases: ✅ in spec file
  - Update acceptance criteria status
  - Add implementation notes (if needed)
  - Check if all phases complete → Move to completed/
  - Generate commit message with spec reference

Example:
  Phase 1: Authentication Flow Design - ✅ Complete
  Phase 2: JWT Implementation - ✅ Complete
  Phase 3: Session Management - ✅ Complete
  Phase 4: Security Testing - ✅ Complete

  → All phases complete
  → Move spec-feature-001 from active/ to completed/
  → Ready for review and PR creation
```

### Final Validation

**Before Declaring Complete:**
1. Run full test suite: `uv run pytest` or equivalent
2. Check git status: No unintended changes
3. Verify specification: All acceptance criteria met
4. Review documentation: Complete and accurate
5. Confirm quality gates: All passed

### Completion Response

**Standard Response Format:**
```
✅ Implementation Complete

Specification: spec-feature-001 - User Authentication System
Status: All phases completed, moved to completed/

Quality Gates:
- ✅ Tests: 42 passed, 0 failed
- ✅ Linting: 0 errors, 0 warnings
- ✅ Type checking: Clean
- ✅ Coverage: 92% (target: 90%)

Changes:
- 3 new files created
- 2 existing files modified
- 42 tests added
- 0 breaking changes

Ready for review phase. Use /review command to validate and create PR.
```

---

## Error Handling & Recovery

### Common Issues

**Issue: Tests Failing**
```yaml
Recovery:
  1. Analyze: Identify root cause
  2. Fix: Address failing tests
  3. Validate: Re-run test suite
  4. Continue: If fixed, proceed; if persistent, use qa agent for analysis
```

**Issue: Linting Errors**
```yaml
Recovery:
  1. Auto-fix: Run linter with --fix flag
  2. Manual: Address remaining issues
  3. Validate: Re-run linter
  4. Continue: Proceed when clean
```

**Issue: Type Checking Errors**
```yaml
Recovery:
  1. Analyze: Identify type mismatches
  2. Fix: Add proper type annotations
  3. Validate: Re-run type checker
  4. Continue: Proceed when clean
```

**Issue: Specification Conflict**
```yaml
Recovery:
  1. Review: Check specification requirements
  2. Discuss: Clarify with user if ambiguous
  3. Adjust: Modify implementation or specification
  4. Continue: Proceed with aligned understanding
```

---

*Complete workflow for production-quality implementation with quality gates and specification tracking*
