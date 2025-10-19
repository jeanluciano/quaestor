"""Centralized constants for quaestor."""

# Directory name for Quaestor files
QUAESTOR_DIR_NAME = ".quaestor"

# Template file mappings (template filename -> output filename)
TEMPLATE_FILES = {
    "agent.md": "AGENT.md",
    "architecture.md": "ARCHITECTURE.md",
    "rules.md": "RULES.md",
}

# Template base path within package
TEMPLATE_BASE_PATH = "quaestor"

# Quaestor config markers for CLAUDE.md
QUAESTOR_CONFIG_START = "<!-- QUAESTOR CONFIG START -->"
QUAESTOR_CONFIG_END = "<!-- QUAESTOR CONFIG END -->"
