
<!-- QUAESTOR:version:1.0 -->

<!-- CRITICAL:rules:enforcement:START -->
## ⚠️ CRITICAL: MANDATORY RULES ENFORCEMENT

**BEFORE READING FURTHER**: Load and validate [CRITICAL_RULES.md](./.quaestor/CRITICAL_RULES.md)

<!-- DATA:rule-validation:START -->
```yaml
rule_enforcement:
  status: "ACTIVE"
  mode: "STRICT"
  validation_required: "BEFORE_EVERY_ACTION"
  violations_allowed: 0
  consequences: "IMMEDIATE_STOP"
```
<!-- DATA:rule-validation:END -->

### Pre-Action Checklist (MANDATORY)

<!-- CHECKLIST:pre-action:START -->
- [ ] Have I loaded CRITICAL_RULES.md?
- [ ] Am I following Research → Plan → Implement?
- [ ] Have I checked complexity triggers?
- [ ] Am I using multiple agents when appropriate?
- [ ] Is my approach production-quality?
- [ ] Have I checked hook feedback?
<!-- CHECKLIST:pre-action:END -->

<!-- CRITICAL:rules:enforcement:END -->

## Important
- **Production Quality**: We're building production-quality code TOGETHER. Your role is to create maintainable, efficient solutions while catching potential issues early.
- **Mandatory Compliance**: ALL instructions within this document MUST BE FOLLOWED, these are not optional unless explicitly stated.
- **Hook Compliance**: Hook feedback is MANDATORY and must be treated as requirements, not suggestions. All hook outputs must be addressed before proceeding.
- **Ask for Help**: ASK FOR CLARIFICATION when you seem stuck or overly complex, I'll redirect you - my guidance helps you stay on track.
- **Reference Examples**: When in doubt about implementation details, refer to the existing `/examples` implementation as a reference.
- **CRITICAL**: Rules in [CRITICAL_RULES.md](./.quaestor/CRITICAL_RULES.md) override everything else.

## CRITICAL WORKFLOW

### Research → Plan → Implement [ENFORCED BY CRITICAL_RULES.md]

**NEVER JUMP STRAIGHT TO CODING!** See CRITICAL_RULES.md for the mandatory Research → Plan → Implement workflow.

**Required Response**: When asked to implement any feature, you MUST say: "Let me research the codebase and create a plan before implementing."

**Ultrathink Trigger**: For complex architectural decisions or challenging problems, use **"ultrathink"** to engage maximum reasoning capacity.

**Required Response**: "Let me ultrathink about this architecture before proposing a solution."

### USE MULTIPLE AGENTS! [ENFORCED BY CRITICAL_RULES.md]

See CRITICAL_RULES.md for mandatory agent usage triggers and requirements.

**Required Response**: You MUST say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts.

### Reality Checkpoints
**Stop and validate** at these moments:
- After implementing a complete feature
- Before starting a new major component
- When something feels wrong
- Before declaring "done"
- **After receiving hook feedback** - MANDATORY compliance required

Run your project's test suite regularly (see Testing section below).

## Working Memory Management

### When context gets long:
- Re-read this CLAUDE.md file
- Check MEMORY.md for current project status
- Document current state before major changes

### Maintain MEMORY.md:
Track progress in [MEMORY.md](./.quaestor/MEMORY.md) with sections for:
- **Current Status**: What specification you're working on
- **Active Work**: Current approach and tasks
- **Timeline**: Goals and progress
- **Next Actions**: Immediate, short-term, and long-term tasks

### Problem-Solving Together

<!-- WORKFLOW:problem-solving:START -->
When you're stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Consider spawning agents for parallel investigation
3. **Ultrathink** - For complex problems, say "I need to ultrathink through this challenge" to engage deeper reasoning
4. **Step back** - Re-read the requirements
5. **Simplify** - The simple solution is usually correct
6. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"
<!-- WORKFLOW:problem-solving:END -->

