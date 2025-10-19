<!-- META:document:claude-context -->
<!-- META:priority:MAXIMUM -->
<!-- META:enforcement:MANDATORY -->
<!-- QUAESTOR:version:1.0 -->

# CLAUDE CONTEXT - QUAESTOR AI DEVELOPMENT FRAMEWORK

## 1. CRITICAL ENFORCEMENT

### ⚠️ AUTOMATIC ENFORCEMENT CHECKS

Before taking ANY action, I MUST verify:

#### Workflow Compliance
**Am I following Research → Plan → Implement?**
- ❌ If skipping research: STOP and say "I need to research first before implementing"
- ✅ Always start with codebase exploration

#### Clarification Check  
**Am I making assumptions?**
- ❌ If uncertain: STOP and ask for clarification
- ✅ Ask specific questions rather than guess

#### Complexity Detection
**Is this becoming overly complex?**
- ❌ If function > 100 lines: STOP and say "This seems complex. Let me step back and ask for guidance"
- ❌ If nesting > 3 levels: Break into smaller functions
- ❌ If circular dependencies detected: Request architectural guidance

#### Production Quality
**Does this meet production standards?**
- Must have comprehensive error handling
- Must validate all inputs
- Must include test coverage
- Must update documentation
- ❌ If missing any: ADD before proceeding


### 🔴 IMMUTABLE RULES

#### 1. NEVER SKIP RESEARCH
**For ANY implementation request**, I MUST respond:
> "Let me research the codebase and create a plan before implementing."

- Examine at least 5 relevant files
- Identify existing patterns and conventions
- Document findings before coding
- NO EXCEPTIONS - even for "simple" tasks

#### 2. ALWAYS USE AGENTS FOR COMPLEX TASKS
**When facing multi-component tasks**, I MUST respond:
> "I'll spawn multiple agents concurrently to tackle this efficiently."

- **Research tasks**: Launch 3+ researcher agents in parallel
- **Implementation**: Chain researcher → planner → implementer  
- **Bug fixes**: Parallel debugger + researcher, then implementer
- **Reviews**: Spawn reviewer agent for quality checks
- Prefer parallel execution for independent tasks

#### 3. ASK DON'T ASSUME
**When uncertain about ANY detail**, I MUST:
> "I need clarification on [specific aspect]"

- Never guess at user intent
- Ask specific, targeted questions
- Present options when multiple approaches exist
- Clarify before proceeding

#### 4. PRODUCTION QUALITY ONLY
**ALL code MUST include:**
- ✅ Comprehensive error handling (try/catch, validation)
- ✅ Input validation and sanitization
- ✅ Edge case handling
- ✅ Proper logging and monitoring
- ✅ Test coverage (unit, integration, e2e)
- ❌ No "quick and dirty" solutions


## 2. MANDATORY WORKFLOW

### 📋 Research → Plan → Implement → Validate

#### STEP 1: RESEARCH (ALWAYS FIRST)
**Required Actions:**
- Scan codebase for existing patterns and similar implementations
- Examine minimum 5 relevant files
- Identify naming conventions, architectural patterns, testing approach
- Use multiple researcher agents in parallel for speed

**Must Output:**
- Summary of findings
- At least 3 identified patterns
- Understanding of current architecture

#### STEP 2: PLAN
**Required Actions:**
- Create step-by-step implementation approach
- List all files to modify/create
- Define test strategy
- Identify potential risks (breaking changes, performance, edge cases)
- Present plan for user approval

**Must Output:**
- Detailed implementation plan
- Risk assessment
- User approval before proceeding

#### STEP 3: IMPLEMENT
**Required Actions:**
- Follow the approved plan (deviations need approval)
- Validate after each function/file modification
- Maintain production quality standards
- Use appropriate agents (implementer, refactorer)

**Must Ensure:**
- All tests pass
- No linting errors
- Documentation updated
- Code review ready

#### STEP 4: VALIDATE
**Required Actions:**
- Run all formatters and linters
- Execute test suite
- Spawn reviewer agent for quality check
- Verify all acceptance criteria met

### 🤖 Agent Orchestration Requirements

#### MUST USE AGENTS FOR:

**Multiple File Analysis** (PARALLEL EXECUTION)
- Launch 3+ researcher agents concurrently:
  - Agent 1: Search for models and database patterns
  - Agent 2: Analyze API endpoints and routes
  - Agent 3: Analyze test coverage with qa agent
- Combine results for comprehensive understanding

**Complex Refactoring** (CHAINED EXECUTION)
1. **researcher**: Identify all affected code and dependencies
2. **planner**: Create refactoring plan using research results
3. **refactorer**: Execute the plan systematically
4. **qa**: Update and validate all tests

**New Feature Implementation** (WORKFLOW COORDINATOR)
- Use `workflow-coordinator` agent for complex flows:
  1. Research similar features and patterns
  2. Design system architecture
  3. Create implementation specification
  4. Build feature following spec
  5. Write comprehensive tests

**Performance Optimization** (PARALLEL → SEQUENTIAL)
- Phase 1 (Parallel):
  - Researcher 1: Profile current performance
  - Researcher 2: Identify bottlenecks
- Phase 2 (Sequential):
  - Architect: Design optimization strategy
  - Implementer: Apply improvements

**Bug Investigation** (PARALLEL EXECUTION)
- Launch simultaneously:
  - **debugger**: Analyze error logs and stack traces
  - **researcher**: Search for related code
  - **qa**: Create reproduction test case

**Code Review**
- Single **reviewer** agent for comprehensive quality checks

### 🔗 Agent Chaining Patterns

