# Quaestor A1 User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Features](#core-features)
5. [Extensions](#extensions)
6. [CLI Commands](#cli-commands)
7. [Configuration](#configuration)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)
10. [Migration from v0.4.0](#migration-from-v040)

## Introduction

Quaestor A1 is a simplified, high-performance AI context management system designed to enhance AI-assisted development workflows. It provides intelligent context tracking, quality monitoring, and learning capabilities while maintaining a clean, maintainable architecture.

### Key Benefits

- **Simplified Architecture**: 79% less code than V2.0 while maintaining full functionality
- **Blazing Performance**: Sub-millisecond response times, minimal memory usage
- **Modular Extensions**: Enable only the features you need
- **Intelligent Learning**: Adapts to your development patterns
- **Quality Focused**: Built-in quality monitoring and analysis

## Installation

### Prerequisites

- Python 3.10 or higher
- uv (recommended) or pip

### Install with uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Quaestor
uv pip install quaestor
```

### Install with pip

```bash
pip install quaestor
```

### Verify Installation

```bash
quaestor a1 --version
# Output: Quaestor A1 - Version 2.1.0
```

## Quick Start

### 1. Initialize A1 in Your Project

```bash
cd your-project
quaestor a1 init
```

This creates a `.quaestor/a1_config.yaml` file with default settings.

### 2. Check System Status

```bash
quaestor a1 status
```

Shows current system status, active components, and extensions.

### 3. Analyze Your Code

```bash
quaestor a1 analysis check src/
```

Performs code quality analysis on your source directory.

### 4. Monitor Performance

```bash
quaestor a1 performance
```

Launches real-time performance monitoring dashboard.

## Core Features

### 1. Event-Driven Architecture

A1 uses an event bus to coordinate all components:

```bash
# View recent events
quaestor a1 event recent

# Monitor events in real-time
quaestor a1 event stream
```

### 2. Context Management

Intelligent context tracking for different work modes:

```bash
# Switch context
quaestor a1 context switch development

# View current context
quaestor a1 context show

# Add files to context
quaestor a1 context add src/main.py
```

Context types:
- `development`: Active coding
- `debugging`: Problem solving
- `testing`: Test creation/execution
- `research`: Documentation/exploration

### 3. Quality Guardian

Continuous code quality monitoring:

```bash
# Run quality check
quaestor a1 quality check

# View quality report
quaestor a1 quality report

# Check specific files
quaestor a1 quality check src/main.py src/utils.py
```

### 4. Learning System

Adapts to your development patterns:

```bash
# View learning insights
quaestor a1 learning show

# Get workflow suggestions
quaestor a1 learning suggest

# View detected patterns
quaestor a1 learning patterns
```

### 5. Code Analysis

Deep code analysis capabilities:

```bash
# Analyze project structure
quaestor a1 analysis structure

# Get code metrics
quaestor a1 analysis metrics

# Find quality issues
quaestor a1 analysis issues
```

## Extensions

A1 includes optional extensions you can enable based on your needs:

### 1. Prediction Engine

AI-powered predictions for tools and files:

```bash
# Enable prediction
quaestor a1 config set extensions.prediction true

# Get predictions
quaestor a1 predict tool
quaestor a1 predict file
```

### 2. State Management

Snapshot and restore project states:

```bash
# Create snapshot
quaestor a1 state snapshot "Before refactoring"

# List snapshots
quaestor a1 state list

# Restore snapshot
quaestor a1 state restore <snapshot-id>

# Undo last change
quaestor a1 state undo
```

### 3. Workflow Detection

Automatic workflow recognition:

```bash
# View current workflows
quaestor a1 extensions workflow status

# Get workflow insights
quaestor a1 extensions workflow analyze
```

### 4. Hook System

Event-driven automation:

```bash
# Configure hooks
quaestor a1 extensions hooks configure

# List active hooks
quaestor a1 extensions hooks list

# Test hooks
quaestor a1 extensions hooks test
```

### 5. Persistence

Data storage and caching:

```bash
# View persistence status
quaestor a1 extensions persistence status

# Clear cache
quaestor a1 extensions persistence clear
```

## CLI Commands

### Global Options

- `--help`: Show help for any command
- `--verbose`: Enable verbose output
- `--json`: Output in JSON format

### Command Structure

```
quaestor a1 <component> <action> [options]
```

### Complete Command Reference

```bash
# System Commands
quaestor a1 status              # System status
quaestor a1 init               # Initialize A1
quaestor a1 performance        # Performance dashboard

# Event Commands
quaestor a1 event recent       # Recent events
quaestor a1 event stream       # Live event stream
quaestor a1 event stats        # Event statistics

# Context Commands
quaestor a1 context show       # Current context
quaestor a1 context switch     # Switch context type
quaestor a1 context add        # Add files to context
quaestor a1 context remove     # Remove files
quaestor a1 context optimize   # Optimize context

# Quality Commands
quaestor a1 quality check      # Run quality check
quaestor a1 quality report     # View report
quaestor a1 quality issues     # List issues
quaestor a1 quality stats      # Quality statistics

# Learning Commands
quaestor a1 learning show      # Learning status
quaestor a1 learning suggest   # Get suggestions
quaestor a1 learning patterns  # View patterns
quaestor a1 learning stats     # Learning statistics

# Analysis Commands
quaestor a1 analysis check     # Analyze code
quaestor a1 analysis structure # Project structure
quaestor a1 analysis metrics   # Code metrics
quaestor a1 analysis issues    # Quality issues

# Configuration Commands
quaestor a1 config show        # Show configuration
quaestor a1 config set         # Set value
quaestor a1 config get         # Get value
quaestor a1 config validate    # Validate config
quaestor a1 config reset       # Reset to defaults

# Extension Commands
quaestor a1 extensions list    # List extensions
quaestor a1 extensions enable  # Enable extension
quaestor a1 extensions disable # Disable extension
quaestor a1 extensions status  # Extension status
```

## Configuration

### Configuration File

A1 uses YAML configuration stored in `.quaestor/a1_config.yaml`:

```yaml
# System Configuration
system:
  version: "2.1.0"
  mode: "production"
  debug: false
  log_level: "info"

# Core Components
core:
  event_bus:
    max_queue_size: 10000
    async_processing: true
  context_manager:
    max_context_size: 50
    auto_optimization: true
  quality_guardian:
    min_quality_score: 70.0
    auto_check: true
  learning_manager:
    pattern_threshold: 3
    max_patterns: 1000
  analysis_engine:
    max_file_size: 1048576
    skip_patterns: ["*.pyc", "__pycache__"]

# Extensions
extensions:
  prediction: true
  hooks: true
  state: true
  workflow: true
  persistence: true

# CLI Settings
cli:
  output_format: "rich"
  color: true
  verbose: false
  json_output: false
```

### Environment Variables

Override configuration with environment variables:

```bash
export QUAESTOR_A1_DEBUG=true
export QUAESTOR_A1_LOG_LEVEL=debug
export QUAESTOR_A1_EXTENSIONS_PREDICTION=false
```

### Configuration Commands

```bash
# View current configuration
quaestor a1 config show

# Set a value
quaestor a1 config set core.quality_guardian.min_quality_score 80

# Get a value
quaestor a1 config get extensions.prediction

# Validate configuration
quaestor a1 config validate

# Reset to defaults
quaestor a1 config reset
```

## Common Workflows

### 1. Development Workflow

```bash
# Start development session
quaestor a1 context switch development

# Add relevant files
quaestor a1 context add src/*.py

# Monitor quality as you code
quaestor a1 quality check --watch

# Create snapshot before major changes
quaestor a1 state snapshot "Before refactoring"

# Get AI suggestions
quaestor a1 learning suggest
```

### 2. Debugging Workflow

```bash
# Switch to debugging context
quaestor a1 context switch debugging

# Analyze problem area
quaestor a1 analysis check src/problematic_module.py

# View recent events
quaestor a1 event recent --filter="error"

# Get debugging suggestions
quaestor a1 predict tool --context=debugging
```

### 3. Testing Workflow

```bash
# Switch to testing context
quaestor a1 context switch testing

# Add test files
quaestor a1 context add tests/*.py

# Check test quality
quaestor a1 quality check tests/

# Monitor test execution
quaestor a1 event stream --filter="test"
```

### 4. Code Review Workflow

```bash
# Analyze entire codebase
quaestor a1 analysis check .

# Generate quality report
quaestor a1 quality report --output=quality_report.html

# List all issues
quaestor a1 quality issues --severity=error

# Check specific metrics
quaestor a1 analysis metrics --metric=complexity
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'quaestor.a1'
# Solution: Ensure you've installed the latest version
uv pip install --upgrade quaestor
```

#### 2. Configuration Not Found

```bash
# Error: Configuration file not found
# Solution: Initialize A1 in your project
quaestor a1 init
```

#### 3. Extension Not Working

```bash
# Check if extension is enabled
quaestor a1 config get extensions.<name>

# Enable extension
quaestor a1 config set extensions.<name> true

# Verify extension status
quaestor a1 extensions status
```

#### 4. Performance Issues

```bash
# Monitor performance
quaestor a1 performance

# Check event queue
quaestor a1 event stats

# Optimize context
quaestor a1 context optimize
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Via environment variable
export QUAESTOR_A1_DEBUG=true

# Via configuration
quaestor a1 config set system.debug true

# Run with verbose output
quaestor a1 --verbose <command>
```

### Getting Help

```bash
# General help
quaestor a1 --help

# Command-specific help
quaestor a1 <command> --help

# System information
quaestor a1 status --detailed
```

## Migration from v0.4.0

### Side-by-Side Installation

A1 can run alongside v0.4.0:

```bash
# V0.4.0 commands
quaestor init
quaestor check

# A1 commands
quaestor a1 init
quaestor a1 quality check
```

### Migration Steps

1. **Install A1** while keeping v0.4.0
2. **Initialize A1** in your project: `quaestor a1 init`
3. **Test A1 features** without affecting v0.4.0
4. **Gradually migrate** workflows to A1
5. **Switch completely** when comfortable

### Feature Mapping

| v0.4.0 Feature | A1 Equivalent |
|----------------|-----------------|
| `quaestor check` | `quaestor a1 quality check` |
| Rule engine | Quality Guardian |
| Hooks | Extension: Hooks |
| Commands | Integrated CLI |
| Memory tracking | Learning Manager |

### Configuration Migration

A1 automatically recognizes v0.4.0 configuration and provides migration:

```bash
# Check migration compatibility
quaestor a1 migrate check

# Perform migration
quaestor a1 migrate run
```

## Best Practices

### 1. Context Management

- Switch contexts when changing work types
- Keep context focused (< 50 files)
- Use auto-optimization feature
- Review context periodically

### 2. Quality Monitoring

- Set appropriate quality thresholds
- Address critical issues immediately
- Use quality gates in CI/CD
- Monitor quality trends

### 3. Extension Usage

- Enable only needed extensions
- Configure extensions appropriately
- Monitor extension performance
- Use hooks for automation

### 4. Performance

- A1 is already highly optimized
- Default settings work for most projects
- Use performance dashboard for monitoring
- Report any performance issues

## Conclusion

Quaestor A1 provides a powerful, simplified approach to AI context management. Its clean architecture, blazing performance, and intelligent features make it an essential tool for modern development workflows.

For more information:
- [API Documentation](./A1_API_REFERENCE.md)
- [Extension Guide](./A1_EXTENSION_GUIDE.md)
- [Configuration Reference](./A1_CONFIG_REFERENCE.md)
- [Migration Guide](./A1_MIGRATION_GUIDE.md)