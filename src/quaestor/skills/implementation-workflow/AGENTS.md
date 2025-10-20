# Agent Orchestration Strategies

This file describes how to coordinate multiple specialized agents for complex implementation tasks.

## Agent Overview

### Available Agents for Implementation

```yaml
workflow-coordinator:
  role: "Workflow validation and phase coordination"
  use_first: true
  validates:
    - Planning phase completed
    - Specification exists in active/
    - Prerequisites met
  coordinates: "Transition from planning to implementation"

implementer:
  role: "Core feature development"
  specializes:
    - Building new features
    - Implementing specifications
    - Writing production code
    - Updating documentation

architect:
  role: "System design and architecture"
  specializes:
    - Architecture decisions
    - Component design
    - System refactoring
    - Design patterns

security:
  role: "Security review and implementation"
  specializes:
    - Authentication systems
    - Authorization logic
    - Encryption implementation
    - Security best practices

qa:
  role: "Quality assurance and testing"
  specializes:
    - Test creation
    - Coverage analysis
    - Test strategy
    - Quality validation

refactorer:
  role: "Code improvement and consistency"
  specializes:
    - Code refactoring
    - Consistency enforcement
    - Code smell removal
    - Multi-file updates

researcher:
  role: "Code exploration and analysis"
  specializes:
    - Dependency mapping
    - Pattern identification
    - Impact analysis
    - Codebase exploration
```

---

## Agent Selection Rules

### Task-Based Selection

**Use this matrix to determine which agents to invoke:**

```yaml
Authentication Feature:
  primary: architect  # Design auth flow
  secondary: security  # Security requirements
  tertiary: implementer  # Build feature
  final: qa  # Create tests

API Development:
  primary: architect  # Design API structure
  secondary: implementer  # Build endpoints
  tertiary: qa  # Create API tests

Bug Fix:
  primary: researcher  # Find root cause
  secondary: implementer  # Fix the bug
  tertiary: qa  # Add regression test

Refactoring:
  primary: researcher  # Analyze impact
  secondary: architect  # Design new structure
  tertiary: refactorer  # Update consistently
  final: qa  # Validate no regressions

Multi-file Changes:
  primary: researcher  # Map dependencies
  secondary: refactorer  # Update consistently
  tertiary: qa  # Ensure nothing breaks

Performance Optimization:
  primary: researcher  # Profile and analyze
  secondary: implementer  # Implement optimization
  tertiary: qa  # Performance tests

Security Feature:
  primary: security  # Define requirements
  secondary: implementer  # Build securely
  tertiary: qa  # Security tests
```

---

## Agent Chaining Patterns

### Sequential Chaining

**When to Use:** Tasks that must be done in a specific order.

**Pattern:**
```yaml
Step 1: Use agent A to complete task
  → Wait for completion
Step 2: Use agent B to build on A's work
  → Wait for completion
Step 3: Use agent C to finalize
  → Wait for completion
```

**Example: Authentication System**
```yaml
Step 1: Use the architect agent to:
  - Design authentication flow
  - Define session management strategy
  - Plan token structure

Step 2: Use the security agent to:
  - Review architect's design
  - Add security requirements
  - Define encryption standards

Step 3: Use the implementer agent to:
  - Implement auth flow per design
  - Apply security requirements
  - Build according to specifications

Step 4: Use the qa agent to:
  - Create unit tests
  - Create integration tests
  - Create security tests
```

### Parallel Coordination

**When to Use:** Independent tasks that can be done simultaneously.

**Pattern:**
```yaml
Spawn Multiple Agents in Parallel:
  - Agent A: Task 1 (independent)
  - Agent B: Task 2 (independent)
  - Agent C: Task 3 (independent)

Wait for All Completions

Consolidate Results
```

**Example: Feature with Multiple Components**
```yaml
Parallel Tasks:
  - Use the implementer agent to: Build API endpoints
  - Use the qa agent to: Create test fixtures
  - Use the researcher agent to: Document existing patterns

All agents work simultaneously on independent tasks.

After All Complete:
  - Integrate API with tests
  - Apply documented patterns
  - Validate complete feature
```

### Iterative Refinement

**When to Use:** Gradual improvement with feedback loops.

**Pattern:**
```yaml
Loop:
  1. Use agent to make changes
  2. Validate changes
  3. If issues found:
     - Use agent to fix issues
     - Validate again
  4. Repeat until quality gates pass
```

**Example: Code Refactoring**
```yaml
Iteration 1:
  - Use refactorer agent to simplify function
  - Run tests → 2 failures
  - Use refactorer agent to fix test compatibility
  - Run tests → All pass

Iteration 2:
  - Use refactorer agent to extract duplicate code
  - Run linter → 3 style issues
  - Use refactorer agent to fix style
  - Run linter → Clean

Iteration 3:
  - Validate: All quality gates pass
  - Complete: Refactoring done
```

---

## Agent Coordination Strategies

### Strategy 1: Single Agent (Simple Tasks)

**Use When:**
- Single file modification
- Simple bug fix
- Documentation update
- Straightforward feature

**Pattern:**
```yaml
Single Agent:
  - Use the implementer agent to:
    - Make the change
    - Add tests
    - Update documentation
```

**Example:**
```
User: "Add a max_length validation to the username field"

Use the implementer agent to:
  - Add max_length=50 to User.username field
  - Add validation test for max_length
  - Update API documentation with constraint
```

### Strategy 2: Agent Pairs (Moderate Complexity)

**Use When:**
- Design + implementation needed
- Security review required
- Test coverage important

**Pattern:**
```yaml
Agent Pair:
  Primary Agent: Core work
  Secondary Agent: Validation/enhancement
```