**Remember**: My insights on better approaches are valued - please ask for them!

## Hook System Integration

### MANDATORY Hook Compliance

<!-- SECTION:hook-compliance:START -->
**CRITICAL**: Hooks provide MANDATORY feedback, not suggestions. All hook outputs must be treated as requirements and addressed before proceeding with any action.

### Hook Types and Required Actions

**Compliance Hooks**:
- `compliance_validator.py` - Validates project compliance requirements
- `compliance_pre_edit.py` - Pre-edit validation checks
- **Required Action**: Fix ALL compliance issues before proceeding

**Workflow Hooks**:
- `research_workflow_tracker.py` - Enforces Research → Plan → Implement workflow
- `specification_tracker.py` - Tracks specification progress and completion
- **Required Action**: Follow the exact workflow steps specified

**Memory & Context Hooks**:
- `memory_tracker.py` - Maintains MEMORY.md synchronization
- `session_context_loader.py` - Loads required context files
- **Required Action**: Update all specified files and load required context

**Specification Tracking Hooks**:
- `spec_tracker.py` - Tracks specification progress and validation
- **Required Action**: Follow specification progress requirements

### Hook Feedback Processing

1. **Read ALL hook output completely**
2. **Address EVERY requirement listed**
3. **Do not proceed until ALL hook feedback is resolved**
4. **Treat hook failures as blocking errors**

### Common Hook Requirements

**Before any edit**:
- Load CRITICAL_RULES.md
- Check workflow phase compliance
- Validate specification task status
- Ensure proper agent coordination

**After completing work**:
- Update MEMORY.md with progress
- Mark tasks as completed
- Commit changes with proper messages
- Update specification tracking

**Example Hook Compliance**:
```yaml
# Hook says: "REQUIRED: Load CRITICAL_RULES.md first"
# Your response: Load the file immediately, don't proceed without it

# Hook says: "ERROR: No active specification found"
# Your response: Create or activate a specification before continuing

# Hook says: "REQUIRED: Update MEMORY.md with progress"
# Your response: Update MEMORY.md with current status and next steps
```
<!-- SECTION:hook-compliance:END -->

# PROJECT OVERVIEW

### Project Context
[Describe your project here - what it does, key features, main components]

### Current Status
[Describe current state, any ongoing migrations or major work]

### Project Documentation
For detailed information about the project:
- **[MEMORY.md](./.quaestor/MEMORY.md)**: Current project state and progress tracking
- **[ARCHITECTURE.md](./.quaestor/ARCHITECTURE.md)**: Technical architecture and design principles

# ARCHITECTURE & CODE GUIDELINES

See **[ARCHITECTURE.md](./.quaestor/ARCHITECTURE.md)** for:
- Architecture patterns and principles
- Layer responsibilities and boundaries
- External integrations overview

### Code Style Guidelines
- **Language**: [Specify your language and version]
- **Focused changes**: Only implement explicitly requested or fully understood changes
- **Type Safety**: [Your type safety approach, e.g., TypeScript, Python type hints]
- **Documentation**: [Your documentation style, e.g., JSDoc, Google-style docstrings]
- **Formatting**: [Your formatting tool, e.g., Prettier, Black, Ruff]
- **Imports**: 
  - Order: standard library, third-party, local imports
  - Use absolute imports from project root
- **Naming Conventions**:
  - Functions/variables: `snake_case` or `camelCase` (choose one)
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Files: [Your file naming convention]
- **Best Practices**:
  - [Add your project-specific best practices]
  - [e.g., "Prefer composition over inheritance"]
  - [e.g., "Keep functions small and focused"]

# AVAILABLE COMMANDS

