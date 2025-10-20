"""
Markdown specification parser - Simple, forgiving, and AI-friendly.

No strict validation, just sensible defaults and auto-correction.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SpecType(Enum):
    """Valid specification types."""

    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"


class SpecStatus(Enum):
    """Specification status values."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SpecPriority(Enum):
    """Specification priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Type mappings for auto-correction
TYPE_MAPPINGS = {
    "removal": "refactor",
    "remove": "refactor",
    "delete": "refactor",
    "deletion": "refactor",
    "cleanup": "refactor",
    "enhancement": "feature",
    "feat": "feature",
    "fix": "bugfix",
    "bug": "bugfix",
    "docs": "documentation",
    "doc": "documentation",
    "perf": "performance",
    "test": "testing",
    "tests": "testing",
    "sec": "security",
}

# Checkbox patterns for task tracking
CHECKBOX_PATTERNS = {
    "unchecked": re.compile(r"^-\s*\[\s*\]\s+(.*)$"),
    "checked": re.compile(r"^-\s*\[x\]\s+(.*)$", re.IGNORECASE),
    "uncertain": re.compile(r"^-\s*\[\?\]\s+(.*)$"),
}


@dataclass
class TaskProgress:
    """Progress tracking information for a specification."""

    total: int = 0
    completed: int = 0
    uncertain: int = 0
    pending: int = 0

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total == 0:
            return 100.0  # No tasks means complete
        return (self.completed / self.total) * 100.0

    @property
    def is_complete(self) -> bool:
        """Check if all tasks are complete."""
        return self.pending == 0 and self.uncertain == 0


@dataclass
class Specification:
    """A parsed specification with all its fields."""

    id: str
    type: SpecType
    status: SpecStatus
    priority: SpecPriority
    title: str = ""
    description: str = ""
    rationale: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    branch: str | None = None
    dependencies: dict[str, list[str]] = field(default_factory=lambda: {"requires": [], "blocks": [], "related": []})
    contract: dict[str, Any] = field(
        default_factory=lambda: {"inputs": {}, "outputs": {}, "behavior": [], "constraints": []}
    )
    acceptance_criteria: list[str] = field(default_factory=list)
    test_scenarios: list[dict[str, str]] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    task_progress: TaskProgress | None = None


class MarkdownSpecParser:
    """Parser for Markdown specification files."""

    @classmethod
    def parse(cls, content: str) -> Specification:
        """Parse a markdown specification file.

        Args:
            content: The markdown file content

        Returns:
            A Specification object

        Raises:
            ValueError: If the content is invalid (but we try to avoid this)
        """
        # Extract frontmatter
        frontmatter = cls._extract_frontmatter(content)
        if not frontmatter:
            raise ValueError("No frontmatter found in specification")

        # Remove frontmatter from content
        content_without_frontmatter = cls._remove_frontmatter(content)

        # Parse sections
        sections = cls._parse_sections(content_without_frontmatter)

        # Store raw content for title extraction
        sections["_raw_content"] = content_without_frontmatter

        # Build specification
        spec = cls._build_specification(frontmatter, sections)

        # Parse task progress from the entire document
        spec.task_progress = cls._parse_task_progress(content)

        return spec

    @classmethod
    def _extract_frontmatter(cls, content: str) -> dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return {}

        frontmatter_text = match.group(1)
        frontmatter = {}

        # Simple key-value parsing (not full YAML)
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                frontmatter[key] = value

        return frontmatter

    @classmethod
    def _remove_frontmatter(cls, content: str) -> str:
        """Remove frontmatter from content."""
        match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if match:
            return content[match.end() :]
        return content

    @classmethod
    def _extract_h1_title(cls, content: str) -> str:
        """Extract the first H1 header as the title."""
        for line in content.split("\n"):
            if line.startswith("# ") and not line.startswith("##"):
                return line[2:].strip()
        return ""

    @classmethod
    def _parse_sections(cls, content: str) -> dict[str, str]:
        """Parse markdown sections by top-level headers (## only)."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split("\n"):
            # Check for top-level headers (## but not ###)
            if line.startswith("##") and not line.startswith("###"):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                header_match = re.match(r"^##\s+(.+)", line)
                if header_match:
                    current_section = header_match.group(1).lower()
                    current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    @classmethod
    def _build_specification(cls, frontmatter: dict[str, Any], sections: dict[str, str]) -> Specification:
        """Build a Specification object from parsed data."""

        # Get ID (required)
        spec_id = frontmatter.get("id")
        if not spec_id:
            raise ValueError("Missing required field: id")

        # Get type with auto-correction
        spec_type = cls._parse_type(frontmatter.get("type", "feature"))

        # Get status with default
        spec_status = cls._parse_status(frontmatter.get("status", "draft"))

        # Get priority with default
        spec_priority = cls._parse_priority(frontmatter.get("priority", "medium"))

        # Get title from first # header or frontmatter
        title = frontmatter.get("title", "")
        if not title:
            # Try to find H1 title in content
            title = cls._extract_h1_title(sections.get("_raw_content", ""))

        # Parse timestamps
        created_at = cls._parse_timestamp(frontmatter.get("created_at"))
        updated_at = cls._parse_timestamp(frontmatter.get("updated_at"))

        # Parse sections
        description = sections.get("description", "")
        rationale = sections.get("rationale", "")

        # Parse dependencies
        dependencies = cls._parse_dependencies(sections.get("dependencies", ""))

        # Parse contract
        contract = cls._parse_contract(sections)

        # Parse acceptance criteria
        acceptance_criteria = cls._parse_acceptance_criteria(sections.get("acceptance criteria", ""))

        # Parse test scenarios
        test_scenarios = cls._parse_test_scenarios(sections.get("test scenarios", ""))

        # Parse risks
        risks = cls._parse_list_section(sections.get("risks", ""))

        # Parse success metrics
        success_metrics = cls._parse_list_section(sections.get("success metrics", ""))

        # Additional metadata
        metadata = {}
        if "metadata" in sections:
            metadata = cls._parse_metadata(sections["metadata"])

        # Add any extra frontmatter fields to metadata
        for key, value in frontmatter.items():
            if key not in ["id", "type", "status", "priority", "title", "created_at", "updated_at", "branch"]:
                metadata[key] = value

        return Specification(
            id=spec_id,
            type=spec_type,
            status=spec_status,
            priority=spec_priority,
            title=title,
            description=description,
            rationale=rationale,
            created_at=created_at,
            updated_at=updated_at,
            branch=frontmatter.get("branch"),
            dependencies=dependencies,
            contract=contract,
            acceptance_criteria=acceptance_criteria,
            test_scenarios=test_scenarios,
            risks=risks,
            success_metrics=success_metrics,
            metadata=metadata,
        )

    @classmethod
    def _parse_type(cls, type_str: str) -> SpecType:
        """Parse type with auto-correction."""
        type_str = type_str.lower().strip()

        # Check if it's already valid
        for spec_type in SpecType:
            if type_str == spec_type.value:
                return spec_type

        # Try to map it
        mapped = TYPE_MAPPINGS.get(type_str)
        if mapped:
            for spec_type in SpecType:
                if mapped == spec_type.value:
                    return spec_type

        # Default to feature
        return SpecType.FEATURE

    @classmethod
    def _parse_status(cls, status_str: str) -> SpecStatus:
        """Parse status with default."""
        status_str = status_str.lower().strip()

        for spec_status in SpecStatus:
            if status_str == spec_status.value:
                return spec_status

        # Default to draft
        return SpecStatus.DRAFT

    @classmethod
    def _parse_priority(cls, priority_str: str) -> SpecPriority:
        """Parse priority with default."""
        priority_str = priority_str.lower().strip()

        for spec_priority in SpecPriority:
            if priority_str == spec_priority.value:
                return spec_priority

        # Default to medium
        return SpecPriority.MEDIUM

    @classmethod
    def _parse_timestamp(cls, timestamp_str: str | None) -> datetime | None:
        """Parse various timestamp formats."""
        if not timestamp_str:
            return None

        # Clean up the string
        timestamp_str = timestamp_str.strip()

        # Try different formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S+00:00",
            "%Y-%m-%dT%H:%M:%S-00:00",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # Try parsing with timezone info
        try:
            # Handle ISO format with timezone
            if "+" in timestamp_str or timestamp_str.endswith("Z"):
                # Replace Z with +00:00 for parsing
                ts = timestamp_str.replace("Z", "+00:00")
                # Try to parse with timezone
                return datetime.fromisoformat(ts.replace("+00:00", "")).replace(tzinfo=None)
        except:
            pass

        # If nothing works, return None (not critical)
        return None

    @classmethod
    def _parse_dependencies(cls, content: str) -> dict[str, list[str]]:
        """Parse dependencies section."""
        deps = {"requires": [], "blocks": [], "related": []}

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Look for patterns like "**Requires**: spec-001, spec-002" or "- **Requires**: spec-001, spec-002"
            # Remove leading dash if present
            if line.startswith("- "):
                line = line[2:].strip()

            for dep_type in ["requires", "blocks", "related"]:
                pattern = rf"\*?\*?{dep_type}\*?\*?:\s*(.+)"
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    spec_list = match.group(1)
                    # Split by comma and clean up, filter out empty strings
                    specs = [s.strip() for s in spec_list.split(",") if s.strip()]
                    deps[dep_type.lower()] = specs
                    break

        return deps

    @classmethod
    def _parse_contract(cls, sections: dict[str, str]) -> dict[str, Any]:
        """Parse contract section."""
        contract = {"inputs": {}, "outputs": {}, "behavior": [], "constraints": []}

        contract_content = sections.get("contract", "")
        if not contract_content:
            return contract

        current_subsection = None

        for line in contract_content.split("\n"):
            line = line.strip()

            # Check for subsection headers
            if line.lower().startswith("### inputs"):
                current_subsection = "inputs"
            elif line.lower().startswith("### outputs"):
                current_subsection = "outputs"
            elif line.lower().startswith("### behavior"):
                current_subsection = "behavior"
            elif line.lower().startswith("### constraints"):
                current_subsection = "constraints"
            elif line.startswith("-") and current_subsection:
                # Parse list item
                item = line[1:].strip()

                if current_subsection in ["inputs", "outputs"]:
                    # Parse parameter definition
                    match = re.match(r"`?(\w+)`?\s*\((\w+)\):\s*(.+)", item)
                    if match:
                        name = match.group(1)
                        param_type = match.group(2)
                        description = match.group(3)
                        contract[current_subsection][name] = {"type": param_type, "description": description}
                elif current_subsection in ["behavior", "constraints"]:
                    contract[current_subsection].append(item)

        return contract

    @classmethod
    def _parse_acceptance_criteria(cls, content: str) -> list[str]:
        """Parse acceptance criteria as checklist items."""
        criteria = []

        for line in content.split("\n"):
            line = line.strip()
            # Look for checkbox items
            if line.startswith("- ["):
                criteria.append(line[2:])  # Keep the checkbox

        return criteria

    @classmethod
    def _parse_task_progress(cls, content: str) -> TaskProgress:
        """Parse all checkbox tasks in the specification.

        Searches entire document for checkbox patterns:
        - [ ] Unchecked task
        - [x] Checked task
        - [?] Uncertain task

        Args:
            content: Full markdown content

        Returns:
            TaskProgress object with counts
        """
        progress = TaskProgress()

        for line in content.split("\n"):
            line = line.strip()

            if CHECKBOX_PATTERNS["checked"].match(line):
                progress.completed += 1
                progress.total += 1
            elif CHECKBOX_PATTERNS["unchecked"].match(line):
                progress.pending += 1
                progress.total += 1
            elif CHECKBOX_PATTERNS["uncertain"].match(line):
                progress.uncertain += 1
                progress.total += 1

        return progress

    @classmethod
    def _parse_test_scenarios(cls, content: str) -> list[dict[str, str]]:
        """Parse test scenarios."""
        scenarios = []
        current_scenario = None
        current_field = None  # Track which field we're accumulating

        for line in content.split("\n"):
            line = line.strip()

            # Check for scenario header
            if line.startswith("###"):
                # Save previous scenario
                if current_scenario:
                    scenarios.append(current_scenario)

                # Start new scenario
                name = line.replace("###", "").strip()
                current_scenario = {"name": name}
                current_field = None
            elif current_scenario:
                # Parse Given/When/Then - support both **Given**: and **Given:**
                if line.startswith("**Given**:") or line.startswith("**Given:**"):
                    text = line.replace("**Given**:", "").replace("**Given:**", "").strip()
                    current_scenario["given"] = text
                    current_field = "given" if not text else None
                elif line.startswith("**When**:") or line.startswith("**When:**"):
                    text = line.replace("**When**:", "").replace("**When:**", "").strip()
                    current_scenario["when"] = text
                    current_field = "when" if not text else None
                elif line.startswith("**Then**:") or line.startswith("**Then:**"):
                    text = line.replace("**Then**:", "").replace("**Then:**", "").strip()
                    current_scenario["then"] = text
                    current_field = "then" if not text else None
                elif line.startswith("**Examples**:") or line.startswith("**Examples:**"):
                    current_field = None  # Stop accumulating
                elif current_field and line:
                    # Continue accumulating multi-line content for given/when/then
                    if line.startswith("-"):
                        # List item
                        current_scenario[current_field] += "\n" + line
                    elif not line.startswith("**"):
                        # Regular continuation
                        current_scenario[current_field] += " " + line
                elif line and "description" not in current_scenario and "given" not in current_scenario:
                    current_scenario["description"] = line

        # Save last scenario
        if current_scenario:
            # Ensure description exists (required field)
            if "description" not in current_scenario:
                current_scenario["description"] = ""
            scenarios.append(current_scenario)

        # Ensure all scenarios have required fields
        for scenario in scenarios:
            scenario.setdefault("description", "")
            scenario.setdefault("given", "")
            scenario.setdefault("when", "")
            scenario.setdefault("then", "")

        return scenarios

    @classmethod
    def _parse_list_section(cls, content: str) -> list[str]:
        """Parse a section containing a list of items."""
        items = []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                items.append(line[1:].strip())
            elif line and not line.startswith("#"):
                # Non-list item, add as-is
                items.append(line)

        return items

    @classmethod
    def _parse_metadata(cls, content: str) -> dict[str, Any]:
        """Parse metadata section."""
        metadata = {}

        for line in content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata


def convert_yaml_to_markdown(yaml_spec: dict[str, Any]) -> str:
    """Convert a YAML specification to Markdown format.

    Args:
        yaml_spec: Dictionary containing YAML specification data

    Returns:
        Markdown formatted specification
    """
    lines = []

    # Add frontmatter
    lines.append("---")
    for key in ["id", "type", "status", "priority", "created_at", "updated_at", "branch"]:
        if key in yaml_spec:
            lines.append(f"{key}: {yaml_spec[key]}")
    lines.append("---")
    lines.append("")

    # Add title
    title = yaml_spec.get("title", yaml_spec.get("id", "Untitled"))
    lines.append(f"# {title}")
    lines.append("")

    # Add description
    if "description" in yaml_spec:
        lines.append("## Description")
        lines.append(yaml_spec["description"])
        lines.append("")

    # Add rationale
    if "rationale" in yaml_spec:
        lines.append("## Rationale")
        lines.append(yaml_spec["rationale"])
        lines.append("")

    # Add dependencies
    if "dependencies" in yaml_spec:
        deps = yaml_spec["dependencies"]
        if deps.get("requires") or deps.get("blocks") or deps.get("related"):
            lines.append("## Dependencies")
            if deps.get("requires"):
                lines.append(f"- **Requires**: {', '.join(deps['requires'])}")
            if deps.get("blocks"):
                lines.append(f"- **Blocks**: {', '.join(deps['blocks'])}")
            if deps.get("related"):
                lines.append(f"- **Related**: {', '.join(deps['related'])}")
            lines.append("")

    # Add contract
    if "contract" in yaml_spec:
        contract = yaml_spec["contract"]
        lines.append("## Contract")
        lines.append("")

        if contract.get("inputs"):
            lines.append("### Inputs")
            for name, details in contract["inputs"].items():
                if isinstance(details, dict):
                    lines.append(f"- `{name}` ({details.get('type', 'unknown')}): {details.get('description', '')}")
                else:
                    lines.append(f"- `{name}`: {details}")
            lines.append("")

        if contract.get("outputs"):
            lines.append("### Outputs")
            for name, details in contract["outputs"].items():
                if isinstance(details, dict):
                    lines.append(f"- `{name}` ({details.get('type', 'unknown')}): {details.get('description', '')}")
                else:
                    lines.append(f"- `{name}`: {details}")
            lines.append("")

        if contract.get("behavior"):
            lines.append("### Behavior")
            for item in contract["behavior"]:
                lines.append(f"- {item}")
            lines.append("")

        if contract.get("constraints"):
            lines.append("### Constraints")
            for item in contract["constraints"]:
                lines.append(f"- {item}")
            lines.append("")

    # Add acceptance criteria
    if "acceptance_criteria" in yaml_spec:
        lines.append("## Acceptance Criteria")
        for criterion in yaml_spec["acceptance_criteria"]:
            # Check if already has checkbox
            if criterion.startswith("[x]") or criterion.startswith("[ ]"):
                lines.append(f"- {criterion}")
            else:
                lines.append(f"- [ ] {criterion}")
        lines.append("")

    # Add test scenarios
    if "test_scenarios" in yaml_spec:
        lines.append("## Test Scenarios")
        lines.append("")
        for scenario in yaml_spec["test_scenarios"]:
            lines.append(f"### {scenario.get('name', 'Unnamed Scenario')}")
            if "description" in scenario:
                lines.append(scenario["description"])
            if "given" in scenario:
                lines.append(f"**Given**: {scenario['given']}")
            if "when" in scenario:
                lines.append(f"**When**: {scenario['when']}")
            if "then" in scenario:
                lines.append(f"**Then**: {scenario['then']}")
            lines.append("")

    # Add risks
    if "risks" in yaml_spec:
        lines.append("## Risks")
        for risk in yaml_spec["risks"]:
            lines.append(f"- {risk}")
        lines.append("")

    # Add success metrics
    if "success_metrics" in yaml_spec:
        lines.append("## Success Metrics")
        for metric in yaml_spec["success_metrics"]:
            lines.append(f"- {metric}")
        lines.append("")

    # Add metadata
    if "metadata" in yaml_spec:
        lines.append("## Metadata")
        for key, value in yaml_spec["metadata"].items():
            lines.append(f"{key}: {value}")
        lines.append("")

    return "\n".join(lines)


def convert_markdown_to_dict(spec: Specification) -> dict[str, Any]:
    """Convert a Specification object to a dictionary.

    Args:
        spec: A Specification object

    Returns:
        Dictionary representation
    """
    result = {
        "id": spec.id,
        "type": spec.type.value,
        "status": spec.status.value,
        "priority": spec.priority.value,
        "title": spec.title,
        "description": spec.description,
        "rationale": spec.rationale,
    }

    if spec.created_at:
        result["created_at"] = spec.created_at.isoformat()

    if spec.updated_at:
        result["updated_at"] = spec.updated_at.isoformat()

    if spec.branch:
        result["branch"] = spec.branch

    if spec.dependencies:
        result["dependencies"] = spec.dependencies

    if spec.contract:
        result["contract"] = spec.contract

    if spec.acceptance_criteria:
        result["acceptance_criteria"] = spec.acceptance_criteria

    if spec.test_scenarios:
        result["test_scenarios"] = spec.test_scenarios

    if spec.risks:
        result["risks"] = spec.risks

    if spec.success_metrics:
        result["success_metrics"] = spec.success_metrics

    if spec.metadata:
        result["metadata"] = spec.metadata

    # Include task progress if available
    if spec.task_progress:
        result["task_progress"] = {
            "total": spec.task_progress.total,
            "completed": spec.task_progress.completed,
            "pending": spec.task_progress.pending,
            "uncertain": spec.task_progress.uncertain,
            "completion_percentage": spec.task_progress.completion_percentage,
            "is_complete": spec.task_progress.is_complete,
        }

    return result
