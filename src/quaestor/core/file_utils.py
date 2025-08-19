"""Common file operation utilities."""

import shutil
from collections.abc import Callable
from pathlib import Path

from rich.console import Console

console = Console()


def create_directory(path: Path, exist_ok: bool = True) -> bool:
    """Create a directory safely with error handling.

    Args:
        path: Path to create
        exist_ok: Don't raise error if directory exists

    Returns:
        True if successful, False otherwise
    """
    try:
        path.mkdir(parents=True, exist_ok=exist_ok)
        return True
    except Exception as e:
        console.print(f"[red]Failed to create directory {path}: {e}[/red]")
        return False


def safe_write_text(file_path: Path, content: str, backup: bool = False) -> bool:
    """Write text to file safely with optional backup.

    Args:
        file_path: Path to write to
        content: Content to write
        backup: Create backup of existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if requested and file exists
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            shutil.copy2(file_path, backup_path)

        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        console.print(f"[red]Failed to write {file_path}: {e}[/red]")
        return False


def safe_read_text(file_path: Path, default: str = "") -> str:
    """Read text from file safely with default fallback.

    Args:
        file_path: Path to read from
        default: Default value if file cannot be read

    Returns:
        File content or default value
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        return default


def update_gitignore(target_dir: Path, entries: list[str], section_name: str | None = None) -> bool:
    """Update .gitignore with new entries, avoiding duplicates.

    Args:
        target_dir: Directory containing .gitignore
        entries: List of entries to add
        section_name: Optional section header

    Returns:
        True if successful, False otherwise
    """
    gitignore_path = target_dir / ".gitignore"

    try:
        # Read existing content
        existing_content = ""
        if gitignore_path.exists():
            existing_content = gitignore_path.read_text(encoding="utf-8")

        # Check if section already exists
        if section_name and f"# {section_name}" in existing_content:
            console.print(f"  [dim]○[/dim] .gitignore already has {section_name} entries")
            return True

        # Parse existing entries
        existing_lines = set(line.strip() for line in existing_content.splitlines() if line.strip())

        # Find new entries to add
        new_entries = [entry for entry in entries if entry not in existing_lines]

        if not new_entries:
            console.print("  [dim]○[/dim] .gitignore already up to date")
            return True

        # Build new content
        if existing_content and not existing_content.endswith("\n"):
            existing_content += "\n"

        new_content = existing_content + "\n"

        if section_name:
            new_content += f"# {section_name}\n"

        for entry in new_entries:
            new_content += f"{entry}\n"

        gitignore_path.write_text(new_content, encoding="utf-8")
        console.print(f"  [blue]✓[/blue] Updated .gitignore with {len(new_entries)} new entries")
        return True

    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not update .gitignore: {e}")
        return False


def copy_file_with_processing(
    source_path: Path, dest_path: Path, processor: Callable | None = None, create_dirs: bool = True
) -> bool:
    """Copy file with optional content processing.

    Args:
        source_path: Source file path
        dest_path: Destination file path
        processor: Optional function to process content (content -> processed_content)
        create_dirs: Create destination directories if needed

    Returns:
        True if successful, False otherwise
    """
    try:
        if create_dirs:
            dest_path.parent.mkdir(parents=True, exist_ok=True)

        content = source_path.read_text(encoding="utf-8")

        if processor:
            content = processor(content)

        dest_path.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        console.print(f"[red]Failed to copy {source_path} to {dest_path}: {e}[/red]")
        return False


def find_project_root(start_path: Path | None = None, markers: list[str] | None = None) -> Path:
    """Find project root by looking for marker files/directories.

    Args:
        start_path: Starting directory (defaults to current working directory)
        markers: List of marker files/directories to look for

    Returns:
        Path to project root or start_path if not found
    """
    if start_path is None:
        start_path = Path.cwd()

    if markers is None:
        markers = [".git", ".quaestor", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]

    current = start_path.resolve()

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    return start_path


def clean_empty_directories(base_path: Path, preserve_base: bool = True) -> int:
    """Remove empty directories recursively.

    Args:
        base_path: Base directory to clean
        preserve_base: Don't remove the base directory itself

    Returns:
        Number of directories removed
    """
    removed_count = 0

    try:
        # Walk bottom-up to handle nested empty directories
        for dirpath in reversed(list(base_path.rglob("*"))):
            if dirpath.is_dir() and dirpath != base_path:
                try:
                    # Only remove if empty (no files or subdirectories)
                    if not any(dirpath.iterdir()):
                        dirpath.rmdir()
                        removed_count += 1
                except OSError:
                    # Directory not empty or permission error
                    pass

        # Handle base directory
        if not preserve_base:
            try:
                if not any(base_path.iterdir()):
                    base_path.rmdir()
                    removed_count += 1
            except OSError:
                pass

    except Exception as e:
        console.print(f"[yellow]Warning: Error cleaning directories: {e}[/yellow]")

    return removed_count


def get_file_size_summary(base_path: Path, extensions: list[str] | None = None) -> dict:
    """Get summary of file sizes by extension.

    Args:
        base_path: Base directory to analyze
        extensions: Optional list of extensions to include (e.g., ['.py', '.js'])

    Returns:
        Dictionary with extension stats
    """
    stats = {}
    total_size = 0
    total_files = 0

    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()

            if extensions is None or ext in extensions:
                size = file_path.stat().st_size

                if ext not in stats:
                    stats[ext] = {"count": 0, "size": 0}

                stats[ext]["count"] += 1
                stats[ext]["size"] += size
                total_size += size
                total_files += 1

    return {
        "by_extension": stats,
        "total_size": total_size,
        "total_files": total_files,
    }
