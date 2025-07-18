"""Centralized constants for quaestor."""

from pathlib import Path

# Command files that get installed to ~/.claude/commands
COMMAND_FILES = [
    "project-init.md",  # Initialize project documentation
    "task.md",  # Unified task command (auto-detects language)
    "status.md",  # Show project status
    "check.md",  # Run quality validation
    "analyze.md",  # Multi-dimensional code analysis
    "milestone.md",  # Manage project milestones
    "auto-commit.md",  # Auto-commit completed TODO items
    "milestone-pr.md",  # Create PR for completed milestones
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


# Template file mappings (actual filename -> output filename)
TEMPLATE_FILES = {
    "quaestor_claude.md": "QUAESTOR_CLAUDE.md",
    "critical_rules.md": "CRITICAL_RULES.md",
    "architecture.md": "ARCHITECTURE.md",
    "memory.md": "MEMORY.md",
    "patterns.md": "PATTERNS.md",
    "validation.md": "VALIDATION.md",
    "automation.md": "AUTOMATION.md",
}

# Template base path within assets
TEMPLATE_BASE_PATH = "quaestor.assets.templates"
