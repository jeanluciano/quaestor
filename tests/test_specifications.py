"""Tests for the simplified specifications module."""

from datetime import datetime
from pathlib import Path

import pytest

from quaestor.core.specifications import (
    Contract,
    Specification,
    SpecPriority,
    SpecStatus,
    SpecTestScenario,
    SpecType,
    find_specs_in_folder,
    get_spec_progress,
    load_spec_from_file,
    move_spec_between_folders,
    save_spec_to_file,
)


class TestSpecificationDataStructures:
    """Test specification data structure validation."""

    def test_contract_creation(self):
        """Test Contract dataclass creation."""
        contract = Contract(
            inputs={"param1": "string"},
            outputs={"result": "dict"},
            behavior=["Must validate input", "Must return valid output"],
            constraints=["Response time < 100ms"],
            error_handling={"validation_error": "Return 400 status"},
        )

        assert contract.inputs == {"param1": "string"}
        assert contract.outputs == {"result": "dict"}
        assert len(contract.behavior) == 2
        assert len(contract.constraints) == 1
        assert "validation_error" in contract.error_handling

    def test_contract_defaults(self):
        """Test Contract with default values."""
        contract = Contract()

        assert contract.inputs == {}
        assert contract.outputs == {}
        assert contract.behavior == []
        assert contract.constraints == []
        assert contract.error_handling == {}

    def test_test_scenario_creation(self):
        """Test TestScenario dataclass creation."""
        scenario = SpecTestScenario(
            name="Happy path test",
            description="Test successful operation",
            given="Valid input data",
            when="Process is executed",
            then="Returns expected result",
            examples=[{"input": "test", "output": "processed"}],
        )

        assert scenario.name == "Happy path test"
        assert scenario.description == "Test successful operation"
        assert scenario.given == "Valid input data"
        assert scenario.when == "Process is executed"
        assert scenario.then == "Returns expected result"
        assert len(scenario.examples) == 1

    def test_specification_creation(self):
        """Test Specification dataclass creation."""
        spec = Specification(
            id="feat-001",
            title="Test Feature",
            type=SpecType.FEATURE,
            status=SpecStatus.DRAFT,
            priority=SpecPriority.HIGH,
            description="A test feature",
            rationale="Needed for testing",
        )

        assert spec.id == "feat-001"
        assert spec.title == "Test Feature"
        assert spec.type == SpecType.FEATURE
        assert spec.status == SpecStatus.DRAFT
        assert spec.priority == SpecPriority.HIGH
        assert spec.description == "A test feature"
        assert spec.rationale == "Needed for testing"
        assert isinstance(spec.created_at, datetime)
        assert isinstance(spec.updated_at, datetime)


