"""Test folder management integration with SpecificationManager."""

import tempfile
from pathlib import Path

import pytest

from quaestor.core.specifications import SpecificationManager, SpecPriority, SpecStatus, SpecType


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_folder_structure_creation(temp_project):
    """Test that folder structure is created on initialization."""
    SpecificationManager(temp_project)

    # Check folders exist
    assert (temp_project / ".quaestor" / "specifications" / "draft").exists()
    assert (temp_project / ".quaestor" / "specifications" / "active").exists()
    assert (temp_project / ".quaestor" / "specifications" / "completed").exists()


def test_spec_lifecycle_with_folders(temp_project):
    """Test specification lifecycle through folder transitions."""
    manager = SpecificationManager(temp_project)

    # Create a draft specification
    spec = manager.create_specification(
        title="Test Feature",
        spec_type=SpecType.FEATURE,
        description="Test description",
        rationale="Test rationale",
        priority=SpecPriority.HIGH,
    )

    # Check it's in draft folder
    draft_file = temp_project / ".quaestor" / "specifications" / "draft" / f"{spec.id}.yaml"
    assert draft_file.exists()

    # Activate the specification
    success = manager.activate_specification(spec.id)
    assert success

    # Check it moved to active folder
    active_file = temp_project / ".quaestor" / "specifications" / "active" / f"{spec.id}.yaml"
    assert active_file.exists()
    assert not draft_file.exists()

    # Complete the specification
    success = manager.complete_specification(spec.id)
    assert success

    # Check it moved to completed folder
    completed_file = temp_project / ".quaestor" / "specifications" / "completed" / f"{spec.id}.yaml"
    assert completed_file.exists()
    assert not active_file.exists()


def test_active_limit_enforcement(temp_project):
    """Test that active specification limit is enforced."""
    manager = SpecificationManager(temp_project)

    # Create and activate 3 specifications (the limit)
    for i in range(3):
        spec = manager.create_specification(
            title=f"Feature {i}", spec_type=SpecType.FEATURE, description=f"Description {i}", rationale=f"Rationale {i}"
        )
        success = manager.activate_specification(spec.id)
        assert success

    # Try to activate a 4th specification
    spec4 = manager.create_specification(
        title="Feature 4", spec_type=SpecType.FEATURE, description="Description 4", rationale="Rationale 4"
    )

    # Should fail due to active limit
    success = manager.activate_specification(spec4.id)
    assert not success

    # Complete one specification
    active_specs = manager.list_specifications(status=SpecStatus.ACTIVE)
    success = manager.complete_specification(active_specs[0].id)
    assert success

    # Now we should be able to activate the 4th
    success = manager.activate_specification(spec4.id)
    assert success


def test_migrate_flat_specifications(temp_project):
    """Test migration of flat specifications to folder structure."""
    # Create some specs in flat structure first
    specs_dir = temp_project / ".quaestor" / "specifications"
    specs_dir.mkdir(parents=True, exist_ok=True)

    # Create a flat spec file
    flat_spec_file = specs_dir / "test-spec.yaml"
    flat_spec_file.write_text("""
id: test-spec
title: Test Specification
type: feature
status: active
priority: high
description: Test description
rationale: Test rationale
created_at: "2024-01-01T00:00:00"
updated_at: "2024-01-01T00:00:00"
""")

    # Create manager and migrate
    manager = SpecificationManager(temp_project)
    success = manager.migrate_to_folder_structure()
    assert success

    # Check spec moved to correct folder
    active_file = specs_dir / "active" / "test-spec.yaml"
    assert active_file.exists()
    assert not flat_spec_file.exists()

    # Verify spec is loaded correctly
    spec = manager.get_specification("test-spec")
    assert spec is not None
    assert spec.status == SpecStatus.ACTIVE
