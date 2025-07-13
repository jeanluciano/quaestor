# Modes and Customization Guide

## Overview

Quaestor 0.4+ introduces flexible modes and powerful customization options to suit different workflows.

## Installation Modes

### Personal Mode (Default)

Personal mode creates a self-contained setup within your project, perfect for individual developers.

```bash
quaestor init  # or explicitly: quaestor init --mode personal
```

**File Structure:**
```
project/
├── .claude/                    # All AI files (gitignored)
│   ├── CLAUDE.md              # Context-aware rules
│   ├── commands/              # Local command copies
│   │   ├── task.md
│   │   ├── status.md
│   │   └── ...
│   └── settings.json          # Hooks configuration
├── .quaestor/                 # Optional, for docs
│   ├── ARCHITECTURE.md        # Project structure
│   ├── MEMORY.md             # Progress tracking
│   ├── command-config.yaml   # Command customization
│   └── commands/             # Command overrides
└── .gitignore                # Auto-updated with .claude/
```

**Benefits:**
- Everything is local to your project
- No global installation needed
- Easy to experiment with different rules
- Fully gitignored by default

### Team Mode

Team mode uses shared global commands with project-specific rules, ideal for consistent team standards.

```bash
quaestor init --mode team
```

**File Structure:**
```
project/
├── CLAUDE.md                  # Team rules (committed)
├── .quaestor/                 # Shared documentation
│   ├── QUAESTOR_CLAUDE.md    # AI instructions
│   ├── CRITICAL_RULES.md     # Quality standards
│   ├── ARCHITECTURE.md       # Project structure
│   ├── MEMORY.md            # Progress tracking
│   └── command-config.yaml  # Command config
├── ~/.claude/commands/       # Global commands (shared)
└── .claude/settings.json    # Local hooks only
```

**Benefits:**
- Consistent commands across all projects
- Shared team standards in version control
- Central command updates
- Project-specific overrides still possible

## Context-Aware Rules

Quaestor analyzes your project and generates appropriate rules:

### Project Analysis

The `ProjectAnalyzer` checks for:
- Programming language (Python, Rust, JS/TS, Go, etc.)
- Project size (file count, directory depth)
- Test framework presence
- CI/CD configuration
- Team markers (CODEOWNERS, PR templates)
- Documentation presence

### Rule Levels

1. **Minimal Rules** (Simple Projects)
   - Basic code quality checks
   - Simple testing requirements
   - Documentation reminders

2. **Standard Rules** (Typical Projects)
   - Progressive workflow (research for complex tasks)
   - Quality gates before implementation
   - Agent delegation suggestions

3. **Strict Rules** (Complex/Team Projects)
   - Mandatory research phase
   - Required planning with approval
   - Forced agent usage for multi-file tasks
   - Continuous validation

### Disable Contextual Analysis

To use basic rules regardless of project complexity:
```bash
quaestor init --no-contextual
```

## Command Configuration

### Configuration File

Create a configuration file to customize command behavior:

```bash
quaestor configure --init
```

This creates `.quaestor/command-config.yaml`:

```yaml
# Command Configuration
commands:
  task:
    enforcement: default  # Options: strict, default, relaxed
    require_planning: true
    agent_threshold: 3
    parameters:
      minimum_test_coverage: 80
      max_function_lines: 50
    custom_rules:
      - Always use type hints in Python code
      - Include integration tests for API changes
  
  check:
    auto_fix: true
    strict_mode: false
    include_checks:
      - lint
      - test
      - type
  
  milestone:
    auto_commit: true
    require_tests: true
```

### Configuration Options

#### Enforcement Levels

- **strict**: All rules are mandatory, zero tolerance
- **default**: Standard enforcement with some flexibility
- **relaxed**: Focus on practicality over strict compliance

#### Parameters

Override specific values used by commands:
- `minimum_test_coverage`: Required test coverage percentage
- `max_function_lines`: Maximum lines per function
- `agent_threshold`: Files to modify before using agents

#### Custom Rules

Add project-specific requirements that will be enforced:
```yaml
custom_rules:
  - All database queries must use prepared statements
  - API endpoints require rate limiting
  - Use dependency injection for all services
```

## Command Overrides

For complete control, create custom command implementations:

```bash
quaestor configure --command task --create-override
```

This creates `.quaestor/commands/task.md` that you can edit:

```markdown
---
allowed-tools: all
description: Project-specific task implementation
---

# TASK COMMAND - CUSTOM OVERRIDE

## PROJECT-SPECIFIC WORKFLOW

1. Check security implications
2. Review performance impact
3. Standard implementation
4. Security scan before completion

[... your custom implementation ...]
```

## Command Loading Hierarchy

Commands are loaded in this order (first match wins):

1. **Personal Mode**: `.claude/commands/task.md`
2. **Project Override**: `.quaestor/commands/task.md`
3. **Configuration**: `.quaestor/command-config.yaml` modifies base
4. **Global**: `~/.claude/commands/task.md` (base command)

## Ambient Rule Enforcement

Unlike systems that only enforce rules within commands, Quaestor's rules work ambiently:

### Example: Thinking Patterns

```markdown
<!-- In CLAUDE.md -->
## 🧠 THINKING PATTERNS

Before EVERY response, I'll consider:

1. **Complexity Check**: 
   - Simple request? → Direct implementation
   - Multiple components? → "Let me research and plan this"
   - Unclear requirements? → "I need clarification on..."

2. **Quality Gates**:
   - About to write code? → Consider tests first
   - Touching existing code? → Research patterns first
   - Making claims? → Verify with checks

3. **Delegation Triggers**:
   ```
   if (files_to_modify > 3 || parallel_tasks_possible) {
     say("I'll spawn agents to handle this efficiently")
   }
   ```
```

These patterns influence Claude's behavior even in regular conversation!

## Migration Guide

### From Global to Personal Mode

If you have an existing global Quaestor installation:

```bash
# In your project
quaestor init --mode personal

# Your global commands remain untouched
# New project uses local commands
```

### From Personal to Team Mode

To convert a personal project to team standards:

```bash
# First, commit any important customizations
git add .quaestor/

# Reinitialize in team mode
quaestor init --mode team --force

# Your customizations in .quaestor/ are preserved
```

## Best Practices

### For Personal Projects

1. Use personal mode (default)
2. Customize freely in `.claude/CLAUDE.md`
3. Override specific commands as needed
4. Keep `.claude/` in .gitignore

### For Team Projects

1. Use team mode for consistency
2. Put shared rules in `.quaestor/CRITICAL_RULES.md`
3. Use `command-config.yaml` for project standards
4. Commit `.quaestor/` to version control

### For Open Source Projects

1. Use team mode with minimal rules
2. Document AI assistant setup in README
3. Provide example overrides for contributors
4. Keep rules focused on project standards

## Troubleshooting

### Commands Not Working as Expected

1. Check which mode you're in:
   ```bash
   quaestor configure
   ```

2. Verify command loading order
3. Look for overrides in `.quaestor/commands/`
4. Check `command-config.yaml` settings

### Rules Too Strict/Lenient

1. Adjust enforcement in `command-config.yaml`:
   ```yaml
   commands:
     task:
       enforcement: relaxed  # or strict
   ```

2. Or reinitialize with different settings:
   ```bash
   quaestor init --no-contextual  # Simple rules
   ```

### Updating Commands

Personal mode:
```bash
quaestor update  # Updates templates, preserves customizations
```

Team mode:
```bash
# Updates global commands for all projects
cd any-project && quaestor update
```