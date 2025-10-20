"""Utility functions for Quaestor evaluations."""

import re
import traceback
from pathlib import Path

from quaestor.scripts.markdown_spec import MarkdownSpecParser
from quaestor.scripts.specifications import load_spec_from_file

from .models import SpecificationOutput, TaskProgressModel, TestScenarioModel


def load_spec_as_eval_output(spec_path: Path) -> SpecificationOutput | None:
    """Load a specification file and convert it to evaluation output format.

    Args:
        spec_path: Path to the specification markdown file

    Returns:
        SpecificationOutput model or None if parsing fails
    """
    if not spec_path.exists():
        print(f"Error: Spec file does not exist: {spec_path}")
        return None

    # Load the spec using the official function
    spec = load_spec_from_file(spec_path)
    if not spec:
        print(f"Error: load_spec_from_file returned None for: {spec_path}")
        # Try to get more details
        try:
            content = spec_path.read_text()
            MarkdownSpecParser.parse(content)
            print("  But MarkdownSpecParser succeeded, so error is in Specification construction")
        except Exception as e:
            print(f"  Parse error: {type(e).__name__}: {e}")
        return None

    try:
        # Convert test scenarios to models
        test_scenarios = [
            TestScenarioModel(
                name=ts.name,
                description=ts.description,
                given=ts.given,
                when=ts.when,
                then=ts.then,
                examples=ts.examples,
            )
            for ts in spec.test_scenarios
        ]

        # Create SpecificationOutput
        return SpecificationOutput(
            id=spec.id,
            title=spec.title,
            type=spec.type.value,
            status=spec.status.value,
            priority=spec.priority.value,
            description=spec.description,
            rationale=spec.rationale,
            acceptance_criteria=spec.acceptance_criteria,
            test_scenarios=test_scenarios,
            contract=spec.contract.__dict__,
            estimated_hours=spec.metadata.get("estimated_hours"),
        )
    except Exception as e:
        print(f"Error converting spec to evaluation output: {e}")
        print(f"Spec path: {spec_path}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return None


def calculate_spec_progress(spec_path: Path) -> TaskProgressModel:
    """Calculate task progress from a specification file.

    Args:
        spec_path: Path to specification file

    Returns:
        TaskProgressModel with progress information
    """
    if not spec_path.exists():
        return TaskProgressModel()

    content = spec_path.read_text()
    markdown_spec = MarkdownSpecParser.parse(content)

    if markdown_spec.task_progress:
        progress = markdown_spec.task_progress
        return TaskProgressModel(
            total=progress.total,
            completed=progress.completed,
            uncertain=progress.uncertain,
            pending=progress.pending,
        )

    return TaskProgressModel()


def count_acceptance_criteria_met(spec_path: Path) -> tuple[int, int]:
    """Count how many acceptance criteria checkboxes are checked.

    Args:
        spec_path: Path to specification file

    Returns:
        Tuple of (completed, total) acceptance criteria
    """
    if not spec_path.exists():
        return (0, 0)

    content = spec_path.read_text()

    # Find acceptance criteria section
    ac_section_match = re.search(r"## Acceptance Criteria\s*\n(.*?)(?=\n##|$)", content, re.DOTALL)
    if not ac_section_match:
        return (0, 0)

    ac_section = ac_section_match.group(1)

    # Count checkboxes
    total = len(re.findall(r"- \[[ x]\]", ac_section))
    completed = len(re.findall(r"- \[x\]", ac_section))

    return (completed, total)


def has_required_spec_fields(spec_output: SpecificationOutput) -> tuple[bool, list[str]]:
    """Check if specification has all required fields with meaningful content.

    Args:
        spec_output: SpecificationOutput model to validate

    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    missing_fields = []

    # Check required string fields are not empty
    if not spec_output.title or len(spec_output.title) < 5:
        missing_fields.append("title (must be at least 5 characters)")

    if not spec_output.description or len(spec_output.description) < 20:
        missing_fields.append("description (must be at least 20 characters)")

    if not spec_output.rationale or len(spec_output.rationale) < 10:
        missing_fields.append("rationale (must be at least 10 characters)")

    # Check lists have items
    if not spec_output.acceptance_criteria or len(spec_output.acceptance_criteria) == 0:
        missing_fields.append("acceptance_criteria (must have at least one)")

    if not spec_output.test_scenarios or len(spec_output.test_scenarios) == 0:
        missing_fields.append("test_scenarios (must have at least one)")

    # Check contract exists (behavior is optional since parser may not extract it perfectly)
    # Just check that contract object exists
    if not spec_output.contract:
        missing_fields.append("contract (must be defined)")

    return (len(missing_fields) == 0, missing_fields)


def spec_matches_request(spec_output: SpecificationOutput, user_request: str) -> bool:
    """Check if specification appears to address the user's request.

    This is a simple heuristic check - looks for key terms from the request
    in the specification title and description.

    Args:
        spec_output: Generated specification
        user_request: Original user request

    Returns:
        True if spec appears to match the request
    """
    # Extract key terms (words longer than 4 characters, excluding common words)
    common_words = {
        "with",
        "that",
        "have",
        "this",
        "from",
        "would",
        "should",
        "could",
        "need",
        "want",
        "like",
    }

    request_words = {
        word.lower() for word in re.findall(r"\b\w{4,}\b", user_request) if word.lower() not in common_words
    }

    # Check if key terms appear in title or description
    spec_text = (spec_output.title + " " + spec_output.description).lower()

    # At least 40% of key terms should appear in the spec
    matches = sum(1 for word in request_words if word in spec_text)

    if len(request_words) == 0:
        return True  # No meaningful words to match

    match_ratio = matches / len(request_words)
    return match_ratio >= 0.4


def find_specs_in_quaestor_folder(base_path: Path, status: str = "active") -> list[Path]:
    """Find specification files in the .quaestor folder.

    Args:
        base_path: Base project path
        status: Specification status folder (draft, active, completed, archived)

    Returns:
        List of paths to specification files
    """
    specs_folder = base_path / ".quaestor" / "specs" / status
    if not specs_folder.exists():
        return []

    return sorted(specs_folder.glob("spec-*.md"))
