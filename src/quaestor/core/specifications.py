"""Simplified specification system for Quaestor.

This module provides basic specification types and utilities.
Lifecycle management is now handled by Agent Skills.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .markdown_spec import (
    MarkdownSpecParser,
    TaskProgress,
    convert_markdown_to_dict,
    convert_yaml_to_markdown,
)


# Re-export enums from markdown_spec for backwards compatibility
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
class SpecTestScenario:
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
    test_scenarios: list[SpecTestScenario] = field(default_factory=list)
    dependencies: dict[str, list[str]] = field(default_factory=lambda: {"requires": [], "blocks": [], "related": []})
    branch: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    task_progress: TaskProgress | None = None


# Simple utility functions


def load_spec_from_file(spec_path: Path) -> Specification | None:
    """Load a specification from a Markdown file.

    Args:
        spec_path: Path to the specification file

    Returns:
        Specification object or None if failed to parse
    """
    if not spec_path.exists():
        return None

    try:
        content = spec_path.read_text()
        markdown_spec = MarkdownSpecParser.parse(content)

        # Convert to our Specification format
        spec_dict = convert_markdown_to_dict(markdown_spec)

        # Build Specification object
        spec = Specification(
            id=spec_dict["id"],
            title=spec_dict["title"],
            type=SpecType(spec_dict["type"]),
            status=SpecStatus(spec_dict["status"]),
            priority=SpecPriority(spec_dict["priority"]),
            description=spec_dict["description"],
            rationale=spec_dict["rationale"],
            use_cases=spec_dict.get("use_cases", []),
            contract=Contract(**spec_dict.get("contract", {})),
            acceptance_criteria=spec_dict.get("acceptance_criteria", []),
            test_scenarios=[SpecTestScenario(**ts) for ts in spec_dict.get("test_scenarios", [])],
            dependencies=spec_dict.get("dependencies", {"requires": [], "blocks": [], "related": []}),
            branch=spec_dict.get("branch"),
            created_at=(
                datetime.fromisoformat(spec_dict["created_at"]) if spec_dict.get("created_at") else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(spec_dict["updated_at"]) if spec_dict.get("updated_at") else datetime.now()
            ),
            metadata=spec_dict.get("metadata", {}),
            task_progress=markdown_spec.task_progress,
        )

        return spec
    except Exception:
        return None


def save_spec_to_file(spec: Specification, spec_path: Path) -> bool:
    """Save a specification to a Markdown file.

    Args:
        spec: Specification to save
        spec_path: Path where to save the file

    Returns:
        True if successful
    """
    try:
        # Convert to dict
        spec_dict = {
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
            "created_at": spec.created_at.isoformat() if spec.created_at else None,
            "updated_at": spec.updated_at.isoformat() if spec.updated_at else None,
            "metadata": spec.metadata,
        }

        # Convert to Markdown
        markdown_content = convert_yaml_to_markdown(spec_dict)

        # Ensure directory exists
        spec_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        spec_path.write_text(markdown_content)
        return True
    except Exception:
        return False


def find_specs_in_folder(folder_path: Path) -> list[Path]:
    """Find all specification files in a folder.

    Args:
        folder_path: Path to folder to search

    Returns:
        List of paths to specification files
    """
    if not folder_path.exists():
        return []

    return sorted(folder_path.glob("spec-*.md"))


def move_spec_between_folders(spec_id: str, from_folder: Path, to_folder: Path) -> bool:
    """Move a specification from one folder to another.

    Args:
        spec_id: Specification ID
        from_folder: Source folder path
        to_folder: Destination folder path

    Returns:
        True if successful
    """
    source_path = from_folder / f"{spec_id}.md"
    if not source_path.exists():
        return False

    # Ensure destination folder exists
    to_folder.mkdir(parents=True, exist_ok=True)

    # Move file
    dest_path = to_folder / f"{spec_id}.md"
    source_path.rename(dest_path)

    return True


def get_spec_progress(spec_path: Path) -> TaskProgress | None:
    """Get progress information from a specification file.

    Args:
        spec_path: Path to specification file

    Returns:
        TaskProgress or None if file doesn't exist
    """
    spec = load_spec_from_file(spec_path)
    return spec.task_progress if spec else None
