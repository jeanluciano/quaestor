"""Quaestor hooks for Claude Code integration.

This module contains self-contained hooks that integrate with Claude Code's
hook system to provide automated workflow management, validation, and tracking.

Available hooks:
- milestone_tracker: Tracks milestone progress and validates work tracking
- memory_tracker: Syncs MEMORY.md with TODO completions and work progress
- research_workflow_tracker: Tracks research phase activities
- todo_milestone_connector: Connects TODO changes to milestone tracking
- compliance_validator: Validates Quaestor compliance requirements
- file_change_tracker: Tracks file changes and reminds about updates
- base: Base hook class with common utilities
"""

__all__ = [
    "milestone_tracker",
    "memory_tracker",
    "research_workflow_tracker",
    "todo_milestone_connector",
    "compliance_validator",
    "file_change_tracker",
    "base",
]
