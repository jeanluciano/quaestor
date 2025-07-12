# Changelog

All notable changes to Quaestor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.42] - 2025-01-12

### Major Improvements

#### 🔧 Claude Code Integration Fixes
- Fixed hooks format to match new Claude Code requirements
- Updated hooks location from .claude/settings/claude_code_hooks.json to .claude/settings.json
- Changed matcher format from object to string patterns

#### 📋 Comprehensive Milestone Tracking
- Added 7 new hooks for complete workflow compliance
- Enhanced update-memory.py with intelligent milestone detection
- Added mandatory milestone awareness to task command
- Created CRITICAL_RULES.md with enforcement guidelines

#### 🧪 Workflow Validation System
- New comprehensive-compliance-check.py for full system validation
- Enhanced workflow state tracking
- Multi-layer compliance verification
- Automatic milestone progress detection

#### 📚 Documentation Updates
- Simplified README while maintaining accuracy (50% reduction)
- Enhanced task command documentation
- Added critical rules for milestone tracking

### New Hooks Added
- track-research.py - Research phase tracking
- track-implementation.py - Implementation phase tracking  
- pre-implementation-declaration.py - Mandatory milestone declaration
- todo-milestone-connector.py - Links todos to milestones
- file-change-tracker.py - Detects untracked changes
- milestone-validator.py - Validates compliance
- comprehensive-compliance-check.py - Full system validation

### Fixed
- Fixed hooks generation bug with Jinja2 templates
- Fixed all ruff linting issues (36 errors resolved)
- Fixed bare except clauses and missing newlines in hook scripts
- Fixed hook configuration format to match Claude Code documentation

## [0.3.3] - 2024-07-11

### Fixed
- Various bug fixes and improvements

## [0.3.0] - 2024-07-10

### Added
- Non-intrusive CLAUDE.md integration that preserves user content
- Smart merging capability for CLAUDE.md with clear config sections
- QUAESTOR_CLAUDE.md as the main framework file (stored in .quaestor/)
- CLAUDE_INCLUDE.md template for minimal user-facing config
- `constants.py` module to centralize configuration values
- Version headers to all template files for better tracking

### Changed
- CLAUDE.md is now categorized as USER_EDITABLE (never overwritten)
- Reorganized template files into `templates/` directory
- Improved project structure for better maintainability
- Enhanced README with focus on quick usage and technical transparency
- Updated file categorization to respect user customizations

### Removed
- Redundant `pytest.ini` file (configuration now in `pyproject.toml`)
- Development file `main.py`
- Build artifacts from version control

### Breaking Changes
- CLAUDE.md is no longer replaced during init - existing content is preserved
- Full framework instructions moved to .quaestor/QUAESTOR_CLAUDE.md

## [0.2.4] - 2024-01-10

### Added
- Intelligent update system with file manifest tracking
- Smart updater that preserves user customizations
- Update command with `--check`, `--backup`, and `--force` options
- File categorization system (SYSTEM, USER_EDITABLE, COMMAND, TEMPLATE)
- Version tracking in file headers
- Comprehensive test coverage for update functionality

### Fixed
- Version mismatch in `__init__.py`
- Update logic to prevent overwriting user modifications

## [0.2.3] - 2024-01-09

### Fixed
- Added missing `milestone-commit.md` to command files list

## [0.2.2] - 2024-01-09

### Added
- Claude Code hooks integration for workflow automation
- Hooks modules for enforcement, automation, and intelligence
- Automated milestone commit workflow

## [0.2.1] - 2024-01-08

### Fixed
- Milestone status detection in MEMORY.md converter

## [0.2.0] - 2024-01-08

### Added
- Workflow automation with milestone-commit command
- AI-optimized markdown format converters
- Enhanced MEMORY.md tracking

## [0.1.0] - 2024-01-01

### Added
- Initial release of Quaestor
- Core CLI with `init` command
- CLAUDE.md and CRITICAL_RULES.md templates
- Command templates for project management
- Basic project structure initialization
- Integration with Claude AI assistant configuration