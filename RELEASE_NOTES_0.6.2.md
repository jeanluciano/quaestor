# Quaestor v0.6.2 Release Notes

## 🎉 Major Features

### Language Configuration Integration System
Quaestor now actively uses language configurations to dynamically populate templates with project-specific settings. This means your AI context automatically adapts to your project's language and tooling!

#### Key Improvements:
- **Dynamic Templates**: Templates now populate with 50+ language-specific placeholders
- **5-Layer Configuration**: Sophisticated precedence system for maximum flexibility
- **Type-Safe Schemas**: Pydantic-based validation ensures configuration integrity
- **Smart Defaults**: Sensible defaults for Python, JavaScript, TypeScript, Rust, Go, Java, and Ruby

### New CLI Configuration Commands
Managing your Quaestor configuration is now easier than ever with the new `quaestor config` command suite:

```bash
# View your current configuration
quaestor config show

# Get specific values
quaestor config get languages.python.lint_command

# Set overrides
quaestor config set languages.python.coverage_threshold 95

# Validate your configuration
quaestor config validate

# Reset to defaults
quaestor config reset
```

## 🔧 Technical Improvements

### Simplified Configuration System
- Removed unused configuration fields (QualityConfig, WorkflowConfig, etc.)
- Focused on essential language configurations
- Cleaner, more maintainable codebase

### Enhanced Template System
- Templates now support conditional sections based on language features
- Automatic adaptation to detected project type
- New `rules.md` template for language-specific development guidance

### Removed Backward Compatibility
- Eliminated legacy `QuaestorConfig` class
- Direct use of modern `ConfigManager` throughout
- Cleaner API with better documentation

## 📚 New Documentation

### Configuration Examples
- `.quaestor/languages.yaml.example` - Shows how to override language settings
- `.quaestor/config.yaml.example` - Demonstrates main configuration options
- Comprehensive inline documentation for all settings

## 🐛 Bug Fixes
- Fixed `rules.md` template not being generated during initialization
- Templates now correctly populate with language-specific settings

## 📦 Installation

```bash
pip install quaestor==0.6.2
```

## 🔄 Migration Guide

If you're upgrading from 0.6.1:

1. The backward compatibility layer has been removed. If you were using `QuaestorConfig`, update to use `ConfigManager` directly:
   ```python
   # Old
   from quaestor.core.configuration import QuaestorConfig
   config = QuaestorConfig(project_root)
   
   # New
   from quaestor.core.config_manager import ConfigManager
   config = ConfigManager(project_root)
   ```

2. Configuration schema has been simplified. Remove any references to:
   - `mode` (personal/team)
   - `quality` settings
   - `workflow` settings
   - `command` configurations

3. New CLI commands are available - try `quaestor config show` to see your configuration!

## 🙏 Acknowledgments

Thanks to all contributors and users who provided feedback for this release!

---

For detailed changes, see the [CHANGELOG.md](CHANGELOG.md)