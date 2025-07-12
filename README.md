# Quaestor

> 🏛️ Context management for AI-assisted development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quaestor** helps AI assistants understand your project and maintain quality standards without disrupting your existing setup.

## Why Quaestor?

AI assistants like Claude are powerful but need context. Quaestor provides:
- 📋 Project structure and conventions 
- ✅ Automated quality checks
- 📊 Progress tracking
- 🔄 Smart workflow enforcement

## Quick Start

```bash
# In your project directory:
uvx quaestor init
```

This creates:
- `.quaestor/` - Project documentation and rules
- `~/.claude/commands/` - AI assistant commands
- `.claude/settings/` - Automated hooks (optional)

Now Claude can use commands like:
```
/task: implement user authentication
/status
/help
```

## Installation

```bash
# No install needed (recommended)
uvx quaestor init

# Or install globally
pip install quaestor
```

## Commands

**CLI Commands:**
- `quaestor init` - Set up in your project
- `quaestor update` - Update while preserving your changes

**AI Assistant Commands** (in `~/.claude/commands/`):
- `/task` - Implement features with quality checks
- `/status` - Show project progress
- `/help` - List all commands
- `/milestone` - Manage project phases
- `/check` - Run quality validation

## Key Features

### Non-Intrusive
- Preserves existing CLAUDE.md files
- Adds managed section without disrupting your content
- All configuration in `.quaestor/` directory

### Smart Project Analysis
- Auto-detects language (Python, Rust, JS/TS, Go)
- Identifies frameworks and project structure
- Configures appropriate quality tools

### Quality Workflow
Enforces Research → Plan → Implement pattern:
- Research existing code before changes
- Plan implementation approach
- Apply language-specific quality standards

### Intelligent Updates
- System files auto-update
- User modifications preserved
- All changes tracked in manifest

## Project Structure

```
your-project/
├── .quaestor/
│   ├── QUAESTOR_CLAUDE.md  # AI instructions
│   ├── CRITICAL_RULES.md   # Quality standards
│   ├── ARCHITECTURE.md     # Your project structure
│   ├── MEMORY.md          # Progress tracking
│   └── hooks/             # Automation scripts
├── ~/.claude/commands/    # AI assistant commands
└── CLAUDE.md             # Your existing + Quaestor section
```

## How It Works

1. **Project Analysis** - Detects your tech stack and structure
2. **Documentation Generation** - Creates AI-readable project docs
3. **Command Installation** - Adds powerful commands for Claude
4. **Hook Automation** - Optional quality enforcement
5. **Smart Updates** - Preserves your customizations

### Example: Using /task

```
You: /task: add user authentication

Claude will:
1. Research your existing patterns
2. Plan the implementation
3. Follow your code style
4. Run quality checks
5. Update progress tracking
```

## Automated Hooks

Optional hooks that enforce quality:
- **Pre-edit** - Ensure research before changes
- **Post-edit** - Format code, update progress
- **Pre-commit** - Run tests and quality checks

Hooks use portable Python scripts in `.quaestor/hooks/`.

## Updating

```bash
# Check what would change
quaestor update --check

# Update with backup
quaestor update --backup
```

## Contributing

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
uv sync
uv run pytest
```

## License

MIT

---

<div align="center">

[Documentation](https://github.com/jeanluciano/quaestor) · [Issues](https://github.com/jeanluciano/quaestor/issues)

</div>