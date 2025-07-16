"""Main CLI application setup."""

import typer
from rich.console import Console

from .configure import configure_command
from .init import init_command
from .update import update_command

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

app.command(name="configure")(configure_command)
app.command(name="update")(update_command)

# Add automation subcommand if available
try:
    from quaestor.automation import app as automation_app

    app.add_typer(automation_app, name="automation", help="Claude Code automation management")
except ImportError:
    # Automation module not available
    pass


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
