# Installation

## Requirements

- Claude Code (for AI-assisted development)
- Git (for version control)

That's it! No Python installation needed.

## Quick Start (Recommended)

**Quaestor v1.0 uses Agent Skills** - zero installation, just add the plugin!

1. Install the Quaestor plugin from Claude Code marketplace
2. In Claude Code, run: `/quaestor:project-init`
3. Start planning: `/quaestor:plan "User Authentication"`

**What you get:**
- ✅ **Agent Skills** - Auto-activating capabilities for spec management
- ✅ **No CLI needed** - Everything works through Claude Code
- ✅ **No dependencies** - Pure markdown specifications
- ✅ **Zero config** - Just describe features, get specs

## Traditional Installation

Install globally with pip:

```bash
pip install quaestor
```

## Install from Source

For development or latest features:

```bash
git clone https://github.com/jeanluciano/quaestor.git
cd quaestor
pip install -e .
```

## Verify Installation

```bash
quaestor --version
```

## Claude Code Integration

Quaestor is designed to work seamlessly with Claude Code:

1. Install the Quaestor plugin from the Claude Code marketplace
2. In Claude Code, run: `/quaestor:project-init` to set up your project
3. All slash commands are automatically available via the plugin

The plugin provides:
- **Commands**: `/quaestor:plan`, `/quaestor:impl`, `/quaestor:research`, `/quaestor:review`, `/quaestor:debug`, `/quaestor:project-init`
- **Agents**: Specialized agents for planning, implementation, debugging, etc.
- **Hooks**: Automated context loading and specification tracking

**No CLI commands needed!** Everything works through Claude Code slash commands.

## Optional Dependencies

For enhanced functionality, you may want to install:

```bash
# For GitHub integration
pip install gh

# For advanced YAML processing
pip install ruamel.yaml

# For rich console output
pip install rich
```

## Troubleshooting

### Permission Issues
If you encounter permission issues during installation:

```bash
pip install --user quaestor
```

### Path Issues
Make sure your Python scripts directory is in your PATH:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
```

### Claude Code Integration Issues
If slash commands don't work:

1. Ensure you're in a Quaestor-initialized project
2. Check that `.quaestor/` directory exists
3. Verify Claude Code is properly configured

## What Gets Created

When you run `/quaestor:project-init` in Claude Code, it creates:

```
your-project/
├── .quaestor/
│   ├── AGENT.md          # AI development context and rules
│   ├── ARCHITECTURE.md   # System design documentation
│   ├── RULES.md          # Language-specific guidelines (auto-generated!)
│   └── specs/            # Specification directories
│       ├── draft/        # Draft specifications
│       ├── active/       # Active specifications
│       ├── completed/    # Completed specifications
│       └── archived/     # Archived specifications
└── CLAUDE.md             # Main entry point with Quaestor config
```

**Key Features:**
- ✅ **RULES.md** auto-generated with your detected language commands (pytest, ruff, etc.)
- ✅ **Edit `.quaestor/RULES.md` directly** to customize (no config files needed!)
- ✅ Commands, agents, and hooks provided by the Claude Code plugin

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to initialize your first project.