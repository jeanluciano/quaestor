"""Test template population with proper data."""

import tempfile
from pathlib import Path

import pytest

from quaestor.core.template_engine import get_project_data, process_template


class TestTemplatePopulation:
    """Test that templates are properly populated with project data."""

    def test_validation_template_population_removed(self, tmp_path):
        """REMOVED: validation.md template was removed from the project."""
        pytest.skip("validation.md template was removed")
        return

    def _test_validation_template_population(self, tmp_path):
        """Test VALIDATION.md template is populated correctly."""
        # Create a minimal Python project
        (tmp_path / "setup.py").write_text("# Setup file")
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "__init__.py").touch()
        (tmp_path / "src" / "main.py").write_text("print('hello')")

        # Get project data
        project_data = get_project_data(tmp_path)

        # Create a minimal validation template
        template_content = """# Validation
- **Linting**: {{linter_config}}
- **Type Checking**: {{type_checker}}
- **Test Coverage**: Minimum {{test_coverage_threshold}}%
- **Security Scanner**: {{security_scanner}}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
            tf.write(template_content)
            template_path = Path(tf.name)

        try:
            # Process template
            result = process_template(template_path, project_data)

            # Check that placeholders were replaced
            assert "{{linter_config}}" not in result
            assert "{{type_checker}}" not in result
            assert "{{test_coverage_threshold}}" not in result
            assert "{{security_scanner}}" not in result

            # Check specific values for Python project
            assert "ruff check ." in result
            assert "mypy ." in result
            assert "80%" in result
            assert "bandit -r src/" in result
        finally:
            template_path.unlink()

    def test_automation_template_population_removed(self, tmp_path):
        """REMOVED: automation.md template was removed from the project."""
        pytest.skip("automation.md template was removed")
        return

    def _test_automation_template_population(self, tmp_path):
        """Test AUTOMATION.md template is populated correctly."""
        # Create a minimal JavaScript project
        (tmp_path / "package.json").write_text('{"name": "test"}')

        # Get project data
        project_data = get_project_data(tmp_path)

        # Create a minimal automation template
        template_content = """# Automation
## Hook Configuration
```json
{{hook_configuration}}
```

## Scripts
- Pre-edit: {{pre_edit_script}}
- Post-edit: {{post_edit_script}}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
            tf.write(template_content)
            template_path = Path(tf.name)

        try:
            # Process template
            result = process_template(template_path, project_data)

            # Check that placeholders were replaced
            assert "{{hook_configuration}}" not in result
            assert "{{pre_edit_script}}" not in result
            assert "{{post_edit_script}}" not in result

            # Check hook configuration is present
            assert ".quaestor/hooks/validation/research_enforcer.py" in result
            assert ".quaestor/hooks/workflow/research_tracker.py" in result

            # Check scripts are present
            assert "npx eslint ." in result  # JavaScript linter
            assert "npx prettier --write ." in result  # JavaScript formatter
        finally:
            template_path.unlink()

    def test_unknown_project_type_defaults(self, tmp_path):
        """Test templates work with unknown project types."""
        # Create empty directory (unknown project type)

        # Get project data
        project_data = get_project_data(tmp_path)

        # Create template with various placeholders
        template_content = """# Project Info
Type: {{project_type}}
Linter: {{linter_config}}
Coverage: {{test_coverage_threshold}}%
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
            tf.write(template_content)
            template_path = Path(tf.name)

        try:
            # Process template
            result = process_template(template_path, project_data)

            # Check no placeholders remain
            assert "{{" not in result
            assert "}}" not in result

            # Check defaults are used
            assert "Type: unknown" in result
            assert "# Configure your linter" in result
            assert "Coverage:" in result  # Should have some coverage value
        finally:
            template_path.unlink()

    def test_all_validation_placeholders_have_values_removed(self):
        """REMOVED: validation.md template was removed from the project."""
        pytest.skip("validation.md template was removed")
        return

    def _test_all_validation_placeholders_have_values(self):
        """Ensure all placeholders in validation.md have mappings."""
        # List of all placeholders used in validation.md
        validation_placeholders = [
            "linter_config",
            "type_checker",
            "test_coverage_threshold",
            "security_scanner",
            "sast_tools",
            "vulnerability_scanner",
            "max_build_time",
            "max_bundle_size",
            "memory_threshold",
            "performance_budget",
            "pre_commit_hooks",
            "ci_pipeline_config",
            "test_coverage_target",
            "current_coverage",
            "max_duplication",
            "current_duplication",
            "max_debt_hours",
            "current_debt",
            "max_bugs_per_kloc",
            "current_bug_density",
        ]

        # Get mappings for a Python project
        from quaestor.core.template_engine import _create_template_mappings

        mappings = _create_template_mappings({"lint_command": "test"}, "python")

        # Check all placeholders have values
        for placeholder in validation_placeholders:
            assert placeholder in mappings, f"Missing mapping for {placeholder}"
            assert mappings[placeholder] is not None

    def test_all_automation_placeholders_have_values_removed(self):
        """REMOVED: automation.md template was removed from the project."""
        pytest.skip("automation.md template was removed")
        return

    def _test_all_automation_placeholders_have_values(self):
        """Ensure all placeholders in automation.md have mappings."""
        # List of all placeholders used in automation.md
        automation_placeholders = [
            "hook_configuration",
            "pre_edit_script",
            "post_edit_script",
            "auto_commit_rules",
            "branch_rules",
            "pr_automation",
            "specification_automation",
            "context_rules",
            "rule_enforcement",
            "template_automation",
            "doc_automation",
            "retry_configuration",
            "fallback_behavior",
            "error_handling_pattern",
            "logging_config",
            "monitoring_setup",
            "debug_configuration",
        ]

        # Get mappings
        from quaestor.core.template_engine import _create_template_mappings

        mappings = _create_template_mappings({}, "unknown")

        # Check all placeholders have values
        for placeholder in automation_placeholders:
            assert placeholder in mappings, f"Missing mapping for {placeholder}"
            assert mappings[placeholder] is not None
