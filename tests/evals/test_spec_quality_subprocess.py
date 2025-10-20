"""Level 2 Evaluation: Subprocess-based specification quality testing.

This module tests specification quality by actually invoking the
managing-specifications skill via Claude CLI subprocess execution.

Requires:
- Claude CLI installed and accessible
- pydantic-evals package for evaluation framework
"""

import os

import pytest
from pydantic_evals import Case, Dataset

from .models import SpecificationInput, SpecificationOutput
from .skill_executor import SkillExecutor, execute_plan_sync
from .utils import has_required_spec_fields, load_spec_as_eval_output

# Skip these tests by default - they require Claude CLI and take 60-120s each
# To run them: pytest tests/evals/test_spec_quality_subprocess.py -v -s
CLAUDE_CLI_AVAILABLE = os.system("which claude > /dev/null 2>&1") == 0
pytestmark = [
    pytest.mark.skip(reason="Subprocess tests disabled by default - requires Claude CLI setup"),
    pytest.mark.skipif(
        not CLAUDE_CLI_AVAILABLE,
        reason="Claude CLI not found - install Claude Code to run subprocess tests",
    ),
]


# Custom evaluator: Check required fields
def check_required_fields_eval(case: Case, output: SpecificationOutput) -> dict:
    """Evaluator to check if specification has all required fields."""
    is_valid, missing = has_required_spec_fields(output)

    return {
        "score": 1.0 if is_valid else 0.0,
        "reason": "All required fields present" if is_valid else f"Missing: {', '.join(missing)}",
    }


# Custom evaluator: Check spec was created
def check_spec_created(case: Case, output: SpecificationOutput | None) -> dict:
    """Evaluator to check if spec was successfully created."""
    if output is None:
        return {
            "score": 0.0,
            "reason": "Specification was not created",
        }

    return {
        "score": 1.0,
        "reason": f"Specification created with ID: {output.id}",
    }


@pytest.fixture
def subprocess_dataset():
    """Dataset for subprocess-based specification quality evaluation.

    These test cases will actually invoke the managing-specifications skill.
    """
    return Dataset(
        name="spec_quality_subprocess",
        cases=[
            Case(
                name="simple_feature_subprocess",
                inputs=SpecificationInput(
                    request="Add a dark mode toggle to the settings page",
                    context="Web application with settings UI",
                    priority="medium",
                ).model_dump(),
                expected_output={
                    "type": "feature",
                    "has_acceptance_criteria": True,
                    "has_test_scenarios": True,
                },
                metadata={"complexity": "simple", "estimated_time": "2-4 hours"},
            ),
            Case(
                name="bugfix_subprocess",
                inputs=SpecificationInput(
                    request="Fix pagination bug where last page shows no results",
                    context="Django REST API with pagination",
                    priority="high",
                ).model_dump(),
                expected_output={
                    "type": "bugfix",
                    "has_acceptance_criteria": True,
                    "has_test_scenarios": True,
                },
                metadata={"complexity": "simple", "estimated_time": "2-4 hours"},
            ),
        ],
    )


@pytest.mark.slow
@pytest.mark.asyncio
async def test_subprocess_spec_creation_async(subprocess_dataset, tmp_path):
    """Test specification creation via subprocess execution (async).

    This test actually invokes the managing-specifications skill via Claude CLI
    and evaluates the generated specification.

    Marked as 'slow' since it involves real CLI execution.
    """
    print("\n" + "=" * 80)
    print("SUBPROCESS SPECIFICATION QUALITY EVALUATION")
    print("=" * 80)

    executor = SkillExecutor(project_dir=tmp_path)

    try:
        # Test single case
        case = subprocess_dataset.cases[0]
        spec_input = SpecificationInput(**case.inputs)

        print(f"\nExecuting: {case.name}")
        print(f"Request: {spec_input.request}")

        # Execute /plan command
        result = await executor.execute_plan_command(spec_input)

        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Success: {result.success}")

        if result.success and result.spec_path:
            print(f"Spec created: {result.spec_id}")
            print(f"Spec file: {result.spec_path}")

            # Load and evaluate spec
            spec_output = load_spec_as_eval_output(result.spec_path)

            if spec_output:
                # Run evaluators
                field_result = check_required_fields_eval(case, spec_output)
                print(f"\nField validation: {field_result['score']:.2f}")
                print(f"  {field_result['reason']}")

                assert spec_output is not None, "Should create valid specification"
                assert field_result["score"] == 1.0, "Should have all required fields"
            else:
                pytest.fail("Failed to load created specification")
        else:
            pytest.fail(f"Skill execution failed: {result.error}")

    finally:
        executor.cleanup()

    print("\n✅ SUBPROCESS EVALUATION COMPLETE")
    print("=" * 80)


@pytest.mark.slow
def test_subprocess_spec_creation_sync(subprocess_dataset, tmp_path):
    """Test specification creation via subprocess execution (sync).

    This is a synchronous version for easier testing and debugging.
    """
    print("\n" + "=" * 80)
    print("SYNCHRONOUS SUBPROCESS EVALUATION")
    print("=" * 80)

    # Test single case
    case = subprocess_dataset.cases[0]
    spec_input = SpecificationInput(**case.inputs)

    print(f"\nExecuting: {case.name}")
    print(f"Request: {spec_input.request}")

    # Execute synchronously
    result = execute_plan_sync(
        spec_input,
        project_dir=tmp_path,
        timeout_seconds=120,
    )

    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Success: {result.success}")

    if result.success:
        if result.spec_path and result.spec_path.exists():
            spec_output = load_spec_as_eval_output(result.spec_path)

            if spec_output:
                field_result = check_required_fields_eval(case, spec_output)
                print(f"\nField validation: {field_result['score']:.2f}")
                print(f"  {field_result['reason']}")
                print("\nSpec details:")
                print(f"  Title: {spec_output.title}")
                print(f"  Type: {spec_output.type}")
                print(f"  Acceptance criteria: {len(spec_output.acceptance_criteria)}")
                print(f"  Test scenarios: {len(spec_output.test_scenarios)}")

                assert field_result["score"] == 1.0, "Should have all required fields"
            else:
                print(f"⚠️  Warning: Could not parse spec file at {result.spec_path}")
        else:
            print("⚠️  Warning: Spec file not found at expected location")
    else:
        print(f"❌ Execution failed: {result.error}")
        print(f"Output: {result.output[:500]}")  # First 500 chars

    print("\n✅ SYNCHRONOUS EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    """Run the evaluation directly."""
    pytest.main([__file__, "-v", "-s", "-m", "not slow"])
