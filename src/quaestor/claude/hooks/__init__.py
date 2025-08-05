"""Quaestor hooks for Claude Code integration.

This module contains self-contained hooks that integrate with Claude Code's
hook system to provide automated workflow management, validation, and tracking.

Available hooks:
- spec_tracker: Tracks specification progress and validates work tracking
- memory_tracker: Syncs spec status with TODO completions and work progress
- research_workflow_tracker: Tracks research phase activities
- file_change_tracker: Tracks file changes and reminds about updates
- rule_injection: Injects general rules and reminders
- session_context_loader: Loads project context at session start
- spec_lifecycle: Manages specification lifecycle transitions
- base: Base hook class with common utilities
"""

__all__ = [
    "spec_tracker",
    "memory_tracker",
    "research_workflow_tracker",
    "file_change_tracker",
    "rule_injection",
    "session_context_loader",
    "spec_lifecycle",
    "base",
]
