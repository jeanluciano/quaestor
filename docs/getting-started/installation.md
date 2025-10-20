# Installation

## Requirements

- Claude Code
- Git (for version control)

## Installation Methods

### As a Claude Code Plugin (Recommended)

First, add the Quaestor marketplace:
```bash
/plugin marketplace add jeanluciano/quaestor
```

Then install the plugin:
```bash
/plugin install quaestor:quaestor
```

See [Claude Code plugins documentation](https://docs.claude.com/en/docs/claude-code/plugins) for details.

**What you get:**
- 7 auto-activating Skills
- 3 slash commands (/plan, /implement, /research)
- Folder-based spec management
- No Python installation required

### Via pip/uv (Project-Level)

For project-level installation:

```bash
pip install quaestor
# or
uv pip install quaestor
```

Then initialize in your project:
```bash
quaestor init
```

### Install from Source

For development:

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
pip install -e .
```

## Verify Installation

```bash
quaestor --version
```

## What Gets Created

When you initialize Quaestor (via plugin or `quaestor init`), it creates:

```
your-project/
├── .quaestor/
│   └── specs/            # Specification directories
│       ├── draft/        # Planned work
│       ├── active/       # In progress (max 3)
│       └── completed/    # Finished work
```

The plugin provides Skills and slash commands - no additional configuration needed.

## Troubleshooting

### Permission Issues
If you encounter permission issues during pip installation:

```bash
pip install --user quaestor
```

### Path Issues
Make sure your Python scripts directory is in your PATH:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
```

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to initialize your first project.