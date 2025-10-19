"""CLI commands for Quaestor hooks - callable via uvx."""

import json
import sys
import traceback
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Hidden app for hook commands - not shown in main help
hooks_app = typer.Typer(hidden=True, help="Claude hook commands (for internal use)")


@hooks_app.command(name="session-context-loader")
def session_context_loader():
    """Claude hook: Load active specifications into session context."""
    try:
        from quaestor.hooks.session_context_loader import SessionContextLoaderHook

        hook = SessionContextLoaderHook()
        hook.run()
    except Exception as e:
        # Output error in Claude-compatible format
        output = {"error": str(e), "blocking": False}
        print(json.dumps(output))
        sys.exit(1)


@hooks_app.command(name="validate-spec")
def validate_spec(spec_file: str = typer.Argument(..., help="Path to the specification markdown file")):
    """Claude hook: Validate a specification file after writing."""
    try:
        from quaestor.cli.spec import get_spec_manager, validate_single_spec

        file_path = Path(spec_file).resolve()
        spec_id = file_path.stem

        spec_mgr = get_spec_manager()
        if not spec_mgr:
            output = {"error": "Could not initialize specification manager", "blocking": True}
            print(json.dumps(output))
            sys.exit(1)

        result = validate_single_spec(spec_mgr, spec_id)

        if result.valid:
            # Success - output Claude-compatible message
            output = {"message": f"✅ Specification '{spec_id}' is valid", "blocking": False, "spec_id": spec_id}
            print(json.dumps(output))
            sys.exit(0)
        else:
            # Validation failed - block the operation
            errors = [i for i in result.issues if i["level"] == "error"]
            warnings = [i for i in result.issues if i["level"] == "warning"]

            error_msg = f"❌ Specification '{spec_id}' validation failed:\n"
            for error in errors[:5]:  # Show first 5 errors
                error_msg += f"  • {error['message']}\n"

            if warnings:
                error_msg += "\nWarnings:\n"
                for warning in warnings[:3]:
                    error_msg += f"  ⚠️  {warning['message']}\n"

            output = {
                "error": error_msg,
                "blocking": True,
                "spec_id": spec_id,
                "validation_errors": errors,
                "warnings": warnings,
            }
            print(json.dumps(output))
            sys.exit(1)

    except Exception as e:
        # Unexpected error
        output = {"error": f"Failed to validate spec: {str(e)}", "blocking": True, "traceback": traceback.format_exc()}
        print(json.dumps(output))
        sys.exit(1)


def main():
    """Entry point for hook commands."""
    hooks_app()