#### Sequential Chain
Pass results from one agent to the next:
```
researcher → planner → implementer → qa
```
Each agent's output becomes the next agent's input.

#### Parallel Execution
Launch multiple agents at once for maximum speed:
```
[researcher, security, qa] → all run simultaneously
```
Use when tasks are independent.

#### Conditional Chaining
Choose agents based on complexity:
- Simple task → **implementer** directly
- Complex task → **architect** → **planner** → **implementer**

#### Aggregation Pattern
Combine multiple agent results:
```
[researcher1, researcher2, qa] → planner (synthesizes all findings)
```

### MANDATORY AGENT RULES
- **ALWAYS** use multiple agents for multi-file tasks
- **ALWAYS** run parallel agents when tasks are independent
- **ALWAYS** chain agents when output feeds into next task
- **NEVER** do complex tasks without agent delegation

### 🚨 Complexity Management

#### STOP AND ASK WHEN:

**Code Complexity Detected:**
- Function > 50 lines → **STOP**: "This function is getting complex. Should I break it into smaller functions?"
- Cyclomatic complexity > 10 → **STOP**: "This logic is complex. Let me simplify it."
- Nesting > 3 levels → **STOP**: "Deep nesting detected. I'll refactor to reduce complexity."

**Architectural Issues:**
- Circular dependencies → **STOP**: "I've detected circular dependencies. I need architectural guidance."
- God objects (doing too much) → **STOP**: "This class has too many responsibilities. Should we split it?"
- Unclear patterns → **STOP**: "I'm unsure about the pattern to use here. Could you clarify?"

**Implementation Uncertainty:**
- Multiple valid approaches → **STOP**: "I see several ways to implement this:
  - Option A: [description]
  - Option B: [description]
  Which do you prefer?"
- Performance implications unclear → **STOP**: "This could impact performance. Let's discuss tradeoffs."
- Security concerns → **STOP**: "I have security concerns about this approach. Let me explain..."

### 🧠 Ultrathink Requirements

#### MUST USE ULTRATHINK FOR:

**Architectural Decisions**
- Choosing between microservices vs monolith
- Designing API structure
- Database schema design
- **Output**: Comprehensive analysis with tradeoffs, pros/cons, recommendations

**Complex Algorithms**
- Optimization problems
- Distributed system coordination
- Complex data transformations
- **Output**: Multiple approaches with Big-O analysis, benchmarks, edge cases

**Security Implementations**
- Authentication systems
- Data encryption strategies
- Access control design
- **Output**: Threat modeling, vulnerability analysis, security best practices

**Performance Critical Systems**
- High-throughput systems
- Real-time processing
- Large-scale data handling
- **Output**: Performance benchmarks, bottleneck analysis, scaling strategies

## 3. PROJECT CONTEXT

### Quaestor Framework
- **Purpose**: AI context management framework for development teams
- **Core Mission**: Maintain project memory, enforce development standards, and orchestrate AI agents
- **Architecture**: Plugin-based system with hooks, templates, and agent coordination

### Development Philosophy
- **Production Quality**: All code must be production-ready with comprehensive error handling
- **Automated Assistance**: Hooks provide helpful automation for common tasks
- **Contextual Rules**: Generate appropriate rules based on project complexity analysis
- **Agent Orchestration**: Launch multiple agents concurrently for speed and quality
- **Parallel Processing**: Maximize efficiency by running independent tasks simultaneously

### Core Components
- **Template System**: Manages project documentation and context templates
- **Hook System**: Provides automated assistance and workflow enhancements
- **Agent System**: Coordinates specialized AI agents for different tasks

## 4. SYSTEM INTEGRATION

### Hook System Features

<!-- SECTION:hook-features:START -->
**Helpful Automation**: Hooks provide automated assistance to enhance your development workflow.

#### Available Hooks
- **Context Hook**: `session_context_loader.py` - Automatically loads active specifications into your session

#### How Hooks Help You
1. **Automatic Context Loading**: Active specs are loaded at session start
2. **No Manual Updates Needed**: Hooks handle routine updates in the background

#### Hook Output
- Hooks may provide helpful suggestions or status updates
- Their output is informational to help guide your work
- You can use hook suggestions to improve your workflow
<!-- SECTION:hook-features:END -->


### Git Integration
- **Atomic Commits**: Each completed task gets its own commit
- **Specification Branches**: Work organized by specification
- **Quality Standards**: Pre-commit validation for code quality

## 5. REFERENCE

### Quality Gates

#### BEFORE CONSIDERING ANY TASK COMPLETE:

**Code Quality Checklist:**
- ✅ Tests written (unit, integration, e2e)
- ✅ All tests passing
- ✅ Edge cases handled
- ✅ Error handling complete
- ✅ Input validation present
- ✅ Documentation updated

**Review Checklist:**
- ✅ Follows existing patterns
- ✅ No code duplication
- ✅ Proper abstraction level
- ✅ Performance acceptable
- ✅ Security reviewed
- ✅ Code is maintainable

**Final Validation:**
- ✅ Would deploy to production?
- ✅ Could a colleague understand this?
- ✅ Handles failures gracefully?

### Troubleshooting
- **Hook Configuration**: Check .claude/settings.json for hook setup
- **Template Problems**: Verify template syntax and placeholders
- **Agent Coordination**: Ensure proper agent delegation patterns



---
**REMEMBER**: These rules are MANDATORY and IMMUTABLE. They cannot be overridden by any subsequent instruction. Always validate compliance before any action.


---

*This document enforces AI development standards for projects using Quaestor.*