#!/usr/bin/env python3
"""CLI command for validating specifications."""

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from quaestor.core.spec_schema import SpecificationSchema
from quaestor.core.yaml_utils import load_yaml

app = typer.Typer(help="Validate Quaestor specification files")
console = Console()


@app.command()
def validate(
    spec_file: Path = typer.Argument(
        ...,
        help="Path to the specification YAML file to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation information",
    ),
) -> None:
    """Validate a Quaestor specification file.

    This command checks that a specification file:
    - Contains all required fields
    - Uses valid enum values (type, status, priority)
    - Has properly formatted timestamps
    - Follows the expected schema structure
    """
    try:
        # Load the specification
        console.print(f"\n[blue]Validating:[/blue] {spec_file}")

        spec_data = load_yaml(spec_file)

        if not spec_data:
            console.print("[red]✗[/red] File is empty or invalid YAML")
            raise typer.Exit(1)

        # Get spec ID for display
        spec_id = spec_data.get("id", "unknown")

        # Validate using the schema
        is_valid, errors = SpecificationSchema.validate(spec_data)

        if is_valid:
            console.print(
                Panel(
                    f"[green]✓[/green] Specification '{spec_id}' is valid!",
                    title="[green]Validation Successful[/green]",
                    border_style="green",
                )
            )

            if verbose:
                # Show spec summary
                console.print("\n[blue]Specification Summary:[/blue]")
                console.print(f"  • ID: {spec_id}")
                console.print(f"  • Title: {spec_data.get('title', 'N/A')}")
                console.print(f"  • Type: {spec_data.get('type', 'N/A')}")
                console.print(f"  • Status: {spec_data.get('status', 'N/A')}")
                console.print(f"  • Priority: {spec_data.get('priority', 'N/A')}")

                # Check optional fields
                if "acceptance_criteria" in spec_data:
                    criteria_count = len(spec_data["acceptance_criteria"])
                    console.print(f"  • Acceptance Criteria: {criteria_count} items")

                if "test_scenarios" in spec_data:
                    scenario_count = len(spec_data["test_scenarios"])
                    console.print(f"  • Test Scenarios: {scenario_count} scenarios")

                if "dependencies" in spec_data:
                    deps = spec_data["dependencies"]
                    requires = len(deps.get("requires", []))
                    blocks = len(deps.get("blocks", []))
                    if requires or blocks:
                        console.print(f"  • Dependencies: {requires} requires, {blocks} blocks")

        else:
            console.print(
                Panel(
                    f"[red]✗[/red] Specification '{spec_id}' validation failed",
                    title="[red]Validation Failed[/red]",
                    border_style="red",
                )
            )

            console.print("\n[red]Errors found:[/red]")
            for error in errors:
                console.print(f"  [red]•[/red] {error}")

            raise typer.Exit(1)

    except FileNotFoundError:
        console.print(f"[red]✗[/red] File not found: {spec_file}")
        raise typer.Exit(1) from None
    except yaml.YAMLError as e:
        console.print(f"[red]✗[/red] Invalid YAML format: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1) from None


@app.command()
def validate_all(
    spec_dir: Path = typer.Option(
        ".quaestor/specs",
        "--dir",
        "-d",
        help="Directory containing specifications",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation information",
    ),
) -> None:
    """Validate all specifications in a directory.

    Recursively validates all YAML files in the specs directory.
    """
    console.print(f"\n[blue]Validating all specs in:[/blue] {spec_dir}")

    # Find all YAML files
    yaml_files = list(spec_dir.glob("**/*.yaml")) + list(spec_dir.glob("**/*.yml"))

    if not yaml_files:
        console.print("[yellow]No specification files found[/yellow]")
        return

    valid_count = 0
    invalid_count = 0

    for spec_file in yaml_files:
        try:
            spec_data = load_yaml(spec_file)
            if not spec_data:
                continue

            spec_id = spec_data.get("id", spec_file.stem)
            is_valid, errors = SpecificationSchema.validate(spec_data)

            if is_valid:
                console.print(f"  [green]✓[/green] {spec_id}")
                valid_count += 1
            else:
                console.print(f"  [red]✗[/red] {spec_id}")
                if verbose:
                    for error in errors[:3]:  # Show first 3 errors
                        console.print(f"      {error}")
                invalid_count += 1

        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] {spec_file.name}: {e}")
            invalid_count += 1

    # Summary
    console.print("\n[blue]Summary:[/blue]")
    console.print(f"  • Valid: {valid_count}")
    console.print(f"  • Invalid: {invalid_count}")
    console.print(f"  • Total: {valid_count + invalid_count}")

    if invalid_count > 0:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
