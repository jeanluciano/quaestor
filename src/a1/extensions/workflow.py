"""Simple Workflow Detection - Core workflow pattern recognition for A1

Provides essential workflow detection functionality extracted from V2.0's complex system:
- Basic workflow detection from event streams
- Simple pattern recognition with frequency-based analysis
- Core metrics collection (duration, success rate, step count)
- Essential anomaly detection (timeouts, failures)
- Event bus integration

Replaces V2.0's 6,355+ line system with ~500 focused lines.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..core.event_bus import EventBus
from ..core.events import FileChangeEvent, ToolUseEvent, UserActionEvent


class WorkflowType(Enum):
    """Core workflow types detected by the system."""

    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIX = "bug_fix"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SETUP_CONFIG = "setup_config"
    UNKNOWN = "unknown"


class WorkflowStep(Enum):
    """Essential workflow steps tracked by the system."""

    # Planning and research
    RESEARCH = "research"
    PLANNING = "planning"

    # Development
    CODING = "coding"
    EDITING = "editing"

    # Testing and validation
    TESTING = "testing"
    DEBUGGING = "debugging"

    # Documentation
    DOCUMENTING = "documenting"

    # Version control
    COMMITTING = "committing"
    BRANCHING = "branching"

    # Build and deployment
    BUILDING = "building"
    DEPLOYING = "deploying"

    # Refactoring
    REFACTORING = "refactoring"

    # Other
    UNKNOWN = "unknown"


class WorkflowState(Enum):
    """Workflow execution states."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class WorkflowInstance:
    """Simple workflow instance with essential tracking."""

    id: str
    type: WorkflowType
    state: WorkflowState
    start_time: float
    end_time: float | None = None
    steps: list[WorkflowStep] = field(default_factory=list)
    step_times: list[float] = field(default_factory=list)
    files_touched: set[str] = field(default_factory=set)
    tools_used: list[str] = field(default_factory=list)
    success: bool = True

    @property
    def duration(self) -> float:
        """Calculate workflow duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def step_count(self) -> int:
        """Get total number of steps."""
        return len(self.steps)

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)
        self.step_times.append(time.time())

    def add_file(self, file_path: str) -> None:
        """Track a file that was touched in this workflow."""
        self.files_touched.add(file_path)

    def add_tool(self, tool_name: str) -> None:
        """Track a tool that was used in this workflow."""
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)


@dataclass
class WorkflowPattern:
    """Simple workflow pattern with frequency tracking."""

    type: WorkflowType
    step_sequence: list[WorkflowStep]
    frequency: int = 1
    avg_duration: float = 0.0
    success_rate: float = 1.0
    last_seen: float = field(default_factory=time.time)

    def update_stats(self, duration: float, success: bool) -> None:
        """Update pattern statistics."""
        self.frequency += 1
        self.avg_duration = (self.avg_duration + duration) / 2
        self.success_rate = (self.success_rate + (1.0 if success else 0.0)) / 2
        self.last_seen = time.time()


@dataclass
class WorkflowMetrics:
    """Simple workflow metrics."""

    total_workflows: int = 0
    active_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    avg_duration: float = 0.0
    success_rate: float = 1.0
    most_common_type: WorkflowType | None = None
    most_common_steps: list[WorkflowStep] = field(default_factory=list)


class SimpleWorkflowDetector:
    """Simplified workflow detection system."""

    def __init__(self, event_bus: EventBus | None = None):
        self.event_bus = event_bus

        # Active workflow tracking
        self.active_workflows: dict[str, WorkflowInstance] = {}
        self.completed_workflows: list[WorkflowInstance] = []

        # Pattern recognition
        self.patterns: dict[str, WorkflowPattern] = {}
        self.step_transitions: dict[tuple[WorkflowStep, WorkflowStep], int] = defaultdict(int)

        # Configuration
        self.workflow_timeout = 1800  # 30 minutes
        self.min_pattern_frequency = 3
        self.max_workflows_history = 100

        # Tool to step mapping
        self.tool_step_mapping = {
            "Read": WorkflowStep.RESEARCH,
            "Edit": WorkflowStep.CODING,
            "Write": WorkflowStep.CODING,
            "MultiEdit": WorkflowStep.EDITING,
            "Bash": WorkflowStep.BUILDING,
            "Grep": WorkflowStep.RESEARCH,
            "Glob": WorkflowStep.RESEARCH,
            "TodoWrite": WorkflowStep.PLANNING,
            "WebFetch": WorkflowStep.RESEARCH,
            "WebSearch": WorkflowStep.RESEARCH,
        }

        # File extension to workflow type mapping
        self.file_type_mapping = {
            ".py": WorkflowType.FEATURE_DEVELOPMENT,
            ".js": WorkflowType.FEATURE_DEVELOPMENT,
            ".ts": WorkflowType.FEATURE_DEVELOPMENT,
            ".test.py": WorkflowType.TESTING,
            ".test.js": WorkflowType.TESTING,
            ".spec.py": WorkflowType.TESTING,
            ".md": WorkflowType.DOCUMENTATION,
            ".txt": WorkflowType.DOCUMENTATION,
            ".yaml": WorkflowType.SETUP_CONFIG,
            ".yml": WorkflowType.SETUP_CONFIG,
            ".json": WorkflowType.SETUP_CONFIG,
        }

        # Subscribe to events if event bus provided
        if self.event_bus:
            self.event_bus.subscribe(self.handle_tool_use_event, "tool_use")
            self.event_bus.subscribe(self.handle_file_change_event, "file_change")
            self.event_bus.subscribe(self.handle_user_action_event, "user_action")

    async def handle_tool_use_event(self, event: ToolUseEvent) -> None:
        """Handle tool use events for workflow detection."""
        try:
            # Map tool to workflow step
            step = self.tool_step_mapping.get(event.tool_name, WorkflowStep.UNKNOWN)

            # Get or create active workflow
            workflow = self._get_or_create_workflow(event.tool_name)

            # Add step to workflow
            workflow.add_step(step)
            workflow.add_tool(event.tool_name)

            # Update workflow state based on success
            if not event.success:
                workflow.success = False

            await self._emit_workflow_event(
                "step_added", {"workflow_id": workflow.id, "step": step.value, "tool": event.tool_name}
            )

        except Exception as e:
            print(f"Error handling tool use event: {e}")

    async def handle_file_change_event(self, event: FileChangeEvent) -> None:
        """Handle file change events for workflow detection."""
        try:
            # Determine workflow type from file
            workflow_type = self._detect_workflow_type_from_file(event.file_path)

            # Get or create active workflow
            workflow = self._get_or_create_workflow(f"file_{workflow_type.value}")
            workflow.type = workflow_type

            # Map change type to step
            step_mapping = {
                "created": WorkflowStep.CODING,
                "modified": WorkflowStep.EDITING,
                "deleted": WorkflowStep.REFACTORING,
            }
            step = step_mapping.get(event.change_type, WorkflowStep.EDITING)

            # Add step and file to workflow
            workflow.add_step(step)
            workflow.add_file(event.file_path)

            await self._emit_workflow_event(
                "file_changed",
                {"workflow_id": workflow.id, "file_path": event.file_path, "change_type": event.change_type},
            )

        except Exception as e:
            print(f"Error handling file change event: {e}")

    async def handle_user_action_event(self, event: UserActionEvent) -> None:
        """Handle user action events for workflow detection."""
        try:
            # Map user actions to workflow steps
            action_step_mapping = {
                "commit": WorkflowStep.COMMITTING,
                "branch": WorkflowStep.BRANCHING,
                "test": WorkflowStep.TESTING,
                "build": WorkflowStep.BUILDING,
                "deploy": WorkflowStep.DEPLOYING,
            }

            action_type = event.action_type.lower()
            step = None

            for action_key, workflow_step in action_step_mapping.items():
                if action_key in action_type:
                    step = workflow_step
                    break

            if step:
                workflow = self._get_or_create_workflow(f"action_{action_type}")
                workflow.add_step(step)

                await self._emit_workflow_event(
                    "user_action", {"workflow_id": workflow.id, "action": action_type, "step": step.value}
                )

        except Exception as e:
            print(f"Error handling user action event: {e}")

    def _get_or_create_workflow(self, context: str) -> WorkflowInstance:
        """Get existing active workflow or create new one."""
        # Clean up expired workflows first
        self._cleanup_expired_workflows()

        # Look for recent active workflow (within last 5 minutes)
        current_time = time.time()
        for workflow in self.active_workflows.values():
            if current_time - workflow.start_time < 300:  # 5 minutes
                return workflow

        # Create new workflow
        workflow_id = f"workflow_{int(current_time * 1000000)}"
        workflow = WorkflowInstance(
            id=workflow_id, type=WorkflowType.UNKNOWN, state=WorkflowState.ACTIVE, start_time=current_time
        )

        self.active_workflows[workflow_id] = workflow
        return workflow

    def _detect_workflow_type_from_file(self, file_path: str) -> WorkflowType:
        """Detect workflow type based on file path and extension."""
        path_lower = file_path.lower()

        # Check for specific patterns in path first (higher priority)
        if "test" in path_lower or "spec" in path_lower:
            return WorkflowType.TESTING
        elif "doc" in path_lower or "readme" in path_lower:
            return WorkflowType.DOCUMENTATION
        elif "config" in path_lower or "setup" in path_lower:
            return WorkflowType.SETUP_CONFIG
        elif "fix" in path_lower or "bug" in path_lower:
            return WorkflowType.BUG_FIX

        # Check file extension for remaining files
        for ext, workflow_type in self.file_type_mapping.items():
            if file_path.endswith(ext):
                return workflow_type

        return WorkflowType.FEATURE_DEVELOPMENT

    def _cleanup_expired_workflows(self) -> None:
        """Clean up workflows that have been inactive too long."""
        current_time = time.time()
        expired_workflows = []

        for workflow_id, workflow in self.active_workflows.items():
            if current_time - workflow.start_time > self.workflow_timeout:
                # Mark as abandoned and move to completed
                workflow.state = WorkflowState.ABANDONED
                workflow.end_time = current_time
                workflow.success = False

                self.completed_workflows.append(workflow)
                expired_workflows.append(workflow_id)

        # Remove from active workflows
        for workflow_id in expired_workflows:
            del self.active_workflows[workflow_id]

        # Limit history size
        if len(self.completed_workflows) > self.max_workflows_history:
            self.completed_workflows = self.completed_workflows[-self.max_workflows_history :]

    def complete_workflow(self, workflow_id: str, success: bool = True) -> WorkflowInstance | None:
        """Manually complete an active workflow."""
        if workflow_id not in self.active_workflows:
            return None

        workflow = self.active_workflows[workflow_id]
        workflow.state = WorkflowState.COMPLETED if success else WorkflowState.FAILED
        workflow.end_time = time.time()
        workflow.success = success

        # Move to completed workflows
        self.completed_workflows.append(workflow)
        del self.active_workflows[workflow_id]

        # Learn pattern from completed workflow
        self._learn_pattern(workflow)

        return workflow

    def _learn_pattern(self, workflow: WorkflowInstance) -> None:
        """Learn workflow patterns from completed workflows."""
        if len(workflow.steps) < 2:
            return

        # Create pattern key from workflow type and step sequence
        step_sequence = workflow.steps[:10]  # Limit to first 10 steps
        pattern_key = f"{workflow.type.value}:{'-'.join(step.value for step in step_sequence)}"

        if pattern_key in self.patterns:
            # Update existing pattern
            pattern = self.patterns[pattern_key]
            pattern.update_stats(workflow.duration, workflow.success)
        else:
            # Create new pattern
            self.patterns[pattern_key] = WorkflowPattern(
                type=workflow.type,
                step_sequence=step_sequence,
                avg_duration=workflow.duration,
                success_rate=1.0 if workflow.success else 0.0,
            )

        # Update step transitions
        for i in range(len(workflow.steps) - 1):
            transition = (workflow.steps[i], workflow.steps[i + 1])
            self.step_transitions[transition] += 1

    def get_workflow_suggestions(self, current_steps: list[WorkflowStep]) -> list[WorkflowStep]:
        """Get suggested next steps based on learned patterns."""
        if not current_steps:
            return [WorkflowStep.RESEARCH, WorkflowStep.PLANNING, WorkflowStep.CODING]

        # Find most common next steps based on transitions
        last_step = current_steps[-1]
        suggestions = []

        for (from_step, to_step), count in self.step_transitions.items():
            if from_step == last_step and count >= self.min_pattern_frequency:
                suggestions.append((to_step, count))

        # Sort by frequency and return top 3
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [step for step, _ in suggestions[:3]]

    def detect_anomalies(self) -> list[dict[str, Any]]:
        """Detect basic workflow anomalies."""
        anomalies = []
        current_time = time.time()

        # Check for long-running workflows
        for workflow in self.active_workflows.values():
            duration = current_time - workflow.start_time
            if duration > self.workflow_timeout:
                anomalies.append(
                    {
                        "type": "timeout",
                        "workflow_id": workflow.id,
                        "duration": duration,
                        "message": f"Workflow {workflow.id} has been running for {duration / 60:.1f} minutes",
                    }
                )

        # Check for failed workflows pattern
        recent_workflows = [w for w in self.completed_workflows[-10:]]
        if len(recent_workflows) >= 3:
            failed_count = sum(1 for w in recent_workflows if not w.success)
            failure_rate = failed_count / len(recent_workflows)

            if failure_rate > 0.5:
                anomalies.append(
                    {
                        "type": "high_failure_rate",
                        "failure_rate": failure_rate,
                        "message": f"High failure rate detected: {failure_rate:.1%} of recent workflows failed",
                    }
                )

        return anomalies

    def get_metrics(self) -> WorkflowMetrics:
        """Get basic workflow metrics."""
        all_workflows = list(self.active_workflows.values()) + self.completed_workflows

        if not all_workflows:
            return WorkflowMetrics()

        completed_workflows = [w for w in all_workflows if w.state in [WorkflowState.COMPLETED, WorkflowState.FAILED]]
        successful_workflows = [w for w in completed_workflows if w.success]

        # Calculate metrics
        total_workflows = len(all_workflows)
        active_workflows = len(self.active_workflows)
        completed_count = len(completed_workflows)
        failed_count = len([w for w in completed_workflows if not w.success])

        avg_duration = 0.0
        if completed_workflows:
            avg_duration = sum(w.duration for w in completed_workflows) / len(completed_workflows)

        success_rate = 0.0
        if completed_workflows:
            success_rate = len(successful_workflows) / len(completed_workflows)

        # Most common workflow type
        type_counts = defaultdict(int)
        for workflow in all_workflows:
            type_counts[workflow.type] += 1

        most_common_type = max(type_counts.keys(), key=lambda t: type_counts[t]) if type_counts else None

        # Most common steps
        step_counts = defaultdict(int)
        for workflow in all_workflows:
            for step in workflow.steps:
                step_counts[step] += 1

        most_common_steps = sorted(step_counts.keys(), key=lambda s: step_counts[s], reverse=True)[:5]

        return WorkflowMetrics(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            completed_workflows=completed_count,
            failed_workflows=failed_count,
            avg_duration=avg_duration,
            success_rate=success_rate,
            most_common_type=most_common_type,
            most_common_steps=most_common_steps,
        )

    def get_patterns(self, min_frequency: int | None = None) -> list[WorkflowPattern]:
        """Get learned workflow patterns."""
        threshold = min_frequency or self.min_pattern_frequency
        return [pattern for pattern in self.patterns.values() if pattern.frequency >= threshold]

    def get_active_workflows(self) -> list[WorkflowInstance]:
        """Get currently active workflows."""
        self._cleanup_expired_workflows()
        return list(self.active_workflows.values())

    def get_workflow_history(self, limit: int = 20) -> list[WorkflowInstance]:
        """Get recent workflow history."""
        return self.completed_workflows[-limit:]

    async def _emit_workflow_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit workflow-related events."""
        if self.event_bus:
            try:
                event = UserActionEvent(action_type=f"workflow_{event_type}", action_details=data)
                await self.event_bus.publish(event)
            except RuntimeError:
                # No event loop running - skip event emission
                pass


# Convenience functions for easy usage
_detector_instance: SimpleWorkflowDetector | None = None


def initialize_workflow_detector(event_bus: EventBus | None = None) -> SimpleWorkflowDetector:
    """Initialize the global workflow detector."""
    global _detector_instance
    _detector_instance = SimpleWorkflowDetector(event_bus)
    return _detector_instance


def get_workflow_detector() -> SimpleWorkflowDetector | None:
    """Get the global workflow detector instance."""
    return _detector_instance


def get_current_workflows() -> list[WorkflowInstance]:
    """Get currently active workflows."""
    if _detector_instance:
        return _detector_instance.get_active_workflows()
    return []


def get_workflow_metrics() -> WorkflowMetrics | None:
    """Get workflow metrics."""
    if _detector_instance:
        return _detector_instance.get_metrics()
    return None


def get_workflow_suggestions(current_steps: list[WorkflowStep]) -> list[WorkflowStep]:
    """Get suggested next workflow steps."""
    if _detector_instance:
        return _detector_instance.get_workflow_suggestions(current_steps)
    return []


def detect_workflow_anomalies() -> list[dict[str, Any]]:
    """Detect workflow anomalies."""
    if _detector_instance:
        return _detector_instance.detect_anomalies()
    return []
