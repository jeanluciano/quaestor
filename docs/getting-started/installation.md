# Installation

## Requirements

- Python 3.8 or higher
- Git (for branch management and hooks)
- Claude Code (recommended for full integration)

## Install via pip

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

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to initialize your first project.