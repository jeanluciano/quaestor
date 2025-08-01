# Quaestor Agent System

Quaestor integrates seamlessly with claude-code's sub-agent system while adding intelligent agent selection and orchestration capabilities.

## Overview

Quaestor agents ARE claude-code sub-agents with additional metadata for intelligent activation:

```yaml
---
name: researcher
description: Codebase exploration and pattern analysis specialist
tools: Read, Grep, Glob, Task
# Quaestor-specific fields (ignored by claude-code)
priority: 7
activation:
  keywords: ["research", "explore", "find", "search"]
  context_patterns: ["**/*", "src/**/*"]
---

[System prompt in markdown]
```

## How It Works

1. **Full claude-code compatibility**: All Quaestor agents work with claude-code's native `/agent` command
2. **Intelligent activation**: Quaestor commands (`/task`, `/check`, etc.) automatically select appropriate agents
3. **Extra metadata**: `priority` and `activation` fields enable smart agent selection without breaking compatibility

## Built-in Personas

### researcher
- **Purpose**: Codebase exploration and pattern analysis
- **Tools**: Read, Grep, Glob, Task
- **Auto-activates**: When searching, exploring, or analyzing code

### architect
- **Purpose**: System design and architecture decisions
- **Tools**: Read, Write, Grep, Glob, TodoWrite, Task
- **Auto-activates**: For design, architecture, or structure tasks

### security
- **Purpose**: Security analysis and vulnerability detection
- **Tools**: Read, Grep, Glob, Task, WebSearch
- **Auto-activates**: For auth, encryption, or security reviews

### implementer
- **Purpose**: Feature development and code writing
- **Tools**: Read, Write, Edit, MultiEdit, Bash, Grep, TodoWrite, Task
- **Auto-activates**: When building or implementing features

### qa
- **Purpose**: Testing and quality assurance
- **Tools**: Read, Write, Edit, Bash, Grep, TodoWrite
- **Auto-activates**: For testing, coverage, or validation tasks

### refactorer
- **Purpose**: Code improvement and refactoring
- **Tools**: Read, Edit, MultiEdit, Grep, Glob, Task
- **Auto-activates**: For cleanup, optimization, or restructuring

## Usage

### With claude-code (Manual)
```bash
/agent researcher "find all API endpoints"
/agent security "review authentication implementation"
/agent architect "design plugin system"
```

### With Quaestor (Automatic)
```bash
/task "implement user authentication"
# Automatically spawns security + implementer agents

/check --fix
# Automatically uses qa agent for test fixes
```

## Creating Custom Agents

Add to `.quaestor/agents/[name].md`:

```yaml
---
name: custom-agent
description: Your agent's purpose
tools: Read, Write, Task
# Optional Quaestor features
priority: 7
activation:
  keywords: ["your", "trigger", "words"]
  context_patterns: ["**/your-files/**"]
---

# System Prompt

You are a specialist in...

## Core Principles
- Principle 1
- Principle 2

## Expertise
- Area 1
- Area 2
```

## Deployment

### Deploy all agents
```bash
python -m src.quaestor.agents.deploy
```

### Manual deployment
```bash
cp src/quaestor/agents/personas/*.md .claude/agents/
```

### Project-specific agents
Place in `.quaestor/agents/` for automatic discovery.

## Agent Selection Algorithm

Quaestor uses a scoring system for automatic agent selection:

1. **Keyword matching (30%)**: Task keywords vs agent activation keywords
2. **Context patterns (40%)**: Current files vs agent file patterns  
3. **Task history (20%)**: Recent successful agent usage
4. **Complexity score (10%)**: Task complexity vs agent specialization

## Integration with Commands

### /task Command
- Complexity > 0.7: Spawns architect + implementer
- Security keywords: Adds security reviewer
- Multiple files: Uses researcher first

### /check Command
- Linting issues: formatting agent
- Test failures: qa agent
- Security warnings: security agent

### /analyze Command
- Deploys specialized analysis agents
- Coordinates multi-perspective reviews

## Advanced Features

### Multi-Agent Orchestration
```python
orchestrator = AgentOrchestrator()
plan = orchestrator.plan_multi_agent_task(
    "implement oauth2 with refresh tokens",
    max_agents=3
)
# Returns: security + architect + implementer collaboration plan
```

### Agent Handoffs
Agents can pass context between each other:
```yaml
<!-- AGENT:HANDOFF:START -->
From: researcher
To: implementer
Summary: Found 3 similar patterns...
Context: {...}
<!-- AGENT:HANDOFF:END -->
```

## Best Practices

1. **Let Quaestor choose**: The automatic selection usually picks the right agents
2. **Override when needed**: Use `/agent` directly for specific needs
3. **Create project personas**: Add domain-specific agents to `.quaestor/agents/`
4. **Keep prompts focused**: Each agent should excel at one thing
5. **Use standard tools**: Stick to claude-code's available tools

## Troubleshooting

### Agent not found
- Check `.claude/agents/` directory
- Run deployment script
- Verify agent name (kebab-case)

### Agent not auto-selected
- Check activation keywords
- Verify context patterns
- Review priority settings

### Tools not working
- Use comma-separated format
- Verify tool names match claude-code's list
- Check for typos

## Future Enhancements

- Agent performance tracking
- Dynamic priority adjustment
- Cross-agent learning
- Team-specific personas
- Agent composition patterns