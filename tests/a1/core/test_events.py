"""Tests for A1 event system."""

import pytest
from datetime import datetime

from a1.core.events import Event, ClaudeEvent, QuaestorEvent, ToolUseEvent


class TestEvent:
    """Test base Event class."""
    
    def test_event_is_abstract(self):
        """Test that Event is abstract."""
        with pytest.raises(TypeError):
            Event()
            
    def test_concrete_event_creation(self):
        """Test creating a concrete event."""
        event = ToolUseEvent(tool_name="Read", success=True)
        assert event.timestamp is not None
        assert isinstance(event.timestamp, float)
        assert event.get_event_type() == "tool_use"
        
    def test_event_to_dict(self):
        """Test event serialization."""
        event = ToolUseEvent(tool_name="Edit", duration_ms=150.5)
        data = event.to_dict()
        
        assert "timestamp" in data
        assert isinstance(data["timestamp"], float)
        assert "type" in data
        assert data["type"] == "tool_use"
        assert data["data"]["tool_name"] == "Edit"


class TestClaudeEvent:
    """Test ClaudeEvent class."""
    
    def test_claude_event_creation(self):
        """Test creating a Claude event."""
        event = ClaudeEvent(
            type="post_tool_use",
            data={"tool": "Read", "file_path": "/test.py"}
        )
        
        assert event.type == "post_tool_use"
        assert event.data["tool"] == "Read"
        assert event.source == "claude_code"
        assert event.get_event_type() == "claude_post_tool_use"
        
    def test_claude_event_defaults(self):
        """Test Claude event default values."""
        event = ClaudeEvent()
        
        assert event.type == ""
        assert event.data == {}
        assert event.source == "claude_code"
        assert isinstance(event.timestamp, datetime)
        
    def test_claude_event_to_dict(self):
        """Test Claude event serialization."""
        event = ClaudeEvent(
            type="pre_file_edit",
            data={"file": "test.py", "action": "edit"}
        )
        data = event.to_dict()
        
        assert data["type"] == "claude_pre_file_edit"
        assert data["data"]["hook_type"] == "pre_file_edit"
        assert data["data"]["hook_data"]["file"] == "test.py"
        assert data["source"] == "claude_code"
        assert "timestamp" in data


class TestQuaestorEvent:
    """Test QuaestorEvent class."""
    
    def test_quaestor_event_creation(self):
        """Test creating a Quaestor event."""
        event = QuaestorEvent(
            type="milestone_updated",
            data={"milestone_id": "a1_phase_1", "progress": 75},
            component="milestone_tracker",
            source="quaestor"
        )
        
        assert event.type == "milestone_updated"
        assert event.data["milestone_id"] == "a1_phase_1"
        assert event.component == "milestone_tracker"
        assert event.source == "quaestor"
        assert event.get_event_type() == "quaestor_milestone_updated"
        
    def test_quaestor_event_defaults(self):
        """Test Quaestor event default values."""
        event = QuaestorEvent()
        
        assert event.type == ""
        assert event.data == {}
        assert event.component == ""
        assert event.source == "quaestor"
        
    def test_quaestor_event_to_dict(self):
        """Test Quaestor event serialization."""
        event = QuaestorEvent(
            type="config_changed",
            data={"setting": "debug", "value": True},
            component="config_manager"
        )
        data = event.to_dict()
        
        assert data["type"] == "quaestor_config_changed"
        assert data["data"]["quaestor_type"] == "config_changed"
        assert data["data"]["event_data"]["setting"] == "debug"
        assert data["data"]["component"] == "config_manager"
        assert data["source"] == "quaestor"
        assert "timestamp" in data