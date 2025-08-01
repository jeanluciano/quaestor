# Quaestor

> 🏛️ Context management for AI-assisted development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jeanluciano.github.io/quaestor)

**Quaestor** enhances AI-assisted development with structured context management, intelligent agents, and specification-driven workflows for Claude Code.

## Key Features

- 🤖 **Intelligent Agent System** - Specialized AI agents for different development phases
- 🔄 **Smart Automation Hooks** - Automatic workflow enforcement and progress tracking  
- 🎯 **Specification-Driven Development** - Clear contracts with acceptance criteria
- 📊 **Progress Management** - Visual dashboards and milestone tracking

## Quick Start

```bash
# Install
pip install quaestor

# Personal mode (default) - local configuration
quaestor init

# Team mode - shared configuration
quaestor init --mode team

# Create your first specification
/plan --spec "User Authentication"

# Implement it
/impl "implement user login"
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
- CLAUDE.md with project-specific rules

### Team Mode
For shared projects with consistent standards:
```bash
quaestor init --mode team
```
- Commands in `.claude/commands/` (committed, shared with team)
- Settings in `.claude/settings.json` (committed)
- Project files in `.quaestor/` (committed)
- CLAUDE.md with team standards

**Key Difference**: Personal mode keeps configuration local, Team mode shares everything with the team.

## Core Commands

- `/plan` - Dashboard and specification management
- `/plan --spec "Title"` - Create new specification
- `/impl "description"` - Implement features
- `/research "topic"` - Analyze codebase
- `/review` - Quality validation

## How It Works

1. **Create Specifications** - Define what to build with clear contracts
2. **Auto-Branch Linking** - Specifications automatically link to git branches
3. **Guided Implementation** - AI agents follow specification contracts
4. **Progress Tracking** - Hooks automatically update status and milestones

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