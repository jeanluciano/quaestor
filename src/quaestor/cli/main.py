"""Main CLI application setup."""

import typer
from rich.console import Console

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


# Import and register commands at module level
from .init import init_command

# Add commands to app
app.command(name="init")(init_command)

# Register other commands
from .configure import configure_command
from .update import update_command

app.command(name="configure")(configure_command)
app.command(name="update")(update_command)

# Add hooks subcommand if available
try:
    from ..hooks import app as hooks_app

    app.add_typer(hooks_app, name="hooks", help="Claude Code hooks management")
except ImportError:
    # Hooks module not available
    pass


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
