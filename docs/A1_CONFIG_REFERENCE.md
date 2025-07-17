# Quaestor A1 Configuration Reference

## Table of Contents

1. [Overview](#overview)
2. [Configuration File](#configuration-file)
3. [System Configuration](#system-configuration)
4. [Core Components](#core-components)
5. [Extensions](#extensions)
6. [CLI Settings](#cli-settings)
7. [Features](#features)
8. [User Preferences](#user-preferences)
9. [Environment Variables](#environment-variables)
10. [Configuration Management](#configuration-management)
11. [Examples](#examples)

## Overview

A1 uses a hierarchical configuration system with:
- YAML/JSON configuration files
- Environment variable overrides
- Programmatic configuration
- Default values for all settings

### Configuration Hierarchy

1. **Default Values**: Built into the code
2. **Configuration File**: `.quaestor/a1_config.yaml`
3. **Environment Variables**: `QUAESTOR_A1_*`
4. **Runtime Overrides**: Via CLI or API

## Configuration File

### Location

The main configuration file is located at:
```
.quaestor/a1_config.yaml
```

### Format

A1 supports both YAML (preferred) and JSON formats:

```yaml
# YAML format (recommended)
system:
  version: "2.1.0"
  mode: "production"
  
core:
  event_bus:
    max_queue_size: 10000
```

```json
// JSON format (alternative)
{
  "system": {
    "version": "2.1.0",
    "mode": "production"
  },
  "core": {
    "event_bus": {
      "max_queue_size": 10000
    }
  }
}
```

## System Configuration

System-level settings that affect the entire application.

```yaml
system:
  # Version of configuration schema
  version: "2.1.0"
  
  # Operation mode
  # Options: "development", "production", "testing"
  # Default: "production"
  mode: "production"
  
  # Debug mode - enables verbose logging
  # Default: false
  debug: false
  
  # Logging level
  # Options: "debug", "info", "warning", "error", "critical"
  # Default: "info"
  log_level: "info"
  
  # Telemetry and usage tracking
  # Default: false
  telemetry_enabled: false
  
  # Automatic updates
  # Default: true
  auto_update: true
  
  # Working directory (relative to project root)
  # Default: "."
  working_directory: "."
```

## Core Components

Configuration for the five core A1 components.

### Event Bus

```yaml
core:
  event_bus:
    # Maximum queue size for events
    # Default: 10000
    max_queue_size: 10000
    
    # Enable async event processing
    # Default: true
    async_processing: true
    
    # Event processing timeout (seconds)
    # Default: 30.0
    processing_timeout: 30.0
    
    # Dead letter queue for failed events
    # Default: true
    enable_dlq: true
    
    # Maximum retries for failed events
    # Default: 3
    max_retries: 3
```

### Context Manager

```yaml
core:
  context_manager:
    # Maximum files in context
    # Default: 50
    max_context_size: 50
    
    # Minimum relevance score to keep files
    # Default: 0.3
    relevance_threshold: 0.3
    
    # Automatically optimize context
    # Default: true
    auto_optimization: true
    
    # Context switch timeout (seconds)
    # Default: 0.5
    context_switch_timeout: 0.5
    
    # Context cache size
    # Default: 100
    cache_size: 100
    
    # Default context type
    # Options: "development", "debugging", "testing", "research"
    # Default: "development"
    default_context_type: "development"
```

### Quality Guardian

```yaml
core:
  quality_guardian:
    # Minimum acceptable quality score (0-100)
    # Default: 70.0
    min_quality_score: 70.0
    
    # Automatically check quality on file changes
    # Default: true
    auto_check: true
    
    # Quality check timeout (seconds)
    # Default: 60.0
    check_timeout: 60.0
    
    # Maximum issues to track
    # Default: 1000
    max_tracked_issues: 1000
    
    # Issue severity thresholds
    severity_thresholds:
      error: 65.0      # Below this is error
      warning: 75.0    # Below this is warning
      info: 85.0       # Below this is info
    
    # Dimension weights for overall score
    dimension_weights:
      maintainability: 0.25
      readability: 0.25
      complexity: 0.20
      testability: 0.20
      documentation: 0.10
```

### Learning Manager

```yaml
core:
  learning_manager:
    # Minimum occurrences to detect pattern
    # Default: 3
    pattern_threshold: 3
    
    # Maximum patterns to track
    # Default: 1000
    max_patterns: 1000
    
    # Pattern decay rate (0-1)
    # Default: 0.95
    pattern_decay: 0.95
    
    # Confidence threshold for suggestions
    # Default: 0.6
    suggestion_confidence: 0.6
    
    # Learning rate for adaptation
    # Default: 0.1
    learning_rate: 0.1
    
    # Enable real-time learning
    # Default: true
    real_time_learning: true
```

### Analysis Engine

```yaml
core:
  analysis_engine:
    # Maximum file size to analyze (bytes)
    # Default: 1048576 (1MB)
    max_file_size: 1048576
    
    # Patterns to skip during analysis
    # Default: ["*.pyc", "__pycache__", "*.so", "*.dll"]
    skip_patterns:
      - "*.pyc"
      - "__pycache__"
      - "*.so"
      - "*.dll"
      - ".git"
      - "node_modules"
      - ".venv"
      - "venv"
    
    # Language-specific analyzers
    # Default: all enabled
    analyzers:
      python: true
      javascript: true
      typescript: true
      rust: true
      go: true
    
    # Analysis timeout per file (seconds)
    # Default: 30.0
    file_timeout: 30.0
    
    # Enable parallel analysis
    # Default: true
    parallel_analysis: true
    
    # Number of analysis workers
    # Default: 4
    worker_count: 4
```

## Extensions

Configuration for optional A1 extensions.

### Extension Enable/Disable

```yaml
extensions:
  # Enable/disable specific extensions
  prediction: true
  hooks: true
  state: true
  workflow: true
  persistence: true
```

### Prediction Engine

```yaml
extensions_config:
  prediction:
    # Maximum predictions to return
    # Default: 5
    max_predictions: 5
    
    # Minimum confidence for predictions
    # Default: 0.3
    min_confidence: 0.3
    
    # History size for pattern learning
    # Default: 100
    history_size: 100
    
    # Cache predictions
    # Default: true
    cache_enabled: true
    
    # Cache TTL (seconds)
    # Default: 300
    cache_ttl: 300
```

### Hook System

```yaml
extensions_config:
  hooks:
    # Hook configuration file
    # Default: ".quaestor/hooks.json"
    config_file: ".quaestor/hooks.json"
    
    # Enable hook execution
    # Default: true
    enabled: true
    
    # Hook execution timeout (seconds)
    # Default: 30
    timeout: 30
    
    # Allow shell commands
    # Default: false
    allow_shell: false
    
    # Hook failure behavior
    # Options: "continue", "stop", "warn"
    # Default: "warn"
    on_failure: "warn"
```

### State Management

```yaml
extensions_config:
  state:
    # State storage directory
    # Default: ".quaestor/state"
    storage_path: ".quaestor/state"
    
    # Maximum snapshots to keep
    # Default: 50
    max_snapshots: 50
    
    # Enable compression
    # Default: true
    compression: true
    
    # Auto-snapshot interval (seconds)
    # 0 = disabled
    # Default: 0
    auto_snapshot_interval: 0
    
    # Snapshot on significant changes
    # Default: true
    snapshot_on_change: true
```

### Workflow Detection

```yaml
extensions_config:
  workflow:
    # Minimum events for workflow detection
    # Default: 5
    min_events: 5
    
    # Workflow timeout (seconds)
    # Default: 300
    workflow_timeout: 300
    
    # Confidence threshold
    # Default: 0.7
    confidence_threshold: 0.7
    
    # Track anonymous workflows
    # Default: false
    track_anonymous: false
```

### Persistence

```yaml
extensions_config:
  persistence:
    # Storage backend
    # Options: "file", "memory"
    # Default: "file"
    backend: "file"
    
    # Storage root directory
    # Default: ".quaestor/data"
    storage_root: ".quaestor/data"
    
    # Enable encryption
    # Default: false
    encryption_enabled: false
    
    # Backup configuration
    backup:
      enabled: true
      interval: 3600  # seconds
      keep_count: 5
```

## CLI Settings

Configuration for command-line interface behavior.

```yaml
cli:
  # Output format
  # Options: "rich", "plain", "json"
  # Default: "rich"
  output_format: "rich"
  
  # Enable colors in output
  # Default: true
  color: true
  
  # Verbose output
  # Default: false
  verbose: false
  
  # JSON output for all commands
  # Default: false
  json_output: false
  
  # Interactive mode
  # Default: true
  interactive: true
  
  # Progress bars
  # Default: true
  show_progress: true
  
  # Confirmation prompts
  # Default: true
  confirm_actions: true
  
  # Command history size
  # Default: 100
  history_size: 100
  
  # Default command timeout (seconds)
  # Default: 300
  command_timeout: 300
```

## Features

Feature flags for experimental or optional functionality.

```yaml
features:
  # Experimental features
  experimental:
    # AI-powered code generation
    # Default: false
    ai_codegen: false
    
    # Quantum-inspired algorithms
    # Default: false
    quantum_algorithms: false
    
    # Advanced pattern recognition
    # Default: false
    advanced_patterns: false
  
  # Beta features
  beta:
    # Smart context switching
    # Default: true
    smart_context: true
    
    # Predictive file loading
    # Default: true
    predictive_loading: true
    
    # Auto-learning optimization
    # Default: true
    auto_optimization: true
  
  # Stable features (can be disabled)
  stable:
    # Event streaming
    # Default: true
    event_streaming: true
    
    # Quality monitoring
    # Default: true
    quality_monitoring: true
    
    # Performance tracking
    # Default: true
    performance_tracking: true
```

## User Preferences

User-specific preferences for A1 behavior.

```yaml
preferences:
  # Editor integration
  editor:
    # Default editor command
    # Default: "code"
    command: "code"
    
    # Open files in editor on error
    # Default: true
    open_on_error: true
    
    # Editor line format
    # Default: "{file}:{line}:{column}"
    line_format: "{file}:{line}:{column}"
  
  # Notification preferences
  notifications:
    # Enable desktop notifications
    # Default: false
    desktop: false
    
    # Enable sound alerts
    # Default: false
    sound: false
    
    # Notification level
    # Options: "all", "errors", "none"
    # Default: "errors"
    level: "errors"
  
  # Display preferences
  display:
    # Theme
    # Options: "auto", "light", "dark"
    # Default: "auto"
    theme: "auto"
    
    # Date format
    # Default: "YYYY-MM-DD HH:mm:ss"
    date_format: "YYYY-MM-DD HH:mm:ss"
    
    # Number format
    # Options: "comma", "space", "none"
    # Default: "comma"
    number_format: "comma"
    
    # Max output lines
    # Default: 1000
    max_output_lines: 1000
```

## Environment Variables

All configuration values can be overridden using environment variables.

### Naming Convention

Environment variables follow the pattern:
```
QUAESTOR_A1_<SECTION>_<SUBSECTION>_<KEY>
```

### Examples

```bash
# System settings
export QUAESTOR_A1_SYSTEM_DEBUG=true
export QUAESTOR_A1_SYSTEM_LOG_LEVEL=debug
export QUAESTOR_A1_SYSTEM_MODE=development

# Core component settings
export QUAESTOR_A1_CORE_EVENT_BUS_MAX_QUEUE_SIZE=20000
export QUAESTOR_A1_CORE_CONTEXT_MANAGER_MAX_CONTEXT_SIZE=100
export QUAESTOR_A1_CORE_QUALITY_GUARDIAN_MIN_QUALITY_SCORE=80

# Extension settings
export QUAESTOR_A1_EXTENSIONS_PREDICTION=false
export QUAESTOR_A1_EXTENSIONS_CONFIG_PREDICTION_MAX_PREDICTIONS=10

# CLI settings
export QUAESTOR_A1_CLI_OUTPUT_FORMAT=json
export QUAESTOR_A1_CLI_VERBOSE=true

# Feature flags
export QUAESTOR_A1_FEATURES_EXPERIMENTAL_AI_CODEGEN=true
export QUAESTOR_A1_FEATURES_BETA_SMART_CONTEXT=false
```

### Special Environment Variables

```bash
# Override config file location
export QUAESTOR_A1_CONFIG_FILE=/path/to/config.yaml

# Disable all extensions
export QUAESTOR_A1_EXTENSIONS_ALL=false

# Set multiple values with JSON
export QUAESTOR_A1_CORE_QUALITY_GUARDIAN='{"min_quality_score":80,"auto_check":false}'
```

## Configuration Management

### Initialization

Create default configuration:

```bash
quaestor a1 config init
```

This creates `.quaestor/a1_config.yaml` with sensible defaults.

### Validation

Validate configuration file:

```bash
quaestor a1 config validate
```

Output:
```
✓ Configuration valid
  - Schema version: 2.1.0
  - Components configured: 5
  - Extensions enabled: 5
  - No errors found
```

### Viewing Configuration

Show current configuration:

```bash
# Show all configuration
quaestor a1 config show

# Show specific section
quaestor a1 config show system

# Show specific value
quaestor a1 config get core.quality_guardian.min_quality_score
```

### Modifying Configuration

Set configuration values:

```bash
# Set single value
quaestor a1 config set system.debug true

# Set nested value
quaestor a1 config set core.quality_guardian.min_quality_score 80

# Set with JSON
quaestor a1 config set extensions_config.prediction '{"max_predictions":10}'
```

### Reset Configuration

Reset to defaults:

```bash
# Reset everything
quaestor a1 config reset

# Reset specific section
quaestor a1 config reset core.quality_guardian
```

### Configuration Profiles

A1 supports configuration profiles for different environments:

```yaml
# .quaestor/profiles/development.yaml
system:
  mode: "development"
  debug: true
  log_level: "debug"

core:
  quality_guardian:
    min_quality_score: 60.0  # More lenient in dev

# .quaestor/profiles/production.yaml  
system:
  mode: "production"
  debug: false
  log_level: "warning"

core:
  quality_guardian:
    min_quality_score: 85.0  # Strict in production
```

Load profile:
```bash
quaestor a1 --profile development <command>
```

## Examples

### Minimal Configuration

```yaml
# Minimal .quaestor/a1_config.yaml
system:
  version: "2.1.0"
```

### Development Configuration

```yaml
# Development-focused configuration
system:
  version: "2.1.0"
  mode: "development"
  debug: true
  log_level: "debug"

core:
  context_manager:
    max_context_size: 100  # More files in dev
  quality_guardian:
    min_quality_score: 65.0  # More lenient
    auto_check: false  # Manual checks only
  learning_manager:
    real_time_learning: true
    pattern_threshold: 2  # Learn faster

extensions:
  prediction: true
  hooks: true
  state: true
  workflow: true
  persistence: true

cli:
  verbose: true
  confirm_actions: false  # Skip confirmations

features:
  beta:
    smart_context: true
    predictive_loading: true
```

### Production Configuration

```yaml
# Production-optimized configuration
system:
  version: "2.1.0"
  mode: "production"
  debug: false
  log_level: "warning"
  telemetry_enabled: true

core:
  event_bus:
    max_queue_size: 50000  # Handle high load
    processing_timeout: 60.0
  context_manager:
    max_context_size: 30  # Conservative
    auto_optimization: true
  quality_guardian:
    min_quality_score: 85.0  # Strict
    auto_check: true
    severity_thresholds:
      error: 80.0
      warning: 85.0
      info: 90.0
  analysis_engine:
    parallel_analysis: true
    worker_count: 8  # More workers

extensions:
  prediction: true
  hooks: false  # No arbitrary code execution
  state: true
  workflow: true
  persistence: true

extensions_config:
  persistence:
    encryption_enabled: true
    backup:
      enabled: true
      interval: 3600
      keep_count: 10

cli:
  output_format: "plain"
  json_output: true  # Machine-readable
  confirm_actions: true

features:
  experimental:
    ai_codegen: false  # No experimental features
  stable:
    performance_tracking: true
```

### CI/CD Configuration

```yaml
# CI/CD pipeline configuration
system:
  version: "2.1.0"
  mode: "testing"
  debug: false
  log_level: "info"

core:
  quality_guardian:
    min_quality_score: 80.0
    auto_check: true
    check_timeout: 120.0  # Longer timeout for CI
  analysis_engine:
    parallel_analysis: true
    worker_count: 4

extensions:
  prediction: false  # Not needed in CI
  hooks: true  # For CI integration
  state: false
  workflow: false
  persistence: true

cli:
  output_format: "plain"
  json_output: true
  interactive: false  # Non-interactive
  confirm_actions: false
  show_progress: false  # Clean logs

features:
  stable:
    quality_monitoring: true
    performance_tracking: false  # Not in CI
```

### Extension-Specific Configuration

```yaml
# Focus on specific extensions
system:
  version: "2.1.0"

# Disable most core features
core:
  quality_guardian:
    auto_check: false
  learning_manager:
    real_time_learning: false

# Enable only needed extensions  
extensions:
  prediction: true
  hooks: false
  state: true
  workflow: false
  persistence: false

# Configure enabled extensions
extensions_config:
  prediction:
    max_predictions: 10
    min_confidence: 0.5
    history_size: 200
    cache_enabled: true
    
  state:
    max_snapshots: 100
    compression: true
    auto_snapshot_interval: 300  # Every 5 minutes
```

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   ```bash
   # Check file exists
   ls -la .quaestor/a1_config.yaml
   
   # Validate syntax
   quaestor a1 config validate
   ```

2. **Environment variables not working**
   ```bash
   # Check variable is exported
   echo $QUAESTOR_A1_SYSTEM_DEBUG
   
   # Use explicit export
   export QUAESTOR_A1_SYSTEM_DEBUG=true
   ```

3. **Values not updating**
   ```bash
   # Check configuration precedence
   quaestor a1 config show --source
   
   # Force reload
   quaestor a1 config reload
   ```

### Configuration Debugging

Enable configuration debugging:

```bash
QUAESTOR_A1_CONFIG_DEBUG=true quaestor a1 config show
```

This shows:
- Configuration file path
- Loaded values and their sources
- Environment variable overrides
- Validation results

## Best Practices

1. **Start with defaults**: Only override what you need
2. **Use profiles**: Different configs for dev/prod
3. **Version control**: Track config files in git
4. **Document changes**: Comment why values are set
5. **Validate regularly**: Run validation in CI/CD
6. **Use environment variables**: For secrets and deployment-specific values
7. **Keep it simple**: Don't over-configure
8. **Monitor performance**: Adjust based on metrics

## Migration from v0.4.0

A1 can import v0.4.0 configuration:

```bash
# Import v0.4.0 config
quaestor a1 config import --from=v0.4.0

# Review imported config
quaestor a1 config show

# Validate
quaestor a1 config validate
```

Key mapping:
- `mode` → `system.mode`
- `hooks.enabled` → `extensions.hooks`
- `rules` → `core.quality_guardian`
- `project.complexity` → Used for auto-configuration