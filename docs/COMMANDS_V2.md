# Quaestor Commands - 5-Command Workflow

Quaestor implements a streamlined 5-command workflow that mirrors the natural software development cycle:

**Research → Plan → Implement ↔ Debug → Review**

## Overview

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `/research` | Explore and understand codebase | Multi-agent search, pattern analysis, dependency mapping |
| `/plan` | Strategic planning and progress tracking | Milestone management, velocity tracking, architecture planning |
| `/task` | Implementation with quality gates | Agent orchestration, language detection, parallel execution |
| `/debug` | Fix issues and troubleshoot | Root cause analysis, performance profiling, test fixing |
| `/review` | Validate, commit, and ship | Multi-agent review, auto-fixing, smart commits, PR creation |

## Command Details

### `/research` - Intelligent Discovery & Understanding

**Purpose**: Explore codebases to understand context, patterns, and dependencies before making changes.

**Usage**:
```bash
/research "authentication patterns"
/research "how does the payment system work"
/research --scope "src/api" --depth deep
/research --architecture "user service dependencies"
```

**Agent Strategy**:
- `researcher`: Primary exploration and pattern finding
- `architect`: System design analysis
- `security`: Security pattern identification
- `explorer`: Deep codebase navigation

**Key Features**:
- Multi-agent parallel search
- Relevance-based result ranking
- Pattern recognition across modules
- Dependency graph construction
- Context preservation for other commands

### `/plan` - Strategic Planning & Progress Management

**Purpose**: Plan work, manage milestones, track progress, and make strategic decisions.

**Usage**:
```bash
/plan                           # Progress dashboard
/plan --create "MVP Complete"   # Create milestone
/plan --complete               # Complete current milestone
/plan --analyze                # Strategic analysis
/plan --velocity              # Velocity metrics
/plan --architecture          # Architecture planning
```

**Agent Strategy**:
- `architect`: System design and milestone structure
- `planner`: Task breakdown and estimation
- `implementer`: Effort estimation
- `security`: Risk assessment

**Key Features**:
- Visual progress dashboards
- Velocity tracking and trends
- Architecture health monitoring
- Strategic analysis and recommendations
- Milestone lifecycle management

**Absorbed Commands**: `/status`, planning features from `/analyze`

### `/task` - Implementation with Agent Orchestration

**Purpose**: Execute implementations with intelligent agent selection and quality gates.

**Usage**:
```bash
/task "implement user authentication"
/task [description] [--strategy systematic|agile|focused]
```

**Agent Strategy**:
- Dynamic selection based on task complexity
- `architect` + `implementer` for complex tasks
- `security` + `qa` for sensitive features
- `researcher` + `refactorer` for multi-file changes

**Key Features**:
- Auto-detect language and standards
- Intelligent agent orchestration
- Built-in quality cycles
- Parallel execution for complex tasks
- Milestone integration

### `/debug` - Interactive Debugging & Troubleshooting

**Purpose**: Investigate issues, fix bugs, and optimize performance with specialized agents.

**Usage**:
```bash
/debug "test failures in auth module"
/debug "performance bottleneck in API"
/debug --error "TypeError: undefined is not a function"
/debug --profile "slow database queries"
```

**Agent Strategy**:
- `qa`: Test failure analysis
- `debugger`: General debugging
- `security`: Security issue fixes
- `implementer`: Performance optimization
- `architect`: Design flaw resolution

**Key Features**:
- Root cause analysis
- Interactive debugging sessions
- Performance profiling
- Test-driven bug fixing
- Strategic logging placement

### `/review` - Comprehensive Review & Ship

**Purpose**: Final validation, commit generation, and PR creation with multi-agent expertise.

**Usage**:
```bash
/review                    # Full pipeline
/review --commit-only      # Generate commits
/review --validate-only    # Fix quality issues
/review --pr-only         # Create PR
/review --analysis        # Deep analysis
/review --quick           # Fast review
```

**Agent Strategy**:
- `refactorer`: Code quality review
- `security`: Security validation
- `qa`: Test coverage analysis
- `reviewer`: Comprehensive review
- `implementer`: Documentation check

**Key Features**:
- Multi-agent parallel review
- Automatic issue fixing
- Smart commit generation
- PR creation with rich context
- Quality gate enforcement

**Absorbed Commands**: `/commit`, `/check`, review features from `/analyze`

## Workflow Integration

### Context Flow Between Commands

```
/research → findings → /plan
    ↓                    ↓
relevant files      milestones
    ↓                    ↓
/task ← implementation → /debug
    ↓                    ↑
changes              fixes
    ↓                    ↓
/review → commits → PR → ship
```

### Agent Handoffs

Each command can pass context to specialized agents in the next command:
- Research findings inform planning agents
- Plan decisions guide implementation agents
- Implementation context helps debugging agents
- All contexts merge for final review

## Deprecated Commands

The following commands have been absorbed into the new workflow:
- `/status` → absorbed into `/plan`
- `/check` → absorbed into `/review`
- `/analyze` → split between `/research` and `/review`
- `/commit` → absorbed into `/review`

## Best Practices

1. **Start with Research**: Always understand before implementing
2. **Plan Before Coding**: Use `/plan` to structure work
3. **Debug Early**: Don't wait for issues to accumulate
4. **Review Thoroughly**: Let agents catch issues before shipping
5. **Leverage Agents**: Each command has specialized agents - use them

## Migration Guide

For users familiar with the old commands:
- Use `/plan` instead of `/status` for progress tracking
- Use `/review --validate-only` instead of `/check`
- Use `/research` for exploration, `/review --analysis` for quality analysis
- Use `/review --commit-only` instead of `/commit`

## Configuration

Commands can be customized via:
- `.quaestor/command-config.yaml` - Override command behavior
- `.claude/agents/` - Add project-specific agents
- Agent strategies in command frontmatter

## Summary

The 5-command workflow provides a cleaner, more intuitive interface while preserving all functionality and adding powerful new capabilities through native agent integration. Each command represents a distinct phase of development with specialized agent support.