"""Specification management system for Quaestor.

This module implements the core specification-driven development functionality,
allowing users to define, track, and manage specifications as first-class entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from quaestor.utils.yaml_utils import load_yaml, save_yaml

from .folder_manager import FolderManager


class SpecType(Enum):
    """Types of specifications."""

    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"


class SpecStatus(Enum):
    """Status of a specification."""

    DRAFT = "draft"
    STAGED = "staged"
    ACTIVE = "active"
    COMPLETED = "completed"


class SpecPriority(Enum):
    """Priority levels for specifications."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Contract:
    """Specification contract defining inputs, outputs, and behavior."""

    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    behavior: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    error_handling: dict[str, str] = field(default_factory=dict)


@dataclass
class TestScenario:
    """Test scenario for a specification."""

    name: str
    description: str
    given: str
    when: str
    then: str
    examples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Specification:
    """Core specification entity."""

    id: str
    title: str
    type: SpecType
    status: SpecStatus
    priority: SpecPriority
    description: str
    rationale: str
    use_cases: list[str] = field(default_factory=list)
    contract: Contract = field(default_factory=Contract)
    acceptance_criteria: list[str] = field(default_factory=list)
    test_scenarios: list[TestScenario] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    branch: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecManifest:
    """Manifest tracking all specifications and their states."""

    version: str = "1.0"
    specifications: dict[str, Specification] = field(default_factory=dict)
    branch_mapping: dict[str, str] = field(default_factory=dict)  # branch -> spec_id
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SpecificationManager:
    """Manages the lifecycle of specifications."""

    def __init__(self, project_dir: Path):
        """Initialize the specification manager.

        Args:
            project_dir: Root directory of the project
        """
        self.project_dir = project_dir
        self.specs_dir = project_dir / ".quaestor" / "specifications"
        self.manifest_path = self.specs_dir / "manifest.yaml"
        self._manifest: SpecManifest | None = None

        # Initialize FolderManager for lifecycle management
        self.folder_manager = FolderManager(self.specs_dir)

        # Ensure directories exist (including folder structure)
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.folder_manager.create_folder_structure()

    def load_manifest(self) -> SpecManifest:
        """Load the specification manifest."""
        if self._manifest is None:
            manifest_data = load_yaml(self.manifest_path, {})
            if manifest_data:
                self._manifest = self._deserialize_manifest(manifest_data)
            else:
                self._manifest = SpecManifest()

            # Also load specs from folder structure
            self._sync_manifest_with_folders()

        return self._manifest

    def _sync_manifest_with_folders(self) -> None:
        """Sync manifest with specifications in folder structure."""
        if self._manifest is None:
            return

        # Scan all folders for spec files
        for folder in ["draft", "active", "completed"]:
            folder_path = self.specs_dir / folder
            if not folder_path.exists():
                continue

            for spec_file in folder_path.glob("*.yaml"):
                if spec_file.name == "manifest.yaml":
                    continue

                # Load spec from file
                spec_data = load_yaml(spec_file, {})
                if spec_data:
                    spec = self._deserialize_spec(spec_data)

                    # Update status based on folder
                    folder_to_status = {
                        "draft": SpecStatus.DRAFT,
                        "active": SpecStatus.ACTIVE,
                        "completed": SpecStatus.COMPLETED,
                    }
                    expected_status = folder_to_status.get(folder)
                    if expected_status and spec.status != expected_status:
                        spec.status = expected_status

                    # Add to manifest if not present or update
                    self._manifest.specifications[spec.id] = spec

    def save_manifest(self) -> bool:
        """Save the specification manifest."""
        if self._manifest is not None:
            manifest_data = self._serialize_manifest(self._manifest)
            return save_yaml(self.manifest_path, manifest_data)
        return False

    def create_specification(
        self,
        title: str,
        spec_type: SpecType,
        description: str,
        rationale: str,
        priority: SpecPriority = SpecPriority.MEDIUM,
    ) -> Specification:
        """Create a new specification.

        Args:
            title: Title of the specification
            spec_type: Type of specification
            description: Detailed description
            rationale: Why this specification is needed
            priority: Priority level

        Returns:
            Created specification
        """
        # Generate ID
        spec_id = self._generate_spec_id(spec_type, title)

        # Create specification
        spec = Specification(
            id=spec_id,
            title=title,
            type=spec_type,
            status=SpecStatus.DRAFT,
            priority=priority,
            description=description,
            rationale=rationale,
        )

        # Add to manifest
        manifest = self.load_manifest()
        manifest.specifications[spec_id] = spec
        manifest.updated_at = datetime.now()
        self.save_manifest()

        # Save specification file
        self._save_spec_file(spec)

        return spec

    def get_specification(self, spec_id: str) -> Specification | None:
        """Get a specification by ID.

        Args:
            spec_id: Specification ID

        Returns:
            Specification or None if not found
        """
        # Force reload to support concurrent access
        self._manifest = None
        manifest = self.load_manifest()
        return manifest.specifications.get(spec_id)

    def update_specification(self, spec_id: str, updates: dict[str, Any]) -> Specification | None:
        """Update a specification.

        Args:
            spec_id: Specification ID
            updates: Dictionary of updates

        Returns:
            Updated specification or None if not found
        """
        manifest = self.load_manifest()
        spec = manifest.specifications.get(spec_id)

        if spec is None:
            return None

        # Check if status is changing to ACTIVE
        old_status = spec.status
        new_status = updates.get("status")

        # Apply updates
        for key, value in updates.items():
            if hasattr(spec, key):
                setattr(spec, key, value)

        spec.updated_at = datetime.now()
        manifest.updated_at = datetime.now()

        # If transitioning to ACTIVE, enforce active limit
        if old_status != SpecStatus.ACTIVE and new_status == SpecStatus.ACTIVE:
            can_activate, messages = self.enforce_active_limit()
            if not can_activate:
                # Revert status change
                spec.status = old_status
                return None

        # Save changes (will handle folder moves automatically)
        self.save_manifest()
        self._save_spec_file(spec)

        return spec

    def link_spec_to_branch(self, spec_id: str, branch: str) -> bool:
        """Link a specification to a git branch.

        Args:
            spec_id: Specification ID
            branch: Git branch name

        Returns:
            True if successful
        """
        manifest = self.load_manifest()
        spec = manifest.specifications.get(spec_id)

        if spec is None:
            return False

        # Update branch mapping
        manifest.branch_mapping[branch] = spec_id
        spec.branch = branch
        spec.status = SpecStatus.ACTIVE
        spec.updated_at = datetime.now()
        manifest.updated_at = datetime.now()

        # Save changes
        self.save_manifest()
        self._save_spec_file(spec)

        return True

    def get_spec_by_branch(self, branch: str) -> Specification | None:
        """Get specification associated with a branch.

        Args:
            branch: Git branch name

        Returns:
            Specification or None if not found
        """
        manifest = self.load_manifest()
        spec_id = manifest.branch_mapping.get(branch)

        if spec_id:
            return manifest.specifications.get(spec_id)

        return None

    def list_specifications(
        self,
        status: SpecStatus | None = None,
        spec_type: SpecType | None = None,
        priority: SpecPriority | None = None,
    ) -> list[Specification]:
        """List specifications with optional filters.

        Args:
            status: Filter by status
            spec_type: Filter by type
            priority: Filter by priority

        Returns:
            List of specifications
        """
        manifest = self.load_manifest()
        specs = list(manifest.specifications.values())

        # Apply filters
        if status:
            specs = [s for s in specs if s.status == status]
        if spec_type:
            specs = [s for s in specs if s.type == spec_type]
        if priority:
            specs = [s for s in specs if s.priority == priority]

        # Sort by priority and creation date
        priority_order = {
            SpecPriority.CRITICAL: 0,
            SpecPriority.HIGH: 1,
            SpecPriority.MEDIUM: 2,
            SpecPriority.LOW: 3,
        }

        specs.sort(
            key=lambda s: (priority_order[s.priority], -s.created_at.timestamp()),
        )

        return specs

    def migrate_to_folder_structure(self) -> bool:
        """Migrate existing flat specifications to folder structure.

        Returns:
            True if migration successful
        """
        result = self.folder_manager.migrate_flat_specifications()

        if result.success:
            # Reload manifest to pick up migrated specs
            self._manifest = None
            self.load_manifest()

        return result.success

    def enforce_active_limit(self) -> tuple[bool, list[str]]:
        """Enforce the limit on active specifications.

        Returns:
            Tuple of (success, list of messages)
        """
        return self.folder_manager.enforce_active_limit()

    def complete_specification(self, spec_id: str) -> bool:
        """Mark a specification as completed and move to completed folder.

        Args:
            spec_id: Specification ID

        Returns:
            True if successful
        """
        spec = self.get_specification(spec_id)
        if spec is None:
            return False

        # Update status
        spec.status = SpecStatus.COMPLETED
        spec.updated_at = datetime.now()

        # Save will automatically move to completed folder
        manifest = self.load_manifest()
        manifest.specifications[spec_id] = spec
        manifest.updated_at = datetime.now()
        self.save_manifest()

        return self._save_spec_file(spec)

    def activate_specification(self, spec_id: str) -> bool:
        """Activate a specification, moving it to active folder.

        Args:
            spec_id: Specification ID

        Returns:
            True if successful
        """
        # Check active limit first
        can_activate, messages = self.enforce_active_limit()
        if not can_activate:
            for msg in messages:
                print(f"Warning: {msg}")
            return False

        spec = self.get_specification(spec_id)
        if spec is None:
            return False

        # Update status
        spec.status = SpecStatus.ACTIVE
        spec.updated_at = datetime.now()

        # Save will automatically move to active folder
        manifest = self.load_manifest()
        manifest.specifications[spec_id] = spec
        manifest.updated_at = datetime.now()
        self.save_manifest()

        return self._save_spec_file(spec)

    def _generate_spec_id(self, spec_type: SpecType, title: str) -> str:
        """Generate a unique specification ID.

        Args:
            spec_type: Type of specification
            title: Specification title

        Returns:
            Generated ID
        """
        # Create base ID from type and title
        type_prefix = {
            SpecType.FEATURE: "feat",
            SpecType.BUGFIX: "fix",
            SpecType.REFACTOR: "refactor",
            SpecType.DOCUMENTATION: "docs",
            SpecType.PERFORMANCE: "perf",
            SpecType.SECURITY: "sec",
            SpecType.TESTING: "test",
        }

        prefix = type_prefix.get(spec_type, "spec")
        title_part = title.lower().replace(" ", "-")[:20]

        # Ensure uniqueness
        manifest = self.load_manifest()
        base_id = f"{prefix}-{title_part}"
        spec_id = base_id
        counter = 1

        while spec_id in manifest.specifications:
            spec_id = f"{base_id}-{counter}"
            counter += 1

        return spec_id

    def _save_spec_file(self, spec: Specification) -> bool:
        """Save a specification to its file in the appropriate folder.

        Args:
            spec: Specification to save

        Returns:
            True if successful
        """
        # Determine target folder based on status
        status_to_folder = {
            SpecStatus.DRAFT: "draft",
            SpecStatus.STAGED: "draft",  # Staged specs still in draft folder
            SpecStatus.ACTIVE: "active",
            SpecStatus.COMPLETED: "completed",
        }

        target_folder = status_to_folder.get(spec.status, "draft")
        spec_file = self.specs_dir / target_folder / f"{spec.id}.yaml"

        # Ensure the spec file is in the right folder
        # Check all folders to find existing file
        existing_file = None
        for folder in ["draft", "active", "completed"]:
            potential_file = self.specs_dir / folder / f"{spec.id}.yaml"
            if potential_file.exists():
                existing_file = potential_file
                break

        # If spec exists and needs to move to different folder
        if existing_file and existing_file.parent.name != target_folder:
            result = self.folder_manager.move_specification(existing_file, target_folder)
            if not result.success:
                return False
            # Update spec_file to the new location
            if result.moved_files:
                spec_file = Path(result.moved_files[0])

        # Save specification data
        spec_data = self._serialize_spec(spec)
        return save_yaml(spec_file, spec_data)

    def _serialize_spec(self, spec: Specification) -> dict[str, Any]:
        """Serialize a specification to dict.

        Args:
            spec: Specification to serialize

        Returns:
            Serialized data
        """
        return {
            "id": spec.id,
            "title": spec.title,
            "type": spec.type.value,
            "status": spec.status.value,
            "priority": spec.priority.value,
            "description": spec.description,
            "rationale": spec.rationale,
            "use_cases": spec.use_cases,
            "contract": {
                "inputs": spec.contract.inputs,
                "outputs": spec.contract.outputs,
                "behavior": spec.contract.behavior,
                "constraints": spec.contract.constraints,
                "error_handling": spec.contract.error_handling,
            },
            "acceptance_criteria": spec.acceptance_criteria,
            "test_scenarios": [
                {
                    "name": ts.name,
                    "description": ts.description,
                    "given": ts.given,
                    "when": ts.when,
                    "then": ts.then,
                    "examples": ts.examples,
                }
                for ts in spec.test_scenarios
            ],
            "dependencies": spec.dependencies,
            "branch": spec.branch,
            "created_at": spec.created_at.isoformat(),
            "updated_at": spec.updated_at.isoformat(),
            "metadata": spec.metadata,
        }

    def _deserialize_spec(self, data: dict[str, Any]) -> Specification:
        """Deserialize a specification from dict.

        Args:
            data: Serialized data

        Returns:
            Specification object
        """
        contract_data = data.get("contract", {})
        contract = Contract(
            inputs=contract_data.get("inputs", {}),
            outputs=contract_data.get("outputs", {}),
            behavior=contract_data.get("behavior", []),
            constraints=contract_data.get("constraints", []),
            error_handling=contract_data.get("error_handling", {}),
        )

        test_scenarios = []
        for ts_data in data.get("test_scenarios", []):
            test_scenarios.append(
                TestScenario(
                    name=ts_data["name"],
                    description=ts_data["description"],
                    given=ts_data["given"],
                    when=ts_data["when"],
                    then=ts_data["then"],
                    examples=ts_data.get("examples", []),
                )
            )

        return Specification(
            id=data["id"],
            title=data["title"],
            type=SpecType(data["type"]),
            status=SpecStatus(data["status"]),
            priority=SpecPriority(data["priority"]),
            description=data["description"],
            rationale=data["rationale"],
            use_cases=data.get("use_cases", []),
            contract=contract,
            acceptance_criteria=data.get("acceptance_criteria", []),
            test_scenarios=test_scenarios,
            dependencies=data.get("dependencies", []),
            branch=data.get("branch"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
        )

    def _serialize_manifest(self, manifest: SpecManifest) -> dict[str, Any]:
        """Serialize a manifest to dict.

        Args:
            manifest: Manifest to serialize

        Returns:
            Serialized data
        """
        return {
            "version": manifest.version,
            "specifications": {
                spec_id: self._serialize_spec(spec) for spec_id, spec in manifest.specifications.items()
            },
            "branch_mapping": manifest.branch_mapping,
            "created_at": manifest.created_at.isoformat(),
            "updated_at": manifest.updated_at.isoformat(),
        }

    def _deserialize_manifest(self, data: dict[str, Any]) -> SpecManifest:
        """Deserialize a manifest from dict.

        Args:
            data: Serialized data

        Returns:
            Manifest object
        """
        specifications = {}
        for spec_id, spec_data in data.get("specifications", {}).items():
            specifications[spec_id] = self._deserialize_spec(spec_data)

        return SpecManifest(
            version=data.get("version", "1.0"),
            specifications=specifications,
            branch_mapping=data.get("branch_mapping", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
