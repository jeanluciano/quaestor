"""Basic State Management Integration Example

Demonstrates how to use the simplified A1 state management system
with event bus integration and common patterns.
"""

from pathlib import Path

from ..core.event_bus import EventBus
from .state import SimpleStateManager


def main():
    """Example usage of simplified state management."""
    project_root = Path("/path/to/project")

    # Initialize event bus and state manager
    event_bus = EventBus()
    state_manager = SimpleStateManager(project_root, event_bus)

    # Track important files
    state_manager.track_files(["src/**/*.py", "*.json", "*.yaml", "*.md"])

    # Create initial snapshot
    initial_snapshot = state_manager.create_snapshot(
        "Initial project state", metadata={"type": "initial", "user": "developer"}
    )
    print(f"Created initial snapshot: {initial_snapshot}")

    # Simulate some work...
    # (In real usage, files would be modified here)

    # Create checkpoint after major changes
    checkpoint_snapshot = state_manager.create_snapshot(
        "After implementing feature X", metadata={"type": "checkpoint", "feature": "feature_x"}
    )
    print(f"Created checkpoint: {checkpoint_snapshot}")

    # Show current status
    status = state_manager.get_status()
    print(f"State manager status: {status}")

    # Demonstrate undo functionality
    if status["undo_available"]:
        previous = state_manager.undo()
        print(f"Undid to snapshot: {previous}")

    # Demonstrate redo functionality
    if state_manager.get_status()["redo_available"]:
        next_snapshot = state_manager.redo()
        print(f"Redid to snapshot: {next_snapshot}")

    # List all snapshots
    snapshots = state_manager.list_snapshots()
    print(f"\\nAvailable snapshots ({len(snapshots)}):")
    for snapshot in snapshots:
        print(f"  {snapshot.id}: {snapshot.description}")
        print(f"    Files: {len(snapshot.file_states)}")
        print(f"    Time: {snapshot.timestamp}")

    # Compare snapshots
    if len(snapshots) >= 2:
        diff = state_manager.get_file_diff(snapshots[1].id, snapshots[0].id)
        print("\\nDifference between snapshots:")
        print(f"  Added files: {len(diff['added_files'])}")
        print(f"  Removed files: {len(diff['removed_files'])}")
        print(f"  Modified files: {len(diff['modified_files'])}")
        print(f"  Total changes: {diff['total_changes']}")

    # Clean up old snapshots
    deleted_count = state_manager.cleanup_old_snapshots(keep_count=10)
    print(f"\\nCleaned up {deleted_count} old snapshots")


if __name__ == "__main__":
    main()
