"""Tests for A1 intent detection system."""

import pytest
from datetime import datetime, timedelta

from a1.core.events import ClaudeEvent
from a1.core.intent import Intent, IntentDetector


class TestIntent:
    """Test Intent class."""
    
    def test_intent_creation(self):
        """Test creating an intent."""
        intent = Intent(
            intent_type="exploring",
            confidence=0.85,
            evidence={"tool_ratio": 0.8, "indicators_matched": 0.9}
        )
        
        assert intent.type == "exploring"
        assert intent.confidence == 0.85
        assert intent.evidence["tool_ratio"] == 0.8
        assert intent.detected_at is not None
        
    def test_intent_to_dict(self):
        """Test intent serialization."""
        intent = Intent(
            intent_type="implementing",
            confidence=0.95,
            evidence={"edit_count": 5}
        )
        
        data = intent.to_dict()
        assert data["type"] == "implementing"
        assert data["confidence"] == 0.95
        assert data["evidence"]["edit_count"] == 5
        assert "detected_at" in data


class TestIntentDetector:
    """Test IntentDetector class."""
    
    def test_detector_creation(self):
        """Test creating intent detector."""
        detector = IntentDetector(history_size=30, time_window=180)
        
        assert detector.history_size == 30
        assert detector.time_window == timedelta(seconds=180)
        assert detector.current_intent is None
        assert len(detector.event_history) == 0
        
    @pytest.mark.asyncio
    async def test_exploring_intent(self):
        """Test detecting exploring intent."""
        detector = IntentDetector()
        
        # Simulate exploring pattern
        events = [
            ClaudeEvent(type="post_tool_use", data={"tool": "Read", "file": "main.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Grep", "pattern": "function"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Read", "file": "utils.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "LS", "path": "/src"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Glob", "pattern": "*.py"}),
        ]
        
        for event in events:
            intent = await detector.update(event)
            
        assert intent.type == IntentDetector.EXPLORING
        assert intent.confidence >= 0.6
        
    @pytest.mark.asyncio
    async def test_implementing_intent(self):
        """Test detecting implementing intent."""
        detector = IntentDetector()
        
        # Simulate implementing pattern
        events = [
            ClaudeEvent(type="post_tool_use", data={"tool": "Read", "file": "app.py"}),
            ClaudeEvent(type="pre_file_edit", data={"file": "app.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Edit", "file": "app.py"}),
            ClaudeEvent(type="post_file_edit", data={"file": "app.py"}),
        ]
        
        for event in events:
            intent = await detector.update(event)
            
        assert intent.type == IntentDetector.IMPLEMENTING
        assert intent.confidence >= 0.5
        
    @pytest.mark.asyncio
    async def test_debugging_intent(self):
        """Test detecting debugging intent."""
        detector = IntentDetector()
        
        # Simulate debugging pattern
        events = [
            ClaudeEvent(type="test_run", data={"result": "failed"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Read", "file": "test.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Bash", "command": "pytest -v"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Edit", "file": "test.py"}),
        ]
        
        for event in events:
            intent = await detector.update(event)
            
        assert intent.type == IntentDetector.DEBUGGING
        assert intent.confidence >= 0.5
        
    @pytest.mark.asyncio
    async def test_refactoring_intent(self):
        """Test detecting refactoring intent."""
        detector = IntentDetector()
        
        # Simulate refactoring pattern - multiple edits quickly
        base_time = datetime.now()
        events = [
            ClaudeEvent(type="post_tool_use", data={"tool": "MultiEdit", "file": "models.py"}),
            ClaudeEvent(type="post_file_edit", data={"file": "models.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Edit", "file": "views.py"}),
            ClaudeEvent(type="post_file_edit", data={"file": "views.py"}),
            ClaudeEvent(type="post_tool_use", data={"tool": "Edit", "file": "utils.py"}),
            ClaudeEvent(type="post_file_edit", data={"file": "utils.py"}),
        ]
        
        # Set timestamps to be within time constraint
        for i, event in enumerate(events):
            event.timestamp = base_time + timedelta(seconds=i*10)
            
        for event in events:
            intent = await detector.update(event)
            
        assert intent.type == IntentDetector.REFACTORING
        assert intent.confidence >= 0.5
        
    @pytest.mark.asyncio
    async def test_idle_intent(self):
        """Test idle intent when no clear pattern."""
        detector = IntentDetector()
        
        # No events
        intent = await detector.update(ClaudeEvent(type="unknown", data={}))
        
        # Should be idle with low confidence
        assert intent.type == IntentDetector.IDLE
        assert intent.confidence < 0.5
        
    @pytest.mark.asyncio
    async def test_intent_history(self):
        """Test intent history tracking."""
        detector = IntentDetector()
        
        # Generate different intents
        patterns = [
            [ClaudeEvent(type="post_tool_use", data={"tool": "Read"}) for _ in range(5)],
            [ClaudeEvent(type="post_tool_use", data={"tool": "Edit"}) for _ in range(3)],
            [ClaudeEvent(type="test_run", data={}) for _ in range(2)],
        ]
        
        for pattern in patterns:
            for event in pattern:
                await detector.update(event)
                
        history = detector.get_intent_history(limit=5)
        assert len(history) <= 5
        assert all(isinstance(intent, Intent) for intent in history)
        
    @pytest.mark.asyncio
    async def test_time_window_filtering(self):
        """Test that old events are filtered out."""
        detector = IntentDetector(time_window=60)  # 1 minute window
        
        # Add old event
        old_event = ClaudeEvent(type="post_tool_use", data={"tool": "Read"})
        old_event.timestamp = datetime.now() - timedelta(minutes=2)
        await detector.update(old_event)
        
        # Add recent events
        for _ in range(3):
            await detector.update(ClaudeEvent(type="post_tool_use", data={"tool": "Edit"}))
            
        intent = await detector.update(ClaudeEvent(type="post_file_edit", data={}))
        
        # Should detect implementing, not exploring (old event filtered)
        assert intent.type == IntentDetector.IMPLEMENTING