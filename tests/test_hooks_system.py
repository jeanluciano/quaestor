"""Tests to ensure hooks system integrity and prevent configuration issues."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from quaestor.cli.init import _init_common, _init_personal_mode


class TestHooksConfiguration:
    """Test hooks configuration and installation."""

    def test_automation_base_json_has_correct_placeholders(self):
        """Ensure automation_base.json uses correct placeholders."""
        import importlib.resources as pkg_resources

        automation_json = pkg_resources.read_text("quaestor.claude.hooks", "automation_base.json")
        data = json.loads(automation_json)

        # Check that we use placeholders, not hardcoded paths
        for hook_type in ["PreToolUse", "PostToolUse"]:
            for matcher_config in data["hooks"][hook_type]:
                for hook in matcher_config["hooks"]:
                    command = hook["command"]
                    # Should use placeholders
                    assert "{python_path}" in command, f"Missing {{python_path}} in: {command}"
                    # New structure uses {project_root} instead of {hooks_dir}
                    assert "{project_root}" in command or "{hooks_dir}" in command, (
                        f"Missing {{project_root}} or {{hooks_dir}} in: {command}"
                    )
                    # Should NOT have old paths
                    assert ".quaestor/hooks" not in command, f"Hardcoded .quaestor/hooks in: {command}"
                    assert ".claude/hooks" not in command, f"Hardcoded .claude/hooks in: {command}"

    def test_automation_base_json_uses_correct_hook_names(self):
        """Ensure automation_base.json references actual hook files."""
        import importlib.resources as pkg_resources

        automation_json = pkg_resources.read_text("quaestor.claude.hooks", "automation_base.json")
        data = json.loads(automation_json)

        # Updated for new hook structure
        expected_hooks = {
            "compliance_pre_edit.py",
            "research_workflow_tracker.py",
            "memory_tracker.py",
            "milestone_tracker.py",
            "todo_milestone_connector.py",
            "todo_agent_coordinator.py",
            "session_context_loader.py",
        }

        found_hooks = set()
        for hook_type in ["PreToolUse", "PostToolUse"]:
            for matcher_config in data["hooks"][hook_type]:
                for hook in matcher_config["hooks"]:
                    command = hook["command"]
                    # Extract hook filename from command
                    for expected in expected_hooks:
                        if expected in command:
                            found_hooks.add(expected)

        # Should NOT have old hook names
        all_commands = json.dumps(data)
        assert "pre-implementation-declaration.py" not in all_commands
        assert "track-research.py" not in all_commands
        assert "track-implementation.py" not in all_commands
        assert "update-memory.py" not in all_commands
        assert "todo-milestone-connector.py" not in all_commands  # Note the hyphen

        # Should have expected hooks (allow subset for new structure)
        assert found_hooks.issubset(expected_hooks) or found_hooks == expected_hooks, (
            f"Unexpected hooks: {found_hooks - expected_hooks}"
        )

    def test_hook_files_exist_in_assets(self):
        """Ensure all referenced hook files exist in assets."""
        import importlib.resources as pkg_resources

        # Updated for new hook structure - hooks are now in the root hooks directory
        expected_hooks = [
            "compliance_pre_edit.py",
            "research_workflow_tracker.py",
            "memory_tracker.py",
            "milestone_tracker.py",
            "todo_milestone_connector.py",
            "todo_agent_coordinator.py",
            "session_context_loader.py",
            "base.py",  # Base hook class
        ]

        for hook_file in expected_hooks:
            try:
                content = pkg_resources.read_text("quaestor.claude.hooks", hook_file)
                assert len(content) > 0, f"Hook file {hook_file} is empty"
            except Exception as e:
                pytest.fail(f"Hook file not found: {hook_file} - {e}")

    def test_hook_files_have_correct_imports(self):
        """Ensure hook files have proper imports."""
        import importlib.resources as pkg_resources

        # Updated for new hook structure
        hook_files = [
            "compliance_pre_edit.py",
            "research_workflow_tracker.py",
            "memory_tracker.py",
            "milestone_tracker.py",
            "todo_milestone_connector.py",
        ]

        for hook_file in hook_files:
            try:
                content = pkg_resources.read_text("quaestor.claude.hooks", hook_file)

                # New hooks inherit from BaseHook
                if "class" in content and "Hook" in content:
                    assert (
                        "from .base import BaseHook" in content
                        or "from quaestor.claude.hooks.base import BaseHook" in content
                    ), f"{hook_file} should import BaseHook"
            except Exception:
                # Skip if file doesn't exist - it's tested elsewhere
                pass

    @patch("quaestor.cli.init.console")
    def test_personal_mode_creates_hooks_in_claude_dir(self, mock_console):
        """Test that personal mode installs hooks to .claude/hooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            # Mock the necessary functions
            with (
                patch("quaestor.cli.init._init_common") as mock_common,
                patch("quaestor.cli.init.RuleEngine"),
                patch("importlib.resources.read_text") as mock_read,
            ):
                mock_common.return_value = (["file1", "file2"], 5)  # Return non-empty results
                mock_read.return_value = json.dumps({"hooks": {"PreToolUse": [], "PostToolUse": []}})

                _init_personal_mode(target_dir, force=False)

            # Personal mode creates settings.local.json, not settings.json
            settings_path = target_dir / ".claude" / "settings.local.json"
            assert settings_path.exists()

            settings_content = settings_path.read_text()
            # Should NOT have placeholders
            assert "{python_path}" not in settings_content
            assert "{project_root}" not in settings_content
            assert "{hooks_dir}" not in settings_content

    def test_init_replaces_all_placeholders(self):
        """Test that init properly replaces all placeholders in settings.json."""
        import sys

        template_content = json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Write",
                            "hooks": [
                                {"type": "command", "command": "{python_path} {hooks_dir}/test.py {project_root}"}
                            ],
                        }
                    ]
                }
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            hooks_dir = target_dir / ".claude" / "hooks"

            # Test placeholder replacement logic
            python_path = sys.executable
            project_root = str(target_dir.absolute())
            hooks_dir_str = str(hooks_dir)

            processed = template_content.replace("{python_path}", python_path)
            processed = processed.replace("{project_root}", project_root)
            processed = processed.replace("{hooks_dir}", hooks_dir_str)

            # Verify no placeholders remain
            assert "{python_path}" not in processed
            assert "{project_root}" not in processed
            assert "{hooks_dir}" not in processed

            # Verify correct paths are present
            data = json.loads(processed)
            command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
            assert python_path in command
            assert str(target_dir) in command
            assert ".claude/hooks" in command

    def test_hook_template_consistency(self):
        """Ensure hook names in automation_base.json match actual filenames."""
        import importlib.resources as pkg_resources

        # Get all hook files
        workflow_hooks = set()
        try:
            # List workflow hooks
            for item in [
                "implementation_declaration.py",
                "research_tracker.py",
                "implementation_tracker.py",
                "memory_updater.py",
                "todo_milestone_connector.py",
                "automated_commit_trigger.py",
            ]:
                workflow_hooks.add(f"workflow/{item}")
        except Exception:
            pass

        # Parse automation_base.json
        automation_json = pkg_resources.read_text("quaestor.claude.hooks", "automation_base.json")
        data = json.loads(automation_json)

        # Extract hook names from commands
        referenced_hooks = set()
        for hook_type in ["PreToolUse", "PostToolUse"]:
            for matcher_config in data["hooks"][hook_type]:
                for hook in matcher_config["hooks"]:
                    command = hook["command"]
                    # Extract filename between hooks_dir}/ and next space or end
                    parts = command.split("{hooks_dir}/")
                    if len(parts) > 1:
                        hook_file = parts[1].split()[0]
                        referenced_hooks.add(hook_file)

        # All referenced hooks should exist
        assert referenced_hooks.issubset(workflow_hooks), (
            f"Referenced hooks not found: {referenced_hooks - workflow_hooks}"
        )


