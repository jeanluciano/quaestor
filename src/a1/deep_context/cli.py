"""CLI interface for A1 Deep Context analysis.

This module provides a command-line interface to demonstrate
the deep context analysis capabilities.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from .code_index import CodeNavigationIndex
from .incremental_analyzer import IncrementalAnalyzer
from .symbol_table import SymbolType

app = typer.Typer()
console = Console()


@app.command()
def index(
    path: Path = typer.Argument(..., help="Path to directory to index"),
    output: Path | None = typer.Option(None, help="Output index to file"),
):
    """Index a Python project for deep context analysis."""
    console.print(f"[bold blue]Indexing {path}...[/bold blue]")

    index = CodeNavigationIndex()
    index.index_directory(path)

    stats = index.symbol_table.get_statistics()

    # Display statistics
    table = Table(title="Index Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")

    for metric, count in stats.items():
        table.add_row(metric.replace("_", " ").title(), str(count))

    console.print(table)

    if output:
        # Export to file
        data = index.symbol_table.export_to_dict()
        with open(output, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]Index exported to {output}[/green]")


@app.command()
def find(
    symbol: str = typer.Argument(..., help="Symbol name to find"),
    path: Path = typer.Argument(..., help="Project path"),
    type: str | None = typer.Option(None, help="Symbol type filter"),
):
    """Find symbol definitions in a project."""
    console.print(f"[bold blue]Searching for '{symbol}'...[/bold blue]")

    index = CodeNavigationIndex()
    index.index_directory(path)

    # Search for symbols
    symbol_type = SymbolType(type) if type else None
    results = index.search_symbols(symbol, symbol_type)

    if not results:
        console.print(f"[red]No symbols found matching '{symbol}'[/red]")
        return

    # Display results
    for sym in results:
        console.print(f"\n[bold cyan]{sym.qualified_name}[/bold cyan]")
        console.print(f"  Type: [yellow]{sym.symbol_type.value}[/yellow]")
        console.print(f"  File: [green]{sym.location.file_path}:{sym.location.line_start}[/green]")

        if sym.docstring:
            console.print(f"  Docs: {sym.docstring.split('\\n')[0]}...")

        if sym.signature:
            console.print(f"  Signature: [magenta]{sym.signature}[/magenta]")

        # Show code context
        context = index._get_code_context(sym.location, context_lines=1)
        if context:
            syntax = Syntax(context, "python", line_numbers=True, start_line=sym.location.line_start - 1)
            console.print(syntax)


@app.command()
def goto(
    symbol: str = typer.Argument(..., help="Symbol to find definition for"),
    file: Path = typer.Argument(..., help="Current file path"),
    line: int = typer.Argument(..., help="Current line number"),
    project: Path = typer.Option(Path.cwd(), help="Project root"),
):
    """Find definition of a symbol (go-to-definition)."""
    console.print(f"[bold blue]Finding definition of '{symbol}'...[/bold blue]")

    index = CodeNavigationIndex()
    index.index_directory(project)

    results = index.go_to_definition(symbol, file, line)

    if not results:
        console.print(f"[red]No definitions found for '{symbol}'[/red]")
        return

    # Display top results
    for i, result in enumerate(results[:3]):
        console.print(f"\n[bold]Result {i + 1}[/bold] (score: {result.score:.2f})")
        console.print(f"  [cyan]{result.symbol.qualified_name}[/cyan]")
        console.print(f"  [green]{result.location.file_path}:{result.location.line_start}[/green]")

        syntax = Syntax(result.context, "python", line_numbers=True, start_line=result.location.line_start - 2)
        console.print(syntax)


@app.command()
def refs(
    symbol: str = typer.Argument(..., help="Symbol to find references for"),
    path: Path = typer.Argument(..., help="Project path"),
):
    """Find all references to a symbol."""
    console.print(f"[bold blue]Finding references to '{symbol}'...[/bold blue]")

    index = CodeNavigationIndex()
    index.index_directory(path)

    # First find the symbol
    symbols = index.search_symbols(symbol)
    if not symbols:
        console.print(f"[red]Symbol '{symbol}' not found[/red]")
        return

    # Get references for first match
    sym = symbols[0]
    references = index.find_references(sym.qualified_name)

    console.print(f"\n[bold]References to {sym.qualified_name}:[/bold]")

    for ref in references:
        console.print(f"\n  [green]{ref.location.file_path}:{ref.location.line_start}[/green]")

        syntax = Syntax(ref.context, "python", line_numbers=True, start_line=ref.location.line_start - 1)
        console.print(syntax)


@app.command()
def deps(
    path: Path = typer.Argument(..., help="Project path"),
    check_circular: bool = typer.Option(False, "--circular", help="Check for circular dependencies"),
):
    """Analyze project dependencies."""
    console.print("[bold blue]Analyzing dependencies...[/bold blue]")

    index = CodeNavigationIndex()
    analyzer = index.analyzer

    # Build import graph
    import_graph = analyzer.build_import_graph(path)

    # Display as tree
    tree = Tree("[bold]Import Dependencies[/bold]")

    for module, edges in sorted(import_graph.items()):
        if edges:
            module_node = tree.add(f"[cyan]{module}[/cyan]")
            for edge in edges[:5]:  # Limit display
                module_node.add(f"[yellow]{edge.target}[/yellow]")

    console.print(tree)

    if check_circular:
        console.print("\n[bold]Checking for circular dependencies...[/bold]")
        cycles = analyzer.find_circular_dependencies(import_graph)

        if cycles:
            console.print(f"[red]Found {len(cycles)} circular dependencies:[/red]")
            for cycle in cycles:
                console.print(f"  {' -> '.join(cycle)}")
        else:
            console.print("[green]No circular dependencies found![/green]")


@app.command()
def watch(
    path: Path = typer.Argument(..., help="Project path to watch"),
    cache: Path | None = typer.Option(None, help="Cache file for incremental updates"),
):
    """Watch for changes and update analysis incrementally."""
    console.print(f"[bold blue]Setting up incremental analysis for {path}...[/bold blue]")

    index = CodeNavigationIndex()
    index.index_directory(path)

    analyzer = IncrementalAnalyzer(index)
    if cache:
        analyzer.set_cache_file(cache)

    console.print("[yellow]Initial indexing complete. Checking for changes...[/yellow]")

    # Simulate a check (in real implementation would use file watchers)
    update = analyzer.analyze_changes(path)

    table = Table(title="Change Detection Results")
    table.add_column("Change Type", style="cyan")
    table.add_column("Count", style="magenta")

    table.add_row("Modified Files", str(len(update.updated_files)))
    table.add_row("Deleted Files", str(len(update.removed_files)))
    table.add_row("Affected Files", str(len(update.affected_files)))
    table.add_row("Analysis Time", f"{update.duration_ms:.1f}ms")

    console.print(table)

    if update.updated_files or update.removed_files:
        console.print("\n[yellow]Updating index incrementally...[/yellow]")
        update = analyzer.update_incrementally(path)
        console.print(f"[green]Update completed in {update.duration_ms:.1f}ms[/green]")


if __name__ == "__main__":
    app()
