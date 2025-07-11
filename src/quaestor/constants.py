"""Centralized constants for quaestor."""

from pathlib import Path

# Command files that get installed to ~/.claude/commands
COMMAND_FILES = [
    "help.md",  # Show available commands
    "project-init.md",  # Initialize project documentation
    "task.md",  # Unified task command (auto-detects language)
    "status.md",  # Show project status
    "check.md",  # Run quality validation
    "milestone.md",  # Manage project milestones
    "milestone-commit.md",  # Create atomic commits
]

# File categorization for update logic
SYSTEM_FILES = ["CRITICAL_RULES.md", "hooks.json", "QUAESTOR_CLAUDE.md"]
USER_EDITABLE_FILES = ["ARCHITECTURE.md", "MEMORY.md", "MANIFEST.yaml", "CLAUDE.md"]

# Version extraction patterns
VERSION_PATTERNS = [
    r"<!--\s*QUAESTOR:version:([0-9.]+)\s*-->",
    r"<!--\s*META:version:([0-9.]+)\s*-->",
    r"<!--\s*VERSION:([0-9.]+)\s*-->",
]

# Default paths
DEFAULT_CLAUDE_DIR = Path.home() / ".claude"
DEFAULT_COMMANDS_DIR = DEFAULT_CLAUDE_DIR / "commands"
QUAESTOR_DIR_NAME = ".quaestor"

# File mappings for init command
INIT_FILES = {
    "QUAESTOR_CLAUDE.md": f"{QUAESTOR_DIR_NAME}/QUAESTOR_CLAUDE.md",  # Source -> Target
    "CRITICAL_RULES.md": f"{QUAESTOR_DIR_NAME}/CRITICAL_RULES.md",
}

# Quaestor config markers for CLAUDE.md
QUAESTOR_CONFIG_START = "<!-- QUAESTOR CONFIG START -->"
QUAESTOR_CONFIG_END = "<!-- QUAESTOR CONFIG END -->"

# Manifest file mappings (source package -> target path in .quaestor)
MANIFEST_FILES = {
    "ARCHITECTURE.md": "ARCHITECTURE.md",
    "MEMORY.md": "MEMORY.md",
}

# Template file mappings
TEMPLATE_FILES = {
    "ARCHITECTURE.template.md": "ARCHITECTURE.md",
    "MEMORY.template.md": "MEMORY.md",
}