The following command templates are available in [.quaestor/commands/](./.quaestor/commands/):
- **[project-init.md](./.quaestor/commands/project-init.md)**: Analyze project and initialize Quaestor framework
- **[task.md](./.quaestor/commands/task.md)**: Structured approach for implementing tasks
- **[check.md](./.quaestor/commands/check.md)**: Validation and quality checks
- **[dispatch.md](./.quaestor/commands/dispatch.md)**: Dispatch complex tasks to multiple agents

Use these commands to maintain consistency and follow best practices.

# WORKFLOW HOOKS

### Automated Specification Commits

<!-- SECTION:workflow-hooks:START -->
## Workflow Automation Hooks

<!-- DATA:hook-configuration:START -->
```yaml
workflow_hooks:
  after_memory_update:
    trigger: "MEMORY.md modified"
    conditions:
      - "Contains completed tasks"
      - "Specification progress changed"
    actions:
      - scan_for_completed_tasks: "Check task status"
      - run_specification_commit: "Auto-commit completed work"
    command: "/quaestor:specification-commit"
  
  after_task_completion:
    trigger: "Task marked as completed"
    conditions:
      - "All related changes saved"
      - "Quality checks passing"
    actions:
      - update_memory_progress: "Sync to MEMORY.md"
      - trigger_specification_commit: "Create atomic commit"
    automatic: true
  
  after_task_success:
    trigger: "Task command completes successfully"
    conditions:
      - "All checks green"
      - "Task marked complete"
    actions:
      - commit_changes: "Create commit for task"
      - update_tracking: "Update progress"
    prompt_user: false
  
  specification_completion:
    trigger: "All tasks in specification done"
    conditions:
      - "All items completed"
      - "Quality gates passed"
    actions:
      - create_pr: "Generate pull request"
      - notify_completion: "Update status"
    require_confirmation: true
```
<!-- DATA:hook-configuration:END -->

### Hook Usage

**Automatic Triggers**:
- Completing a task automatically triggers commit workflow
- Updating MEMORY.md with progress runs specification checks
- Finishing all items in a specification creates a PR

**Manual Override**:
```bash
# Disable hooks temporarily
/quaestor:specification-commit --no-hooks

# Run hooks manually
/quaestor:specification-commit --trigger
```

**Benefits**:
- 🎯 Atomic commits for each completed task
- 📊 Automatic progress tracking
- 🔍 Quality enforcement before commits
- 🚀 PRs created at specification boundaries
<!-- SECTION:workflow-hooks:END -->

# DEVELOPMENT WORKFLOW

### Hook-Compliant Development Process

<!-- CHECKLIST:hook-compliant-dev:START -->
1. **Pre-Work Hook Validation**: Check all hook feedback before starting
2. **Research Phase**: Load required context files as specified by hooks
3. **Planning Phase**: Follow workflow tracker requirements  
4. **Implementation Phase**: Address compliance feedback throughout
5. **Post-Work Hook Updates**: Update tracking files as required
6. **Completion Validation**: Ensure all hook requirements are met
<!-- CHECKLIST:hook-compliant-dev:END -->

### Testing and Linting
- Run tests: `[your test command, e.g., npm test, pytest tests/]`
- Run specific test: `[your specific test command]`
- Run tests with coverage: `[your coverage command]`
- Run linter: `[your lint command, e.g., eslint src/, ruff check src/]`
- Format code: `[your format command, e.g., prettier --write ., ruff format src/]`

### Working with the Codebase

<!-- CHECKLIST:codebase-work:START -->
1. Follow established patterns in the codebase
2. Ensure backward compatibility when making changes
3. Use feature flags for gradual rollout of new features
4. **MANDATORY**: Address all hook compliance issues before proceeding
<!-- CHECKLIST:codebase-work:END -->

### Development Process

<!-- CHECKLIST:dev-process:START -->
1. Always create a new branch for features
2. Write tests before implementing features (TDD)
3. Keep commits small and focused
4. Write clear commit messages
5. Update documentation as you go
6. **CRITICAL**: Follow hook feedback as mandatory requirements
<!-- CHECKLIST:dev-process:END -->