# Configuration

Quaestor uses a layered configuration system that adapts to your project's language and allows customization at multiple levels.

## Configuration System Overview

Quaestor's configuration follows a 5-layer precedence system, where each layer can override settings from previous layers:

1. **Built-in Defaults** - Core defaults embedded in Quaestor
2. **Base Language Config** - Language-specific defaults from `languages.yaml`
3. **Project Config** - Project-specific settings in `.quaestor/config.yaml`
4. **Project Language Override** - Language overrides in `.quaestor/languages.yaml`
5. **Runtime Config** - Command-line arguments and environment variables

## Configuration Files

### Core Configuration (`.quaestor/config.yaml`)

The main configuration file for your project:

```yaml
version: "1.0"
hooks:
  enabled: true
  strict_mode: false  # When true, hook failures block operations
```

### Language Configuration (`.quaestor/languages.yaml`)

Customize language-specific settings for your project:

```yaml
version: "1.0"
languages:
  python:
    # Testing configuration
    test_command: "pytest -xvs"
    test_directory: "tests"
    test_framework: "pytest"
    coverage_threshold: 80
    
    # Linting and formatting
    lint_command: "ruff check"
    format_command: "ruff format"
    
    # Type checking
    type_check_command: "mypy src/"
    
    # Import style
    import_style: "absolute"
    
    # Documentation
    docstring_style: "google"
    
    # Build and packaging
    build_command: "python -m build"
    package_manager: "pip"
    
    # Performance targets
    performance_target: "10ms"
    
    # File patterns
    source_directories: ["src", "lib"]
    test_file_pattern: "test_*.py"
    
  typescript:
    test_command: "npm test"
    lint_command: "eslint . --fix"
    format_command: "prettier --write ."
    build_command: "npm run build"
    package_manager: "npm"
    
  rust:
    test_command: "cargo test"
    lint_command: "cargo clippy"
    format_command: "cargo fmt"
    build_command: "cargo build --release"
```

## CLI Configuration Commands

Quaestor provides CLI commands for managing configuration:

### View Configuration
```bash
# Show all configuration layers
quaestor config show

# Show specific configuration value
quaestor config get python.test_command

# Show configuration for a specific language
quaestor config show --language python
```

### Modify Configuration
```bash
# Set a configuration value
quaestor config set python.coverage_threshold 90

# Reset configuration to defaults
quaestor config reset

# Reset specific language configuration
quaestor config reset --language python
```

### Validate Configuration
```bash
# Validate all configuration files
quaestor config validate

# Initialize missing configuration files
quaestor config init
```

## Installation Modes

### Project Mode (Default)
Best for shared repositories:
- Files installed in `.quaestor/` directory
- Configuration committed to repository
- Consistent setup across team

```bash
quaestor init --project
```

### Personal Mode
Best for individual use:
- Files installed in `.claude/` directory
- Personal preferences preserved
- Works on individual projects

```bash
quaestor init --personal
```

## Language Detection

Quaestor automatically detects your project's primary language based on:

1. **Manifest files**: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`
2. **Configuration files**: `.python-version`, `tsconfig.json`, `rustfmt.toml`
3. **File extensions**: Most common extension in source directories
4. **Directory structure**: Presence of language-specific directories

### Supported Languages

- **Python**: Full support with pytest, ruff, mypy
- **TypeScript/JavaScript**: ESLint, Prettier, Jest/Vitest
- **Rust**: Cargo, clippy, rustfmt
- **Go**: go test, golangci-lint, gofmt
- **Java**: Maven/Gradle, JUnit
- **C++**: CMake, clang-format
- **Ruby**: RSpec, RuboCop
- **Swift**: XCTest, SwiftLint

## Configuration Precedence

Settings are applied in order (later overrides earlier):

1. **Built-in Defaults** - Core Quaestor defaults
2. **Base Language Config** - From Quaestor's `languages.yaml`
3. **Project Config** - Your `.quaestor/config.yaml`
4. **Project Language Config** - Your `.quaestor/languages.yaml`
5. **Runtime Arguments** - CLI flags and environment variables

### Example: Test Command Resolution

```yaml
# 1. Built-in default
test_command: "echo 'No test command configured'"

# 2. Base language config (Quaestor's languages.yaml)
python:
  test_command: "pytest"

# 3. Project language config (your .quaestor/languages.yaml)
python:
  test_command: "pytest -xvs --cov=src"

# 4. Runtime override
quaestor test --command "pytest -xvs --timeout=10"
```

## Environment Variables

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `QUAESTOR_CONFIG_PATH` | Path to config directory | `.quaestor` |
| `QUAESTOR_DEBUG` | Enable debug logging | `false` |
| `QUAESTOR_HOOKS_ENABLED` | Enable/disable hooks | `true` |
| `QUAESTOR_STRICT_MODE` | Make hook failures blocking | `false` |

### Language Override

You can override language detection:

```bash
export QUAESTOR_LANGUAGE=typescript
```

## Advanced Configuration

### Custom Language Configuration

Add support for additional languages or tools:

```yaml
# .quaestor/languages.yaml
version: "1.0"
languages:
  custom_lang:
    test_command: "custom-test-runner"
    lint_command: "custom-linter"
    format_command: "custom-formatter"
    # Add any custom fields needed by your templates
    custom_field: "custom_value"
```

### Template Variables

All language configuration fields are available as template variables:

```markdown
<!-- In templates like RULES.md -->
## Testing
Run tests with: `{{ test_command }}`
Coverage threshold: {{ coverage_threshold }}%
```

### Validation Rules

Configuration validation includes:

- **Type checking**: Ensures correct data types
- **Range validation**: Coverage thresholds must be 0-100
- **Command validation**: Warns if commands aren't found in PATH
- **Deprecation warnings**: Alerts for outdated configuration

## Migration from Older Versions

### From v0.5.x or earlier

1. Run `quaestor update` to migrate configuration automatically
2. Review `.quaestor/config.yaml` for new structure
3. Move language customizations to `.quaestor/languages.yaml`

### Deprecated Configuration

The following configuration options have been removed:

- `quality` block - Use language-specific settings instead
- `workflow` block - Now handled by hooks
- `mode` enum - Use `--personal` or `--project` flags
- `commands` block - Commands are now in `.claude/commands/`

## Troubleshooting

### Configuration Not Taking Effect

1. Check precedence order with `quaestor config show`
2. Validate syntax with `quaestor config validate`
3. Ensure you're in the correct directory
4. Check for typos in configuration keys

### Reset Configuration

```bash
# Reset all configuration to defaults
quaestor config reset

# Reset specific language
quaestor config reset --language python

# Reinitialize configuration files
quaestor config init
```

### Debug Configuration Loading

```bash
# Show configuration with source information
QUAESTOR_DEBUG=true quaestor config show

# Validate configuration with detailed output
quaestor config validate --verbose
```

## Best Practices

1. **Commit `.quaestor/config.yaml`** - Share project settings with team
2. **Customize `.quaestor/languages.yaml`** - Override language defaults for your project
3. **Use `quaestor config validate`** - Check configuration before committing
4. **Document custom settings** - Add comments explaining non-standard configuration
5. **Start with defaults** - Only override what you need to change

## Next Steps

- Learn about [Hooks System](../hooks/overview.md)
- Explore [Specification-Driven Development](../specs/overview.md)
- Read about [Claude Integration](../claude/overview.md)