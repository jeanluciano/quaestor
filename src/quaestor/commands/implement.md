---
allowed-tools: [Read, Write, Edit, MultiEdit, Bash, Grep, Glob, TodoWrite, Task, Skill]
description: "Execute specification-driven implementation with the implementation-workflow skill"
---

# /implement - Specification-Driven Implementation

ARGUMENTS: $SPEC_ID_OR_DESCRIPTION

## Purpose
Invoke the implementation-workflow skill interactively to implement features following the complete specification-driven development process.

## Usage
```bash
# Implement a specific specification by ID
/implement spec-auth-001

# Implement by description (will find/create spec)
/implement "user authentication system"

# Resume implementation
/implement --resume
```

## Interactive Decision-Making

I will ask clarifying questions to ensure you're in control:

**Before Implementation:**
- **Approach Selection**: When multiple valid approaches exist, I'll present 2-3 options with pros/cons for you to choose
- **Scope Boundaries**: I'll confirm what's included/excluded from this implementation
- **Trade-offs**: You'll decide priorities like speed vs simplicity, flexibility vs constraints
- **Integration**: You'll choose how this connects to existing systems

**During Planning:**
- I'll present an implementation plan and WAIT for your approval before coding
- You can request changes or alternative approaches

**You maintain explicit control over key technical decisions.**

## What This Does

This command is a direct entry point to the **implementation-workflow** skill, which provides:

1. **Specification-First Development**
   - Loads or creates specifications
   - Ensures acceptance criteria are clear
   - Tracks progress automatically

2. **Quality-Focused Implementation**
   - Follows best practices and patterns
   - Includes tests from the start
   - Maintains code quality standards

3. **Complete Lifecycle**
   - Implementation → Testing → Documentation
   - Progress tracking via TODOs
   - Automatic spec updates

## The Implementation Workflow

The skill guides you through:

```yaml
workflow:
  1_load_spec:
    - Find or create specification
    - Review acceptance criteria
    - Set up TODO tracking

  2_implement:
    - Follow spec requirements
    - Write tests alongside code
    - Maintain quality standards

  3_verify:
    - Run tests
    - Check acceptance criteria
    - Update progress

  4_complete:
    - Mark criteria as complete
    - Update documentation
    - Move spec to completed
```

## When to Use

**Use `/implement` when:**
- You have a specification ready to implement
- You want structured, guided implementation
- You need automatic progress tracking
- You want quality built-in from the start

**Don't use when:**
- Just exploring code (`/research` instead)
- Quick fixes (direct edit is fine)
- Planning phase (`/plan` instead)

## Example Session

```
User: /implement spec-auth-001

🔄 Loading specification: spec-auth-001
📋 Title: User Authentication System
✅ Acceptance Criteria:
  1. [ ] Login endpoint accepts email/password
  2. [ ] JWT tokens generated on successful login
  3. [ ] Token validation middleware
  4. [ ] Logout invalidates tokens
  5. [ ] Password hashing with bcrypt

🎯 Starting implementation workflow...

[Skill invoked: implementation-workflow]

📝 Creating TODO list for tracking...
✓ Loaded implementation patterns
✓ Loaded quality standards
✓ Ready to implement

Let's start with criterion 1: Login endpoint...
```

## Skill Integration

This command loads and follows:
- `@skills/implementation-workflow/SKILL.md` - Main workflow
- `@skills/implementation-workflow/SPECS.md` - Spec handling
- `@skills/implementation-workflow/QUALITY.md` - Quality standards
- `@skills/implementation-workflow/WORKFLOW.md` - Step-by-step process
- `@skills/implementation-workflow/AGENTS.md` - When to use agents

## Arguments

```yaml
arguments:
  spec_id:
    description: "ID of specification to implement"
    example: "spec-auth-001"
    optional: true

  description:
    description: "Feature description (will find/create spec)"
    example: "user authentication"
    optional: true

  --resume:
    description: "Resume in-progress implementation"
    example: "/implement --resume"
```

## Success Criteria

Implementation is complete when:
- ✅ All acceptance criteria checked off
- ✅ Tests passing
- ✅ Code follows quality standards
- ✅ Documentation updated
- ✅ Specification moved to completed

---
*This command invokes the implementation-workflow skill for structured, quality-focused development*
