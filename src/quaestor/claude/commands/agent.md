---
allowed-tools: [Task, TodoWrite, Read, Write, Edit, MultiEdit, Bash, Glob, Grep]
description: "Manual agent control for testing - use /task for normal workflows"
performance-profile: "standard"
agent-strategy:
  default: [auto-select]
---

# /agent - Manual Agent Control (Testing)

> **Note**: This command is for testing and manual agent control. For normal workflows, use Quaestor's main commands (`/task`, `/check`, `/analyze`) which automatically leverage agents.

## Usage
```
/agent [persona] "task description"    # Use specific persona
/agent auto "task description"         # Auto-select best persona
/agent list                           # List available personas
/agent test [persona]                 # Test persona configuration
```

## Primary Agent Integration

Quaestor agents are automatically used by these commands:
- **`/task`** - Spawns agents based on complexity and task type
- **`/check`** - Uses qa, security, and performance agents
- **`/analyze`** - Deploys analysis specialists
- **`/dispatch`** - Orchestrates multi-agent workflows

## Manual Usage (Testing Only)

### Specific Persona
```
/agent architect "design plugin system for extensibility"
/agent security "review authentication implementation"
/agent researcher "find all database query patterns"
```

### Auto-Selection
```
/agent auto "optimize database queries"
# Automatically selects performance agent
```

### Testing Personas
```
/agent test security
# Shows configuration and runs validation
```

## How It Works

1. **Persona Selection**: Based on task keywords and complexity
2. **Context Preparation**: Gathers project context
3. **Agent Spawning**: Uses claude-code's Task tool
4. **Result Integration**: Formats output for Quaestor

## Integration with Commands

### In /task command
```yaml
# Automatically activated when:
- Complexity > 0.7: Spawns architect + implementer
- Security keywords: Adds security reviewer
- Multiple files: Parallel researcher agents
```

### In /check command
```yaml
# Specialized agents for:
- Linting issues: formatting agent
- Test failures: qa agent
- Security warnings: security agent
```

## Creating Custom Personas

Add to `.quaestor/agents/[name].md`:
```yaml
---
name: "custom-persona"
description: "Specialized for your project"
tools: [Read, Write, Task]
activation:
  keywords: ["your", "keywords"]
---
# Persona definition...
```

Remember: This command is mainly for testing. Use `/task` and other Quaestor commands for production workflows!