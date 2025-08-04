"""Comprehensive tests for the specifications module."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from quaestor.core.specifications import (
    Contract,
    Specification,
    SpecificationManager,
    SpecManifest,
    SpecPriority,
    SpecStatus,
    SpecType,
    TestScenario,
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
        scenario = TestScenario(
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

    def test_spec_manifest_creation(self):
        """Test SpecManifest dataclass creation."""
        manifest = SpecManifest()

        assert manifest.version == "1.0"
        assert manifest.specifications == {}
        assert manifest.branch_mapping == {}
        assert isinstance(manifest.created_at, datetime)
        assert isinstance(manifest.updated_at, datetime)


class TestSpecificationManager:
    """Test SpecificationManager functionality."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)
            yield project_dir

    @pytest.fixture
    def spec_manager(self, temp_project):
        """Create SpecificationManager instance."""
        return SpecificationManager(temp_project)

    def test_init_creates_directories(self, temp_project):
        """Test that initialization creates necessary directories."""
        manager = SpecificationManager(temp_project)

        assert manager.project_dir == temp_project
        assert manager.specs_dir.exists()
        assert manager.specs_dir == temp_project / ".quaestor" / "specs"
        assert manager.manifest_path == manager.specs_dir / "manifest.yaml"

    def test_load_manifest_empty_project(self, spec_manager):
        """Test loading manifest from empty project."""
        manifest = spec_manager.load_manifest()

        assert isinstance(manifest, SpecManifest)
        assert manifest.version == "1.0"
        assert manifest.specifications == {}
        assert manifest.branch_mapping == {}

    def test_create_specification(self, spec_manager):
        """Test creating a new specification."""
        spec = spec_manager.create_specification(
            title="Test Feature",
            spec_type=SpecType.FEATURE,
            description="A test feature implementation",
            rationale="Needed to validate specification system",
            priority=SpecPriority.HIGH,
        )

        assert spec.id.startswith("feat-")
        assert spec.title == "Test Feature"
        assert spec.type == SpecType.FEATURE
        assert spec.status == SpecStatus.DRAFT
        assert spec.priority == SpecPriority.HIGH
        assert spec.description == "A test feature implementation"
        assert spec.rationale == "Needed to validate specification system"

        # Verify it's in the manifest
        manifest = spec_manager.load_manifest()
        assert spec.id in manifest.specifications

    def test_get_specification(self, spec_manager):
        """Test retrieving a specification by ID."""
        # Create a specification
        spec = spec_manager.create_specification(
            title="Get Test",
            spec_type=SpecType.BUGFIX,
            description="Test retrieval",
            rationale="Testing get functionality",
        )

        # Retrieve it
        retrieved = spec_manager.get_specification(spec.id)

        assert retrieved is not None
        assert retrieved.id == spec.id
        assert retrieved.title == "Get Test"
        assert retrieved.type == SpecType.BUGFIX

    def test_get_nonexistent_specification(self, spec_manager):
        """Test retrieving non-existent specification."""
        result = spec_manager.get_specification("nonexistent-id")
        assert result is None

    def test_update_specification(self, spec_manager):
        """Test updating a specification."""
        # Create initial spec
        spec = spec_manager.create_specification(
            title="Original Title",
            spec_type=SpecType.FEATURE,
            description="Original description",
            rationale="Original rationale",
        )
        original_updated_at = spec.updated_at

        # Update it
        updates = {
            "title": "Updated Title",
            "description": "Updated description",
            "status": SpecStatus.STAGED,
        }
        updated_spec = spec_manager.update_specification(spec.id, updates)

        assert updated_spec is not None
        assert updated_spec.title == "Updated Title"
        assert updated_spec.description == "Updated description"
        assert updated_spec.status == SpecStatus.STAGED
        assert updated_spec.updated_at > original_updated_at

    def test_update_nonexistent_specification(self, spec_manager):
        """Test updating non-existent specification."""
        result = spec_manager.update_specification("nonexistent-id", {"title": "New"})
        assert result is None

    def test_link_spec_to_branch(self, spec_manager):
        """Test linking specification to git branch."""
        spec = spec_manager.create_specification(
            title="Branch Test",
            spec_type=SpecType.FEATURE,
            description="Test branch linking",
            rationale="Testing branch functionality",
        )

        # Link to branch
        success = spec_manager.link_spec_to_branch(spec.id, "feature/branch-test")

        assert success is True

        # Verify updates
        updated_spec = spec_manager.get_specification(spec.id)
        assert updated_spec.branch == "feature/branch-test"
        assert updated_spec.status == SpecStatus.ACTIVE

        # Verify branch mapping
        manifest = spec_manager.load_manifest()
        assert manifest.branch_mapping["feature/branch-test"] == spec.id

    def test_link_nonexistent_spec_to_branch(self, spec_manager):
        """Test linking non-existent spec to branch."""
        success = spec_manager.link_spec_to_branch("nonexistent-id", "test-branch")
        assert success is False

    def test_get_spec_by_branch(self, spec_manager):
        """Test retrieving specification by branch."""
        spec = spec_manager.create_specification(
            title="Branch Retrieval Test",
            spec_type=SpecType.REFACTOR,
            description="Test branch retrieval",
            rationale="Testing branch-based lookup",
        )

        # Link to branch
        spec_manager.link_spec_to_branch(spec.id, "refactor/test-branch")

        # Retrieve by branch
        retrieved = spec_manager.get_spec_by_branch("refactor/test-branch")

        assert retrieved is not None
        assert retrieved.id == spec.id
        assert retrieved.title == "Branch Retrieval Test"

    def test_get_spec_by_nonexistent_branch(self, spec_manager):
        """Test retrieving spec by non-existent branch."""
        result = spec_manager.get_spec_by_branch("nonexistent-branch")
        assert result is None

    def test_list_specifications(self, spec_manager):
        """Test listing specifications with filters."""
        # Create multiple specifications
        spec1 = spec_manager.create_specification(
            title="Critical Feature",
            spec_type=SpecType.FEATURE,
            description="Critical feature",
            rationale="High priority",
            priority=SpecPriority.CRITICAL,
        )

        spec2 = spec_manager.create_specification(
            title="Bug Fix",
            spec_type=SpecType.BUGFIX,
            description="Fix a bug",
            rationale="Bug needs fixing",
            priority=SpecPriority.HIGH,
        )

        _spec3 = spec_manager.create_specification(
            title="Documentation",
            spec_type=SpecType.DOCUMENTATION,
            description="Update docs",
            rationale="Docs outdated",
            priority=SpecPriority.LOW,
        )

        # Update one to staged status
        spec_manager.update_specification(spec2.id, {"status": SpecStatus.STAGED})

        # Test all specifications
        all_specs = spec_manager.list_specifications()
        assert len(all_specs) == 3

        # Test filter by status
        draft_specs = spec_manager.list_specifications(status=SpecStatus.DRAFT)
        assert len(draft_specs) == 2

        staged_specs = spec_manager.list_specifications(status=SpecStatus.STAGED)
        assert len(staged_specs) == 1
        assert staged_specs[0].id == spec2.id

        # Test filter by type
        feature_specs = spec_manager.list_specifications(spec_type=SpecType.FEATURE)
        assert len(feature_specs) == 1
        assert feature_specs[0].id == spec1.id

        # Test filter by priority
        critical_specs = spec_manager.list_specifications(priority=SpecPriority.CRITICAL)
        assert len(critical_specs) == 1
        assert critical_specs[0].id == spec1.id

        # Test sorting (critical should come first)
        assert all_specs[0].priority == SpecPriority.CRITICAL

    def test_generate_spec_id_uniqueness(self, spec_manager):
        """Test that spec ID generation ensures uniqueness."""
        # Create two specs with same title
        spec1 = spec_manager.create_specification(
            title="Duplicate Title",
            spec_type=SpecType.FEATURE,
            description="First spec",
            rationale="First rationale",
        )

        spec2 = spec_manager.create_specification(
            title="Duplicate Title",
            spec_type=SpecType.FEATURE,
            description="Second spec",
            rationale="Second rationale",
        )

        assert spec1.id != spec2.id
        assert spec1.id.startswith("feat-duplicate-title")
        assert spec2.id.startswith("feat-duplicate-title")
        assert spec2.id.endswith("-1")  # Should have counter suffix

    def test_spec_id_prefixes(self, spec_manager):
        """Test that different spec types get correct ID prefixes."""
        test_cases = [
            (SpecType.FEATURE, "feat-"),
            (SpecType.BUGFIX, "fix-"),
            (SpecType.REFACTOR, "refactor-"),
            (SpecType.DOCUMENTATION, "docs-"),
            (SpecType.PERFORMANCE, "perf-"),
            (SpecType.SECURITY, "sec-"),
            (SpecType.TESTING, "test-"),
        ]

        for spec_type, expected_prefix in test_cases:
            spec = spec_manager.create_specification(
                title="Test Spec",
                spec_type=spec_type,
                description="Test description",
                rationale="Test rationale",
            )
            assert spec.id.startswith(expected_prefix)


