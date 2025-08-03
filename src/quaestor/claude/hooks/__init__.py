"""Quaestor hooks for Claude Code integration.

This module contains self-contained hooks that integrate with Claude Code's
hook system to provide automated workflow management, validation, and tracking.

Available hooks:
- spec_tracker: Tracks specification progress and validates work tracking
- memory_tracker: Syncs MEMORY.md with TODO completions and work progress
- research_workflow_tracker: Tracks research phase activities
- compliance_validator: Validates Quaestor compliance requirements
- file_change_tracker: Tracks file changes and reminds about updates
- user_prompt_submit: Detects user intent and sets session mode (framework/drive)
- mode_detection: Core mode detection logic for dual-mode behavior
- base: Base hook class with common utilities
"""

__all__ = [
    "spec_tracker",
    "memory_tracker",
    "research_workflow_tracker",
    "compliance_validator",
    "file_change_tracker",
    "user_prompt_submit",
    "mode_detection",
    "base",
]
