"""Pydantic models for Quaestor evaluations.

These models define the input/output schemas for evaluating skills, commands, and agents.
"""

from enum import Enum

from pydantic import BaseModel, Field


class SpecType(str, Enum):
    """Types of specifications."""

    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"


class SpecStatus(str, Enum):
    """Status of a specification."""

    DRAFT = "draft"
    STAGED = "staged"
    ACTIVE = "active"
    COMPLETED = "completed"


class SpecPriority(str, Enum):
    """Priority levels for specifications."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContractModel(BaseModel):
    """Specification contract model for validation."""

    inputs: dict[str, str] = Field(default_factory=dict)
    outputs: dict[str, str] = Field(default_factory=dict)
    behavior: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    error_handling: dict[str, str] = Field(default_factory=dict)


class TestScenarioModel(BaseModel):
    """Test scenario model for validation."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")  # Allow empty description
    given: str = Field(default="")  # Allow empty given
    when: str = Field(default="")  # Allow empty when
    then: str = Field(default="")  # Allow empty then
    examples: list[dict] = Field(default_factory=list)


class SpecificationInput(BaseModel):
    """Input model for specification creation evaluation.

    This represents the user's request that will be turned into a specification.
    """

    request: str = Field(..., min_length=10, description="User's feature request or bug description")
    context: str | None = Field(None, description="Additional context about the codebase or project")
    priority: SpecPriority | None = Field(None, description="Requested priority level")


class SpecificationOutput(BaseModel):
    """Output model for specification quality evaluation.

    This represents the generated specification that should be validated.
    """

    id: str = Field(..., pattern=r"^spec-\d{8}-\d{6}$", description="Unique specification ID")
    title: str = Field(..., min_length=1, max_length=200, description="Clear, descriptive title")
    type: SpecType = Field(..., description="Type of specification")
    status: SpecStatus = Field(..., description="Current status")
    priority: SpecPriority = Field(..., description="Priority level")
    description: str = Field(default="", description="Detailed description")  # Allow empty for poor specs
    rationale: str = Field(default="", description="Why this change is needed")  # Allow empty for poor specs
    acceptance_criteria: list[str] = Field(default_factory=list, description="Acceptance criteria")  # Allow empty
    test_scenarios: list[TestScenarioModel] = Field(
        default_factory=list,
        description="Test scenarios",  # Allow empty for poor specs
    )
    contract: ContractModel = Field(..., description="Contract defining inputs, outputs, behavior")
    estimated_hours: int | None = Field(None, ge=1, le=160, description="Estimated effort in hours")


class TaskProgressModel(BaseModel):
    """Model for tracking task progress."""

    total: int = Field(0, ge=0)
    completed: int = Field(0, ge=0)
    uncertain: int = Field(0, ge=0)
    pending: int = Field(0, ge=0)

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100.0


class ImplementationInput(BaseModel):
    """Input model for implementation evaluation.

    This represents the specification and context for implementation.
    """

    spec_id: str = Field(..., pattern=r"^spec-\d{8}-\d{6}$")
    spec_title: str = Field(..., min_length=1)
    acceptance_criteria: list[str] = Field(..., min_items=1)
    test_scenarios: list[TestScenarioModel] = Field(..., min_items=1)
    codebase_context: str | None = Field(None, description="Relevant codebase information")


class ImplementationOutput(BaseModel):
    """Output model for implementation success evaluation.

    This represents the result of implementing a specification.
    """

    spec_id: str = Field(..., pattern=r"^spec-\d{8}-\d{6}$")
    status: SpecStatus = Field(..., description="Should be 'completed' for successful implementation")
    progress_percentage: float = Field(..., ge=0, le=100, description="Percentage of tasks completed")
    tests_passing: bool = Field(..., description="Whether all tests pass")
    acceptance_criteria_met: list[str] = Field(..., description="List of acceptance criteria IDs that are met")
    files_changed: list[str] = Field(default_factory=list, description="List of files modified")
    tests_added: int = Field(0, ge=0, description="Number of tests added")
    implementation_notes: str | None = Field(None, description="Notes about the implementation")


class EndToEndInput(BaseModel):
    """Input model for end-to-end workflow evaluation.

    This represents a complete user request from start to finish.
    """

    user_request: str = Field(..., min_length=10, description="Original user request")
    expected_outcome: str = Field(..., min_length=10, description="Expected final outcome")
    estimated_hours: int | None = Field(None, ge=1, le=160, description="Estimated time in hours")


class EndToEndOutput(BaseModel):
    """Output model for end-to-end success evaluation.

    This represents the complete workflow result.
    """

    spec_created: bool = Field(..., description="Whether specification was created")
    implementation_completed: bool = Field(..., description="Whether implementation finished")
    tests_passing: bool = Field(..., description="Whether all tests pass")
    acceptance_criteria_met: bool = Field(..., description="Whether acceptance criteria satisfied")
    actual_hours: int | None = Field(None, ge=0, description="Actual time spent in hours")
    success: bool = Field(..., description="Overall success indicator")
    failure_reason: str | None = Field(None, description="Reason for failure if applicable")
