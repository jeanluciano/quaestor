"""Centralized constants for quaestor."""

from pathlib import Path

# Command files that get installed to ~/.claude/commands
COMMAND_FILES = [
    "project-init.md",  # Initialize project documentation
    "research.md",  # Intelligent codebase exploration and discovery
    "plan.md",  # Strategic planning and progress management
    "impl.md",  # Implementation with agent orchestration
    "debug.md",  # Interactive debugging and troubleshooting
    "review.md",  # Comprehensive review, validation, and shipping
]

# Deprecated commands (to be removed in future version)
DEPRECATED_COMMANDS = [
    "status.md",  # Absorbed into /plan
    "check.md",  # Absorbed into /review
    "analyze.md",  # Split between /research and /review
    "commit.md",  # Absorbed into /review
]

# File categorization for update logic
SYSTEM_FILES = ["AGENT.md", "hooks.json"]
USER_EDITABLE_FILES = ["ARCHITECTURE.md", "MANIFEST.yaml", "CLAUDE.md"]

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
    "AGENT.md": f"{QUAESTOR_DIR_NAME}/AGENT.md",  # Source -> Target
}

# Quaestor config markers for CLAUDE.md
QUAESTOR_CONFIG_START = "<!-- QUAESTOR CONFIG START -->"
QUAESTOR_CONFIG_END = "<!-- QUAESTOR CONFIG END -->"


# Template file mappings (actual filename -> output filename)
TEMPLATE_FILES = {
    "agent.md": "AGENT.md",
    "architecture.md": "ARCHITECTURE.md",
    "rules.md": "RULES.md",
}

# Template base path within assets
TEMPLATE_BASE_PATH = "quaestor.claude"