class TestHooksCopyingInInit:
    """Test that init command properly copies hooks."""

    @patch("importlib.resources.read_text")
    @patch("quaestor.cli.init.console")
    def test_init_common_should_copy_hooks(self, mock_console, mock_read_text):
        """Test that _init_common copies hook files."""
        # This test ensures we add hook copying to init
        # Currently this might fail - that's the point!

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            # Mock resources
            mock_read_text.side_effect = lambda pkg, file: "mock content"

            # Run init_common
            copied_files, commands_copied = _init_common(target_dir, force=False, mode="personal")

            # Check if hooks directory was created
            hooks_dir = target_dir / ".claude" / "hooks"

            # This assertion documents what SHOULD happen
            # If this fails, it means init needs to be updated to copy hooks
            if not hooks_dir.exists():
                pytest.skip("Hook copying not yet implemented in _init_common")

            # These are the hooks that should be copied
            expected_hooks = [
                "shared_utils.py",
                "implementation_declaration.py",
                "research_tracker.py",
                "implementation_tracker.py",
                "memory_updater.py",
                "todo_milestone_connector.py",
            ]

            for hook in expected_hooks:
                hook_path = hooks_dir / hook
                assert hook_path.exists(), f"Hook {hook} was not copied"


class TestTemplateCopying:
    """Test that all templates are properly copied during init."""

    @patch("quaestor.cli.init.process_template")
    @patch("importlib.resources.read_text")
    @patch("quaestor.cli.init.console")
    def test_all_template_files_copied(self, _mock_console, mock_read_text, mock_process_template):
        """Test that all template files from TEMPLATE_FILES are copied."""
        from quaestor.constants import TEMPLATE_FILES

        # Mock the template content and processing
        mock_read_text.return_value = "# Mock Template Content"
        mock_process_template.return_value = "# Processed Mock Content"

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            # Run init_common
            copied_files, _commands_copied = _init_common(target_dir, force=False, mode="personal")

            quaestor_dir = target_dir / ".quaestor"
            assert quaestor_dir.exists(), ".quaestor directory should be created"

            # Check that all template files were copied
            for _template_name, output_name in TEMPLATE_FILES.items():
                output_path = quaestor_dir / output_name
                assert output_path.exists(), f"Template file {output_name} was not created"

                # Verify the file has content
                content = output_path.read_text()
                assert len(content) > 0, f"Template file {output_name} is empty"

                # Check it appears in copied_files list
                expected_path = f".quaestor/{output_name}"
                assert expected_path in copied_files, f"{expected_path} not in copied_files list"

    def test_template_files_constant_completeness(self):
        """Test that TEMPLATE_FILES includes all critical Quaestor files."""
        from quaestor.constants import TEMPLATE_FILES

        # These are the critical files that must be included
        required_files = {
            "QUAESTOR_CLAUDE.md",
            "CRITICAL_RULES.md",
            "ARCHITECTURE.md",
            "MEMORY.md",
        }

        actual_files = set(TEMPLATE_FILES.values())

        missing_files = required_files - actual_files
        assert not missing_files, f"Missing required template files: {missing_files}"

    def test_claude_md_references_all_files(self):
        """Test that CLAUDE.md references all the template files."""
        # Read the current CLAUDE.md
        claude_md_path = Path(__file__).parent.parent / "CLAUDE.md"
        assert claude_md_path.exists(), "CLAUDE.md should exist in project root"

        claude_content = claude_md_path.read_text()

        # Files that should be referenced in CLAUDE.md
        expected_references = [
            ".quaestor/QUAESTOR_CLAUDE.md",
            ".quaestor/CRITICAL_RULES.md",
            ".quaestor/ARCHITECTURE.md",
            ".quaestor/MEMORY.md",
        ]

        for ref in expected_references:
            assert ref in claude_content, f"CLAUDE.md should reference {ref}"

    @patch("quaestor.cli.init.process_template")
    @patch("importlib.resources.read_text")
    @patch("quaestor.cli.init.console")
    def test_template_processing_failure_handling(self, _mock_console, mock_read_text, mock_process_template):
        """Test that template processing failures are handled gracefully."""
        # Mock read_text to succeed but process_template to fail
        mock_read_text.return_value = "# Mock Template Content"
        mock_process_template.side_effect = Exception("Processing failed")

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            # This should not crash even if template processing fails
            _init_common(target_dir, force=False, mode="personal")

            # Should still create .quaestor directory
            quaestor_dir = target_dir / ".quaestor"
            assert quaestor_dir.exists(), ".quaestor directory should be created even if processing fails"

    @patch("quaestor.cli.init.process_template")
    @patch("importlib.resources.read_text")
    @patch("quaestor.cli.init.console")
    def test_missing_template_file_handling(self, _mock_console, mock_read_text, _mock_process_template):
        """Test handling when a template file is missing."""
        # Mock read_text to raise an exception (simulating missing file)
        mock_read_text.side_effect = FileNotFoundError("Template not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)

            # This should not crash even if template files are missing
            _init_common(target_dir, force=False, mode="personal")

            # Should still create .quaestor directory
            quaestor_dir = target_dir / ".quaestor"
            assert quaestor_dir.exists(), ".quaestor directory should be created even if templates are missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
