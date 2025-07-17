"""Simple Workflow Detection Integration Example

Demonstrates how to use the simplified A1 workflow detection system
with event bus integration and pattern learning.
"""

import asyncio

from ..core.event_bus import EventBus
from ..core.events import FileChangeEvent, ToolUseEvent, UserActionEvent
from .workflow import (
    WorkflowStep,
    detect_workflow_anomalies,
    get_workflow_metrics,
    get_workflow_suggestions,
    initialize_workflow_detector,
)


async def main():
    """Example usage of simplified workflow detection."""
    # Initialize event bus and workflow detector
    event_bus = EventBus()
    await event_bus.start()

    # Initialize global workflow detector
    detector = initialize_workflow_detector(event_bus)

    print("🔄 Workflow Detection System Initialized")
    print("=" * 50)

    # Simulate a development workflow
    print("\\n📋 Simulating Feature Development Workflow...")

    # 1. Research phase
    await event_bus.publish(ToolUseEvent(tool_name="WebSearch", success=True, duration_ms=2500))

    await event_bus.publish(ToolUseEvent(tool_name="Read", success=True, duration_ms=1200))

    # 2. Planning phase
    await event_bus.publish(ToolUseEvent(tool_name="TodoWrite", success=True, duration_ms=800))

    # 3. Coding phase
    await event_bus.publish(FileChangeEvent(file_path="src/feature.py", change_type="created"))

    await event_bus.publish(ToolUseEvent(tool_name="Edit", success=True, duration_ms=5000))

    await event_bus.publish(ToolUseEvent(tool_name="Write", success=True, duration_ms=3000))

    # 4. Testing phase
    await event_bus.publish(FileChangeEvent(file_path="tests/test_feature.py", change_type="created"))

    await event_bus.publish(ToolUseEvent(tool_name="Bash", success=True, duration_ms=15000))

    # 5. Commit phase
    await event_bus.publish(UserActionEvent(action_type="git_commit", action_details={"message": "Add new feature"}))

    # Allow events to process
    await asyncio.sleep(0.1)

    # Show current workflow state
    print("\\n📊 Current Workflow Status:")
    active_workflows = detector.get_active_workflows()
    for workflow in active_workflows:
        print(f"  🔄 {workflow.id}")
        print(f"     Type: {workflow.type.value}")
        print(f"     Steps: {len(workflow.steps)} ({[s.value for s in workflow.steps[-3:]]})")
        print(f"     Duration: {workflow.duration:.1f}s")
        print(f"     Files: {len(workflow.files_touched)}")
        print(f"     Tools: {workflow.tools_used}")

    # Complete the workflow manually
    if active_workflows:
        completed = detector.complete_workflow(active_workflows[0].id, success=True)
        print(f"\\n✅ Completed workflow: {completed.id}")

    # Simulate another workflow (bug fix)
    print("\\n🐛 Simulating Bug Fix Workflow...")

    await event_bus.publish(ToolUseEvent(tool_name="Grep", success=True, duration_ms=800))

    await event_bus.publish(FileChangeEvent(file_path="src/bugfix.py", change_type="modified"))

    await event_bus.publish(ToolUseEvent(tool_name="Edit", success=True, duration_ms=2000))

    await event_bus.publish(
        ToolUseEvent(
            tool_name="Bash",
            success=False,  # Test failed
            duration_ms=8000,
        )
    )

    # Allow processing
    await asyncio.sleep(0.1)

    # Show workflow metrics
    print("\\n📈 Workflow Metrics:")
    metrics = get_workflow_metrics()
    if metrics:
        print(f"  Total workflows: {metrics.total_workflows}")
        print(f"  Active workflows: {metrics.active_workflows}")
        print(f"  Completed workflows: {metrics.completed_workflows}")
        print(f"  Success rate: {metrics.success_rate:.1%}")
        print(f"  Average duration: {metrics.avg_duration:.1f}s")
        if metrics.most_common_type:
            print(f"  Most common type: {metrics.most_common_type.value}")
        if metrics.most_common_steps:
            print(f"  Most common steps: {[s.value for s in metrics.most_common_steps[:3]]}")

    # Show workflow suggestions
    print("\\n💡 Workflow Suggestions:")
    current_steps = [WorkflowStep.RESEARCH, WorkflowStep.CODING]
    suggestions = get_workflow_suggestions(current_steps)
    if suggestions:
        print(f"  After {[s.value for s in current_steps]}, consider:")
        for step in suggestions:
            print(f"    • {step.value}")
    else:
        print("  No suggestions available (need more pattern data)")

    # Check for anomalies
    print("\\n⚠️  Anomaly Detection:")
    anomalies = detect_workflow_anomalies()
    if anomalies:
        for anomaly in anomalies:
            print(f"  {anomaly['type']}: {anomaly['message']}")
    else:
        print("  No anomalies detected")

    # Show learned patterns
    print("\\n🧠 Learned Patterns:")
    patterns = detector.get_patterns(min_frequency=1)
    for pattern in patterns[:3]:  # Show top 3
        print(f"  {pattern.type.value}:")
        print(f"    Steps: {[s.value for s in pattern.step_sequence[:5]]}")
        print(f"    Frequency: {pattern.frequency}")
        print(f"    Success rate: {pattern.success_rate:.1%}")
        print(f"    Avg duration: {pattern.avg_duration:.1f}s")

    # Show workflow history
    print("\\n📚 Workflow History:")
    history = detector.get_workflow_history(limit=5)
    for workflow in history:
        status = "✅" if workflow.success else "❌"
        print(f"  {status} {workflow.type.value} - {workflow.step_count} steps, {workflow.duration:.1f}s")

    await event_bus.stop()
    print("\\n🏁 Workflow detection example completed!")


if __name__ == "__main__":
    asyncio.run(main())
