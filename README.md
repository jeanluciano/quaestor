# Quaestor

> 🏛️ Context management for AI-assisted development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jeanluciano.github.io/quaestor)

**Quaestor** transforms AI-assisted development through **specification-driven workflows**, Agent Skills automation, intelligent agent orchestration, and streamlined context management for Claude Code.

## Key Features

- 🎯 **Specification-Driven Development** - Clear contracts with acceptance criteria and automatic lifecycle management
- ✨ **Agent Skills** - Auto-activating capabilities for spec creation, progress tracking, and PR generation
- 🤖 **10 Specialized AI Agents** - Expert agents for research, planning, implementation, and review
- 📁 **Folder-Based State** - Draft/active/completed folders as source of truth (no complex tracking)
- 🔄 **Smart Automation Hooks** - Automatic spec progress tracking via Claude Code hooks

## Quick Start

### Using uvx (Recommended - No Installation Required)
```bash
# Initialize Quaestor without installing it
uvx quaestor init

# Team mode - shared configuration
uvx quaestor init --mode team

# Update to latest version
uvx quaestor update
```

### Traditional Installation
```bash
# Install globally
pip install quaestor

# Initialize project
quaestor init

# Create specification (Skills handle it automatically!)
/plan "User Authentication System"

# Implement the specification
/impl spec-auth-001

# Check progress (Skills calculate automatically!)
"What's the status of my specs?"
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

- `/plan "Feature Name"` - Create specification with clear contracts (Spec Writing Skill)
- `/impl spec-id` - Implement according to specification
- `/research "topic"` - Analyze codebase patterns and architecture
- `/review spec-id` - Validate implementation quality

## Natural Language Commands (Agent Skills)

Just talk to Claude naturally - Skills activate automatically:
- "Create a spec for user authentication" - Creates specification
- "What's the status of my specs?" - Shows progress dashboard
- "Activate spec-feature-001" - Moves spec to active
- "Complete spec-feature-001" - Moves spec to completed
- "Create a pull request" - Generates and submits PR

## How It Works

### Specification-First Development
1. **Plan with Contracts** - `/plan` creates detailed specifications with input/output contracts (Spec Writing Skill)
2. **Automatic Lifecycle** - Agent Skills move specs through `draft/` → `active/` → `completed/` folders
3. **Agent Orchestration** - 10 specialized agents collaborate on implementation
4. **Progress Tracking** - Skills calculate progress from checkbox completion
5. **Quality Assurance** - Built-in testing and review workflows

### Example Workflow
```bash
# 1. Create specification (Spec Writing Skill activates)
/plan "JWT Authentication API"
# → Creates spec-auth-001.md in draft/ folder

# 2. Activate and implement
"Activate spec-auth-001"  # Spec Management Skill moves to active/
/impl spec-auth-001       # Implementer agent builds feature

# 3. Check progress (Spec Management Skill calculates)
"What's the status?"
# → "spec-auth-001: 80% complete (4/5 criteria)"

# 4. Complete and create PR (Skills handle transitions)
"Complete spec-auth-001"     # Moves to completed/
"Create a pull request"      # PR Generation Skill creates GitHub PR
```

## Hook System

Quaestor's hooks integrate seamlessly with Claude Code using `uvx`, requiring no local installation:

- **Session Context Loader** - Automatically loads active specifications at session start
- **Progress Tracker** - Updates specification progress when TODOs are completed (syncs with Skills)
- **No Python Required** - Hooks run via `uvx` without installing Quaestor in your project

The hooks are configured in `.claude/settings.json` and work alongside Agent Skills for complete automation.

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