"""Tests for V2.1 Simple Workflow Detection

Tests the simplified workflow detection system including:
- Workflow detection from events
- Pattern learning and recognition
- Basic metrics collection
- Anomaly detection
- Event bus integration
"""

import time
from unittest.mock import Mock

import pytest

from a1.core.events import FileChangeEvent, ToolUseEvent, UserActionEvent
from a1.extensions.workflow import (
    SimpleWorkflowDetector,
    WorkflowInstance,
    WorkflowPattern,
    WorkflowState,
    WorkflowStep,
    WorkflowType,
    get_current_workflows,
    get_workflow_detector,
    get_workflow_metrics,
    initialize_workflow_detector,
)


class TestWorkflowEnums:
    """Tests for workflow enumeration types."""

    def test_workflow_type_enum(self):
        """Test workflow type enumeration."""
        assert WorkflowType.FEATURE_DEVELOPMENT.value == "feature_development"
        assert WorkflowType.BUG_FIX.value == "bug_fix"
        assert WorkflowType.TESTING.value == "testing"
        assert WorkflowType.UNKNOWN.value == "unknown"

    def test_workflow_step_enum(self):
        """Test workflow step enumeration."""
        assert WorkflowStep.RESEARCH.value == "research"
        assert WorkflowStep.CODING.value == "coding"
        assert WorkflowStep.TESTING.value == "testing"
        assert WorkflowStep.COMMITTING.value == "committing"

    def test_workflow_state_enum(self):
        """Test workflow state enumeration."""
        assert WorkflowState.ACTIVE.value == "active"
        assert WorkflowState.COMPLETED.value == "completed"
        assert WorkflowState.FAILED.value == "failed"
        assert WorkflowState.ABANDONED.value == "abandoned"


class TestWorkflowInstance:
    """Tests for WorkflowInstance data structure."""

    def test_workflow_instance_creation(self):
        """Test creating a workflow instance."""
        workflow = WorkflowInstance(
            id="test_workflow",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            state=WorkflowState.ACTIVE,
            start_time=time.time(),
        )

        assert workflow.id == "test_workflow"
        assert workflow.type == WorkflowType.FEATURE_DEVELOPMENT
        assert workflow.state == WorkflowState.ACTIVE
        assert workflow.step_count == 0
        assert len(workflow.files_touched) == 0
        assert len(workflow.tools_used) == 0

    def test_workflow_duration_calculation(self):
        """Test workflow duration calculation."""
        start_time = time.time()
        workflow = WorkflowInstance(
            id="test", type=WorkflowType.TESTING, state=WorkflowState.ACTIVE, start_time=start_time
        )

        # Active workflow
        duration1 = workflow.duration
        assert duration1 >= 0

        # Completed workflow
        workflow.end_time = start_time + 100
        duration2 = workflow.duration
        assert duration2 == 100

    def test_add_step(self):
        """Test adding steps to workflow."""
        workflow = WorkflowInstance(
            id="test", type=WorkflowType.FEATURE_DEVELOPMENT, state=WorkflowState.ACTIVE, start_time=time.time()
        )

        workflow.add_step(WorkflowStep.RESEARCH)
        workflow.add_step(WorkflowStep.CODING)

        assert workflow.step_count == 2
        assert workflow.steps == [WorkflowStep.RESEARCH, WorkflowStep.CODING]
        assert len(workflow.step_times) == 2

    def test_add_file_and_tool(self):
        """Test adding files and tools to workflow."""
        workflow = WorkflowInstance(
            id="test", type=WorkflowType.FEATURE_DEVELOPMENT, state=WorkflowState.ACTIVE, start_time=time.time()
        )

        workflow.add_file("test.py")
        workflow.add_file("test.py")  # Duplicate should not add twice
        workflow.add_file("other.py")

        workflow.add_tool("Edit")
        workflow.add_tool("Read")
        workflow.add_tool("Edit")  # Duplicate should not add twice

        assert len(workflow.files_touched) == 2
        assert "test.py" in workflow.files_touched
        assert "other.py" in workflow.files_touched

        assert len(workflow.tools_used) == 2
        assert "Edit" in workflow.tools_used
        assert "Read" in workflow.tools_used


