# Quaestor Evaluation Tests

This directory contains evaluation tests for Quaestor skills using [Pydantic AI Evals](https://ai.pydantic.dev/evals/).

## Quick Start

```bash
# Run all evaluations
pytest tests/evals/ -v

# Run with detailed output
pytest tests/evals/ -v -s

# Run specific evaluation
pytest tests/evals/test_spec_quality.py -v
```

## What's Evaluated

### 1. Specification Quality (`test_spec_quality.py`)
Tests whether the `managing-specifications` skill creates complete, clear, and actionable specifications.

**Test Cases:** 5 scenarios (simple feature, complex feature, bugfix, refactor, ambiguous request)

### 2. Implementation Success (`test_implementation.py`)
Tests whether the `implementing-features` skill successfully implements specifications with passing tests and met acceptance criteria.

**Test Cases:** 4 scenarios (simple feature, complex feature, bugfix, refactor)

### 3. End-to-End Workflow (`test_e2e_workflow.py`)
Tests the complete workflow from user request → specification → implementation → working feature.

**Test Cases:** 3 real-world scenarios (simple, medium, complex)

## File Structure

```
tests/evals/
├── README.md                    # This file
├── __init__.py
├── models.py                    # Pydantic models for inputs/outputs
├── utils.py                     # Helper functions
├── test_spec_quality.py         # Specification quality evaluation
├── test_implementation.py       # Implementation success evaluation
├── test_e2e_workflow.py         # End-to-end workflow evaluation
└── datasets/
    ├── spec_quality.yaml        # 5 test cases
    ├── implementation_success.yaml  # 4 test cases
    └── e2e_workflow.yaml        # 3 test cases
```

## Integration Status

✅ **Level 1 Integration Complete:** The evaluation framework now works with **real specification files**!

### What's Working Now

**Real File Testing:**
- Load and evaluate actual `.quaestor/specs/` files
- Test with pre-created fixture specs (good, poor, edge case)
- Track progress on active specifications
- Validate completed implementations
- Simulate workflows with file changes

**New Test Functions:**
```bash
# Test real specification quality
pytest tests/evals/test_spec_quality.py::test_spec_quality_with_real_files -v -s

# Test implementation progress tracking
pytest tests/evals/test_implementation.py::test_implementation_with_real_spec -v -s

# Simulate complete workflow
pytest tests/evals/test_implementation.py::test_implementation_simulation -v -s
```

### Available Fixtures

Use these fixtures in your tests (defined in `conftest.py`):

- `good_quality_spec` - High-quality spec for testing
- `poor_quality_spec` - Low-quality baseline
- `edge_case_spec` - Complex multi-criteria spec
- `active_spec_with_progress` - Partial completion (3/8 done)
- `completed_spec` - Fully completed (8/8 done)
- `temp_project` / `temp_git_project` - Test environments

### How to Use

**Option 1: Test with fixtures**
```python
def test_my_evaluation(good_quality_spec):
    spec = load_spec_as_eval_output(good_quality_spec)
    is_valid, missing = has_required_spec_fields(spec)
    assert is_valid
```

**Option 2: Test your own specs**
```python
def test_real_spec():
    spec_path = Path(".quaestor/specs/draft/spec-20250101-120000.md")
    spec = load_spec_as_eval_output(spec_path)
    # Run evaluations
```

**Option 3: Create specs via Quaestor**
1. Use `/plan` in Claude Code to create a spec
2. Spec saved to `.quaestor/specs/draft/`
3. Load and evaluate the spec file

### Future Automation

See `docs/EVALUATION.md` for plans to automate:
- Level 2: Subprocess execution of skills
- Level 3: File-based communication with Claude Code
- Level 4: Non-interactive skill testing mode

## Evaluators

Each test uses deterministic evaluators:

- **Field validation** - Check required fields are present
- **Progress tracking** - Calculate completion percentages
- **File change detection** - Verify implementation modified files
- **Quality comparison** - Compare good vs poor specs

**Note:** LLM-based judges were removed. All evaluations use deterministic code-based checks with real specification files.

## CI/CD Integration

These tests run automatically via GitHub Actions on:
- Pull requests to `main`/`develop`
- Pushes to `main`
- Manual workflow dispatch

See `.github/workflows/evals.yml` for configuration.

## Documentation

For full documentation, see: `docs/EVALUATION.md`

## Resources

- [Pydantic AI Evals](https://ai.pydantic.dev/evals/)
- [Evaluation Documentation](../../docs/EVALUATION.md)
- [Quaestor Skills](../../src/quaestor/skills/)
