"""Simple test to debug review archiving."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from quaestor.claude.hooks.review_archiver import ReviewArchiverHook
from quaestor.core.specifications import SpecificationManager, SpecPriority, SpecStatus, SpecType


def test_basic_hook_flow():
    """Test basic hook flow step by step."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        (project_dir / ".quaestor" / "specifications").mkdir(parents=True)

        # Create and activate a spec
        spec_manager = SpecificationManager(project_dir)
        spec = spec_manager.create_specification(
            title="Test Feature",
            spec_type=SpecType.FEATURE,
            description="Test",
            rationale="Test",
            priority=SpecPriority.HIGH,
        )

        # Activate it
        result = spec_manager.activate_specification(spec.id)
        print(f"Activation result: {result}")

        # Verify it's active
        active_spec = spec_manager.get_specification(spec.id)
        print(f"Spec status after activation: {active_spec.status}")

        # Check if it's in active folder
        active_file = project_dir / ".quaestor" / "specifications" / "active" / f"{spec.id}.yaml"
        print(f"Active file exists: {active_file.exists()}")

        # Now test the hook
        with patch("quaestor.claude.hooks.review_archiver.get_project_root", return_value=project_dir):
            hook = ReviewArchiverHook()

            # Mock minimal data
            hook.input_data = {
                "command": "/review",
                "tool_name": "Bash",
                "tool_input": {"command": "gh pr create"},
                "output": f"Completed {spec.id}",
            }

            # Mock methods
            hook.is_framework_mode = MagicMock(return_value=True)
            hook.output_success = MagicMock()
            hook.output_error = MagicMock()

            # Test individual methods
            print(f"Is review command: {hook._is_review_command()}")
            print(f"PR created: {hook._check_pr_created()}")

            # Get active specs
            active_specs = hook.spec_manager.list_specifications(status=SpecStatus.ACTIVE)
            print(f"Active specs: {[s.id for s in active_specs]}")

            # Detect completed
            completed = hook._detect_completed_specs(active_specs)
            print(f"Detected as completed: {[s.id for s in completed]}")

            # Execute the hook
            hook.execute()

            print(f"Output success calls: {hook.output_success.call_args_list}")
            print(f"Output error calls: {hook.output_error.call_args_list}")

        # Check final state
        final_spec = spec_manager.get_specification(spec.id)
        print(f"Final spec status: {final_spec.status}")

        completed_file = project_dir / ".quaestor" / "specifications" / "completed" / f"{spec.id}.yaml"
        print(f"Completed file exists: {completed_file.exists()}")


if __name__ == "__main__":
    test_basic_hook_flow()