class TestWorkflowPattern:
    """Tests for WorkflowPattern data structure."""

    def test_pattern_creation(self):
        """Test creating a workflow pattern."""
        pattern = WorkflowPattern(type=WorkflowType.TESTING, step_sequence=[WorkflowStep.CODING, WorkflowStep.TESTING])

        assert pattern.type == WorkflowType.TESTING
        assert pattern.step_sequence == [WorkflowStep.CODING, WorkflowStep.TESTING]
        assert pattern.frequency == 1
        assert pattern.success_rate == 1.0

    def test_pattern_stats_update(self):
        """Test updating pattern statistics."""
        pattern = WorkflowPattern(
            type=WorkflowType.FEATURE_DEVELOPMENT,
            step_sequence=[WorkflowStep.RESEARCH, WorkflowStep.CODING],
            avg_duration=100.0,
            success_rate=1.0,
        )

        # Update with successful workflow
        pattern.update_stats(200.0, True)

        assert pattern.frequency == 2
        assert pattern.avg_duration == 150.0  # (100 + 200) / 2
        assert pattern.success_rate == 1.0  # (1.0 + 1.0) / 2

        # Update with failed workflow
        pattern.update_stats(50.0, False)

        assert pattern.frequency == 3
        assert pattern.success_rate == 0.5  # (1.0 + 0.0) / 2


