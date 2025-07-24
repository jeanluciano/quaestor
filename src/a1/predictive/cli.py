"""CLI commands for the A1 predictive engine."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from a1.core.event_bus import EventBus

from .patterns import PatternType
from .predictive_engine import PredictiveEngine

app = typer.Typer(help="A1 Predictive Engine commands")
console = Console()


def get_engine() -> PredictiveEngine:
    """Get or create predictive engine instance."""
    event_bus = EventBus()
    return PredictiveEngine(event_bus)


@app.command()
def status():
    """Show predictive engine status and statistics."""
    engine = get_engine()
    stats = engine.get_pattern_statistics()
    workflow_status = engine.get_workflow_status()

    # Create status table
    table = Table(title="Predictive Engine Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Patterns", str(stats["total_patterns"]))
    table.add_row("High Confidence", str(stats["high_confidence"]))
    table.add_row("Recent Discoveries", str(stats["recent_discoveries"]))

    # Pattern breakdown
    for ptype, count in stats["by_type"].items():
        table.add_row(f"  {ptype}", str(count))

    # Active workflows
    if workflow_status["active_workflows"]:
        table.add_row("Active Workflows", str(len(workflow_status["active_workflows"])))

    console.print(table)

    # Show active workflows detail
    if workflow_status["active_workflows"]:
        console.print("\n[bold]Active Workflows:[/bold]")
        for workflow in workflow_status["active_workflows"]:
            progress_bar = "█" * int(workflow["progress"] * 10) + "░" * (10 - int(workflow["progress"] * 10))
            console.print(
                f"  {workflow['name']}: [{progress_bar}] {workflow['completed_steps']}/{workflow['total_steps']} steps"
            )


@app.command()
def patterns(
    pattern_type: str = typer.Option(None, "--type", "-t", help="Filter by pattern type"),
    min_confidence: float = typer.Option(0.0, "--min-confidence", "-c", help="Minimum confidence"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of patterns to show"),
):
    """List discovered patterns."""
    engine = get_engine()

    # Get patterns
    if pattern_type:
        try:
            ptype = PatternType(pattern_type)
            patterns = engine.pattern_store.get_patterns_by_type(ptype)
        except ValueError:
            console.print(f"[red]Invalid pattern type: {pattern_type}[/red]")
            console.print(f"Valid types: {', '.join(p.value for p in PatternType)}")
            return
    else:
        patterns = list(engine.pattern_store.patterns.values())

    # Filter by confidence
    if min_confidence > 0:
        patterns = [p for p in patterns if p.confidence >= min_confidence]

    # Sort by confidence
    patterns.sort(key=lambda p: p.confidence * p.frequency, reverse=True)

    # Create patterns table
    table = Table(title=f"Discovered Patterns (showing {min(limit, len(patterns))} of {len(patterns)})")
    table.add_column("Type", style="cyan")
    table.add_column("Pattern", style="white")
    table.add_column("Confidence", style="green")
    table.add_column("Frequency", style="yellow")

    for pattern in patterns[:limit]:
        # Format pattern based on type
        if hasattr(pattern, "command_sequence"):
            pattern_str = " → ".join(pattern.command_sequence)
        elif hasattr(pattern, "workflow_name"):
            pattern_str = pattern.workflow_name
        elif hasattr(pattern, "file_sequence"):
            pattern_str = " → ".join(pattern.file_sequence[-3:])
        else:
            pattern_str = str(pattern.id)

        table.add_row(
            pattern.pattern_type.value,
            pattern_str,
            f"{pattern.confidence:.2f}",
            str(pattern.frequency),
        )

    console.print(table)


@app.command()
def suggest(
    context_file: Path = typer.Option(None, "--context", "-c", help="JSON file with context"),
):
    """Get suggestions based on current context."""
    engine = get_engine()

    # Load context if provided
    context = {}
    if context_file and context_file.exists():
        with open(context_file) as f:
            context = json.load(f)

    # Get suggestions
    suggestions = engine.get_suggestions(context)

    if not suggestions:
        console.print("[yellow]No suggestions available for current context[/yellow]")
        return

    # Display suggestions
    console.print("[bold]Suggested Next Actions:[/bold]\n")

    for i, suggestion in enumerate(suggestions, 1):
        confidence_color = "green" if suggestion["confidence"] > 0.7 else "yellow"
        console.print(
            f"{i}. [bold]{suggestion['type']}[/bold] "
            f"([{confidence_color}]{suggestion['confidence']:.2f}[/{confidence_color}] confidence)"
        )

        action = suggestion["action"]
        if action["type"] == "command":
            console.print(f"   Command: {action['command']}")
            if action.get("parameters"):
                console.print(f"   Parameters: {action['parameters']}")
        elif action["type"] == "file_access":
            console.print(f"   File: {action['file']}")
            console.print(f"   Operation: {action['operation']}")
        elif action["type"] == "workflow_step":
            console.print(f"   Step: {action['step']['description']}")
            console.print(f"   Workflow: {action['workflow']}")

        console.print(f"   Pattern: {suggestion['pattern_type']} ({suggestion['pattern_id']})\n")


@app.command()
def export(
    output_path: Path = typer.Argument(..., help="Path to export patterns"),
):
    """Export learned patterns to a file."""
    engine = get_engine()
    engine.export_patterns(output_path)
    console.print(f"[green]✓[/green] Exported patterns to {output_path}")


@app.command()
def analyze(
    event_log: Path = typer.Argument(..., help="Path to event log file"),
    mine_patterns: bool = typer.Option(True, "--mine/--no-mine", help="Mine patterns from log"),
):
    """Analyze an event log for patterns."""
    if not event_log.exists():
        console.print(f"[red]Event log not found: {event_log}[/red]")
        return

    engine = get_engine()

    # Load and process events
    with open(event_log) as f:
        events = json.load(f)

    console.print(f"[cyan]Processing {len(events)} events...[/cyan]")

    # Process events through engine
    for event_data in events:
        # Convert to event object (simplified)
        class MockEvent:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

        event = MockEvent(event_data)
        engine._handle_event(event)

    if mine_patterns:
        # Force pattern mining
        engine._mine_patterns()

    # Show results
    stats = engine.get_pattern_statistics()
    console.print("\n[green]✓[/green] Analysis complete!")
    console.print(f"  Discovered {stats['total_patterns']} patterns")
    console.print(f"  High confidence: {stats['high_confidence']}")

    # Show pattern breakdown
    for ptype, count in stats["by_type"].items():
        if count > 0:
            console.print(f"  {ptype}: {count}")


@app.command()
def prune(
    days: int = typer.Option(30, "--days", "-d", help="Prune patterns inactive for N days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pruned"),
):
    """Prune old/inactive patterns."""
    engine = get_engine()

    if dry_run:
        # Count patterns that would be pruned
        import time

        current_time = time.time()
        cutoff_time = current_time - (days * 86400)

        to_prune = [p for p in engine.pattern_store.patterns.values() if p.last_seen < cutoff_time and p.frequency < 5]

        console.print(f"[yellow]Would prune {len(to_prune)} patterns[/yellow]")
        for pattern in to_prune[:10]:  # Show first 10
            console.print(f"  - {pattern.pattern_type.value}: {pattern.id}")
        if len(to_prune) > 10:
            console.print(f"  ... and {len(to_prune) - 10} more")
    else:
        pruned = engine.pattern_store.prune_old_patterns(days_inactive=days)
        console.print(f"[green]✓[/green] Pruned {pruned} inactive patterns")


if __name__ == "__main__":
    app()
