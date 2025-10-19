# Quaestor Plugin for Claude Code

Complete specification-driven development framework for Claude Code.

## Quick Install

```bash
# From Claude Code
/plugin marketplace add jeanluciano/quaestor
/plugin install quaestor

# Or install directly from GitHub
/plugin install jeanluciano/quaestor
```

## What's Included

### 🎯 Session Context Loading
Automatically loads active specifications at session start.

### 📋 Slash Commands (8 commands)
- `/plan` - Create and manage specifications
- `/impl` - Execute specification-driven implementation
- `/research` - Intelligent codebase exploration
- `/review` - Comprehensive code review with PR creation
- `/debug` - Interactive debugging assistance
- `/project-init` - Initialize Quaestor in new projects

### 🤖 Specialized Agents (14 agents)
- `planner` - Strategic planning
- `implementer` - Code writing
- `speccer` - Specification generation
- `architect` - System design
- `researcher` - Codebase exploration
- `reviewer` - Code review
- `debugger` - Bug fixing
- `qa` - Testing
- `refactorer` - Code improvement
- `security` - Security analysis
- `spec-manager` - Spec lifecycle
- `workflow-coordinator` - Workflow enforcement

## Requirements

- Claude Code v0.4.0+
- Python 3.7+ (for hooks)

## Usage

Initialize in your project:
```bash
/project-init
```

Create a specification:
```bash
/plan "Add user authentication"
```

Implement it:
```bash
/impl
```

Review your work:
```bash
/review
```

## Documentation

Full documentation: https://github.com/jeanluciano/quaestor

## License

MIT License - see [LICENSE](../LICENSE)