class TestSpecificationUtilities:
    """Test specification utility functions."""

    def test_load_spec_from_file_success(self, tmp_path):
        """Test loading a specification from a Markdown file."""
        spec_content = """---
id: spec-test-001
type: feature
status: active
priority: high
---

# Test Specification

## Description
A test specification for loading.

## Acceptance Criteria
- [ ] Criterion 1
- [x] Criterion 2
- [ ] Criterion 3
"""
        spec_path = tmp_path / "spec-test-001.md"
        spec_path.write_text(spec_content)

        spec = load_spec_from_file(spec_path)

        assert spec is not None
        assert spec.id == "spec-test-001"
        assert spec.type == SpecType.FEATURE
        assert spec.status == SpecStatus.ACTIVE
        assert spec.priority == SpecPriority.HIGH
        assert spec.title == "Test Specification"

    def test_load_spec_from_file_not_found(self, tmp_path):
        """Test loading a non-existent specification."""
        spec_path = tmp_path / "nonexistent.md"

        spec = load_spec_from_file(spec_path)

        assert spec is None

    def test_load_spec_from_file_invalid_content(self, tmp_path):
        """Test loading an invalid specification file."""
        spec_path = tmp_path / "invalid.md"
        spec_path.write_text("This is not a valid spec")

        spec = load_spec_from_file(spec_path)

        assert spec is None  # Parser handles errors gracefully

    def test_save_spec_to_file(self, tmp_path):
        """Test saving a specification to a Markdown file."""
        spec = Specification(
            id="spec-save-001",
            title="Save Test",
            type=SpecType.FEATURE,
            status=SpecStatus.DRAFT,
            priority=SpecPriority.MEDIUM,
            description="Test saving specification",
            rationale="For testing save functionality",
        )

        spec_path = tmp_path / "spec-save-001.md"
        save_spec_to_file(spec, spec_path)

        assert spec_path.exists()
        content = spec_path.read_text()
        assert "id: spec-save-001" in content
        assert "type: feature" in content
        assert "# Save Test" in content

    def test_find_specs_in_folder(self, tmp_path):
        """Test finding all specifications in a folder."""
        # Create test specs
        for i in range(3):
            spec_content = f"""---
id: spec-test-{i:03d}
type: feature
status: active
priority: medium
---

# Test Spec {i}

## Description
Test specification {i}
"""
            (tmp_path / f"spec-test-{i:03d}.md").write_text(spec_content)

        # Also create a non-spec file
        (tmp_path / "README.md").write_text("# README")

        spec_paths = find_specs_in_folder(tmp_path)

        assert len(spec_paths) == 3
        # Returns list of Path objects
        assert all(isinstance(p, Path) for p in spec_paths)
        spec_names = {p.stem for p in spec_paths}
        assert spec_names == {"spec-test-000", "spec-test-001", "spec-test-002"}

    def test_find_specs_in_empty_folder(self, tmp_path):
        """Test finding specs in an empty folder."""
        specs = find_specs_in_folder(tmp_path)

        assert specs == []

    def test_move_spec_between_folders(self, tmp_path):
        """Test moving a specification between folders."""
        # Create source and destination folders
        draft_folder = tmp_path / "draft"
        active_folder = tmp_path / "active"
        draft_folder.mkdir()
        active_folder.mkdir()

        # Create a spec in draft
        spec_content = """---
id: spec-move-001
type: feature
status: draft
priority: high
---

# Move Test

## Description
Test moving specification
"""
        spec_path = draft_folder / "spec-move-001.md"
        spec_path.write_text(spec_content)

        # Move the spec (returns bool)
        success = move_spec_between_folders(spec_id="spec-move-001", from_folder=draft_folder, to_folder=active_folder)

        assert success is True
        assert (active_folder / "spec-move-001.md").exists()
        assert not spec_path.exists()

    def test_move_spec_nonexistent(self, tmp_path):
        """Test moving a non-existent specification."""
        draft_folder = tmp_path / "draft"
        active_folder = tmp_path / "active"
        draft_folder.mkdir()
        active_folder.mkdir()

        success = move_spec_between_folders(spec_id="nonexistent", from_folder=draft_folder, to_folder=active_folder)

        assert success is False

    def test_get_spec_progress(self, tmp_path):
        """Test getting specification progress from checkboxes."""
        spec_content = """---
id: spec-progress-001
type: feature
status: active
priority: high
---

# Progress Test

## Acceptance Criteria
- [x] Completed criterion 1
- [x] Completed criterion 2
- [ ] Incomplete criterion 3
- [ ] Incomplete criterion 4
- [x] Completed criterion 5

## Test Scenarios
- [x] Test 1 done
- [ ] Test 2 pending
"""
        spec_path = tmp_path / "spec-progress-001.md"
        spec_path.write_text(spec_content)

        progress = get_spec_progress(spec_path)

        assert progress is not None
        # 3 completed out of 5 in acceptance criteria + 1 completed out of 2 in test scenarios = 4/7 total
        assert progress.total == 7
        assert progress.completed == 4
        assert progress.completion_percentage == pytest.approx(57.14, abs=0.1)

    def test_get_spec_progress_nonexistent(self, tmp_path):
        """Test getting progress for non-existent spec."""
        progress = get_spec_progress(tmp_path / "nonexistent.md")

        assert progress is None

    def test_get_spec_progress_no_checkboxes(self, tmp_path):
        """Test getting progress with no checkboxes."""
        spec_content = """---
id: spec-no-progress-001
type: feature
status: active
priority: high
---

# No Progress Test

## Description
This spec has no checkboxes.
"""
        spec_path = tmp_path / "spec-no-progress-001.md"
        spec_path.write_text(spec_content)

        progress = get_spec_progress(spec_path)

        assert progress is not None
        assert progress.total == 0
        assert progress.completed == 0
        # No tasks means 100% complete (nothing to do)
        assert progress.completion_percentage == 100.0


class TestSpecificationEdgeCases:
    """Test edge cases in specification handling."""

    def test_spec_with_missing_optional_fields(self, tmp_path):
        """Test loading spec with only required fields."""
        spec_content = """---
id: spec-minimal-001
type: feature
---

# Minimal Spec
"""
        spec_path = tmp_path / "spec-minimal-001.md"
        spec_path.write_text(spec_content)

        spec = load_spec_from_file(spec_path)

        assert spec is not None
        assert spec.id == "spec-minimal-001"
        assert spec.status == SpecStatus.DRAFT  # default
        assert spec.priority == SpecPriority.MEDIUM  # default

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test that saving and loading a spec preserves data."""
        original_spec = Specification(
            id="spec-roundtrip-001",
            title="Roundtrip Test",
            type=SpecType.BUGFIX,
            status=SpecStatus.ACTIVE,
            priority=SpecPriority.CRITICAL,
            description="Test roundtrip preservation",
            rationale="Ensure no data loss",
        )

        spec_path = tmp_path / "spec-roundtrip-001.md"
        save_spec_to_file(original_spec, spec_path)
        loaded_spec = load_spec_from_file(spec_path)

        assert loaded_spec is not None
        assert loaded_spec.id == original_spec.id
        assert loaded_spec.title == original_spec.title
        assert loaded_spec.type == original_spec.type
        assert loaded_spec.status == original_spec.status
        assert loaded_spec.priority == original_spec.priority
        assert loaded_spec.description == original_spec.description
