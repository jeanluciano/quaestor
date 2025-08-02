"""Quaestor hooks for Claude Code integration.

This module contains self-contained hooks that integrate with Claude Code's
hook system to provide automated workflow management, validation, and tracking.

Available hooks:
- spec_tracker: Tracks specification progress and validates work tracking
- memory_tracker: Syncs MEMORY.md with TODO completions and work progress
- research_workflow_tracker: Tracks research phase activities
- todo_agent_coordinator: Coordinates agent usage based on TODO patterns
- compliance_validator: Validates Quaestor compliance requirements
- file_change_tracker: Tracks file changes and reminds about updates
- base: Base hook class with common utilities
"""

__all__ = [
    "spec_tracker",
    "memory_tracker",
    "research_workflow_tracker",
    "todo_agent_coordinator",
    "compliance_validator",
    "file_change_tracker",
    "base",
]
