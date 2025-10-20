"""
Tests for the Markdown specification parser.
"""

from textwrap import dedent

import pytest

from quaestor.core.markdown_spec import (
    MarkdownSpecParser,
    SpecPriority,
    SpecStatus,
    SpecType,
    convert_yaml_to_markdown,
)


class TestMarkdownSpecParser:
    """Test the Markdown specification parser."""

    def test_parse_minimal_spec(self):
        """Test parsing a minimal valid specification."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            created_at: 2024-01-15T10:00:00Z
            updated_at: 2024-01-15T10:00:00Z
            ---

            # Test Specification

            ## Description
            This is a test specification.

            ## Rationale
            We need this for testing.
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.id == "spec-test-001"
        assert spec.type == SpecType.FEATURE
        assert spec.status == SpecStatus.DRAFT
        assert spec.priority == SpecPriority.HIGH
        assert spec.title == "Test Specification"
        assert spec.description == "This is a test specification."
        assert spec.rationale == "We need this for testing."

    def test_parse_full_spec(self):
        """Test parsing a complete specification with all sections."""
        content = dedent("""
            ---
            id: spec-auth-001
            type: feature
            status: active
            priority: critical
            created_at: 2024-01-15T10:00:00Z
            updated_at: 2024-01-16T14:30:00Z
            branch: feat/auth
            ---

            # User Authentication System

            ## Description
            Implement secure user authentication with JWT tokens.

            ## Rationale
            Modern applications require robust authentication.

            ## Dependencies
            - **Requires**: database-setup, crypto-lib
            - **Blocks**: user-profile, permissions
            - **Related**: session-management

            ## Contract

            ### Inputs
            - `username` (string): User email or username
            - `password` (string): User password

            ### Outputs
            - `token` (string): JWT access token
            - `refresh_token` (string): Refresh token

            ### Behavior
            - Validate credentials against database
            - Generate JWT with 24h expiration

            ### Constraints
            - Password must be at least 8 characters
            - Tokens must use RS256 algorithm

            ## Acceptance Criteria
            - [x] Users can login with valid credentials
            - [ ] Invalid credentials return 401 error
            - [x] Passwords are securely hashed
            - [ ] Tokens expire after 24 hours

            ## Test Scenarios

            ### Successful Login
            **Given**: Valid user credentials
            **When**: Login endpoint is called
            **Then**: JWT token is returned

            ### Invalid Password
            **Given**: Valid username, invalid password
            **When**: Login endpoint is called
            **Then**: 401 error is returned
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        # Check basic fields
        assert spec.id == "spec-auth-001"
        assert spec.type == SpecType.FEATURE
        assert spec.status == SpecStatus.ACTIVE
        assert spec.priority == SpecPriority.CRITICAL
        assert spec.branch == "feat/auth"

        # Check dependencies
        assert spec.dependencies["requires"] == ["database-setup", "crypto-lib"]
        assert spec.dependencies["blocks"] == ["user-profile", "permissions"]
        assert spec.dependencies["related"] == ["session-management"]

        # Check contract
        assert "username" in spec.contract["inputs"]
        assert spec.contract["inputs"]["username"]["type"] == "string"
        assert "token" in spec.contract["outputs"]
        assert len(spec.contract["behavior"]) == 2
        assert len(spec.contract["constraints"]) == 2

        # Check acceptance criteria
        assert len(spec.acceptance_criteria) == 4
        assert "[x]" in spec.acceptance_criteria[0]
        assert "[ ]" in spec.acceptance_criteria[1]

        # Check test scenarios
        assert len(spec.test_scenarios) == 2
        assert spec.test_scenarios[0]["name"] == "Successful Login"
        assert "Valid user credentials" in spec.test_scenarios[0]["given"]

    def test_parse_missing_frontmatter(self):
        """Test error handling for missing frontmatter."""
        content = dedent("""
            # Test Specification

            ## Description
            This has no frontmatter.
        """).strip()

        with pytest.raises(ValueError, match="No frontmatter found"):
            MarkdownSpecParser.parse(content)

    def test_parse_missing_required_fields(self):
        """Test forgiving parser with missing required fields (uses defaults)."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            ---

            # Test Specification
        """).strip()

        # Parser is forgiving - fills in defaults
        spec = MarkdownSpecParser.parse(content)
        assert spec.id == "spec-test-001"
        assert spec.status == SpecStatus.DRAFT  # default
        assert spec.priority == SpecPriority.MEDIUM  # default

    def test_parse_invalid_enum_values(self):
        """Test forgiving parser with invalid enum values (auto-corrects)."""
        content = dedent("""
            ---
            id: spec-test-001
            type: invalid_type
            status: draft
            priority: high
            ---

            # Test Specification
        """).strip()

        # Parser is forgiving - auto-corrects invalid types
        spec = MarkdownSpecParser.parse(content)
        assert spec.id == "spec-test-001"
        # Invalid type should be auto-corrected to a valid type (likely feature)
        assert spec.type in [SpecType.FEATURE, SpecType.BUGFIX, SpecType.REFACTOR]

    def test_parse_empty_sections(self):
        """Test parsing with empty or missing sections."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: low
            ---

            # Test Specification
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.description == ""
        assert spec.rationale == ""
        assert spec.dependencies == {"requires": [], "blocks": [], "related": []}
        assert spec.contract == {"inputs": {}, "outputs": {}, "behavior": [], "constraints": []}
        assert spec.acceptance_criteria == []
        assert spec.test_scenarios == []

    def test_parse_multiline_content(self):
        """Test parsing multiline content in sections."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: medium
            ---

            # Complex Feature

            ## Description
            This is a multiline description.
            It spans multiple lines.

            And even has paragraphs.

            ## Rationale
            Line 1 of rationale.
            Line 2 of rationale.
            Line 3 of rationale.
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert "multiple lines" in spec.description
        assert "paragraphs" in spec.description
        assert "Line 1" in spec.rationale
        assert "Line 3" in spec.rationale

    def test_timestamp_parsing(self):
        """Test various timestamp formats."""
        # ISO format with Z
        content1 = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            created_at: 2024-01-15T10:00:00Z
            ---
            # Test
        """).strip()

        spec1 = MarkdownSpecParser.parse(content1)
        assert spec1.created_at.year == 2024

        # ISO format with timezone
        content2 = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            created_at: 2024-01-15T10:00:00+00:00
            ---
            # Test
        """).strip()

        spec2 = MarkdownSpecParser.parse(content2)
        assert spec2.created_at.year == 2024

        # Date only format
        content3 = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            created_at: 2024-01-15
            ---
            # Test
        """).strip()

        spec3 = MarkdownSpecParser.parse(content3)
        assert spec3.created_at.year == 2024

    def test_parse_dependencies_variations(self):
        """Test different dependency format variations."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Test

            ## Dependencies
            - **Requires**: spec-001, spec-002
            - **Blocks**: spec-003
            - **Related**: spec-004, spec-005, spec-006
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert len(spec.dependencies["requires"]) == 2
        assert "spec-001" in spec.dependencies["requires"]
        assert "spec-002" in spec.dependencies["requires"]
        assert spec.dependencies["blocks"] == ["spec-003"]
        assert len(spec.dependencies["related"]) == 3

    def test_parse_acceptance_criteria_mixed(self):
        """Test parsing mixed checked/unchecked acceptance criteria."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: active
            priority: high
            ---

            # Test

            ## Acceptance Criteria
            - [x] First criterion (completed)
            - [ ] Second criterion (pending)
            - [x] Third criterion (completed)
            - [ ] Fourth criterion (pending)
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert len(spec.acceptance_criteria) == 4
        assert spec.acceptance_criteria[0].startswith("[x]")
        assert spec.acceptance_criteria[1].startswith("[ ]")
        assert spec.acceptance_criteria[2].startswith("[x]")
        assert spec.acceptance_criteria[3].startswith("[ ]")


class TestYamlToMarkdownConversion:
    """Test conversion from YAML to Markdown format."""

    def test_convert_minimal_spec(self):
        """Test converting a minimal YAML spec to Markdown."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "draft",
            "priority": "high",
            "title": "Test Feature",
            "description": "A simple test feature.",
            "rationale": "We need this for testing.",
        }

        markdown = convert_yaml_to_markdown(yaml_spec)

        assert "---" in markdown
        assert "id: spec-test-001" in markdown
        assert "# Test Feature" in markdown
        assert "## Description" in markdown
        assert "A simple test feature." in markdown
        assert "## Rationale" in markdown
        assert "We need this for testing." in markdown

    def test_convert_with_dependencies(self):
        """Test converting dependencies to Markdown format."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "active",
            "priority": "high",
            "title": "Test Feature",
            "dependencies": {"requires": ["spec-001", "spec-002"], "blocks": ["spec-003"], "related": ["spec-004"]},
        }

        markdown = convert_yaml_to_markdown(yaml_spec)

        assert "## Dependencies" in markdown
        assert "**Requires**: spec-001, spec-002" in markdown
        assert "**Blocks**: spec-003" in markdown
        assert "**Related**: spec-004" in markdown

    def test_convert_with_contract(self):
        """Test converting contract section to Markdown format."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "active",
            "priority": "high",
            "title": "API Feature",
            "contract": {
                "inputs": {
                    "username": {"type": "string", "description": "User identifier"},
                    "password": {"type": "string", "description": "User password"},
                },
                "outputs": {"token": {"type": "string", "description": "JWT token"}},
                "behavior": ["Validate credentials", "Generate token"],
                "constraints": ["Password min 8 chars", "Token expires in 24h"],
            },
        }

        markdown = convert_yaml_to_markdown(yaml_spec)

        assert "## Contract" in markdown
        assert "### Inputs" in markdown
        assert "`username` (string): User identifier" in markdown
        assert "### Outputs" in markdown
        assert "`token` (string): JWT token" in markdown
        assert "### Behavior" in markdown
        assert "- Validate credentials" in markdown
        assert "### Constraints" in markdown
        assert "- Password min 8 chars" in markdown

    def test_convert_with_acceptance_criteria(self):
        """Test converting acceptance criteria to checkbox format."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "active",
            "priority": "high",
            "title": "Test Feature",
            "acceptance_criteria": ["First criterion", "[x] Already checked criterion", "Third criterion"],
        }

        markdown = convert_yaml_to_markdown(yaml_spec)

        assert "## Acceptance Criteria" in markdown
        assert "- [ ] First criterion" in markdown
        assert "- [x] Already checked criterion" in markdown
        assert "- [ ] Third criterion" in markdown

    def test_convert_with_test_scenarios(self):
        """Test converting test scenarios to Markdown format."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "active",
            "priority": "high",
            "title": "Test Feature",
            "test_scenarios": [
                {
                    "name": "Happy Path",
                    "description": "Test the happy path",
                    "given": "Valid input",
                    "when": "Action is performed",
                    "then": "Expected result",
                },
                {
                    "name": "Error Case",
                    "given": "Invalid input",
                    "when": "Action is performed",
                    "then": "Error is returned",
                },
            ],
        }

        markdown = convert_yaml_to_markdown(yaml_spec)

        assert "## Test Scenarios" in markdown
        assert "### Happy Path" in markdown
        assert "Test the happy path" in markdown
        assert "**Given**: Valid input" in markdown
        assert "**When**: Action is performed" in markdown
        assert "**Then**: Expected result" in markdown
        assert "### Error Case" in markdown

    def test_roundtrip_conversion(self):
        """Test that conversion is reversible."""
        yaml_spec = {
            "id": "spec-test-001",
            "type": "feature",
            "status": "active",
            "priority": "high",
            "title": "Roundtrip Test",
            "description": "Testing roundtrip conversion.",
            "rationale": "Ensure data integrity.",
            "dependencies": {"requires": ["spec-001"], "blocks": [], "related": ["spec-002"]},
            "acceptance_criteria": ["Data is preserved", "Format is valid"],
        }

        # Convert to Markdown
        markdown = convert_yaml_to_markdown(yaml_spec)

        # Parse back
        spec = MarkdownSpecParser.parse(markdown)

        # Verify key fields
        assert spec.id == yaml_spec["id"]
        assert spec.type.value == yaml_spec["type"]
        assert spec.status.value == yaml_spec["status"]
        assert spec.priority.value == yaml_spec["priority"]
        assert spec.title == yaml_spec["title"]
        assert spec.description == yaml_spec["description"]
        assert spec.rationale == yaml_spec["rationale"]
        assert spec.dependencies["requires"] == yaml_spec["dependencies"]["requires"]
        assert spec.dependencies["related"] == yaml_spec["dependencies"]["related"]


