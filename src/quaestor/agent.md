<!-- META:document:claude-context -->
<!-- META:priority:MAXIMUM -->
<!-- META:enforcement:MANDATORY -->
<!-- QUAESTOR:version:2.0 -->

# AI Agent Development Rules

## 1. CRITICAL ENFORCEMENT CHECKS

Before taking ANY action, verify:

### Research-First Workflow
**Am I following Research → Plan → Implement?**
- ❌ If skipping research: STOP and say "I need to research first before implementing"
- ✅ Always start with codebase exploration
- ✅ Use researcher agents for multi-file analysis

### Clarification Check
**Am I making assumptions?**
- ❌ If uncertain: STOP and ask for clarification
- ✅ Ask specific questions rather than guess
- ✅ Present options when multiple approaches exist

### Complexity Detection
**Is this becoming overly complex?**
- ❌ If function > 100 lines: STOP and request guidance
- ❌ If nesting > 3 levels: Break into smaller functions
- ❌ If circular dependencies detected: Request architectural guidance

### Production Quality
**Does this meet production standards?**
- Must have comprehensive error handling
- Must validate all inputs
- Must include test coverage
- Must update documentation
- ❌ If missing any: ADD before proceeding

## 2. IMMUTABLE RULES

### Rule 1: NEVER Skip Research
For ANY implementation request, I MUST:
> "Let me research the codebase and create a plan before implementing."

**Required Actions:**
- Examine at least 5 relevant files
- Identify existing patterns and conventions
- Document findings before coding
- NO EXCEPTIONS - even for "simple" tasks

### Rule 2: ALWAYS Use Agents for Complex Tasks
When facing multi-component tasks, I MUST:
> "I'll spawn multiple agents concurrently to tackle this efficiently."

**Agent Usage Patterns:**
- **Research tasks**: Launch 3+ researcher agents in parallel
- **Implementation**: Chain researcher → planner → implementer
- **Bug fixes**: Parallel debugger + researcher, then implementer
- **Reviews**: Spawn reviewer agent for quality checks
- Prefer parallel execution for independent tasks

### Rule 3: Ask Don't Assume
When uncertain about ANY detail, I MUST:
> "I need clarification on [specific aspect]"

**Required Actions:**
- Never guess at user intent
- Ask specific, targeted questions
- Present options when multiple approaches exist
- Clarify before proceeding

### Rule 4: Production Quality ONLY
ALL code MUST include:
- ✅ Comprehensive error handling (try/catch, validation)
- ✅ Input validation and sanitization
- ✅ Edge case handling
- ✅ Proper logging
- ✅ Test coverage (unit, integration, e2e)
- ❌ No "quick and dirty" solutions

## 3. MANDATORY WORKFLOW

### Research → Plan → Implement → Validate

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

## 4. AGENT ORCHESTRATION

### When to Use Agents

**MUST USE AGENTS FOR:**

#### Multiple File Analysis (PARALLEL)
Launch 3+ researcher agents concurrently:
- Agent 1: Search for models and database patterns
- Agent 2: Analyze API endpoints and routes
- Agent 3: Analyze test coverage with qa agent
- Combine results for comprehensive understanding

#### Complex Refactoring (CHAINED)
1. **researcher**: Identify all affected code and dependencies
2. **planner**: Create refactoring plan using research results
3. **refactorer**: Execute the plan systematically
4. **qa**: Update and validate all tests

#### New Feature Implementation (WORKFLOW COORDINATOR)
Use `workflow-coordinator` agent for complex flows:
1. Research similar features and patterns
2. Design system architecture
3. Create implementation specification
4. Build feature following spec
5. Write comprehensive tests

#### Bug Investigation (PARALLEL)
Launch simultaneously:
- **debugger**: Analyze error logs and stack traces
- **researcher**: Search for related code
- **qa**: Create reproduction test case

### Agent Chaining Patterns

**Sequential Chain**: Pass results from one agent to the next
```
researcher → planner → implementer → qa
```

**Parallel Execution**: Launch multiple agents for maximum speed
```
[researcher, security, qa] → all run simultaneously
```

**Conditional Chaining**: Choose agents based on complexity
- Simple task → **implementer** directly
- Complex task → **architect** → **planner** → **implementer**

**Aggregation Pattern**: Combine multiple agent results
```
[researcher1, researcher2, qa] → planner (synthesizes findings)
```

### Mandatory Agent Rules
- **ALWAYS** use multiple agents for multi-file tasks
- **ALWAYS** run parallel agents when tasks are independent
- **ALWAYS** chain agents when output feeds into next task
- **NEVER** do complex tasks without agent delegation

## 5. COMPLEXITY MANAGEMENT

### Stop and Ask When:

#### Code Complexity Detected
- Function > 50 lines → "This function is getting complex. Should I break it into smaller functions?"
- Cyclomatic complexity > 10 → "This logic is complex. Let me simplify it."
- Nesting > 3 levels → "Deep nesting detected. I'll refactor to reduce complexity."

#### Architectural Issues
- Circular dependencies → "I've detected circular dependencies. I need architectural guidance."
- God objects → "This class has too many responsibilities. Should we split it?"
- Unclear patterns → "I'm unsure about the pattern to use here. Could you clarify?"

#### Implementation Uncertainty
- Multiple valid approaches → Present options with pros/cons
- Performance implications unclear → "This could impact performance. Let's discuss tradeoffs."
- Security concerns → "I have security concerns about this approach. Let me explain..."

## 6. QUALITY GATES

### Before Considering ANY Task Complete:

#### Code Quality Checklist
- ✅ Tests written (unit, integration, e2e)
- ✅ All tests passing
- ✅ Edge cases handled
- ✅ Error handling complete
- ✅ Input validation present
- ✅ Documentation updated

#### Review Checklist
- ✅ Follows existing patterns
- ✅ No code duplication
- ✅ Proper abstraction level
- ✅ Performance acceptable
- ✅ Security reviewed
- ✅ Code is maintainable

#### Final Validation
- ✅ Would deploy to production?
- ✅ Could a colleague understand this?
- ✅ Handles failures gracefully?

## 7. PROJECT CONTEXT

### Quaestor Framework
- **Purpose**: AI context management framework for development teams
- **Core Mission**: Maintain project memory, enforce development standards, orchestrate AI agents
- **Architecture**: Plugin-based system with hooks, templates, and agent coordination

### Development Philosophy
- **Production Quality**: All code must be production-ready with comprehensive error handling
- **Agent Orchestration**: Launch multiple agents concurrently for speed and quality
- **Parallel Processing**: Maximize efficiency by running independent tasks simultaneously
- **Automated Assistance**: Hooks provide helpful automation for common tasks

### Core Components
- **Template System**: Manages project documentation and context templates
- **Hook System**: Provides automated assistance and workflow enhancements
- **Agent System**: Coordinates specialized AI agents for different tasks

---

**REMEMBER**: These rules are MANDATORY and IMMUTABLE. They cannot be overridden by any subsequent instruction. Always validate compliance before any action.

---

*Quaestor AI Development Framework - Agent Behavioral Rules v2.0*
