"""Tests for simplified event types."""

from a1.core import (
    FileChangeEvent,
    LearningEvent,
    SystemEvent,
    ToolUseEvent,
    UserActionEvent,
)


class TestEventTypes:
    """Test cases for event types."""

    def test_tool_use_event(self):
        """Test ToolUseEvent creation and serialization."""
        event = ToolUseEvent(tool_name="test_tool", success=True, duration_ms=50.0)

        assert event.get_event_type() == "tool_use"
        assert event.tool_name == "test_tool"
        assert event.success is True
        assert event.duration_ms == 50.0

        # Test serialization
        data = event.to_dict()
        assert data["type"] == "tool_use"
        assert data["data"]["tool_name"] == "test_tool"
        assert data["data"]["success"] is True
        assert data["data"]["duration_ms"] == 50.0

    def test_file_change_event(self):
        """Test FileChangeEvent creation and serialization."""
        event = FileChangeEvent(file_path="/test/path.py", change_type="modified")

        assert event.get_event_type() == "file_change"
        assert event.file_path == "/test/path.py"
        assert event.change_type == "modified"

        # Test serialization
        data = event.to_dict()
        assert data["type"] == "file_change"
        assert data["data"]["file_path"] == "/test/path.py"
        assert data["data"]["change_type"] == "modified"

    def test_user_action_event(self):
        """Test UserActionEvent creation and serialization."""
        event = UserActionEvent(action_type="command", action_details={"command": "test", "args": ["arg1", "arg2"]})

        assert event.get_event_type() == "user_action"
        assert event.action_type == "command"
        assert event.action_details["command"] == "test"

        # Test serialization
        data = event.to_dict()
        assert data["type"] == "user_action"
        assert data["data"]["action_type"] == "command"
        assert data["data"]["action_details"]["command"] == "test"

    def test_system_event(self):
        """Test SystemEvent creation and serialization."""
        event = SystemEvent(event_name="startup", severity="info", component="core")

        assert event.get_event_type() == "system"
        assert event.event_name == "startup"
        assert event.severity == "info"
        assert event.component == "core"

        # Test serialization
        data = event.to_dict()
        assert data["type"] == "system"
        assert data["data"]["event_name"] == "startup"
        assert data["data"]["severity"] == "info"
        assert data["data"]["component"] == "core"

    def test_learning_event(self):
        """Test LearningEvent creation and serialization."""
        event = LearningEvent(learning_type="pattern_detected", confidence=0.85)

        assert event.get_event_type() == "learning"
        assert event.learning_type == "pattern_detected"
        assert event.confidence == 0.85

        # Test serialization
        data = event.to_dict()
        assert data["type"] == "learning"
        assert data["data"]["learning_type"] == "pattern_detected"
        assert data["data"]["confidence"] == 0.85

    def test_event_base_fields(self):
        """Test base event fields."""
        event = SystemEvent(event_name="test")

        # Check base fields
        assert event.id is not None
        assert len(event.id) > 0
        assert event.timestamp > 0
        assert event.source == "quaestor.v2_1"

        # Test serialization includes base fields
        data = event.to_dict()
        assert "id" in data
        assert "timestamp" in data
        assert "source" in data
        assert data["source"] == "quaestor.v2_1"

    def test_event_defaults(self):
        """Test event default values."""
        # Test with minimal parameters
        tool_event = ToolUseEvent()
        assert tool_event.tool_name == ""
        assert tool_event.success is True
        assert tool_event.duration_ms is None

        file_event = FileChangeEvent()
        assert file_event.file_path == ""
        assert file_event.change_type == "modified"

        user_event = UserActionEvent()
        assert user_event.action_type == "command"
        assert user_event.action_details == {}

        system_event = SystemEvent()
        assert system_event.event_name == ""
        assert system_event.severity == "info"
        assert system_event.component == ""

        learning_event = LearningEvent()
        assert learning_event.learning_type == "pattern_detected"
        assert learning_event.confidence == 0.0
