"""CLI commands for Quaestor hooks - callable via uvx."""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from quaestor.claude.hooks.session_context_loader import SessionContextLoaderHook
from quaestor.claude.hooks.todo_spec_progress import TodoSpecProgressHook
from quaestor.core.spec_schema import SpecificationSchema
from quaestor.utils.yaml_utils import load_yaml

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


@hooks_app.command(name="validate-spec")
def validate_spec(spec_file: str = typer.Argument(..., help="Path to the specification file to validate")):
    """Claude hook: Validate a specification file after writing."""
    try:
        file_path = Path(spec_file)

        # Load and validate the spec
        spec_data = load_yaml(file_path)

        if not spec_data:
            output = {"error": f"File is empty or invalid YAML: {spec_file}", "blocking": True}
            print(json.dumps(output))
            sys.exit(1)

        spec_id = spec_data.get("id", "unknown")
        is_valid, errors = SpecificationSchema.validate(spec_data)

        if is_valid:
            # Success - output Claude-compatible message
            output = {"message": f"✅ Specification '{spec_id}' is valid", "blocking": False}
            print(json.dumps(output))
            sys.exit(0)
        else:
            # Validation failed - block the operation
            error_msg = f"❌ Specification '{spec_id}' validation failed:\n"
            for error in errors[:5]:  # Show first 5 errors
                error_msg += f"  • {error}\n"

            output = {"error": error_msg, "blocking": True, "validation_errors": errors}
            print(json.dumps(output))
            sys.exit(1)

    except Exception as e:
        # Unexpected error
        output = {"error": f"Failed to validate spec: {str(e)}", "blocking": True}
        print(json.dumps(output))
        sys.exit(1)
