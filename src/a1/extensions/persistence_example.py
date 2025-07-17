"""Basic Persistence Integration Example

Demonstrates how to use the simplified A1 persistence system
for storing and retrieving project data, patterns, and configurations.
"""

from pathlib import Path

from ..core.event_bus import EventBus
from .persistence import (
    AdaptationData,
    ConfigurationData,
    PatternData,
    ProjectManifest,
    SimplePersistenceManager,
    get_persistence_manager,
    initialize_persistence,
)


def main():
    """Example usage of simplified persistence system."""
    # Initialize persistence
    project_root = Path("/tmp/quaestor_example")
    project_root.mkdir(exist_ok=True)
    quaestor_dir = project_root / ".quaestor"

    # Initialize with event bus (optional)
    event_bus = EventBus()
    persistence = initialize_persistence(quaestor_dir, event_bus)

    print("🗄️  Persistence System Initialized")
    print("=" * 50)

    # Example 1: Project Manifest
    print("\\n📋 Working with Project Manifest...")

    # Create or load manifest
    manifest = persistence.load_manifest()
    if not manifest:
        print("Creating new project manifest...")
        manifest = ProjectManifest(
            project_path=str(project_root),
            metadata={
                "project_name": "Example Project",
                "version": "1.0.0",
                "description": "Demo of persistence system",
            },
        )

        # Add some file checksums
        manifest.file_checksums["src/main.py"] = "abc123def456"
        manifest.file_checksums["tests/test_main.py"] = "789xyz000"

        # Save manifest
        persistence.save_manifest(manifest)
        print("✅ Manifest saved")
    else:
        print(f"Loaded existing manifest for: {manifest.project_path}")
        print(f"Files tracked: {len(manifest.file_checksums)}")

    # Example 2: Pattern Storage
    print("\\n🔍 Working with Patterns...")

    # Create and save patterns
    pattern1 = PatternData(
        pattern_id="edit_then_test",
        pattern_type="workflow",
        confidence=0.85,
        context={"tools": ["Edit", "Bash"], "file_types": [".py"], "success_rate": 0.92},
    )
    persistence.save_pattern(pattern1)

    pattern2 = PatternData(
        pattern_id="search_before_edit",
        pattern_type="workflow",
        frequency=15,
        confidence=0.90,
        context={
            "tools": ["Grep", "Edit"],
            "common_search": "class.*:",
        },
    )
    persistence.save_pattern(pattern2)

    print("✅ Saved 2 patterns")

    # Load all patterns
    patterns = persistence.load_patterns()
    print(f"\\n📊 Loaded {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"  - {pattern.pattern_id}: freq={pattern.frequency}, conf={pattern.confidence:.2f}")

    # Example 3: Configuration
    print("\\n⚙️  Working with Configuration...")

    config = persistence.load_config()
    if not config:
        print("Creating new configuration...")
        config = ConfigurationData(
            settings={"max_context_size": 100000, "auto_save": True, "theme": "dark"},
            feature_flags={"experimental_search": False, "advanced_patterns": True, "auto_complete": True},
        )
        persistence.save_config(config)
        print("✅ Configuration saved")
    else:
        print("Loaded existing configuration")
        print(f"Settings: {list(config.settings.keys())}")
        print(f"Feature flags: {list(config.feature_flags.keys())}")

    # Example 4: AI Adaptations
    print("\\n🧠 Working with Adaptations...")

    # Create adaptation
    adaptation = AdaptationData(
        adaptation_id="prefer_ruff_over_black",
        adaptation_type="tool_preference",
        trigger="python formatting",
        response="use ruff format instead of black",
    )

    # Simulate usage
    adaptation.success_count = 8
    adaptation.failure_count = 2

    persistence.save_adaptation(adaptation)
    print(f"✅ Saved adaptation with {adaptation.success_rate:.0%} success rate")

    # Load all adaptations
    adaptations = persistence.load_adaptations()
    print(f"\\nLoaded {len(adaptations)} adaptations")

    # Example 5: Backup and Restore
    print("\\n💾 Testing Backup and Restore...")

    # Create a backup
    backup_name = "example_backup_v1"
    backup_path = persistence.create_backup(backup_name)
    print(f"✅ Created backup at: {backup_path}")

    # Modify some data
    manifest.metadata["modified"] = True
    persistence.save_manifest(manifest)

    # Restore from backup
    persistence.restore_backup(backup_name)
    print("✅ Restored from backup")

    # Verify restoration
    restored_manifest = persistence.load_manifest()
    if restored_manifest and "modified" not in restored_manifest.metadata:
        print("✅ Backup restore verified - modifications reverted")

    # Example 6: Using global instance
    print("\\n🌐 Using Global Instance...")

    # Access via global functions
    global_persistence = get_persistence_manager()
    if global_persistence:
        # Clear cache
        global_persistence.clear_cache()
        print("✅ Cache cleared")

        # List pattern files
        pattern_files = global_persistence.backend.list_files("patterns")
        print(f"Pattern files: {pattern_files}")

    # Example 7: Error Handling
    print("\\n⚠️  Testing Error Handling...")

    try:
        # Try to load non-existent file
        persistence.load("nonexistent.json", ProjectManifest)
    except FileNotFoundError as e:
        print(f"✅ Correctly caught: {e}")

    # Example 8: In-Memory Backend (for testing)
    print("\\n🧪 Testing In-Memory Backend...")

    from .persistence import MemoryStorageBackend

    # Create persistence with memory backend
    memory_persistence = SimplePersistenceManager(root_path=Path("/memory"), backend=MemoryStorageBackend())

    # Save and load data in memory
    test_manifest = ProjectManifest(project_path="/memory/test")
    memory_persistence.save_manifest(test_manifest)
    loaded = memory_persistence.load_manifest()

    if loaded and loaded.project_path == "/memory/test":
        print("✅ In-memory backend working correctly")

    print("\\n🎉 Persistence example completed!")
    print(f"\\nStorage location: {quaestor_dir}")
    print("Files created:")
    for item in quaestor_dir.rglob("*"):
        if item.is_file():
            print(f"  - {item.relative_to(quaestor_dir)}")


if __name__ == "__main__":
    main()
