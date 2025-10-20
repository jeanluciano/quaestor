"""Evaluation tests for implementation success.

This module tests whether the implementing-features skill successfully
implements specifications with passing tests and met acceptance criteria.
"""

import pytest

from .models import ImplementationInput, ImplementationOutput
from .utils import calculate_spec_progress, count_acceptance_criteria_met

# Note: These evaluator functions are placeholders for future pydantic-ai integration.
# The actual tests below use direct file-based evaluation without the pydantic-ai framework.


# Custom evaluator: Check tests passing
def check_tests_passing(case, output: ImplementationOutput) -> dict:
    """Evaluator to verify all tests pass."""
    return {
        "score": 1.0 if output.tests_passing else 0.0,
        "reason": "All tests passing" if output.tests_passing else "Some tests failing",
    }


# Custom evaluator: Check acceptance criteria completion
def check_acceptance_criteria(case, output: ImplementationOutput) -> dict:
    """Evaluator to verify acceptance criteria are met."""
    input_data = ImplementationInput(**case.input_data)
    expected_count = len(input_data.acceptance_criteria)
    actual_count = len(output.acceptance_criteria_met)

    score = actual_count / expected_count if expected_count > 0 else 0.0

    return {
        "score": score,
        "reason": f"{actual_count}/{expected_count} acceptance criteria met",
    }


# Custom evaluator: Check progress completion
def check_progress_completion(case, output: ImplementationOutput) -> dict:
    """Evaluator to verify implementation progress is complete."""
    is_complete = output.progress_percentage >= 90.0  # Allow 10% margin

    return {
        "score": 1.0 if is_complete else output.progress_percentage / 100.0,
        "reason": f"{output.progress_percentage:.1f}% complete",
    }


# Custom evaluator: Check files were modified
def check_files_changed(case, output: ImplementationOutput) -> dict:
    """Evaluator to verify implementation modified files."""
    has_changes = len(output.files_changed) > 0

    return {
        "score": 1.0 if has_changes else 0.0,
        "reason": (f"{len(output.files_changed)} files modified" if has_changes else "No files modified"),
    }


# Note: Mock-based tests removed - all tests now use real specification files
# See test_implementation_with_real_spec(), test_implementation_result_validation(),
# and test_implementation_simulation() for examples of evaluating actual implementations


def test_implementation_with_real_spec(active_spec_with_progress, temp_git_project):
    """Test implementation progress tracking with a real specification file.

    This test demonstrates Level 1 integration - checking implementation progress
    against an actual specification that's being actively worked on.

    Uses fixture-provided active spec with partial progress (3/8 criteria complete).
    """

    # Load the real specification

    # Calculate progress from the spec file
    progress = calculate_spec_progress(active_spec_with_progress)

    print("\n" + "=" * 80)
    print("TESTING IMPLEMENTATION PROGRESS WITH REAL SPEC")
    print("=" * 80)
    print(f"Spec file: {active_spec_with_progress.name}")
    print(f"Total tasks: {progress.total}")
    print(f"Completed tasks: {progress.completed}")
    print(f"Pending tasks: {progress.pending}")
    print(f"Completion percentage: {progress.completion_percentage:.1f}%")

    # Count acceptance criteria
    completed, total = count_acceptance_criteria_met(active_spec_with_progress)
    print(f"\nAcceptance Criteria: {completed}/{total} met")

    # Assertions based on the fixture we created
    assert progress.total > 0, "Should have tasks to track"
    assert progress.completed > 0, "Should have some completed tasks"
    assert progress.completed < progress.total, "Should not be 100% complete (active spec)"
    assert completed == 3, "Should have 3 criteria met (as defined in fixture)"
    assert total == 8, "Should have 8 total criteria (as defined in fixture)"

    # Check completion percentage is reasonable
    expected_percentage = (completed / total) * 100
    assert abs(progress.completion_percentage - expected_percentage) < 5.0, (
        f"Progress should be around {expected_percentage}%"
    )

    print("\n✅ REAL IMPLEMENTATION PROGRESS TRACKING WORKS")
    print("=" * 80)


def test_implementation_result_validation(completed_spec, temp_git_project):
    """Test validation of a completed implementation using a real spec file.

    This test demonstrates checking implementation results against
    a completed specification to verify all criteria were met.
    """

    # Load completed spec
    progress = calculate_spec_progress(completed_spec)
    completed, total = count_acceptance_criteria_met(completed_spec)

    print("\n" + "=" * 80)
    print("TESTING COMPLETED IMPLEMENTATION")
    print("=" * 80)
    print(f"Spec file: {completed_spec.name}")
    print(f"Acceptance Criteria: {completed}/{total} met")
    print(f"Completion: {progress.completion_percentage:.1f}%")

    # For a completed spec, all criteria should be met
    assert completed == total, "All acceptance criteria should be met in completed spec"
    assert progress.completion_percentage == 100.0, "Progress should be 100%"

    print("\n✅ COMPLETED IMPLEMENTATION VALIDATED")
    print("=" * 80)


def test_implementation_simulation(temp_git_project):
    """Simulate an implementation workflow and track progress.

    This test demonstrates a more realistic workflow where:
    1. We start with a spec
    2. Make file changes (simulated)
    3. Update acceptance criteria
    4. Track progress over time
    """
    import subprocess
    from datetime import datetime

    # Create a spec in the project
    specs_dir = temp_git_project / ".quaestor/specs/active"
    spec_id = f"spec-{datetime.now().strftime('%Y%m%d-%H%M%S')}-test"
    spec_path = specs_dir / f"{spec_id}.md"

    # Create a simple spec
    spec_content = f"""---
id: {spec_id}
title: Test implementation workflow
type: feature
status: active
priority: medium
---

# Test Implementation

## Acceptance Criteria

- [ ] Create main.py
- [ ] Create tests/test_main.py
- [ ] All tests pass
- [ ] Documentation added
"""

    spec_path.write_text(spec_content)

    # Initial state: 0% complete

    completed, total = count_acceptance_criteria_met(spec_path)
    assert completed == 0, "Should start with no criteria met"
    assert total == 4, "Should have 4 criteria"

    print("\n" + "=" * 80)
    print("SIMULATING IMPLEMENTATION WORKFLOW")
    print("=" * 80)
    print(f"Initial progress: {completed}/{total}")

    # Simulate implementation: create files
    (temp_git_project / "main.py").write_text("# Main implementation")
    tests_dir = temp_git_project / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "test_main.py").write_text("# Tests")

    # Check file changes via git
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=temp_git_project,
        capture_output=True,
        text=True,
    )
    changed_files = [line.split()[-1] for line in result.stdout.strip().split("\n") if line]

    print(f"\nFiles changed: {len(changed_files)}")
    for file in changed_files:
        print(f"  - {file}")

    # Update spec to mark criteria as complete
    updated_spec_content = spec_content.replace("- [ ] Create main.py", "- [x] Create main.py")
    updated_spec_content = updated_spec_content.replace(
        "- [ ] Create tests/test_main.py", "- [x] Create tests/test_main.py"
    )
    spec_path.write_text(updated_spec_content)

    # Check updated progress
    completed, total = count_acceptance_criteria_met(spec_path)
    print(f"\nUpdated progress: {completed}/{total}")

    assert completed == 2, "Should have 2 criteria met after updates"
    assert len(changed_files) >= 2, "Should have created at least 2 files"

    print("\n✅ WORKFLOW SIMULATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    """Run the evaluation directly."""
    pytest.main([__file__, "-v", "-s"])