class TestSimpleWorkflowDetector:
    """Tests for SimpleWorkflowDetector functionality."""

    def test_detector_initialization(self):
        """Test workflow detector initialization."""
        detector = SimpleWorkflowDetector()

        assert len(detector.active_workflows) == 0
        assert len(detector.completed_workflows) == 0
        assert len(detector.patterns) == 0
        assert detector.workflow_timeout == 1800
        assert detector.min_pattern_frequency == 3

    def test_detector_with_event_bus(self):
        """Test detector initialization with event bus."""
        event_bus = Mock()
        detector = SimpleWorkflowDetector(event_bus)

        assert detector.event_bus == event_bus
        # Should have subscribed to events
        assert event_bus.subscribe.call_count == 3

    @pytest.mark.asyncio
    async def test_tool_use_event_handling(self):
        """Test handling tool use events."""
        detector = SimpleWorkflowDetector()

        # Create tool use event
        event = ToolUseEvent(tool_name="Edit", success=True, duration_ms=1000)

        await detector.handle_tool_use_event(event)

        # Should create a workflow
        assert len(detector.active_workflows) == 1

        workflow = list(detector.active_workflows.values())[0]
        assert WorkflowStep.CODING in workflow.steps
        assert "Edit" in workflow.tools_used
        assert workflow.success is True

    @pytest.mark.asyncio
    async def test_file_change_event_handling(self):
        """Test handling file change events."""
        detector = SimpleWorkflowDetector()

        # Create file change event
        event = FileChangeEvent(file_path="src/feature.py", change_type="created")

        await detector.handle_file_change_event(event)

        # Should create a workflow
        assert len(detector.active_workflows) == 1

        workflow = list(detector.active_workflows.values())[0]
        assert workflow.type == WorkflowType.FEATURE_DEVELOPMENT
        assert WorkflowStep.CODING in workflow.steps
        assert "src/feature.py" in workflow.files_touched

    @pytest.mark.asyncio
    async def test_user_action_event_handling(self):
        """Test handling user action events."""
        detector = SimpleWorkflowDetector()

        # Create user action event
        event = UserActionEvent(action_type="git_commit", action_details={"message": "Test commit"})

        await detector.handle_user_action_event(event)

        # Should create a workflow
        assert len(detector.active_workflows) == 1

        workflow = list(detector.active_workflows.values())[0]
        assert WorkflowStep.COMMITTING in workflow.steps

    def test_workflow_type_detection_from_file(self):
        """Test workflow type detection from file paths."""
        detector = SimpleWorkflowDetector()

        # Test file type mapping
        assert detector._detect_workflow_type_from_file("src/feature.py") == WorkflowType.FEATURE_DEVELOPMENT
        assert detector._detect_workflow_type_from_file("config.yaml") == WorkflowType.SETUP_CONFIG
        assert detector._detect_workflow_type_from_file("README.md") == WorkflowType.DOCUMENTATION
        assert detector._detect_workflow_type_from_file("test_feature.py") == WorkflowType.TESTING
        assert detector._detect_workflow_type_from_file("bugfix.py") == WorkflowType.BUG_FIX

    def test_workflow_completion(self):
        """Test manual workflow completion."""
        detector = SimpleWorkflowDetector()

        # Create and add a workflow
        workflow = WorkflowInstance(
            id="test_workflow",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            state=WorkflowState.ACTIVE,
            start_time=time.time(),
        )
        workflow.add_step(WorkflowStep.CODING)
        workflow.add_step(WorkflowStep.TESTING)
        detector.active_workflows["test_workflow"] = workflow

        # Complete the workflow
        completed = detector.complete_workflow("test_workflow", success=True)

        assert completed is not None
        assert completed.state == WorkflowState.COMPLETED
        assert completed.success is True
        assert completed.end_time is not None

        # Should be moved to completed workflows
        assert "test_workflow" not in detector.active_workflows
        assert len(detector.completed_workflows) == 1
        assert len(detector.patterns) == 1  # Should learn pattern

    def test_pattern_learning(self):
        """Test workflow pattern learning."""
        detector = SimpleWorkflowDetector()

        # Create workflow with steps
        workflow = WorkflowInstance(
            id="test",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            state=WorkflowState.COMPLETED,
            start_time=time.time() - 100,
            end_time=time.time(),
            success=True,
        )
        workflow.steps = [WorkflowStep.RESEARCH, WorkflowStep.CODING, WorkflowStep.TESTING]

        # Learn pattern
        detector._learn_pattern(workflow)

        assert len(detector.patterns) == 1

        pattern = list(detector.patterns.values())[0]
        assert pattern.type == WorkflowType.FEATURE_DEVELOPMENT
        assert pattern.step_sequence == workflow.steps
        assert pattern.frequency == 1

    def test_workflow_suggestions(self):
        """Test workflow step suggestions."""
        detector = SimpleWorkflowDetector()

        # Add some transition data
        detector.step_transitions[(WorkflowStep.RESEARCH, WorkflowStep.CODING)] = 5
        detector.step_transitions[(WorkflowStep.RESEARCH, WorkflowStep.PLANNING)] = 3
        detector.step_transitions[(WorkflowStep.CODING, WorkflowStep.TESTING)] = 4

        # Test suggestions
        suggestions = detector.get_workflow_suggestions([WorkflowStep.RESEARCH])

        assert WorkflowStep.CODING in suggestions  # Most frequent
        assert WorkflowStep.PLANNING in suggestions

    def test_anomaly_detection(self):
        """Test workflow anomaly detection."""
        detector = SimpleWorkflowDetector()

        # Create long-running workflow (simulate timeout)
        old_workflow = WorkflowInstance(
            id="old_workflow",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            state=WorkflowState.ACTIVE,
            start_time=time.time() - 2000,  # 2000 seconds ago
        )
        detector.active_workflows["old_workflow"] = old_workflow

        # Create recent failed workflows
        for i in range(5):
            failed_workflow = WorkflowInstance(
                id=f"failed_{i}",
                type=WorkflowType.TESTING,
                state=WorkflowState.FAILED,
                start_time=time.time() - 100,
                end_time=time.time() - 50,
                success=False,
            )
            detector.completed_workflows.append(failed_workflow)

        anomalies = detector.detect_anomalies()

        # Should detect timeout anomaly
        timeout_anomalies = [a for a in anomalies if a["type"] == "timeout"]
        assert len(timeout_anomalies) > 0

        # Should detect high failure rate
        failure_anomalies = [a for a in anomalies if a["type"] == "high_failure_rate"]
        assert len(failure_anomalies) > 0

    def test_workflow_metrics(self):
        """Test workflow metrics calculation."""
        detector = SimpleWorkflowDetector()

        # Add some workflows
        for i in range(3):
            workflow = WorkflowInstance(
                id=f"workflow_{i}",
                type=WorkflowType.FEATURE_DEVELOPMENT,
                state=WorkflowState.COMPLETED,
                start_time=time.time() - 200,
                end_time=time.time() - 100,
                success=i < 2,  # First 2 successful, last one failed
            )
            workflow.steps = [WorkflowStep.CODING, WorkflowStep.TESTING]
            detector.completed_workflows.append(workflow)

        # Add active workflow
        active = WorkflowInstance(
            id="active", type=WorkflowType.BUG_FIX, state=WorkflowState.ACTIVE, start_time=time.time()
        )
        detector.active_workflows["active"] = active

        metrics = detector.get_metrics()

        assert metrics.total_workflows == 4
        assert metrics.active_workflows == 1
        assert metrics.completed_workflows == 3
        assert metrics.failed_workflows == 1
        assert metrics.success_rate == 2 / 3  # 2 out of 3 completed were successful
        assert metrics.most_common_type == WorkflowType.FEATURE_DEVELOPMENT

    def test_workflow_cleanup(self):
        """Test cleanup of expired workflows."""
        detector = SimpleWorkflowDetector()
        detector.workflow_timeout = 100  # 100 seconds

        # Add expired workflow
        expired = WorkflowInstance(
            id="expired",
            type=WorkflowType.TESTING,
            state=WorkflowState.ACTIVE,
            start_time=time.time() - 200,  # 200 seconds ago
        )
        detector.active_workflows["expired"] = expired

        # Add recent workflow
        recent = WorkflowInstance(
            id="recent",
            type=WorkflowType.FEATURE_DEVELOPMENT,
            state=WorkflowState.ACTIVE,
            start_time=time.time() - 50,  # 50 seconds ago
        )
        detector.active_workflows["recent"] = recent

        # Cleanup should move expired to completed
        detector._cleanup_expired_workflows()

        assert "expired" not in detector.active_workflows
        assert "recent" in detector.active_workflows
        assert len(detector.completed_workflows) == 1

        completed = detector.completed_workflows[0]
        assert completed.id == "expired"
        assert completed.state == WorkflowState.ABANDONED


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_initialize_workflow_detector(self):
        """Test global detector initialization."""
        event_bus = Mock()
        detector = initialize_workflow_detector(event_bus)

        assert detector is not None
        assert detector.event_bus == event_bus
        assert get_workflow_detector() == detector

    def test_get_current_workflows(self):
        """Test getting current workflows globally."""
        detector = initialize_workflow_detector()

        # Initially empty
        workflows = get_current_workflows()
        assert len(workflows) == 0

        # Add workflow
        workflow = WorkflowInstance(
            id="test", type=WorkflowType.TESTING, state=WorkflowState.ACTIVE, start_time=time.time()
        )
        detector.active_workflows["test"] = workflow

        workflows = get_current_workflows()
        assert len(workflows) == 1
        assert workflows[0].id == "test"

    def test_get_workflow_metrics_global(self):
        """Test getting workflow metrics globally."""
        detector = initialize_workflow_detector()

        # Initially empty metrics
        metrics = get_workflow_metrics()
        assert metrics.total_workflows == 0

        # Add workflow
        workflow = WorkflowInstance(
            id="test", type=WorkflowType.FEATURE_DEVELOPMENT, state=WorkflowState.ACTIVE, start_time=time.time()
        )
        detector.active_workflows["test"] = workflow

        metrics = get_workflow_metrics()
        assert metrics.total_workflows == 1
        assert metrics.active_workflows == 1


if __name__ == "__main__":
    pytest.main([__file__])