class TestMarkdownSpecPerformance:
    """Test performance characteristics of the Markdown parser."""

    def test_parse_performance(self):
        """Test parsing performance."""
        import time

        content = dedent("""
            ---
            id: spec-perf-001
            type: feature
            status: active
            priority: high
            created_at: 2024-01-15T10:00:00Z
            updated_at: 2024-01-15T10:00:00Z
            ---

            # Performance Test Specification

            ## Description
            This is a longer description to test parsing performance.
            It contains multiple lines and paragraphs.

            The parser should handle this efficiently.

            ## Rationale
            Performance testing is critical for production systems.

            ## Dependencies
            - **Requires**: spec-001, spec-002, spec-003
            - **Blocks**: spec-004, spec-005
            - **Related**: spec-006, spec-007, spec-008, spec-009

            ## Contract

            ### Inputs
            - `param1` (string): First parameter
            - `param2` (integer): Second parameter
            - `param3` (boolean): Third parameter

            ### Outputs
            - `result` (object): Result object
            - `status` (string): Status message

            ## Acceptance Criteria
            - [ ] Criterion 1
            - [ ] Criterion 2
            - [ ] Criterion 3
            - [ ] Criterion 4
            - [ ] Criterion 5

            ## Test Scenarios

            ### Scenario 1
            **Given**: Setup condition
            **When**: Action taken
            **Then**: Expected result

            ### Scenario 2
            **Given**: Another setup
            **When**: Different action
            **Then**: Different result
        """).strip()

        # Parse and measure time
        start = time.perf_counter()
        result = MarkdownSpecParser.parse(content)
        duration = (time.perf_counter() - start) * 1000

        # Should complete in under 10ms
        assert duration < 10
        assert result.id == "spec-perf-001"

    def test_large_spec_performance(self):
        """Test parsing performance with a large specification."""
        import time

        # Generate a large spec
        criteria = [f"- [ ] Criterion {i}" for i in range(100)]
        scenarios = []
        for i in range(50):
            scenarios.append(f"""### Scenario {i}
**Given**: Setup for scenario {i}
**When**: Action for scenario {i}
**Then**: Result for scenario {i}""")

        content = f"""---
id: spec-large-001
type: feature
status: active
priority: high
---

# Large Specification

## Description
{"Large description. " * 100}

## Rationale
{"Large rationale. " * 100}

## Acceptance Criteria
{chr(10).join(criteria)}

## Test Scenarios
{chr(10).join(scenarios)}"""

        start = time.perf_counter()
        spec = MarkdownSpecParser.parse(content)
        duration = (time.perf_counter() - start) * 1000

        # Should parse even large specs in under 20ms
        assert duration < 20
        assert len(spec.acceptance_criteria) == 100


