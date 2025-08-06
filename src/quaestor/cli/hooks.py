"""CLI commands for Quaestor hooks - callable via uvx."""

import json
import sys

import typer
from rich.console import Console

from quaestor.claude.hooks.session_context_loader import SessionContextLoaderHook
from quaestor.claude.hooks.todo_spec_progress import TodoSpecProgressHook

console = Console()

# Hidden app for hook commands - not shown in main help
hooks_app = typer.Typer(hidden=True)


@hooks_app.command(name="session-context-loader")
def session_context_loader():
    """Claude hook: Load active specifications into session context."""
    try:
        hook = SessionContextLoaderHook()
        hook.run()
    except Exception as e:
        # Output error in Claude-compatible format
        output = {"error": str(e), "blocking": False}
        print(json.dumps(output))
        sys.exit(1)


@hooks_app.command(name="todo-spec-progress")
def todo_spec_progress():
    """Claude hook: Track specification progress from TODO completions."""
    try:
        hook = TodoSpecProgressHook()
        hook.run()
    except Exception as e:
        # Output error in Claude-compatible format
        output = {"error": str(e), "blocking": False}
        print(json.dumps(output))
        sys.exit(1)
