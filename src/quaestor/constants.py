"""Centralized constants for quaestor."""

from pathlib import Path

# Command files that get installed to ~/.claude/commands
COMMAND_FILES = [
    "project-init.md",
    "task-py.md",
    "task-rs.md",
    "check.md",
    "compose.md",
    "milestone-commit.md",
]

# File categorization for update logic
SYSTEM_FILES = ["CRITICAL_RULES.md", "hooks.json", "CLAUDE.md"]
USER_EDITABLE_FILES = ["ARCHITECTURE.md", "MEMORY.md", "MANIFEST.yaml"]

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
    "CLAUDE.md": "CLAUDE.md",  # Source -> Target
    "CRITICAL_RULES.md": f"{QUAESTOR_DIR_NAME}/CRITICAL_RULES.md",
}

# Manifest file mappings (source package -> target path in .quaestor)
MANIFEST_FILES = {
    "ARCHITECTURE.md": "ARCHITECTURE.md",
    "MEMORY.md": "MEMORY.md",
}

# Template file mappings
TEMPLATE_FILES = {
    "ai_architecture.md": "ARCHITECTURE.md",
    "ai_memory.md": "MEMORY.md",
}
