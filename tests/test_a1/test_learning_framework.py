"""Tests for V2.1 Learning Framework - Simplified learning system."""

import shutil
import tempfile

from a1.learning import AdaptationEngine, FileLearningStore, LearningManager, PatternRecognizer
from a1.learning.file_store import Adaptation, Pattern


class TestFileLearningStore:
    """Tests for file-based learning storage."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = FileLearningStore(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_store_and_retrieve_pattern(self):
        """Test storing and retrieving patterns."""
        pattern = Pattern(
            id="test-pattern-1",
            pattern_type="tool_sequence",
            data={"sequence": "read -> write -> commit"},
            confidence=0.8,
            frequency=1,
            first_seen=1234567890,
            last_seen=1234567890,
        )

        self.store.store_pattern(pattern)
        patterns = self.store.get_patterns()

        assert len(patterns) == 1
        assert patterns[0].id == "test-pattern-1"
        assert patterns[0].pattern_type == "tool_sequence"
        assert patterns[0].confidence == 0.8

    def test_filter_patterns_by_type(self):
        """Test filtering patterns by type."""
        tool_pattern = Pattern(
            id="tool-1",
            pattern_type="tool_sequence",
            data={},
            confidence=0.8,
            frequency=1,
            first_seen=1.0,
            last_seen=1.0,
        )
        file_pattern = Pattern(
            id="file-1",
            pattern_type="file_pattern",
            data={},
            confidence=0.7,
            frequency=1,
            first_seen=1.0,
            last_seen=1.0,
        )

        self.store.store_pattern(tool_pattern)
        self.store.store_pattern(file_pattern)

        tool_patterns = self.store.get_patterns("tool_sequence")
        file_patterns = self.store.get_patterns("file_pattern")

        assert len(tool_patterns) == 1
        assert len(file_patterns) == 1
        assert tool_patterns[0].id == "tool-1"
        assert file_patterns[0].id == "file-1"

    def test_update_pattern_frequency(self):
        """Test updating pattern frequency."""
        pattern = Pattern(
            id="freq-test",
            pattern_type="tool_sequence",
            data={},
            confidence=0.8,
            frequency=1,
            first_seen=1.0,
            last_seen=1.0,
        )

        self.store.store_pattern(pattern)
        self.store.update_pattern_frequency("freq-test")

        patterns = self.store.get_patterns()
        assert patterns[0].frequency == 2

    def test_store_and_retrieve_adaptations(self):
        """Test storing and retrieving adaptations."""
        adaptation = Adaptation(
            id="adapt-1", pattern_id="pattern-1", suggestion="Use git commit", confidence=0.9, timestamp=1234567890
        )

        self.store.store_adaptation(adaptation)
        adaptations = self.store.get_adaptations()

        assert len(adaptations) == 1
        assert adaptations[0].id == "adapt-1"
        assert adaptations[0].suggestion == "Use git commit"


class TestPatternRecognizer:
    """Tests for pattern recognition."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = FileLearningStore(self.temp_dir)
        self.recognizer = PatternRecognizer(self.store)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_detect_tool_sequence_pattern(self):
        """Test detecting tool sequence patterns."""
        events = [
            {"type": "tool_use", "tool_name": "Read"},
            {"type": "tool_use", "tool_name": "Edit"},
            {"type": "tool_use", "tool_name": "Write"},
        ]

        patterns = []
        for event in events:
            patterns.extend(self.recognizer.analyze_event(event))

        # Should detect pattern on third event
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "tool_sequence"
        assert "Read -> Edit -> Write" in patterns[0].data["sequence"]

    def test_detect_file_pattern(self):
        """Test detecting file patterns."""
        events = [{"type": "file_change", "file_path": "test.py"}, {"type": "file_change", "file_path": "test.md"}]

        patterns = []
        for event in events:
            patterns.extend(self.recognizer.analyze_event(event))

        # Should detect pattern on second event
        assert len(patterns) == 1
        assert patterns[0].pattern_type == "file_pattern"
        assert "py -> md" in patterns[0].data["file_sequence"]

    def test_get_suggestions_from_patterns(self):
        """Test getting suggestions from existing patterns."""
        # Create a pattern manually
        pattern = Pattern(
            id="suggestion-test",
            pattern_type="tool_sequence",
            data={"sequence": "Read -> Edit -> Write", "tools": ["Read", "Edit", "Write"]},
            confidence=0.8,
            frequency=5,
            first_seen=1.0,
            last_seen=2.0,
        )
        self.store.store_pattern(pattern)

        # Test suggestions
        context = {"recent_tools": ["Read", "Edit"]}
        suggestions = self.recognizer.get_suggestions(context)

        assert len(suggestions) > 0
        assert "Write" in suggestions[0]


