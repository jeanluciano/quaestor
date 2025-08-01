"""Smart update logic for Quaestor files.

This module provides intelligent update capabilities that preserve user
customizations while ensuring critical updates are applied.
"""

import importlib.resources as pkg_resources
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from quaestor import __version__
from quaestor.constants import COMMAND_FILES, QUAESTOR_CONFIG_END, QUAESTOR_CONFIG_START
from quaestor.core.project_metadata import FileManifest, FileType, categorize_file, extract_version_from_content

console = Console()


class UpdateResult:
    """Result of an update operation."""

    def __init__(self):
        self.updated: list[str] = []
        self.skipped: list[str] = []
        self.added: list[str] = []
        self.failed: list[tuple[str, str]] = []  # (file, error)
        self.backed_up: list[str] = []

    def summary(self) -> str:
        """Get a summary of the update."""
        parts = []
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        if self.failed:
            parts.append(f"{len(self.failed)} failed")
        return ", ".join(parts) if parts else "No changes"


class QuaestorUpdater:
    """Handles smart updates for Quaestor installations."""

    def __init__(self, target_dir: Path, manifest: FileManifest):
        """Initialize updater.

        Args:
            target_dir: Project root directory
            manifest: FileManifest instance
        """
        self.target_dir = target_dir
        self.quaestor_dir = target_dir / ".quaestor"
        self.manifest = manifest
        self.claude_commands_dir = Path.home() / ".claude" / "commands"

        # Define files to manage in one place to ensure consistency
        self.QUAESTOR_FILES = [
            ("templates/quaestor_claude.md", self.quaestor_dir / "QUAESTOR_CLAUDE.md"),
            ("templates/critical_rules.md", self.quaestor_dir / "CRITICAL_RULES.md"),
            ("templates/architecture.md", self.quaestor_dir / "ARCHITECTURE.md"),
            ("templates/memory.md", self.quaestor_dir / "MEMORY.md"),
        ]

    def check_for_updates(self, show_diff: bool = True) -> dict[str, Any]:
        """Check what would be updated without making changes.

        Args:
            show_diff: Whether to show detailed differences

        Returns:
            Dict with update information
        """
        # Get current version - use manifest version if available and valid,
        # otherwise try to detect from installed files
        current_version = self.manifest.get_quaestor_version()
        if not current_version:
            # Try to detect from existing files
            current_version = self._detect_installed_version()

        updates = {
            "needs_update": False,
            "current_version": current_version,
            "new_version": __version__,
            "files": {"update": [], "add": [], "skip": []},
        }

        # Check version
        if updates["current_version"] != updates["new_version"]:
            updates["needs_update"] = True

        # Check each file type
        self._check_quaestor_files(updates)
        self._check_command_files(updates)

        if show_diff:
            self._display_update_preview(updates)

        return updates

    def _check_quaestor_files(self, updates: dict[str, Any]):
        """Check .quaestor directory files."""
        for resource_path, target_path in self.QUAESTOR_FILES:
            relative_path = str(target_path.relative_to(self.target_dir))
            file_type = categorize_file(target_path, relative_path)

            # Check if file exists
            if not target_path.exists():
                updates["files"]["add"].append((relative_path, file_type.value))
                continue

            # Get manifest info
            manifest_info = self.manifest.get_file_info(relative_path)

            # Determine update strategy based on file type
            if file_type == FileType.SYSTEM:
                # Always update system files if version changed
                if self._has_new_version(resource_path):
                    updates["files"]["update"].append((relative_path, file_type.value, "version changed"))
            elif file_type == FileType.USER_EDITABLE:
                # Skip if file exists and is user-editable
                if manifest_info and manifest_info.get("user_modified"):
                    updates["files"]["skip"].append((relative_path, file_type.value, "user modified"))
                elif not manifest_info:
                    # File exists but not tracked - assume user created it
                    updates["files"]["skip"].append((relative_path, file_type.value, "existing file"))

    def _check_command_files(self, updates: dict[str, Any]):
        """Check command files in ~/.claude/commands."""
        command_files = COMMAND_FILES

        for cmd_file in command_files:
            target_path = self.claude_commands_dir / cmd_file
            if not target_path.exists():
                updates["files"]["add"].append((f"commands/{cmd_file}", FileType.COMMAND.value))

    def _detect_installed_version(self) -> str | None:
        """Try to detect the installed version from existing files.

        Returns:
            Version string or None if not detectable
        """
        # Try to read version from QUAESTOR_CLAUDE.md which should have version info
        version_file = self.quaestor_dir / "QUAESTOR_CLAUDE.md"
        if version_file.exists():
            try:
                content = version_file.read_text()
                version = extract_version_from_content(content)
                if version:
                    return version
            except Exception:
                pass

        # Try CRITICAL_RULES.md as fallback
        critical_rules = self.quaestor_dir / "CRITICAL_RULES.md"
        if critical_rules.exists():
            try:
                content = critical_rules.read_text()
                version = extract_version_from_content(content)
                if version:
                    return version
            except Exception:
                pass

        # If we can't detect, return None
        return None

    def _has_new_version(self, resource_path: str) -> bool:
        """Check if a resource has a newer version than installed.

        Args:
            resource_path: Path to resource in package

        Returns:
            True if newer version available
        """
        try:
            # Read from package location
            content = pkg_resources.read_text("quaestor", resource_path)

            new_version = extract_version_from_content(content)
            if not new_version:
                return True  # Assume update needed if no version found

            # Get current version from manifest or file
            # This is simplified - you might want to read actual file version
            return True  # For now, assume update available

        except Exception:
            return False

    def _display_update_preview(self, updates: dict[str, Any]):
        """Display a preview of what would be updated."""
        console.print("\n[bold]Update Preview[/bold]")
        console.print(f"Current version: {updates['current_version'] or 'unknown'}")
        console.print(f"New version: {updates['new_version']}\n")

        if not updates["needs_update"] and not any(updates["files"].values()):
            console.print("[green]✓ Everything is up to date![/green]")
            return

        # Create table
        table = Table(title="Files to Update")
        table.add_column("Action", style="cyan")
        table.add_column("File", style="white")
        table.add_column("Type", style="dim")
        table.add_column("Reason", style="yellow")

        # Add files to table
        for file_path, file_type in updates["files"]["add"]:
            table.add_row("ADD", file_path, file_type, "new file")

        for file_path, file_type, reason in updates["files"]["update"]:
            table.add_row("UPDATE", file_path, file_type, reason)

        for file_path, file_type, reason in updates["files"]["skip"]:
            table.add_row("SKIP", file_path, file_type, reason)

        console.print(table)

    def update(
        self,
        backup: bool = False,
        force: bool = False,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Perform the update.

        Args:
            backup: Whether to backup files before updating
            force: Force update all files (ignore user modifications)
            dry_run: Show what would be done without doing it

        Returns:
            UpdateResult with details of what was done
        """
        result = UpdateResult()

        # Create backup if requested
        if backup and not dry_run:
            backup_dir = self._create_backup()
            if backup_dir:
                result.backed_up.append(str(backup_dir))
                console.print(f"[green]✓ Created backup in {backup_dir}[/green]")

        # Update quaestor version in manifest
        if not dry_run:
            self.manifest.set_quaestor_version(__version__)

        # Update files
        self._update_quaestor_files(result, force, dry_run)
        self._update_command_files(result, dry_run)
        self._update_claude_md_include(result, dry_run)

        # Save manifest
        if not dry_run:
            self.manifest.save()

        # Validate update completeness
        self._validate_update_result(result)

        return result

    def _create_backup(self) -> Path | None:
        """Create a backup of current installation.

        Returns:
            Path to backup directory or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.quaestor_dir / ".backup" / timestamp

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Backup .quaestor directory
            if self.quaestor_dir.exists():
                for item in self.quaestor_dir.iterdir():
                    if item.name != ".backup":
                        if item.is_dir():
                            shutil.copytree(item, backup_dir / item.name)
                        else:
                            shutil.copy2(item, backup_dir / item.name)

            # Backup CLAUDE.md
            claude_md = self.target_dir / "CLAUDE.md"
            if claude_md.exists():
                shutil.copy2(claude_md, backup_dir / "CLAUDE.md")

            return backup_dir

        except Exception as e:
            console.print(f"[red]Failed to create backup: {e}[/red]")
            return None

    def _update_quaestor_files(self, result: UpdateResult, force: bool, dry_run: bool):
        """Update files in .quaestor directory."""
        for resource_name, target_path in self.QUAESTOR_FILES:
            relative_path = str(target_path.relative_to(self.target_dir))
            file_type = categorize_file(target_path, relative_path)

            try:
                # Read new content
                if resource_name.startswith("templates/"):
                    new_content = pkg_resources.read_text(
                        "quaestor.claude.quaestor.templates", resource_name.replace("templates/", "")
                    )
                else:
                    new_content = pkg_resources.read_text("quaestor", resource_name)

                # Determine if we should update
                # Check if file exists before we potentially create it
                file_existed = target_path.exists()
                should_update = self._should_update_file(target_path, file_type, force)

                if should_update:
                    if not dry_run:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        target_path.write_text(new_content)

                        # Update manifest
                        version = extract_version_from_content(new_content) or "1.0"
                        self.manifest.track_file(target_path, file_type, version, self.target_dir)

                    # Track whether we added or updated
                    if file_existed:
                        result.updated.append(relative_path)
                    else:
                        result.added.append(relative_path)
                else:
                    result.skipped.append(relative_path)

            except Exception as e:
                result.failed.append((relative_path, str(e)))

    def _update_command_files(self, result: UpdateResult, dry_run: bool):
        """Update command files in ~/.claude/commands."""
        command_files = COMMAND_FILES

        for cmd_file in command_files:
            target_path = self.claude_commands_dir / cmd_file

            try:
                # Commands are always safe to update/add
                if not target_path.exists():
                    if not dry_run:
                        content = pkg_resources.read_text("quaestor.claude.commands", cmd_file)
                        self.claude_commands_dir.mkdir(parents=True, exist_ok=True)
                        target_path.write_text(content)
                    result.added.append(f"commands/{cmd_file}")

            except Exception as e:
                result.failed.append((f"commands/{cmd_file}", str(e)))

    def _update_claude_md_include(self, result: UpdateResult, dry_run: bool):
        """Update CLAUDE.md include section if needed."""
        claude_path = self.target_dir / "CLAUDE.md"

        if not claude_path.exists():
            return

        try:
            # Read current content
            current_content = claude_path.read_text()

            # Check if has Quaestor config
            if QUAESTOR_CONFIG_START not in current_content:
                # No config section, skip (user may have removed it intentionally)
                return

            # Get latest include template
            import importlib.resources as pkg_resources

            include_content = pkg_resources.read_text("quaestor.claude.quaestor.templates", "claude_include.md")

            # Extract config section from template
            config_start_idx = include_content.find(QUAESTOR_CONFIG_START)
            config_end_idx = include_content.find(QUAESTOR_CONFIG_END) + len(QUAESTOR_CONFIG_END)
            new_config = include_content[config_start_idx:config_end_idx]

            # Extract current config section
            current_start = current_content.find(QUAESTOR_CONFIG_START)
            current_end = current_content.find(QUAESTOR_CONFIG_END) + len(QUAESTOR_CONFIG_END)
            current_config = current_content[current_start:current_end]

            # Check if update needed
            if new_config != current_config:
                if not dry_run:
                    # Replace config section
                    new_content = current_content[:current_start] + new_config + current_content[current_end:]
                    claude_path.write_text(new_content)

                result.updated.append("CLAUDE.md (config section)")

        except Exception as e:
            result.failed.append(("CLAUDE.md", str(e)))

    def _should_update_file(self, target_path: Path, file_type: FileType, force: bool) -> bool:
        """Determine if a file should be updated.

        Args:
            target_path: Path to target file
            file_type: Type of file
            force: Whether to force update

        Returns:
            True if file should be updated
        """
        if force:
            return True

        if not target_path.exists():
            return True

        if file_type == FileType.SYSTEM:
            # Always update system files
            return True

        if file_type == FileType.USER_EDITABLE:
            # Never auto-update user-editable files if they exist
            return False

        # For other types, check if modified
        relative_path = str(target_path.relative_to(self.target_dir))
        return not self.manifest.is_file_modified(relative_path)

    def _validate_update_result(self, result: UpdateResult):
        """Validate that all expected files were processed.

        Args:
            result: UpdateResult to validate
        """
        # Get all file paths that should have been processed
        expected_files = set()
        for _, target_path in self.QUAESTOR_FILES:
            relative_path = str(target_path.relative_to(self.target_dir))
            expected_files.add(relative_path)

        # Get all files that were actually processed
        processed_files = set()
        processed_files.update(result.added)
        processed_files.update(result.updated)
        processed_files.update(result.skipped)
        processed_files.update([f for f, _ in result.failed])

        # Filter to only quaestor files
        processed_quaestor_files = {f for f in processed_files if f.startswith(".quaestor/")}

        # Check for missing files
        missing_files = expected_files - processed_quaestor_files
        if missing_files:
            console.print("\n[yellow]Warning: The following files were not processed:[/yellow]")
            for file in missing_files:
                console.print(f"  - {file}")

        # Log summary for debugging
        if result.failed:
            console.print("\n[red]Some updates failed. Please check the errors above.[/red]")


def print_update_result(result: UpdateResult):
    """Print a formatted update result.

    Args:
        result: UpdateResult to display
    """
    console.print("\n[bold]Update Summary:[/bold]")

    # Group files by type for clearer output
    quaestor_files = []
    command_files = []
    other_files = []

    def categorize_files(files):
        for file in files:
            if file.startswith(".quaestor/"):
                quaestor_files.append(file)
            elif file.startswith("commands/"):
                command_files.append(file)
            else:
                other_files.append(file)

    if result.updated:
        console.print(f"\n[blue]Updated {len(result.updated)} files:[/blue]")
        categorize_files(result.updated)
        if quaestor_files:
            for file in quaestor_files:
                console.print(f"  - {file}")
        if other_files:
            for file in other_files:
                console.print(f"  - {file}")

    if result.added:
        console.print(f"\n[green]Created {len(result.added)} new files:[/green]")
        added_quaestor = []
        added_commands = []
        for file in result.added:
            if file.startswith(".quaestor/"):
                added_quaestor.append(file)
            elif file.startswith("commands/"):
                added_commands.append(file)

        if added_quaestor:
            for file in added_quaestor:
                console.print(f"  - {file}")
        if added_commands:
            for file in added_commands:
                console.print(f"  - {file}")

    if result.skipped:
        console.print(f"\n[yellow]Skipped {len(result.skipped)} files (preserved your customizations):[/yellow]")
        for file in result.skipped:
            console.print(f"  - {file}")

    if result.failed:
        console.print(f"\n[red]Failed ({len(result.failed)}):[/red]")
        for file, error in result.failed:
            console.print(f"  ✗ {file}: {error}")

    # Show backup location if applicable
    if result.backed_up:
        console.print(f"\n[dim]Backup created at: {result.backed_up[0]}[/dim]")
