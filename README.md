# Quaestor

> 🏛️ AI context management that respects your existing setup

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quaestor** helps Claude (and other AI assistants) understand your project without messing with your existing configuration.

> ⚠️ **Work in Progress**: Quaestor is under active development. While core features are stable, you may encounter bugs or breaking changes between versions.

## 🤔 Why Quaestor?

**The Problem:** AI assistants like Claude are powerful, but they lack context about your project. You end up:
- 🔄 Repeatedly explaining your architecture
- 📋 Copy-pasting the same instructions
- 🤯 Getting inconsistent implementations
- ⚠️ Fighting with conflicting configurations

**The Solution:** Quaestor provides structured context that AI assistants can understand, while respecting your existing setup.

## 🚀 Quick Start (30 seconds)

```bash
# In your project directory:
uvx quaestor init

# That's it! Your AI assistant now understands your project.
```

### What just happened?

```
✅ Preserved your existing CLAUDE.md
📁 Created .quaestor/ with:
   - ARCHITECTURE.md (your project structure)
   - MEMORY.md (progress tracking)
   - CRITICAL_RULES.md (quality standards)
🎯 Installed commands to ~/.claude/commands/
🔧 Set up automated hooks in .claude/settings/
```

Now try this in Claude:
```
/task: implement user authentication with JWT tokens
```

Claude will:
- Research your existing auth patterns
- Follow your project's conventions
- Run quality checks
- Track progress in MEMORY.md

## 🛠️ Installation

```bash
# Recommended - No install needed
uvx quaestor init

# Global install
uv tool install quaestor

# Traditional pip
pip install quaestor
```

## 📚 Commands

### CLI Commands
| Command | What it does | Example |
|---------|--------------|---------|
| `init` | Set up Quaestor in your project | `quaestor init` |
| `update` | Smart update that preserves your changes | `quaestor update --check` |

### Claude Commands (Auto-installed to `~/.claude/commands/`)
| Command | What it does | Example |
|---------|--------------|---------|
| `/help` | Show all available commands | `/help` |
| `/task` | Smart implementation workflow | `/task: add user authentication` |
| `/status` | Check project progress | `/status` |
| `/milestone` | Manage project phases | `/milestone: complete phase 1` |
| `/project-init` | Analyze and document your project | `/project-init` |
| `/check` | Run quality checks | `/check` |
| `/milestone-commit` | Create atomic commits | `/milestone-commit` |

## 🎯 Key Features

### 1. **Non-Intrusive Integration**

Your existing CLAUDE.md stays untouched. Quaestor adds a small managed section:

```markdown
<!-- QUAESTOR CONFIG START -->
> [!IMPORTANT]
> **Claude:** This project uses Quaestor. Please read:
> 1. `.quaestor/QUAESTOR_CLAUDE.md` - Framework instructions
> 2. `.quaestor/CRITICAL_RULES.md` - Quality standards
> 3. `.quaestor/ARCHITECTURE.md` - Project structure
> 4. `.quaestor/MEMORY.md` - Progress tracking
<!-- QUAESTOR CONFIG END -->

# Your existing content remains here...
```

### 2. **Project Analysis**

Quaestor detects:
- **Tech Stack** - Python, Rust, JavaScript, TypeScript, Go
- **Common Frameworks** - Django, FastAPI, React, Next.js
- **Project Structure** - Directories and file organization
- **Dependencies** - From package.json, pyproject.toml, etc.

### 3. **Quality Workflow**

Encourages a Research → Plan → Implement workflow:

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│   Research  │ --> │   Plan   │ --> │ Implement   │
│ (Read/Grep) │     │ (Design) │     │ (Write/Edit)│
└─────────────┘     └──────────┘     └─────────────┘
```

Optional hooks can enforce this workflow when enabled.

### 4. **Smart Updates**

```bash
# See what would change
quaestor update --check