class TestSpecificationSerialization:
    """Test specification serialization and deserialization."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)
            yield project_dir

    @pytest.fixture
    def spec_manager(self, temp_project):
        """Create SpecificationManager instance."""
        return SpecificationManager(temp_project)

    @pytest.fixture
    def sample_spec(self):
        """Create a sample specification with all fields."""
        contract = Contract(
            inputs={"param1": "string", "param2": "int"},
            outputs={"result": "dict"},
            behavior=["Validate inputs", "Process data"],
            constraints=["Performance < 100ms"],
            error_handling={"validation": "Return 400"},
        )

        test_scenario = TestScenario(
            name="Happy path",
            description="Test successful execution",
            given="Valid input",
            when="Function called",
            then="Returns result",
            examples=[{"input": "test", "output": "success"}],
        )

        return Specification(
            id="feat-test-001",
            title="Test Specification",
            type=SpecType.FEATURE,
            status=SpecStatus.STAGED,
            priority=SpecPriority.HIGH,
            description="A comprehensive test specification",
            rationale="Testing serialization functionality",
            use_cases=["Use case 1", "Use case 2"],
            contract=contract,
            acceptance_criteria=["Criterion 1", "Criterion 2"],
            test_scenarios=[test_scenario],
            dependencies=["dep-001", "dep-002"],
            branch="feature/test-branch",
            metadata={"author": "test", "version": "1.0"},
        )

    def test_spec_serialization_roundtrip(self, spec_manager, sample_spec):
        """Test that specification serialization preserves all data."""
        # Serialize
        serialized = spec_manager._serialize_spec(sample_spec)

        # Deserialize
        deserialized = spec_manager._deserialize_spec(serialized)

        # Verify all fields are preserved
        assert deserialized.id == sample_spec.id
        assert deserialized.title == sample_spec.title
        assert deserialized.type == sample_spec.type
        assert deserialized.status == sample_spec.status
        assert deserialized.priority == sample_spec.priority
        assert deserialized.description == sample_spec.description
        assert deserialized.rationale == sample_spec.rationale
        assert deserialized.use_cases == sample_spec.use_cases
        assert deserialized.acceptance_criteria == sample_spec.acceptance_criteria
        assert deserialized.dependencies == sample_spec.dependencies
        assert deserialized.branch == sample_spec.branch
        assert deserialized.metadata == sample_spec.metadata

        # Verify contract
        assert deserialized.contract.inputs == sample_spec.contract.inputs
        assert deserialized.contract.outputs == sample_spec.contract.outputs
        assert deserialized.contract.behavior == sample_spec.contract.behavior
        assert deserialized.contract.constraints == sample_spec.contract.constraints
        assert deserialized.contract.error_handling == sample_spec.contract.error_handling

        # Verify test scenarios
        assert len(deserialized.test_scenarios) == 1
        ts = deserialized.test_scenarios[0]
        orig_ts = sample_spec.test_scenarios[0]
        assert ts.name == orig_ts.name
        assert ts.description == orig_ts.description
        assert ts.given == orig_ts.given
        assert ts.when == orig_ts.when
        assert ts.then == orig_ts.then
        assert ts.examples == orig_ts.examples

    def test_manifest_serialization_roundtrip(self, spec_manager, sample_spec):
        """Test that manifest serialization preserves all data."""
        # Create manifest with spec
        manifest = SpecManifest(
            version="2.0",
            specifications={"feat-test-001": sample_spec},
            branch_mapping={"feature/test": "feat-test-001"},
        )

        # Serialize
        serialized = spec_manager._serialize_manifest(manifest)

        # Deserialize
        deserialized = spec_manager._deserialize_manifest(serialized)

        # Verify manifest fields
        assert deserialized.version == "2.0"
        assert len(deserialized.specifications) == 1
        assert "feat-test-001" in deserialized.specifications
        assert deserialized.branch_mapping == {"feature/test": "feat-test-001"}

        # Verify contained spec
        spec = deserialized.specifications["feat-test-001"]
        assert spec.id == sample_spec.id
        assert spec.title == sample_spec.title

    def test_file_persistence(self, spec_manager):
        """Test that specifications persist to files correctly."""
        # Create specification
        spec = spec_manager.create_specification(
            title="Persistence Test",
            spec_type=SpecType.FEATURE,
            description="Test file persistence",
            rationale="Validate file I/O",
        )

        # Verify spec file exists in the draft folder (default status)
        spec_file = spec_manager.specs_dir / "draft" / f"{spec.id}.yaml"
        assert spec_file.exists()

        # Verify manifest file exists
        assert spec_manager.manifest_path.exists()

        # Create new manager instance to test loading
        new_manager = SpecificationManager(spec_manager.project_dir)
        loaded_spec = new_manager.get_specification(spec.id)

        assert loaded_spec is not None
        assert loaded_spec.title == "Persistence Test"
        assert loaded_spec.type == SpecType.FEATURE


class TestSpecificationErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)
            yield project_dir

    @pytest.fixture
    def spec_manager(self, temp_project):
        """Create SpecificationManager instance."""
        return SpecificationManager(temp_project)

    def test_invalid_datetime_deserialization(self, spec_manager):
        """Test handling of invalid datetime strings."""
        invalid_data = {
            "id": "test-001",
            "title": "Test",
            "type": "feature",
            "status": "draft",
            "priority": "medium",
            "description": "Test",
            "rationale": "Test",
            "created_at": "invalid-datetime",
            "updated_at": "2024-01-01T12:00:00",
        }

        with pytest.raises(ValueError):
            spec_manager._deserialize_spec(invalid_data)

    def test_invalid_enum_values(self, spec_manager):
        """Test handling of invalid enum values."""
        invalid_data = {
            "id": "test-001",
            "title": "Test",
            "type": "invalid_type",  # Invalid enum value
            "status": "draft",
            "priority": "medium",
            "description": "Test",
            "rationale": "Test",
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00",
        }

        with pytest.raises(ValueError):
            spec_manager._deserialize_spec(invalid_data)

    def test_missing_required_fields(self, spec_manager):
        """Test handling of missing required fields."""
        incomplete_data = {
            "id": "test-001",
            "title": "Test",
            # Missing required fields
        }

        with pytest.raises(KeyError):
            spec_manager._deserialize_spec(incomplete_data)

    @patch("quaestor.utils.yaml_utils.load_yaml")
    def test_yaml_loading_error_handling(self, mock_load_yaml, spec_manager):
        """Test handling of YAML loading errors."""
        mock_load_yaml.side_effect = Exception("YAML parsing error")

        # Should handle error gracefully and return empty manifest
        manifest = spec_manager.load_manifest()
        assert isinstance(manifest, SpecManifest)
        assert manifest.specifications == {}

    @patch("quaestor.utils.yaml_utils.save_yaml")
    def test_yaml_saving_error_handling(self, mock_save_yaml, spec_manager):
        """Test handling of YAML saving errors."""
        mock_save_yaml.return_value = False

        # Create a spec
        _spec = spec_manager.create_specification(
            title="Save Error Test",
            spec_type=SpecType.FEATURE,
            description="Test save error handling",
            rationale="Testing error scenarios",
        )

        # This should handle the save error gracefully
        # The exact behavior depends on implementation requirements

    def test_update_with_invalid_attributes(self, spec_manager):
        """Test updating specification with invalid attributes."""
        spec = spec_manager.create_specification(
            title="Update Test",
            spec_type=SpecType.FEATURE,
            description="Test updates",
            rationale="Testing updates",
        )

        # Try to update with invalid attribute
        updates = {
            "invalid_attribute": "some value",
            "title": "Valid Update",
        }

        updated_spec = spec_manager.update_specification(spec.id, updates)

        # Should update valid attributes and ignore invalid ones
        assert updated_spec.title == "Valid Update"
        assert not hasattr(updated_spec, "invalid_attribute")


class TestSpecificationIntegration:
    """Test integration with broader system."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir)
            yield project_dir

    def test_concurrent_access_simulation(self, temp_project):
        """Test concurrent access to specifications (basic simulation)."""
        # Create two manager instances
        manager1 = SpecificationManager(temp_project)
        manager2 = SpecificationManager(temp_project)

        # Create specs from both managers
        spec1 = manager1.create_specification(
            title="Concurrent Test 1",
            spec_type=SpecType.FEATURE,
            description="First concurrent spec",
            rationale="Testing concurrency",
        )

        spec2 = manager2.create_specification(
            title="Concurrent Test 2",
            spec_type=SpecType.BUGFIX,
            description="Second concurrent spec",
            rationale="Testing concurrency",
        )

        # Both should be able to see each other's specs
        assert manager1.get_specification(spec2.id) is not None
        assert manager2.get_specification(spec1.id) is not None

    def test_workflow_simulation(self, temp_project):
        """Test a complete specification workflow."""
        manager = SpecificationManager(temp_project)

        # 1. Create specification
        spec = manager.create_specification(
            title="Workflow Test Feature",
            spec_type=SpecType.FEATURE,
            description="Test complete workflow",
            rationale="Validate end-to-end process",
            priority=SpecPriority.HIGH,
        )
        assert spec.status == SpecStatus.DRAFT

        # 2. Approve specification
        manager.update_specification(
            spec.id,
            {
                "status": SpecStatus.STAGED,
                "use_cases": ["Use case 1", "Use case 2"],
                "acceptance_criteria": ["AC1", "AC2"],
            },
        )

        # 3. Link to branch and start implementation
        manager.link_spec_to_branch(spec.id, "feature/workflow-test")
        updated_spec = manager.get_specification(spec.id)
        assert updated_spec.status == SpecStatus.ACTIVE
        assert updated_spec.branch == "feature/workflow-test"

        # 4. Mark as implemented
        manager.update_specification(spec.id, {"status": SpecStatus.COMPLETED})

        # 5. Mark as tested
        manager.update_specification(spec.id, {"status": SpecStatus.COMPLETED})

        # 6. Mark as deployed
        final_spec = manager.update_specification(spec.id, {"status": SpecStatus.COMPLETED})

        assert final_spec.status == SpecStatus.COMPLETED

        # Verify we can retrieve by branch
        branch_spec = manager.get_spec_by_branch("feature/workflow-test")
        assert branch_spec.id == spec.id
        assert branch_spec.status == SpecStatus.COMPLETED
