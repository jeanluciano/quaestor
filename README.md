# Quaestor

> 🏛️ Context management for AI-assisted development

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quaestor** provides intelligent context management and quality enforcement for AI assistants, with flexible modes for personal and team projects.

## Why Quaestor?

AI assistants like Claude are powerful but need context. Quaestor provides:
- 🧠 **Smart Context** - Automatically adjusts rules based on project complexity
- 🎯 **Flexible Modes** - Personal mode for solo work, team mode for collaboration
- ⚙️ **Command Customization** - Override and configure commands per project
- 📊 **Progress Tracking** - Maintain project memory and milestones
- ✅ **Quality Enforcement** - Ambient rules that work outside commands

## Quick Start

```bash
# Personal mode (default) - Everything local to your project
uvx quaestor init

# Team mode - Shared commands, committed rules
uvx quaestor init --mode team
```

### Personal Mode (Default)
Creates a self-contained setup in your project:
```
project/
├── .claude/           # All AI files (gitignored)
│   ├── CLAUDE.md     # Context-aware rules
│   ├── commands/     # Local commands
│   └── settings.json # Hooks
└── .quaestor/        # Architecture & memory
```

### Team Mode
For shared projects with consistent standards:
```
project/
├── CLAUDE.md         # Team rules (committed)
├── .quaestor/        # Shared documentation
└── ~/.claude/        # Global commands
```

Now Claude can use commands with project-specific behavior:
```
/task: implement user authentication
/status
/configure
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
- `quaestor init` - Initialize with smart defaults
  - `--mode personal` (default) - Local, self-contained setup
  - `--mode team` - Shared commands and rules
  - `--contextual` (default) - Analyze project complexity
- `quaestor configure` - Customize command behavior
  - `--init` - Create command configuration
  - `--command <name> --create-override` - Override specific commands
- `quaestor update` - Update while preserving your changes

**AI Assistant Commands**:
- `/task` - Implement features with orchestration
- `/status` - Show progress with velocity tracking
- `/analyze` - Code analysis across multiple dimensions
- `/milestone` - Manage phases with completion detection
- `/check` - Quality validation and fixing
- `/auto-commit` - Conventional commits for TODOs
- `/milestone-pr` - Automated PR creation
- `/project-init` - Framework detection and project setup

## Key Features

### 🧠 Context-Aware Commands
Quaestor commands use patterns for better Claude integration:
- **Auto-activation** → Context-aware triggers and thresholds
- **Performance profiling** → Standard, optimization, and complex execution modes  
- **Quality gates** → Error fixing with parallel agents
- **Token efficiency** → Reduction through symbol system

Rules work ambiently in CLAUDE.md, not just in commands!

### ⚙️ Command Customization
Configure commands per project with `.quaestor/command-config.yaml`:
```yaml
commands:
  task:
    enforcement: strict
    parameters:
      minimum_test_coverage: 90
      max_function_lines: 30
    custom_rules:
      - "All APIs must have OpenAPI specs"
      - "Database changes require migrations"