**Example:**
```
User: "Implement password reset functionality"

Step 1: Use the architect agent to:
  - Design password reset flow
  - Plan token generation strategy
  - Define security requirements

Step 2: Use the implementer agent to:
  - Implement the designed flow
  - Build according to security requirements
  - Add comprehensive tests
```

### Strategy 3: Agent Chain (High Complexity)

**Use When:**
- System-wide changes
- Architecture modifications
- Security-critical features
- Major refactoring

**Pattern:**
```yaml
Agent Chain:
  Phase 1: Research & Design
    - researcher: Analyze impact
    - architect: Design solution

  Phase 2: Implementation
    - implementer: Build core
    - security: Review (if needed)

  Phase 3: Quality Assurance
    - qa: Comprehensive testing
    - refactorer: Final polish
```

**Example:**
```
User: "Migrate from sessions to JWT authentication"

Phase 1 - Analysis:
  Use the researcher agent to:
    - Find all session usage
    - Map authentication dependencies
    - Identify breaking changes

Phase 2 - Design:
  Use the architect agent to:
    - Design JWT implementation
    - Plan migration strategy
    - Define backwards compatibility

Phase 3 - Security:
  Use the security agent to:
    - Review JWT implementation plan
    - Add security requirements
    - Define token validation rules

Phase 4 - Implementation:
  Use the implementer agent to:
    - Implement JWT manager
    - Add token validation
    - Build according to security requirements

Phase 5 - Migration:
  Use the refactorer agent to:
    - Update all authentication calls
    - Remove session dependencies
    - Ensure consistency

Phase 6 - Testing:
  Use the qa agent to:
    - Create unit tests
    - Create integration tests
    - Create security tests
    - Validate migration
```

### Strategy 4: Parallel + Sequential Hybrid

**Use When:**
- Multiple independent components with dependencies
- Complex features with parallel work streams

**Pattern:**
```yaml
Parallel Phase:
  - Agent A: Independent task 1
  - Agent B: Independent task 2

Sequential Phase (after parallel complete):
  - Agent C: Integration work
  - Agent D: Final validation
```

**Example:**
```
User: "Add real-time notifications with WebSockets"

Parallel Phase:
  Use the architect agent to:
    - Design WebSocket architecture

  Use the implementer agent to (simultaneously):
    - Set up WebSocket server configuration
    - Create notification data models

Sequential Phase:
  Use the implementer agent to:
    - Implement WebSocket handlers
    - Connect to notification models
    - Add client connection management

  Use the qa agent to:
    - Create WebSocket connection tests
    - Create notification delivery tests
    - Test connection stability
```

---

## Agent Communication Patterns

### Explicit Handoff

**Pattern:** Clearly state what the next agent should do based on previous work.

```yaml
Step 1: Use the researcher agent to map all API endpoints
  → Output: List of 47 endpoints in api_map.md

Step 2: Use the architect agent to design new API structure
  Context: Review the 47 endpoints in api_map.md
  Task: Design consolidated API with RESTful patterns

Step 3: Use the refactorer agent to update endpoints
  Context: Follow new structure from architect
  Task: Update all 47 endpoints to match design
```

### Context Sharing

**Pattern:** Ensure agents have necessary context from previous work.

```yaml
Context for Next Agent:
  Previous Work: "architect agent designed auth flow"
  Artifacts: "auth_design.md with flow diagram"
  Requirements: "Must follow JWT pattern with refresh tokens"

Use the implementer agent with this context to:
  - Implement auth flow from auth_design.md
  - Use JWT with refresh token pattern
  - Follow security guidelines from design
```

### Validation Loops

**Pattern:** Use agents to validate each other's work.

```yaml
Create → Validate → Fix Loop:

Step 1: Use the implementer agent to build feature

Step 2: Use the security agent to review implementation
  → If issues found:
    Document security concerns

Step 3: Use the implementer agent to address security concerns
  Context: Security review findings
  Task: Fix identified issues

Step 4: Use the security agent to re-review
  → If clean: Proceed
  → If issues: Repeat loop
```

---

## Quality Checkpoints with Agents

### Code Quality Triggers

**Automatic Agent Invocation Based on Code Metrics:**

```yaml
Function Length > 50 Lines:
  → Use the refactorer agent to:
    - Break into smaller functions
    - Extract helper methods
    - Improve readability

Nesting Depth > 3:
  → Use the refactorer agent to:
    - Flatten conditional logic
    - Extract nested blocks
    - Simplify control flow

Duplicate Code Detected:
  → Use the refactorer agent to:
    - Extract common functionality
    - Create shared utilities
    - Apply DRY principle

Circular Dependencies Found:
  → Use the architect agent to:
    - Review dependency structure
    - Redesign component relationships
    - Break circular references

Performance Concerns:
  → Use the implementer agent to:
    - Add performance measurements
    - Identify bottlenecks
    - Implement optimizations

Security Patterns Detected:
  → Use the security agent to:
    - Review authentication code
    - Validate authorization logic
    - Check encryption usage
```

---

## Agent Coordination Best Practices

### DO:
- ✅ Use workflow-coordinator first to validate workflow state
- ✅ Be explicit about which agent to use and why
- ✅ Provide clear context when chaining agents
- ✅ Validate after each agent completes
- ✅ Use parallel agents for independent tasks
- ✅ Chain agents for dependent tasks

### DON'T:
- ❌ Skip workflow-coordinator validation
- ❌ Use wrong agent for the task
- ❌ Chain agents without clear handoff
- ❌ Run dependent tasks in parallel
- ❌ Forget to validate agent output
- ❌ Over-complicate simple tasks

---

*Comprehensive agent orchestration strategies for complex implementation tasks*
