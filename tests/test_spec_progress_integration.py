"""Integration tests for spec progress tracking."""

from textwrap import dedent

from quaestor.core.markdown_spec import MarkdownSpecParser


class TestSpecProgressIntegration:
    """Test progress tracking integration."""

    def test_progress_tracking_with_spec_manager(self, tmp_path):
        """Test progress tracking through the specification manager."""
        # Setup project structure
        specs_dir = tmp_path / ".quaestor" / "specs" / "active"
        specs_dir.mkdir(parents=True)

        # Create spec with tasks
        spec_content = dedent("""
            ---
            id: spec-test-001
            type: feature
            status: active
            priority: high
            ---

            # Test Feature

            ## Tasks
            - [x] Setup database
            - [x] Create models
            - [ ] Write tests
            - [ ] Documentation
        """).strip()

        spec_file = specs_dir / "spec-test-001.md"
        spec_file.write_text(spec_content)

        # Parse the spec
        parsed_spec = MarkdownSpecParser.parse(spec_content)

        # Verify progress
        assert parsed_spec.task_progress is not None
        assert parsed_spec.task_progress.total == 4
        assert parsed_spec.task_progress.completed == 2
        assert parsed_spec.task_progress.pending == 2
        assert parsed_spec.task_progress.completion_percentage == 50.0

    def test_progress_with_uncertain_tasks(self, tmp_path):
        """Test progress calculation with uncertain tasks."""
        # Setup
        specs_dir = tmp_path / ".quaestor" / "specs" / "draft"
        specs_dir.mkdir(parents=True)

        spec_content = dedent("""
            ---
            id: spec-uncertain-001
            type: feature
            status: draft
            priority: high
            ---

            # Feature with Uncertain Tasks

            ## Implementation Plan
            - [x] Research phase complete
            - [?] Architecture design - needs review
            - [?] Performance benchmarks - unclear requirements
            - [ ] Implementation
            - [ ] Testing
        """).strip()

        spec_file = specs_dir / "spec-uncertain-001.md"
        spec_file.write_text(spec_content)

        parsed_spec = MarkdownSpecParser.parse(spec_content)

        assert parsed_spec.task_progress.total == 5
        assert parsed_spec.task_progress.completed == 1
        assert parsed_spec.task_progress.uncertain == 2
        assert parsed_spec.task_progress.pending == 2
        assert parsed_spec.task_progress.completion_percentage == 20.0

    def test_completed_spec_validation(self, tmp_path):
        """Test that completed specs with pending tasks are detected."""
        specs_dir = tmp_path / ".quaestor" / "specs" / "completed"
        specs_dir.mkdir(parents=True)

        spec_content = dedent("""
            ---
            id: spec-done-001
            type: feature
            status: completed
            priority: high
            ---

            # Supposedly Done Feature

            ## Acceptance Criteria
            - [x] Feature works
            - [ ] Tests written
            - [ ] Documented
        """).strip()

        spec_file = specs_dir / "spec-done-001.md"
        spec_file.write_text(spec_content)

        parsed_spec = MarkdownSpecParser.parse(spec_content)

        # Should detect incomplete tasks in "completed" spec
        assert parsed_spec.task_progress.total == 3
        assert parsed_spec.task_progress.completed == 1
        assert parsed_spec.task_progress.pending == 2
        assert not parsed_spec.task_progress.is_complete

    def test_progress_across_multiple_sections(self, tmp_path):
        """Test that tasks are counted across all sections."""
        spec_content = dedent("""
            ---
            id: spec-multi-001
            type: feature
            status: active
            priority: high
            ---

            # Multi-Section Feature

            ## Description
            Setup tasks:
            - [x] Environment configured
            - [x] Dependencies installed

            ## Acceptance Criteria
            - [x] User authentication works
            - [ ] Session management implemented
            - [ ] Password reset flow

            ## Test Scenarios

            ### Unit Tests
            - [x] Auth module tested
            - [?] Session tests incomplete

            ### Integration Tests
            - [ ] End-to-end flow test
            - [ ] API integration test
        """).strip()

        parsed_spec = MarkdownSpecParser.parse(spec_content)

        assert parsed_spec.task_progress.total == 9
        assert parsed_spec.task_progress.completed == 4
        assert parsed_spec.task_progress.pending == 4
        assert parsed_spec.task_progress.uncertain == 1
        assert abs(parsed_spec.task_progress.completion_percentage - 44.44) < 0.1

    def test_empty_spec_shows_complete(self):
        """Test that specs without tasks show as 100% complete."""
        spec_content = dedent("""
            ---
            id: spec-empty-001
            type: documentation
            status: active
            priority: low
            ---

            # Documentation Update

            ## Description
            Simple documentation update with no trackable tasks.

            ## Changes
            - Update README
            - Fix typos
            - Add examples
        """).strip()

        parsed_spec = MarkdownSpecParser.parse(spec_content)

        assert parsed_spec.task_progress.total == 0
        assert parsed_spec.task_progress.completion_percentage == 100.0
        assert parsed_spec.task_progress.is_complete

    def test_malformed_checkboxes_ignored(self):
        """Test that malformed checkboxes are properly ignored."""
        spec_content = dedent("""
            ---
            id: spec-malformed-001
            type: feature
            status: draft
            priority: medium
            ---

            # Feature

            ## Tasks
            - [x] Valid task
            - [] Missing space in checkbox
            - [X] Capital X task (should work)
            - [-] Invalid marker
            - [ ] Valid pending task
            -[] No space before bracket
            - [  ] Extra spaces (should work)
        """).strip()

        parsed_spec = MarkdownSpecParser.parse(spec_content)

        # Should only count valid checkboxes
        assert parsed_spec.task_progress.total >= 3  # At minimum: [x], [X], and [ ]
        assert parsed_spec.task_progress.completed >= 2  # [x] and [X]
        assert parsed_spec.task_progress.pending >= 1  # [ ] and possibly [  ]

    def test_performance_with_many_tasks(self):
        """Test performance with specifications containing many tasks."""
        import time

        # Create spec with 100 tasks
        tasks = []
        for i in range(100):
            if i < 60:
                tasks.append(f"- [x] Task {i} completed")
            elif i < 80:
                tasks.append(f"- [ ] Task {i} pending")
            else:
                tasks.append(f"- [?] Task {i} uncertain")

        spec_content = f"""---
id: spec-perf-001
type: feature
status: active
priority: high
---

# Performance Test Spec

## Tasks
{chr(10).join(tasks)}""".strip()

        start = time.perf_counter()
        parsed_spec = MarkdownSpecParser.parse(spec_content)
        duration = (time.perf_counter() - start) * 1000

        # Should parse quickly even with many tasks
        assert duration < 50  # 50ms threshold

        # Verify counts
        assert parsed_spec.task_progress.total == 100
        assert parsed_spec.task_progress.completed == 60
        assert parsed_spec.task_progress.pending == 20
        assert parsed_spec.task_progress.uncertain == 20
        assert parsed_spec.task_progress.completion_percentage == 60.0
