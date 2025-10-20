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

### 📋 Slash Commands (3 commands)
- `/plan` - Create and manage specifications
- `/research` - Intelligent codebase exploration
- `/debug` - Interactive debugging assistance

### 🎓 Skills (7 skills)
- `managing-specifications` - Create and manage specifications with lifecycle
- `implementing-features` - Production-quality implementation with agent orchestration
- `reviewing-and-shipping` - Comprehensive review, validation, commit generation, and PR creation
- `debugging-issues` - Systematic debugging
- `security-auditing` - Security patterns and OWASP guidelines
- `optimizing-performance` - Caching and profiling
- `initializing-project` - Intelligent project setup with framework detection

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
# Just ask Claude to set up the project
"Initialize Quaestor in this project"
# or
"Set up Quaestor with intelligent project analysis"
```

Create a specification:
```bash
/plan "Add user authentication"
```

Implement it (uses implementing-features skill automatically):
```bash
"Implement spec-feature-001"
# or natural language:
"Build the user authentication feature"
```

Review your work:
```bash
"Review my changes"
# or
"Create a PR for this feature"
```

## Documentation

Full documentation: https://github.com/jeanluciano/quaestor

## License

MIT License - see [LICENSE](../LICENSE)
