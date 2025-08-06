"""Main CLI application setup."""

import typer
from rich.console import Console

from quaestor.cli.config import config_app
from quaestor.cli.hooks import hooks_app
from quaestor.cli.init import init_command
from quaestor.cli.update import update_command

console = Console()

app = typer.Typer(
    name="quaestor",
    help="Quaestor - Context management for AI-assisted development",
    add_completion=False,
)


@app.callback()
def callback():
    """Quaestor - Context management for AI-assisted development."""
    pass


# Add commands to app
app.command(name="init")(init_command)
app.command(name="update")(update_command)

# Add configuration management commands
app.add_typer(config_app, name="config", help="Configuration management commands")

# Add hook commands (hidden from main help)
app.add_typer(hooks_app, name="hook", help="Claude hook commands (for internal use)")

# Add automation subcommand if available
try:
    from quaestor.automation import app as automation_app

    app.add_typer(automation_app, name="automation", help="Claude Code automation management")
except ImportError:
    # Automation module not available
    pass

# Add A1 integration if available
try:
    from quaestor.integrations import add_a1_to_cli

    add_a1_to_cli(app)
except ImportError:
    # A1 integration not available
    pass


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
