# Evaluation Framework for Quaestor

This document explains how to use the Pydantic AI evaluation framework to test and benchmark Quaestor's skills, commands, and agents.

## Overview

The evaluation framework uses [Pydantic AI Evals](https://ai.pydantic.dev/evals/) to systematically test the quality and success rate of:

1. **Specification Quality** - How well the `managing-specifications` skill creates specs
2. **Implementation Success** - Whether the `implementing-features` skill delivers working code
3. **End-to-End Workflows** - Complete request → spec → implementation cycles

## Quick Start

### Installation

The evaluation tests use the existing Quaestor dependencies (no additional packages required):

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

**Note:** `pydantic-evals` was removed since all tests now use real file-based evaluation.
Future automation (Level 2) may reintroduce it for subprocess-based skill execution.

### Running Evaluations

Run all evaluation tests:

```bash
# Run all evaluations
pytest tests/evals/ -v

# Run specific evaluation
pytest tests/evals/test_spec_quality.py -v
pytest tests/evals/test_implementation.py -v
pytest tests/evals/test_e2e_workflow.py -v
```

Run with detailed output:

```bash
pytest tests/evals/test_spec_quality.py -v -s
```

## Evaluation Structure

### Directory Layout

```
tests/evals/
├── __init__.py
├── models.py                    # Pydantic models for inputs/outputs
├── utils.py                     # Helper functions
├── test_spec_quality.py         # Eval #1: Specification quality
├── test_implementation.py       # Eval #2: Implementation success
├── test_e2e_workflow.py         # Eval #3: End-to-end workflow
└── datasets/
    ├── spec_quality.yaml        # 5 test cases for spec quality
    ├── implementation_success.yaml  # 4 test cases for implementation
    └── e2e_workflow.yaml        # 3 test cases for complete workflows
```

## Evaluation 1: Specification Quality

**Purpose:** Evaluate whether specifications created by `managing-specifications` are complete, clear, and actionable.

**Test Cases:** 5 scenarios
- Simple feature request
- Complex multi-component feature
- Bug fix
- Refactoring task
- Ambiguous request (challenging)

**Evaluators:**
- `check_required_fields` - Validates all mandatory fields present
- `check_matches_request` - Verifies spec addresses user request

**Running:**
```bash
pytest tests/evals/test_spec_quality.py -v -s
```

**Dataset:** `tests/evals/datasets/spec_quality.yaml`

## Evaluation 2: Implementation Success

**Purpose:** Evaluate whether implementations complete acceptance criteria with passing tests.

**Test Cases:** 4 scenarios
- Simple feature implementation
- Complex multi-file feature
- Bug fix with reproduction
- Refactoring with quality improvements

**Evaluators:**
- `check_tests_passing` - All tests must pass
- `check_acceptance_criteria` - Criteria completion percentage
- `check_progress_completion` - Task progress percentage
- `check_files_changed` - Files were modified

**Running:**
```bash
pytest tests/evals/test_implementation.py -v -s
```

**Dataset:** `tests/evals/datasets/implementation_success.yaml`

## Evaluation 3: End-to-End Workflow

**Purpose:** Measure complete workflow success rate from user request to working feature.

**Test Cases:** 3 real-world scenarios
- Simple feature (4 hour estimate)
- Medium bug fix (3 hour estimate)
- Complex feature (56 hour estimate)

**Evaluators:**
- `check_binary_success` - Did workflow complete?
- `check_all_components` - All stages (spec, impl, tests) completed?
- `check_time_accuracy` - Actual vs estimated time accuracy

**Running:**
```bash
pytest tests/evals/test_e2e_workflow.py -v -s
```

**Dataset:** `tests/evals/datasets/e2e_workflow.yaml`

## CI/CD Integration

The evaluation tests run automatically on:
- Pull requests to `main` or `develop`
- Pushes to `main`
- Manual workflow dispatch

**GitHub Actions Workflow:** `.github/workflows/evals.yml`

**Viewing Results:**
1. Go to GitHub Actions tab
2. Select "Evaluation Tests" workflow
3. View job summary for results
4. Download artifacts for detailed logs

## Understanding Results

### Scores

Each evaluator returns a score between 0.0 and 1.0:
- **1.0** - Perfect, meets all criteria
- **0.75-0.99** - Good, minor issues
- **0.5-0.74** - Fair, several improvements needed
- **<0.5** - Poor, major issues

### Success Rate

For end-to-end workflows:
- **80%+** - Excellent reliability
- **66-79%** - Good, some improvements needed
- **50-65%** - Fair, significant issues
- **<50%** - Poor, major problems

## Customizing Evaluations

### Adding New Test Cases

Edit the YAML dataset files:

```yaml
# tests/evals/datasets/spec_quality.yaml
cases:
  - name: my_new_test
    input_data:
      request: "Your feature request here"
      context: "Additional context"
      priority: "medium"
    expected_output:
      type: "feature"
      status: "draft"
    metadata:
      complexity: "simple"
```

### Creating Custom Evaluators

Add evaluator functions to test files:

```python
def my_custom_evaluator(case: Case, output: SpecificationOutput) -> dict:
    """Custom evaluation logic."""
    score = 1.0 if condition else 0.0
    return {
        "score": score,
        "reason": "Explanation of score"
    }

# Add to evaluators list
evaluators = [
    my_custom_evaluator,
    # ... other evaluators
]
```

## Best Practices

### When to Run Evaluations

1. **Before releases** - Verify quality gates pass
2. **After major changes** - Ensure no regressions
3. **Periodic benchmarking** - Track improvement over time
4. **When adding skills** - Create evaluations for new skills

### Interpreting Results

- **Don't rely on single runs** - Run multiple times for confidence
- **Compare trends** - Track scores over time, not absolute values
- **Investigate failures** - Low scores indicate areas for improvement
- **Review evaluator output** - Understand why scores are given

### Real Integration (Level 1 - File-Based Testing)

**✅ IMPLEMENTED:** The evaluation framework now supports testing with real specification files!

**New test functions available:**
- `test_spec_quality_with_real_files` - Tests real specs (good, poor, edge case)
- `test_spec_quality_dataset_integration` - Integrates real specs with Pydantic Evals
- `test_implementation_with_real_spec` - Tracks progress on active specifications
- `test_implementation_result_validation` - Validates completed implementations
- `test_implementation_simulation` - Simulates full workflow with file changes

**How to use:**

1. **Test with fixture specs:**
   ```bash
   # Run tests with pre-created spec fixtures
   pytest tests/evals/test_spec_quality.py::test_spec_quality_with_real_files -v -s
   pytest tests/evals/test_implementation.py::test_implementation_with_real_spec -v -s
   ```

2. **Test with your own specs:**
   ```python
   # In your test
   def test_my_spec():
       spec_path = Path(".quaestor/specs/draft/spec-XXXXXX.md")
       spec = load_spec_as_eval_output(spec_path)
       # Run evaluators
   ```

3. **Create specs manually or via Quaestor:**
   - Use `/plan` in Claude Code to create specs
   - Spec files appear in `.quaestor/specs/draft/`
   - Tests can load and evaluate these files

**Fixtures available:**
- `good_quality_spec` - High-quality spec that should score well
- `poor_quality_spec` - Poor quality spec for baseline comparison
- `edge_case_spec` - Complex spec with many criteria
- `active_spec_with_progress` - Partially complete spec (3/8 done)
- `completed_spec` - Fully completed spec (8/8 done)
- `temp_project` - Temporary project with `.quaestor/` structure
- `temp_git_project` - Git-initialized project for workflow testing

## Level 2: Subprocess Execution (NEW!)

**✅ IMPLEMENTED** - Run real skills via Claude CLI!

### Quick Start

```bash
# Install pydantic-ai
pip install -e ".[dev]"

# Ensure Claude CLI is available
claude --version

# Run subprocess tests (slow)
pytest tests/evals/test_spec_quality_subprocess.py::test_subprocess_spec_creation_sync -v -s
```

### Components

**1. SkillExecutor** (`skill_executor.py`)
- Invokes Claude CLI via subprocess
- Async execution with polling
- Timeout handling
- Captures spec files created

**2. OutputParser** (`output_parser.py`)
- Extracts spec IDs from Claude output
- Parses file paths, progress, test results
- Extracts metadata

**3. Test Suite** (`test_spec_quality_subprocess.py`)
- Real `/plan` command execution
- Pydantic Evals integration
- Deterministic evaluators
- Async and sync test modes

### Usage Examples

**Synchronous execution:**
```python
from tests.evals.skill_executor import execute_plan_sync
from tests.evals.models import SpecificationInput

result = execute_plan_sync(
    SpecificationInput(
        request="Add dark mode toggle",
        context="Settings page",
        priority="medium"
    ),
    timeout_seconds=120
)

if result.success:
    spec = load_spec_as_eval_output(result.spec_path)
```

**Async execution:**
```python
executor = SkillExecutor(project_dir=tmp_path)
result = await executor.execute_plan_command(spec_input)
```

**With Pydantic Evals:**
```python
from pydantic_ai.evals import Dataset, Experiment

experiment = Experiment(
    dataset=subprocess_dataset,
    task=create_spec_via_subprocess,
    evaluators=[
        check_spec_created,
        check_required_fields,
    ],
)

results = experiment.evaluate_sync()
```

### Future Enhancements (Level 3-4)

**Level 3 - File-Based Communication:** (Not yet implemented)
- Test harness coordinates with Claude Code via file system
- Skills watch for test input files
- Results written to test output directory

**Level 4 - Integration Test Framework:** (Not yet implemented)
- Add non-interactive mode to skills
- Skills read structured inputs from files
- Pure integration testing with full automation

## Extending the Framework

### Adding New Evaluations

1. Create new test file: `tests/evals/test_your_eval.py`
2. Define input/output models in `models.py`
3. Create dataset YAML: `tests/evals/datasets/your_eval.yaml`
4. Implement evaluators and experiment
5. Add to CI workflow

### Integration with Real Workflows

**Current approach (Level 1 - File-Based):**

```python
# Load and evaluate real specification files
def test_real_spec():
    spec_path = Path(".quaestor/specs/draft/spec-20250101-120000.md")
    spec = load_spec_as_eval_output(spec_path)

    # Run evaluators
    is_valid, missing = has_required_spec_fields(spec)
    assert is_valid
```

**Current approach (Level 2 - Subprocess - ✅ IMPLEMENTED):**

```python
# Invoke skills programmatically via subprocess
from tests.evals.skill_executor import execute_plan_sync

def real_spec_creation(input_data: dict) -> SpecificationOutput:
    """Invoke real managing-specifications skill via subprocess."""
    spec_input = SpecificationInput(**input_data)

    # Execute /plan command via Claude CLI
    result = execute_plan_sync(
        spec_input,
        project_dir=tmp_path,
        timeout_seconds=120
    )

    # Load and return the created spec
    if result.success and result.spec_path:
        return load_spec_as_eval_output(result.spec_path)

    return None
```

## Troubleshooting

### Import Errors

```bash
# Ensure pydantic-ai is installed
pip install pydantic-ai[openai]>=0.0.47
```

### Timeout Issues

Increase timeout in pytest.ini:

```toml
[tool.pytest.ini_options]
timeout = 120  # 2 minutes per test
```

## Resources

- [Pydantic AI Evals Documentation](https://ai.pydantic.dev/evals/)
- [Quaestor Skills Documentation](../src/quaestor/skills/)
- [Quaestor Commands Documentation](../src/quaestor/commands/)

## Support

For issues or questions:
- Open an issue on GitHub
- Review existing evaluation tests for examples
- Check Pydantic AI documentation for eval framework details