```

Or create full overrides in `.quaestor/commands/task.md`.

### 🎯 Flexible Modes

**Installation modes determine where files are stored:**

**Personal Mode (Default)**:
- Everything local in `.claude/`
- Perfect for solo developers
- Commands and context in one place
- Fully gitignored

**Team Mode**:
- Shared standards in `.quaestor/`
- Global commands in `~/.claude/`
- Consistent across team
- Version controlled rules

**Note**: Both modes support all command complexity levels. Mode choice is about file organization, not project complexity.

### 📊 Smart Project Analysis
- Auto-detects language (Python, Rust, JS/TS, Go, Java, etc.)
- Identifies test frameworks and CI/CD
- Recognizes team markers (CODEOWNERS, PR templates)
- Calculates complexity score

### 🔄 Workflow Orchestration
Adaptive workflow based on scope:
- **Direct execution**: <10 files → Read + Edit operations
- **Parallel agents**: 10-50 files → Multi-agent coordination  
- **Complex systems**: >50 files → Systematic agent delegation
- **Quality cycles**: Execute → Validate → Fix → Complete
- **Auto-escalation**: Complexity threshold triggers

### 📈 Command Complexity Thresholds
Commands adapt their behavior based on task complexity (0.0-1.0):
- **Standard (0.2-0.4)**: Quick, focused operations (e.g., `/status`, `/milestone`)
- **Optimization (0.4-0.6)**: Balanced efficiency with smart features (e.g., `/check`)
- **Complex (0.6-0.8)**: Full orchestration and deep analysis (e.g., `/task`, `/analyze`)

Thresholds control: auto-activation features, parallel processing, quality gates, and error recovery.

## Project Structure

### Personal Mode (Default)
```
your-project/
├── .claude/                    # All AI files (gitignored)
│   ├── CLAUDE.md              # Context-aware rules
│   ├── commands/              # Local command copies
│   │   ├── task.md
│   │   ├── status.md
│   │   └── ...
│   └── settings.json          # Hooks configuration
├── .quaestor/                 # Optional, for docs
│   ├── ARCHITECTURE.md        # Project structure
│   ├── MEMORY.md             # Progress tracking
│   ├── command-config.yaml   # Command customization
│   └── commands/             # Command overrides
│       └── task.md          # Custom task command
└── .gitignore                # Auto-updated
```

### Team Mode
```
your-project/
├── CLAUDE.md                  # Team rules (committed)
├── .quaestor/                 # Shared documentation
│   ├── QUAESTOR_CLAUDE.md    # AI instructions
│   ├── CRITICAL_RULES.md     # Quality standards
│   ├── ARCHITECTURE.md       # Project structure
│   ├── MEMORY.md            # Progress tracking
│   ├── command-config.yaml  # Command config
│   └── hooks/               # Automation scripts
├── ~/.claude/commands/       # Global commands
└── .claude/settings.json    # Local hooks only
```

## How It Works

1. **Project Analysis** - Scans for language, tests, complexity
2. **Context Generation** - Creates appropriate CLAUDE.md rules
3. **Command Setup** - Installs commands (local or global)
4. **Customization** - Allows per-project overrides
5. **Smart Updates** - Preserves your changes

### Example Workflows

**Simple Task Example**:
```
You: /task: add config parser

Claude: Auto-detects Python project, applies ruff+pytest standards
- Direct implementation with quality validation (standard profile)
- Updates milestone progress automatically
- Conventional commit with smart scope detection
```

**Complex Task Example**:
```
You: /task: refactor authentication system

Claude: Complex threshold 0.7+ → orchestration mode
1. "Analyzing current auth architecture..." 🔍
2. "Using agents for parallel refactoring..." ⚡
3. "Quality gates: tests, linting, security validation" ✅
4. "Milestone tracking updated, PR ready" 🚀
```

**Note**: Task complexity is independent of installation mode. Both personal and team modes support all complexity levels.

### Command Customization Example

Create project-specific rules:
```bash
quaestor configure --init
```

Edit `.quaestor/command-config.yaml`:
```yaml
commands:
  task:
    enforcement: strict
    custom_rules:
      - "All endpoints must have rate limiting"
      - "Use dependency injection pattern"
```

Now `/task` enforces your project standards!

## Automated Hooks

Optional hooks enforce quality automatically:
- **Pre-edit** - Ensure research before changes
- **Post-edit** - Format code, update progress
- **Pre-commit** - Run tests and quality checks
- **Milestone** - Track progress, create PRs

Configure in `.claude/settings.json` (created during init).

## Ambient Rule Enforcement

Unlike command-only systems, Quaestor's rules work everywhere:

```markdown
<!-- In your CLAUDE.md -->
## 🧠 THINKING PATTERNS

Before EVERY response, I'll consider:
1. **Complexity Check**: 
   - Simple request? → Direct implementation
   - Multiple components? → "Let me research and plan this"
   
2. **Delegation Triggers**:
   if (files_to_modify > 3) {
     say("I'll spawn agents to handle this efficiently")
   }
```

Claude follows these patterns even outside `/task` commands!

## Updating

```bash
# Check what would change
quaestor update --check

# Update with backup
quaestor update --backup

# Force update all files
quaestor update --force
```

Updates preserve your customizations in user-editable files.

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