# Update with backup
quaestor update --backup
```

- **System files** - Always updated (CRITICAL_RULES.md)
- **Your files** - Never overwritten if modified
- **Tracked changes** - Every modification is logged

## 📁 Project Structure

After initialization:
```
your-project/
├── CLAUDE.md                    # Your config + Quaestor section
├── .quaestor/
│   ├── QUAESTOR_CLAUDE.md       # AI instructions
│   ├── CRITICAL_RULES.md        # Quality standards
│   ├── ARCHITECTURE.md          # Project structure
│   ├── MEMORY.md                # Progress tracking
│   ├── manifest.json            # File tracking
│   └── hooks/                   # Portable hook scripts
│       ├── enforce-research.py
│       ├── quality-check.py
│       └── update-memory.py
└── .claude/
    └── settings/
        └── claude_code_hooks.json # Auto-installed hooks
```

## 🔥 Real-World Examples

### Example 1: Adding a Feature
```
You: /task: add password reset functionality

Claude will:
1. Research existing auth implementation
2. Check email service configuration  
3. Follow your naming conventions
4. Implement with proper error handling
5. Update progress in MEMORY.md
```

### Example 2: Refactoring
```
You: /task: refactor user service to use dependency injection

Claude will:
1. Analyze current service structure
2. Identify all dependencies
3. Plan refactoring approach
4. Implement following your patterns
5. Ensure tests still pass
```

### Example 3: New Milestone
```
You: /milestone: start MVP phase 2

Claude will:
1. Archive current progress
2. Create new milestone section
3. Set up tracking for phase 2
4. Suggest initial tasks
```

## 🪝 Automated Hooks

Hooks are automatically installed to `.claude/settings/` and use local scripts for portability:

### What Hooks Do

- **🚫 Enforce Standards** - Block code without research
- **📊 Track Progress** - Auto-update MEMORY.md
- **✅ Quality Checks** - Run tests before commits
- **🎯 Smart Context** - Refresh on long conversations

### Hook Portability

Hooks work with any installation method (uvx, pip, etc.) by using local Python scripts in `.quaestor/hooks/`.

## 🎓 How It Works

### The Manifest System

Every file is tracked with checksums and versions:

```json
{
  "files": {
    "CLAUDE.md": {
      "type": "user-editable",
      "user_modified": true,
      "original_checksum": "abc123...",
      "current_checksum": "def456..."
    }
  }
}
```

### AI-Optimized Format

Special markers enable precise AI edits:

```markdown
<!-- SECTION:database:config:START -->
```yaml
database:
  type: PostgreSQL
  version: 15
```
<!-- SECTION:database:config:END -->
```

AI can update sections without breaking your documentation.

## 🔄 Updating Quaestor

```bash
# Check what would change
quaestor update --check

# Update with backup
quaestor update --backup

# Force update everything
quaestor update --force
```

## 🤝 Contributing

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
uv sync
uv run pytest
```

### Development Workflow
1. Create feature branch
2. Add tests for new functionality
3. Run `uv run pytest`
4. Submit PR with description

## 📊 Project Status

### ✅ Completed
- Non-intrusive CLAUDE.md integration
- Smart update system with manifest tracking
- Unified `/task` command for all languages
- Claude hooks with portable scripts
- Automated milestone workflows
- Project status tracking
- Command discovery with `/help`

### 🚧 In Progress
- Team synchronization features
- Extended language support
- Plugin system

### 🎯 Planned
- VS Code extension
- Web dashboard
- Team analytics

## 🙏 Acknowledgments

Built with feedback from the Claude community.

## 📄 License

MIT - Use it however you want.

---

<div align="center">

**Remember:** Quaestor enhances your workflow without replacing it.  
Your configs, your rules, just better AI understanding.

[Report Bug](https://github.com/jeanluciano/quaestor/issues) · [Request Feature](https://github.com/jeanluciano/quaestor/issues)

</div>