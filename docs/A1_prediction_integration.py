"""Example: V2.1 Prediction Integration with Event Bus

Demonstrates how the simplified prediction engine integrates with the V2.1 event bus
for real-time learning and prediction.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quaestor.v2_1.core.event_bus import EventBus
from quaestor.v2_1.core.events import FileChangeEvent, ToolUseEvent
from quaestor.v2_1.extensions.prediction import (
    get_prediction_engine,
    predict_next_file,
    predict_next_tool,
)


async def setup_prediction_listener():
    """Set up event bus listener for prediction learning."""

    # Get the prediction engine
    prediction_engine = get_prediction_engine()

    # Create event bus
    event_bus = EventBus()

    # Register prediction handlers
    async def handle_tool_use(event: ToolUseEvent):
        """Handle tool use events for learning."""
        print(f"📝 Learning from tool use: {event.tool_name} (success: {event.success})")
        prediction_engine.handle_tool_use_event(event)

        # Show current predictions after learning
        if event.success:
            predictions = predict_next_tool(max_predictions=2)
            if predictions:
                print("🔮 Next tool predictions:")
                for pred in predictions:
                    print(f"   - {pred.value} (confidence: {pred.confidence:.2f})")
            else:
                print("🔮 No tool predictions yet (building patterns...)")

    async def handle_file_change(event: FileChangeEvent):
        """Handle file change events for learning."""
        print(f"📂 Learning from file change: {event.file_path}")
        prediction_engine.handle_file_change(event.file_path)

        # Show current file predictions
        predictions = predict_next_file(event.file_path, max_predictions=2)
        if predictions:
            print(f"🔮 Next file predictions from {Path(event.file_path).name}:")
            for pred in predictions:
                print(f"   - {Path(pred.value).name} (confidence: {pred.confidence:.2f})")
        else:
            print("🔮 No file predictions yet (building workflow patterns...)")

    # Subscribe to events
    event_bus.subscribe(handle_tool_use, "tool_use")
    event_bus.subscribe(handle_file_change, "file_change")

    return event_bus, prediction_engine


async def simulate_development_workflow():
    """Simulate a typical development workflow."""

    print("🚀 Starting V2.1 Prediction Integration Demo")
    print("=" * 50)

    # Set up prediction system
    event_bus, prediction_engine = await setup_prediction_listener()

    # Start event bus
    await event_bus.start()

    try:
        print("\n📋 Simulating development workflow...")

        # Simulate a typical development session
        workflow_steps = [
            # First cycle: edit -> test -> commit
            ("tool_use", "edit", "main.py"),
            ("file_change", None, "main.py"),
            ("tool_use", "test", None),
            ("file_change", None, "test_main.py"),
            ("tool_use", "commit", None),

            # Second cycle: edit -> test -> commit (reinforcing pattern)
            ("tool_use", "edit", "utils.py"),
            ("file_change", None, "utils.py"),
            ("tool_use", "test", None),
            ("file_change", None, "test_utils.py"),
            ("tool_use", "commit", None),

            # Third cycle: edit -> test (pattern should predict commit)
            ("tool_use", "edit", "config.py"),
            ("file_change", None, "config.py"),
            ("tool_use", "test", None),
            ("file_change", None, "test_config.py"),
        ]

        for i, (event_type, tool_name, file_path) in enumerate(workflow_steps):
            print(f"\n--- Step {i+1}: {event_type} ---")

            if event_type == "tool_use":
                event = ToolUseEvent(
                    tool_name=tool_name,
                    success=True,
                    duration_ms=100.0
                )
                await event_bus.publish(event)

            elif event_type == "file_change":
                event = FileChangeEvent(
                    file_path=file_path,
                    change_type="modified"
                )
                await event_bus.publish(event)

            # Small delay for realism
            await asyncio.sleep(0.1)

        # Show final predictions after learning
        print("\n" + "=" * 50)
        print("🎯 Final Prediction Results")
        print("=" * 50)

        # Tool predictions
        tool_predictions = predict_next_tool(max_predictions=3)
        print("\n🔧 Next Tool Predictions:")
        if tool_predictions:
            for i, pred in enumerate(tool_predictions, 1):
                print(f"   {i}. {pred.value} (confidence: {pred.confidence:.2f}) - {pred.explanation}")
        else:
            print("   No predictions available")

        # File predictions from current context
        file_predictions = predict_next_file("config.py", max_predictions=3)
        print("\n📁 Next File Predictions from config.py:")
        if file_predictions:
            for i, pred in enumerate(file_predictions, 1):
                print(f"   {i}. {pred.value} (confidence: {pred.confidence:.2f}) - {pred.explanation}")
        else:
            print("   No predictions available")

        # Show learned patterns summary
        summary = prediction_engine.get_summary()
        print("\n📊 Learning Summary:")
        print(f"   Tool patterns learned: {summary['tool_patterns']}")
        print(f"   File patterns learned: {summary['file_patterns']}")
        print(f"   Recent tools tracked: {summary['recent_tools']}")
        print(f"   Recent files tracked: {summary['recent_files']}")

    finally:
        # Stop event bus
        await event_bus.stop()
        print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(simulate_development_workflow())
