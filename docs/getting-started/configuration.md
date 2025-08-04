# Configuration

Quaestor uses a combination of configuration files and environment variables to customize its behavior for your project and team preferences.

## Configuration Files

### Project Configuration (`.quaestor/`)

When you initialize Quaestor in a project, it creates a `.quaestor/` directory with several configuration files:

#### `manifest.json`
Tracks installed files and versions:
```json
{
  "version": "1.0.0",
  "install_date": "2024-01-15T10:30:00Z",
  "mode": "team",
  "files": {
    "RULES.md": "abc123...",
    "QUAESTOR_CLAUDE.md": "def456..."
  }
}
```

#### Language Configuration
Quaestor automatically detects your project type and applies appropriate configurations from `languages.yaml`:

- **Python**: Uses ruff for linting/formatting, pytest for testing
- **JavaScript/TypeScript**: Uses ESLint and Prettier
- **Rust**: Uses cargo clippy and rustfmt
- **Go**: Uses golangci-lint and go fmt

## Claude Integration Settings

### Team Settings (`.claude/settings.json`)
Shared settings for the entire team:

```json
{
  "project_standards": {
    "min_test_coverage": 80,
    "max_file_length": 500,
    "required_quality_gates": ["lint", "test", "security"]
  },
  "workflow_rules": {
    "require_specifications": true,
    "branch_naming": "feat/{spec-id}-{description}"
  }
}
```

### Personal Settings (`.claude/settings.local.json`)
Personal overrides (gitignored):

```json
{
  "agent_preferences": {
    "complexity_threshold": 0.5,
    "preferred_agents": ["implementer", "qa"]
  },
  "command_behavior": {
    "impl": {
      "auto_test": true
    }
  }
}
```

## Environment Variables

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `QUAESTOR_MODE` | Installation mode: "personal" or "team" | "team" |
| `QUAESTOR_DEBUG` | Enable debug logging | false |
| `QUAESTOR_HOOK_DEBUG` | Debug hook execution | false |

### Performance Tuning

| Variable | Description | Default |
|----------|-------------|---------|
| `QUAESTOR_AGENT_TIMEOUT` | Agent execution timeout (seconds) | 30 |
| `QUAESTOR_PARALLEL_AGENTS` | Max parallel agent execution | 4 |

### Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `QUAESTOR_EXPERIMENTAL` | Enable experimental features | false |
| `QUAESTOR_DISABLE_HOOKS` | Disable all hooks | false |
| `QUAESTOR_DISABLE_AUTO_FIX` | Disable automatic fixes | false |

## Installation Modes

### Team Mode (Default)
Best for shared repositories:
- Files installed in `.quaestor/` directory
- Configuration committed to repository
- Consistent setup across team

```bash
quaestor init
```

### Personal Mode
Best for individual use:
- Global installation in `~/.quaestor/`
- Personal preferences preserved
- Works across all projects

```bash
quaestor init personal
```

## Configuration Precedence

Settings are applied in order (later overrides earlier):

1. **Built-in Defaults**
2. **Language Configuration** (`languages.yaml`)
3. **Team Settings** (`.claude/settings.json`)
4. **Personal Settings** (`.claude/settings.local.json`)
5. **Environment Variables**
6. **Command Arguments**

## Common Configurations

### For New Users
Start with gentle guidance:

```json
{
  "agent_preferences": {
    "complexity_threshold": 0.3
  },
  "hook_settings": {
    "complexity_monitor": {
      "blocking": false
    }
  }
}
```

### For Power Users
More control, less automation:

```json
{
  "agent_preferences": {
    "complexity_threshold": 0.8,
    "parallel_execution": true
  },
  "command_behavior": {
    "impl": {
      "auto_test": false
    }
  }
}
```

### For Teams
Enforce standards:

```json
{
  "project_standards": {
    "min_test_coverage": 90,
    "required_quality_gates": ["lint", "test", "security", "docs"]
  },
  "workflow_rules": {
    "require_specifications": true,
    "require_pr_review": true
  }
}
```

## Updating Configuration

### Check Current Settings
```bash
# View active configuration
cat .claude/settings.json
cat .claude/settings.local.json

# Check environment
env | grep QUAESTOR
```

### Update Team Settings
Edit `.claude/settings.json` and commit:
```bash
git add .claude/settings.json
git commit -m "chore: update team quality standards"
```

### Update Personal Settings
Edit `.claude/settings.local.json` (won't be committed):
```bash
# This file is gitignored
echo '{"agent_preferences": {"complexity_threshold": 0.4}}' > .claude/settings.local.json
```

## Troubleshooting

### Settings Not Taking Effect
1. Check precedence order - later settings override earlier
2. Verify JSON syntax is valid
3. Restart Claude Code session
4. Check for typos in setting names

### Reset to Defaults
```bash
# Remove all personal overrides
rm .claude/settings.local.json

# Reset team settings
git checkout .claude/settings.json
```

## Next Steps

- Learn about [Claude Agents](../agents/overview.md)
- Explore [Hooks & Automation](../hooks/overview.md)
- Read about [Specification-Driven Development](../specs/overview.md)