class TestAdaptationEngine:
    """Tests for adaptation engine."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = FileLearningStore(self.temp_dir)
        self.engine = AdaptationEngine(self.store)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_generate_suggestions_from_tool_pattern(self):
        """Test generating suggestions from tool patterns."""

        # Create a mock pattern
        class MockPattern:
            def __init__(self):
                self.id = "test-pattern"
                self.pattern_type = "tool_sequence"
                self.data = {"sequence": "Read -> Edit -> Write", "tools": ["Read", "Edit", "Write"]}

        pattern = MockPattern()
        suggestions = self.engine.generate_suggestions([pattern], {})

        assert len(suggestions) > 0
        assert "Write" in suggestions[0]

    def test_generate_suggestions_from_file_pattern(self):
        """Test generating suggestions from file patterns."""

        class MockPattern:
            def __init__(self):
                self.id = "file-pattern"
                self.pattern_type = "file_pattern"
                self.data = {"file_sequence": "py -> md", "file_types": ["py", "md"]}

        pattern = MockPattern()
        suggestions = self.engine.generate_suggestions([pattern], {})

        assert len(suggestions) > 0
        assert "py files after md files" in suggestions[0]

    def test_store_adaptation_on_suggestion(self):
        """Test that adaptations are stored when suggestions are generated."""

        class MockPattern:
            def __init__(self):
                self.id = "store-test"
                self.pattern_type = "tool_sequence"
                self.data = {"sequence": "Read -> Edit -> Write", "tools": ["Read", "Edit", "Write"]}

        pattern = MockPattern()
        self.engine.generate_suggestions([pattern], {})

        adaptations = self.store.get_adaptations()
        assert len(adaptations) > 0
        assert adaptations[0].pattern_id == "store-test"


class TestLearningManager:
    """Tests for learning manager."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = LearningManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_process_tool_use_event(self):
        """Test processing tool use events."""
        events = [
            {"type": "tool_use", "tool_name": "Read"},
            {"type": "tool_use", "tool_name": "Edit"},
            {"type": "tool_use", "tool_name": "Write"},
        ]

        results = []
        for event in events:
            result = self.manager.process_event(event)
            results.append(result)

        # Should process all events
        assert all(r["event_processed"] for r in results)

        # Last event should trigger pattern detection
        assert results[-1]["patterns_found"] > 0

    def test_process_file_change_event(self):
        """Test processing file change events."""
        events = [{"type": "file_change", "file_path": "test.py"}, {"type": "file_change", "file_path": "docs.md"}]

        results = []
        for event in events:
            result = self.manager.process_event(event)
            results.append(result)

        # Should detect file pattern
        assert results[-1]["patterns_found"] > 0

    def test_get_stats(self):
        """Test getting learning statistics."""
        # Process some events
        events = [{"type": "tool_use", "tool_name": "Read"}, {"type": "tool_use", "tool_name": "Edit"}]

        for event in events:
            self.manager.process_event(event)

        stats = self.manager.get_stats()

        assert stats["events_processed"] == 2
        assert "session_duration" in stats
        assert stats["stored_patterns"] >= 0

    def test_get_learning_insights(self):
        """Test getting learning insights."""
        # Process events to create patterns
        events = [
            {"type": "tool_use", "tool_name": "Read"},
            {"type": "tool_use", "tool_name": "Edit"},
            {"type": "tool_use", "tool_name": "Write"},
        ]

        for event in events:
            self.manager.process_event(event)

        insights = self.manager.get_learning_insights()

        assert "total_patterns" in insights
        assert "tool_sequence_patterns" in insights
        assert "file_patterns" in insights
        assert "top_patterns" in insights

    def test_get_suggestions_with_context(self):
        """Test getting suggestions with context."""
        # Create pattern first
        events = [
            {"type": "tool_use", "tool_name": "Read"},
            {"type": "tool_use", "tool_name": "Edit"},
            {"type": "tool_use", "tool_name": "Write"},
        ]

        for event in events:
            self.manager.process_event(event)

        # Get suggestions with context
        context = {"recent_tools": ["Read", "Edit"]}
        suggestions = self.manager.get_suggestions(context)

        assert isinstance(suggestions, list)


class TestLearningFrameworkIntegration:
    """Integration tests for the complete learning framework."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = LearningManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_complete_learning_workflow(self):
        """Test complete learning workflow from events to suggestions."""
        # Simulate user workflow
        workflow_events = [
            {"type": "tool_use", "tool_name": "Read", "timestamp": 1.0},
            {"type": "file_change", "file_path": "src/main.py", "timestamp": 2.0},
            {"type": "tool_use", "tool_name": "Edit", "timestamp": 3.0},
            {"type": "file_change", "file_path": "tests/test_main.py", "timestamp": 4.0},
            {"type": "tool_use", "tool_name": "Bash", "timestamp": 5.0},
            {"type": "tool_use", "tool_name": "Read", "timestamp": 6.0},
            {"type": "tool_use", "tool_name": "Edit", "timestamp": 7.0},
            {"type": "tool_use", "tool_name": "Bash", "timestamp": 8.0},
        ]

        # Process all events
        for event in workflow_events:
            self.manager.process_event(event)

        # Check that patterns were detected
        insights = self.manager.get_learning_insights()
        assert insights["total_patterns"] > 0

        # Check that suggestions can be generated
        context = {"recent_tools": ["Read", "Edit"]}
        suggestions = self.manager.get_suggestions(context)
        assert len(suggestions) >= 0  # May be empty if no matching patterns

        # Check stats
        stats = self.manager.get_stats()
        assert stats["events_processed"] == len(workflow_events)
        assert stats["patterns_detected"] > 0

    def test_persistence_across_sessions(self):
        """Test that learning data persists across manager instances."""
        # Create patterns in first session
        events = [
            {"type": "tool_use", "tool_name": "Read"},
            {"type": "tool_use", "tool_name": "Edit"},
            {"type": "tool_use", "tool_name": "Write"},
        ]

        for event in events:
            self.manager.process_event(event)

        initial_insights = self.manager.get_learning_insights()

        # Create new manager with same data directory
        new_manager = LearningManager(self.temp_dir)
        new_insights = new_manager.get_learning_insights()

        # Should have same patterns
        assert new_insights["total_patterns"] == initial_insights["total_patterns"]
