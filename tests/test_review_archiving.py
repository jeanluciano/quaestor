"""Test review command archiving integration."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from quaestor.core.folder_manager import FolderManager
from quaestor.core.memory_manager import MemoryManager
from quaestor.core.specifications import SpecificationManager, SpecPriority, SpecStatus, SpecType


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        # Create necessary directories
        (project_dir / ".quaestor" / "specifications").mkdir(parents=True)
        yield project_dir


def test_memory_manager_archive_completion(temp_project):
    """Test archiving completed specification in memory."""
    specs_dir = temp_project / ".quaestor" / "specifications"
    folder_manager = FolderManager(specs_dir)
    folder_manager.create_folder_structure()
    memory_manager = MemoryManager(temp_project, folder_manager)

    # Create initial memory file
    memory_manager.update_memory_file()

    # Archive a completed specification
    spec_data = {
        "title": "Test Feature Implementation",
        "start_date": "2024-01-01",
        "acceptance_criteria": ["API endpoint created", "Tests written", "Documentation updated"],
        "learnings": ["Used new async pattern", "Improved error handling"],
        "scope": "feature",
        "complexity": "high",
    }

    success = memory_manager.archive_completed_specification("feat-test-001", spec_data)
    assert success

    # Check memory file contains completion
    memory_content = memory_manager.memory_file.read_text()
    assert "Specification Completed: feat-test-001" in memory_content
    assert "Test Feature Implementation" in memory_content
    assert "✅ API endpoint created" in memory_content
    assert "Used new async pattern" in memory_content
    assert "Status: ✅ Completed" in memory_content


def test_review_archiver_hook_integration(temp_project):
    """Test review archiver hook with specification manager."""
    from quaestor.claude.hooks.review_archiver import ReviewArchiverHook

    # Create a specification
    spec_manager = SpecificationManager(temp_project)
    spec = spec_manager.create_specification(
        title="Review Test Feature",
        spec_type=SpecType.FEATURE,
        description="Test feature for review",
        rationale="Testing review archiving",
        priority=SpecPriority.HIGH,
    )

    # Activate the specification
    spec_manager.activate_specification(spec.id)

    # Mock hook with review command context
    with patch("quaestor.claude.hooks.review_archiver.get_project_root", return_value=temp_project):
        hook = ReviewArchiverHook()

        # Mock input data indicating review completion
        hook.input_data = {
            "command": "/review",
            "tool_name": "Bash",
            "tool_input": {"command": 'gh pr create --title "Test PR"'},
            "output": f"PR created successfully. Completed {spec.id}: {spec.title}",
        }

        # Mock mode detection
        hook.is_framework_mode = MagicMock(return_value=True)
        hook.output_success = MagicMock()

        # Execute hook
        hook.execute()

    # Verify specification was archived
    # Create a new spec manager to force reload from disk
    new_spec_manager = SpecificationManager(temp_project)
    completed_spec = new_spec_manager.get_specification(spec.id)

    # Debug output
    if completed_spec.status != SpecStatus.COMPLETED:
        print(f"Spec status: {completed_spec.status}")
        print(f"Hook output success calls: {hook.output_success.call_args_list}")

    assert completed_spec.status == SpecStatus.COMPLETED

    # Check spec is in completed folder
    completed_file = temp_project / ".quaestor" / "specifications" / "completed" / f"{spec.id}.yaml"
    assert completed_file.exists()

    # Check memory was updated
    memory_file = temp_project / ".quaestor" / "MEMORY.md"
    assert memory_file.exists(), "Memory file should exist"
    memory_content = memory_file.read_text()

    # Check for completion entry
    assert "Specification Completed:" in memory_content or spec.id in memory_content, (
        f"Memory content:\n{memory_content}"
    )


def test_review_archiver_pr_detection(temp_project):
    """Test PR creation detection in review archiver."""
    from quaestor.claude.hooks.review_archiver import ReviewArchiverHook

    with patch("quaestor.claude.hooks.review_archiver.get_project_root", return_value=temp_project):
        hook = ReviewArchiverHook()

        # Test gh pr create detection
        hook.input_data = {"tool_name": "Bash", "tool_input": {"command": 'gh pr create --title "Feature Complete"'}}
        assert hook._check_pr_created() is True

        # Test PR URL detection
        hook.input_data = {"output": "Created PR: https://github.com/user/repo/pull/123"}
        assert hook._check_pr_created() is True

        # Test no PR detection
        hook.input_data = {"tool_name": "Read", "output": "Just reading files"}
        assert hook._check_pr_created() is False


def test_memory_trimming(temp_project):
    """Test that memory manager trims old completions."""
    specs_dir = temp_project / ".quaestor" / "specifications"
    folder_manager = FolderManager(specs_dir)
    folder_manager.create_folder_structure()
    memory_manager = MemoryManager(temp_project, folder_manager)
    memory_manager.update_memory_file()

    # Archive many specifications
    for i in range(10):
        spec_data = {
            "title": f"Feature {i}",
            "start_date": "2024-01-01",
            "acceptance_criteria": ["Done"],
            "scope": "feature",
            "complexity": "medium",
        }
        memory_manager.archive_completed_specification(f"feat-{i}", spec_data)

    # Check memory file is within limits
    memory_content = memory_manager.memory_file.read_text()
    lines = memory_content.split("\n")
    assert len(lines) <= memory_manager.MAX_MEMORY_LINES

    # Check recent completions are kept
    assert "Feature 9" in memory_content

    # Check oldest might be trimmed - the exact ones depend on trimming
    completion_count = memory_content.count("Specification Completed:")
    assert completion_count <= 5  # Should keep only 5 most recent

    # Verify trimming message appears if needed
    if len(lines) > memory_manager.MAX_MEMORY_LINES - 10:
        assert "(older entries trimmed)" in memory_content
