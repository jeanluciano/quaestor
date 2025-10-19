"""Quaestor hooks for Claude Code integration.

This module contains self-contained hooks that integrate with Claude Code's
hook system to provide automated workflow management, validation, and tracking.

Available hooks:
- memory_tracker: Syncs spec status with TODO completions and work progress
- research_workflow_tracker: Tracks research phase activities
- file_change_tracker: Tracks file changes and reminds about updates
- session_context_loader: Loads project context and active specs at session start
- base: Base hook class with common utilities
"""

__all__ = [
    "memory_tracker",
    "research_workflow_tracker",
    "file_change_tracker",
    "session_context_loader",
    "base",
]
