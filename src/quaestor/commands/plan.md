---
allowed-tools: [Skill, Read, Grep, Glob, TodoWrite]
description: "Create and manage specifications through skills-based planning"
---

# /plan - Lightweight Planning Router

ARGUMENTS: $DESCRIPTION

## Purpose
Routes planning requests to specialized skills for specification creation and lifecycle management.

## Usage
```
/plan                    # Create new specification (delegates to spec-writing skill)
/plan "User Auth"        # Create spec with title
/plan --status          # Show dashboard (delegates to spec-management skill)
```

## Interactive Specification Creation

The planning process is interactive - I'll ask clarifying questions to ensure the specification matches your intent:

**What I'll Ask About:**
- **Type & Scope**: What kind of work (feature/bugfix/refactor) and boundaries
- **Approach**: If multiple valid approaches exist, you choose which direction
- **Priorities**: Trade-offs between speed, simplicity, flexibility, maintainability
- **Dependencies**: What must be done first, what this blocks
- **Success Criteria**: How we'll know this is complete

**You'll make key decisions through structured questions before I generate the specification.**

## Execution

This command is a lightweight router that delegates to appropriate skills based on the request:

**Creating Specifications:**
When you request a new spec, immediately invoke the **spec-writing skill** with user requirements.

**Managing Specifications:**
When checking status or managing lifecycle (activate, complete, etc.), invoke the **spec-management skill**.

**Creating Pull Requests:**
When user mentions PR or wants to ship completed work, invoke the **pr-generation skill**.

## Routing Logic

### Request Type Detection

**New Specification:**
- Pattern: `/plan`, `/plan "title"`, "create spec", "plan feature"
- Action: Invoke `spec-writing` skill
- Pass: User requirements, title, description

**Status Dashboard:**
- Pattern: `/plan --status`, "show specs", "spec dashboard"
- Action: Invoke `spec-management` skill with status mode
- Returns: Progress overview, active specs, recommendations

**Lifecycle Management:**
- Pattern: "activate spec-X", "complete spec-X", "move spec-X"
- Action: Invoke `spec-management` skill with spec ID
- Operations: Draft→Active, Active→Completed, validation

**Pull Request Creation:**
- Pattern: "create pr", "ship spec", "pr for spec-X"
- Action: Invoke `pr-generation` skill with spec ID
- Returns: Generated PR with rich context

## Skill Delegation

This command acts as a thin router. All detailed functionality is handled by skills:

- **spec-writing**: Interactive spec creation, requirement gathering, template generation
- **spec-management**: Lifecycle management, progress tracking, status dashboard
- **pr-generation**: Pull request creation from completed specifications

## Implementation Notes

**No Complex Logic:**
This command should only:
1. Parse user intent from arguments
2. Invoke the appropriate skill with Skill tool
3. Pass through user requirements/parameters

**Example Routing:**
```
User: /plan "User Authentication"
→ Detect: New specification request
→ Invoke: Skill("spec-writing") with title="User Authentication"
→ Skill handles: Requirements, criteria, file creation

User: /plan --status
→ Detect: Status dashboard request
→ Invoke: Skill("spec-management") with mode="status"
→ Skill handles: Progress calculation, display

User: "activate spec-feature-001"
→ Detect: Lifecycle management
→ Invoke: Skill("spec-management") with operation="activate", spec="spec-feature-001"
→ Skill handles: Validation, file moving, state updates
```

## Folder Structure Reference

Specifications use folder-based state management:
```
.quaestor/specs/
├── draft/      # Planned (unlimited)
├── active/     # In progress (max 3)
└── completed/  # Finished
```

**See spec-management skill for lifecycle details.**

---

*Simple, interactive specification planning powered by Agent Skills*
