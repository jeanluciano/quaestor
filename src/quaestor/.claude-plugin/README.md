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

### 🎓 Skills (12 skills)
- `project-initialization` - Intelligent project setup with framework detection
- `implementation-workflow` - Production-quality implementation with agent orchestration
- `review-and-ship` - Comprehensive review, validation, commit generation, and PR creation
- `spec-writing` - Specification creation
- `spec-management` - Spec lifecycle management
- `pr-generation` - Pull request generation
- `architecture-patterns` - Architecture design patterns
- `code-quality` - SOLID principles and linting
- `security-audit` - Security patterns and OWASP guidelines
- `testing-strategy` - Test pyramid and pytest patterns
- `performance-optimization` - Caching and profiling
- `debugging-workflow` - Systematic debugging

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

Implement it (uses implementation-workflow skill automatically):
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