class TestTaskProgressTracking:
    """Test task progress tracking functionality."""

    def test_parse_basic_checkboxes(self):
        """Test parsing of standard checkbox formats."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Test Spec

            ## Tasks
            - [x] Completed task
            - [ ] Pending task
            - [?] Uncertain task
            - Regular list item (not counted)
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress is not None
        assert spec.task_progress.total == 3
        assert spec.task_progress.completed == 1
        assert spec.task_progress.pending == 1
        assert spec.task_progress.uncertain == 1
        assert spec.task_progress.completion_percentage == pytest.approx(33.33, rel=0.1)

    def test_acceptance_criteria_progress(self):
        """Test that acceptance criteria checkboxes are tracked."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature

            ## Acceptance Criteria
            - [x] User can login
            - [x] Password is hashed
            - [ ] Session persists
            - [ ] Logout works
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.total == 4
        assert spec.task_progress.completed == 2
        assert spec.task_progress.pending == 2
        assert spec.task_progress.completion_percentage == 50.0

    def test_empty_spec_progress(self):
        """Test spec with no tasks shows 100% complete."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature without tasks

            ## Description
            No checkboxes here.
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.total == 0
        assert spec.task_progress.completion_percentage == 100.0
        assert spec.task_progress.is_complete is True

    def test_case_insensitive_checked(self):
        """Test that [X] and [x] are both recognized."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            ## Tasks
            - [X] Capital X task
            - [x] Lowercase x task
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.completed == 2

    def test_whitespace_tolerance(self):
        """Test parser handles various whitespace formats."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            ## Tasks
            - [ ] Normal spacing
            -  [  ]  Extra spaces
            - [x]No space after
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.total >= 2  # At least the standard formats

    def test_mixed_sections_progress(self):
        """Test checkboxes across multiple sections are counted."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature

            ## Description
            Initial task:
            - [x] Research completed

            ## Acceptance Criteria
            - [x] Core feature works
            - [ ] Edge cases handled

            ## Test Scenarios
            ### Unit Tests
            - [x] Basic test written
            - [?] Advanced test uncertain
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.total == 5
        assert spec.task_progress.completed == 3
        assert spec.task_progress.pending == 1
        assert spec.task_progress.uncertain == 1
        assert spec.task_progress.completion_percentage == 60.0

    def test_no_tasks_in_acceptance_criteria(self):
        """Test acceptance criteria without checkbox format."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature

            ## Acceptance Criteria
            - User can login
            - Password is secure
            - Session persists
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        assert spec.task_progress.total == 0
        assert spec.task_progress.is_complete is True

    def test_progress_with_nested_tasks(self):
        """Test nested checkbox tasks are counted correctly."""
        content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature

            ## Tasks
            - [x] Main task completed
              - [x] Subtask 1 done
              - [ ] Subtask 2 pending
            - [ ] Another main task
              - [?] Uncertain subtask
        """).strip()

        spec = MarkdownSpecParser.parse(content)

        # Should count all checkboxes regardless of nesting
        assert spec.task_progress.total == 5
        assert spec.task_progress.completed == 2
        assert spec.task_progress.pending == 2
        assert spec.task_progress.uncertain == 1
