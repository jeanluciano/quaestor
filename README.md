# Quaestor

> 🏛️ Context management for AI-assisted development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jeanluciano.github.io/quaestor)

**Quaestor** transforms AI-assisted development through **specification-driven workflows**, intelligent agent orchestration, and streamlined context management for Claude Code.

## Key Features

- 🎯 **Specification-Driven Development** - Clear contracts with acceptance criteria and lifecycle management
- 🤖 **12 Specialized AI Agents** - Expert agents for architecture, implementation, testing, and review
- 🔄 **Smart Automation Hooks** - Automatic workflow enforcement and progress tracking  
- ⚡ **40% Faster Context Loading** - Consolidated templates for better performance

## Quick Start

```bash
# Install
pip install quaestor

# Personal mode (default) - local configuration
quaestor init

# Team mode - shared configuration
quaestor init --mode team

# Create your first specification
/plan "User Authentication System"

# Implement the specification
/impl spec-auth-001
```

## Project Modes

### Personal Mode (Default)
Perfect for individual projects:
```bash
quaestor init
```
- Commands installed globally in `~/.claude/commands/`
- Local settings in `.claude/settings.local.json` (not committed)
- Project files in `.quaestor/` (gitignored)
- CLAUDE.md with project-specific context

### Team Mode
For shared projects with consistent standards:
```bash
quaestor init --mode team
```
- Commands in `.claude/commands/` (committed, shared with team)
- Settings in `.claude/settings.json` (committed)
- Project files in `.quaestor/` (committed)
- CLAUDE.md with team standards and context

**Key Difference**: Personal mode keeps configuration local, Team mode shares everything with the team.

## Core Commands

- `/plan "Feature Name"` - Create specification with clear contracts
- `/impl spec-id` - Implement according to specification
- `/research "topic"` - Analyze codebase patterns and architecture
- `/review spec-id` - Validate implementation quality
- `/debug "issue"` - Systematic debugging and fixes

## How It Works

### Specification-First Development
1. **Plan with Contracts** - `/plan` creates detailed specifications with input/output contracts
2. **Lifecycle Management** - Specs move through `draft/` → `active/` → `completed/` folders  
3. **Agent Orchestration** - 12 specialized agents collaborate on implementation
4. **Quality Assurance** - Built-in testing and review workflows

### Example Workflow
```bash
# 1. Create specification
/plan "JWT Authentication API"
# → Creates spec-auth-001.yaml in draft/ folder

# 2. Implement with guided workflow
/impl spec-auth-001  
# → Moves to active/, orchestrates architect → implementer → qa agents

# 3. Review and deploy
/review spec-auth-001
# → Validates quality, moves to completed/ when done
```

## Documentation

📚 **[Full Documentation](https://jeanluciano.github.io/quaestor)**

- [Installation & Setup](https://jeanluciano.github.io/quaestor/getting-started/installation/)
- [Quick Start Guide](https://jeanluciano.github.io/quaestor/getting-started/quickstart/)
- [Specification-Driven Development](https://jeanluciano.github.io/quaestor/specs/overview/)
- [Agent System](https://jeanluciano.github.io/quaestor/agents/overview/)

## Contributing

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
pip install -e .
pytest
```

## License

MIT License

---

<div align="center">

[Documentation](https://jeanluciano.github.io/quaestor) · [Issues](https://github.com/jeanluciano/quaestor/issues)

</div>