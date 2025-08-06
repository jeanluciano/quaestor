# Installation

## Requirements

- Git (for version control)
- Claude Code (for AI-assisted development)
- Either:
  - `uv` for uvx usage (recommended), or
  - Python 3.12+ for traditional installation

## Quick Start with uvx (Recommended)

No installation required! Use `uvx` to run Quaestor directly:

```bash
# Initialize a project without installing Quaestor
uvx quaestor init

# Team mode
uvx quaestor init --mode team

# Update to latest version
uvx quaestor update
```

This approach:
- ✅ No Python dependencies in your project
- ✅ Always uses the latest version
- ✅ Hooks work via uvx commands
- ✅ Clean project environment

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

Quaestor is designed to work seamlessly with Claude Code. To set up the integration:

1. Install Claude Code following the [official documentation](https://docs.anthropic.com/en/docs/claude-code)
2. Initialize Quaestor in your project (see [Quick Start](quickstart.md))
3. The slash commands (`/plan`, `/impl`, etc.) will be automatically available

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

## Migration for Existing Users

If you have an existing Quaestor installation with Python hook files:

### From Python Hooks to uvx Commands

The new version uses `uvx` commands instead of Python files in `.claude/hooks/`:

1. **Remove old hook files** (no longer needed):
   ```bash
   rm -rf .claude/hooks/*.py
   ```

2. **Update settings.json** to use uvx commands:
   ```json
   {
     "hooks": {
       "SessionStart": [{
         "hooks": [{
           "type": "command",
           "command": "uvx --from quaestor quaestor hook session-context-loader"
         }]
       }],
       "PostToolUse": [{
         "matcher": "TodoWrite",
         "hooks": [{
           "type": "command",
           "command": "uvx --from quaestor quaestor hook todo-spec-progress"
         }]
       }]
     }
   }
   ```

3. **Or simply re-run init** to update everything:
   ```bash
   uvx quaestor update
   ```

### Benefits of Migration

- No Python files to maintain in your project
- Hooks always use the latest Quaestor version
- Cleaner project structure
- Works without Python installed locally

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to initialize your first project.