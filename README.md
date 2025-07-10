# Quaestor

> 🏛️ AI context management that respects your existing setup

[![PyPI Version](https://img.shields.io/pypi/v/quaestor.svg)](https://pypi.org/project/quaestor/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quaestor** gives Claude (and other AI assistants) the context they need without messing with your existing configuration. It's smart enough to enhance your workflow, not replace it.

## 🚀 Quick Start (30 seconds)

```bash
# In your project directory:
uvx quaestor init

# That's it! Your AI assistant now understands your project.
```

### What just happened?

Quaestor scanned your project and:
- ✅ **Preserved your existing CLAUDE.md** (if you had one)
- 📁 Created `.quaestor/` with your project's context
- 🎯 Installed smart commands to `~/.claude/commands/`
- 🔧 Generated hooks for automated workflows

**Your existing setup is intact.** Quaestor just made it better.

## 🎯 What It Does (Under the Hood)

### 1. **Non-Intrusive CLAUDE.md Integration** 🆕

Instead of overwriting your CLAUDE.md, Quaestor adds a small managed section:

**Before:**
```markdown
# My Custom Claude Config
My specific instructions...
```

**After:**
```markdown
<!-- BEGIN QUAESTOR CONFIG -->
## 📋 Quaestor Framework Active
[Links to context files]
<!-- END QUAESTOR CONFIG -->

# My Custom Claude Config
My specific instructions...
```

Your content stays exactly where it was. Quaestor just adds pointers to its context files.

### 2. **Smart Project Analysis**

When you run `init`, Quaestor:
- Detects your tech stack from `package.json`, `pyproject.toml`, `Cargo.toml`, etc.
- Identifies frameworks from imports and dependencies
- Maps your architecture from directory structure
- Extracts progress from git history

### 3. **Intelligent Update System**

```bash
quaestor update --check  # See what would change
quaestor update          # Update only what's needed
```

- **System files** (CRITICAL_RULES.md) - Always updated
- **User files** (ARCHITECTURE.md) - Never overwritten if modified
- **Config sections** - Surgically updated without touching your content

### 4. **File Structure**

```
your-project/
├── CLAUDE.md                    # Your existing config + Quaestor section
└── .quaestor/
    ├── QUAESTOR_CLAUDE.md       # Full framework instructions
    ├── CRITICAL_RULES.md        # Enforcement rules
    ├── ARCHITECTURE.md          # Your detected architecture
    ├── MEMORY.md                # Progress tracking
    ├── manifest.json            # Tracks files and modifications
    └── hooks.json               # Automation configuration
```

## 📚 Commands

| Command | What it does | Example |
|---------|--------------|---------|
| `init` | Set up Quaestor in your project | `quaestor init` |
| `update` | Smart update that preserves your changes | `quaestor update --check` |
| **Claude Commands** (in `~/.claude/commands/`) | | |
| `project-init` | Analyze and set up project management | `/project-init` |
| `task-py` | Python implementation workflow | `/task-py implement user auth` |
| `task-rs` | Rust implementation workflow | `/task-rs add error handling` |
| `check` | Run quality checks | `/check` |
| `compose` | Combine commands | `/compose task-py + check` |
| `milestone-commit` | Auto-commit completed work | `/milestone-commit` |

## 🔥 Key Features

### Smart Context Management
- **Preserves your configs** - Never overwrites your CLAUDE.md
- **Tracks modifications** - Knows which files you've customized
- **Surgical updates** - Updates only Quaestor sections
- **Version tracking** - Every file has version headers

### Automated Workflows
- **Progress tracking** - Updates MEMORY.md automatically
- **Quality gates** - Won't commit until tests pass
- **Atomic commits** - Each task gets a clean commit
- **PR generation** - Creates PRs when milestones complete

### Project Intelligence
- **Stack detection** - Knows if you're using React, Django, FastAPI, etc.
- **Pattern recognition** - Identifies MVC, DDD, microservices patterns
- **Tool awareness** - Finds PostgreSQL, Redis, Docker usage
- **Convention learning** - Adapts to your project's style

## 🛠️ Installation Options

```bash
# Recommended - No install needed
uvx quaestor init

# Global install
uv tool install quaestor

# Add to project
uv add quaestor

# Traditional pip
pip install quaestor
```

## 🎓 How It Works

### The Manifest System

Quaestor uses a manifest (`manifest.json`) to track every file it manages:

```json
{
  "version": "1.0",
  "quaestor_version": "0.2.4",
  "files": {
    "CLAUDE.md": {
      "type": "user-editable",
      "version": "1.0",
      "user_modified": true,
      "original_checksum": "...",
      "current_checksum": "..."
    }
  }
}
```

This enables:
- **Smart updates** - Only update what's changed
- **Modification detection** - Via checksums
- **Version tracking** - Know which version of each file
- **Categorization** - Different update strategies per file type

### File Categories

1. **SYSTEM** - Always updated (CRITICAL_RULES.md, QUAESTOR_CLAUDE.md)
2. **USER_EDITABLE** - Never auto-overwritten (ARCHITECTURE.md, MEMORY.md, CLAUDE.md)
3. **COMMAND** - Added if missing (task-py.md, check.md, etc.)
4. **TEMPLATE** - Updated if unmodified

### AI-Optimized Format

Special markers enable precise AI edits:

```markdown
<!-- SECTION:architecture:database:START -->
```yaml
database:
  type: PostgreSQL
  orm: SQLAlchemy
```
<!-- SECTION:architecture:database:END -->
```

AI can update sections without breaking your documentation.

## 🪝 Claude Hooks

Generate automation with:
```bash
quaestor init  # Creates .quaestor/hooks.json
```

Copy to Claude settings:
```bash
cp .quaestor/hooks.json ~/.claude/settings/claude_code_hooks.json
```

### What Hooks Do

- **Enforce** - Block coding without research
- **Automate** - Update progress, create commits
- **Assist** - Refresh context, suggest next steps

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

## 📊 Project Status

- ✅ Non-intrusive CLAUDE.md integration
- ✅ Smart update system with manifest tracking
- ✅ Command templates for Python/Rust
- ✅ Claude hooks integration
- ✅ Automated milestone workflows
- 🚧 JavaScript/TypeScript commands
- 🚧 Team synchronization features

## 📄 License

MIT - Use it however you want.

---

**Remember:** Quaestor enhances your workflow without replacing it. Your configs, your rules, just better AI understanding.