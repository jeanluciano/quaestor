"""Main CLI application setup."""

import os
import sys
import traceback
from datetime import datetime

import typer
from rich.console import Console

from quaestor.cli.config import config_app
from quaestor.cli.hooks import hooks_app
from quaestor.cli.init import init_command


# Enhanced Logging Mechanism
class QuaestorCLILogger:
    @staticmethod
    def log_debug(message: str, log_file: str = "/tmp/quaestor_cli_debug.log"):
        """Log debug messages with comprehensive details."""
        timestamp = datetime.now().isoformat()
        try:
            with open(log_file, "a") as f:
                log_entry = f"{timestamp} | PID:{os.getpid()} | {message}\n"
                f.write(log_entry)
        except Exception as e:
            print(f"Logging failed: {e}", file=sys.stderr)

    @staticmethod
    def log_error(message: str, error: Exception = None):
        """Log error messages with optional traceback."""
        error_log_file = "/tmp/quaestor_cli_error.log"
        timestamp = datetime.now().isoformat()

        try:
            with open(error_log_file, "a") as f:
                log_entry = f"{timestamp} | PID:{os.getpid()} | ERROR: {message}\n"
                if error:
                    log_entry += f"Traceback:\n{traceback.format_exc()}\n"
                f.write(log_entry)
        except Exception as log_error:
            print(f"Error logging failed: {log_error}", file=sys.stderr)


console = Console()

# Create the main Typer application with enhanced configuration
app = typer.Typer(
    name="quaestor",
    help="Quaestor - Context management for AI-assisted development",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120},
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    Global callback for the Quaestor CLI.

    This callback runs before any command and provides global logging and diagnostics.
    """
    # Log CLI invocation details
    QuaestorCLILogger.log_debug(f"CLI Invoked: {sys.argv}")

    # Log context information
    if ctx.invoked_subcommand:
        QuaestorCLILogger.log_debug(f"Subcommand invoked: {ctx.invoked_subcommand}")


# Register subcommands
app.add_typer(config_app, name="config")
app.add_typer(hooks_app, name="hook")
app.command(name="init")(init_command)
