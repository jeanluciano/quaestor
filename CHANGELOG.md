# Changelog

All notable changes to Quaestor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `constants.py` module to centralize configuration values
- Version headers to all template files for better tracking

### Changed
- Reorganized template files into `templates/` directory
- Improved project structure for better maintainability

### Removed
- Redundant `pytest.ini` file (configuration now in `pyproject.toml`)
- Development file `main.py`
- Build artifacts from version control

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