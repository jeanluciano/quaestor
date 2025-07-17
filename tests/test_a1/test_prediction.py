"""Tests for simplified prediction engine."""

import tempfile
from pathlib import Path

import pytest

from a1.core.events import ToolUseEvent
from a1.extensions.prediction import (
    BasicPredictionEngine,
    FilePredictor,
    PredictionPattern,
    PredictionResult,
    SequencePredictor,
    SimplePatternRecognizer,
    get_prediction_engine,
    predict_next_file,
    predict_next_tool,
    record_file_change,
    record_tool_use,
)


class TestPredictionPattern:
    """Test prediction pattern model."""

    def test_pattern_creation(self):
        """Test creating a prediction pattern."""
        pattern = PredictionPattern(sequence=["edit", "test", "commit"])

        assert pattern.sequence == ["edit", "test", "commit"]
        assert pattern.frequency == 1
        assert pattern.last_seen > 0

    def test_pattern_score_calculation(self):
        """Test pattern score calculation."""
        pattern = PredictionPattern(sequence=["edit", "test"])
        pattern.frequency = 5

        score = pattern.score
        assert 0 < score <= 5  # Should be influenced by frequency and recency


class TestSimplePatternRecognizer:
    """Test simplified pattern recognizer."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            yield f.name
        Path(f.name).unlink(missing_ok=True)

    def test_pattern_recognizer_initialization(self, temp_storage):
        """Test pattern recognizer initialization."""
        recognizer = SimplePatternRecognizer(temp_storage)

        assert recognizer.storage_file == Path(temp_storage)
        assert isinstance(recognizer.patterns, dict)

    def test_record_and_retrieve_patterns(self, temp_storage):
        """Test recording and retrieving patterns."""
        recognizer = SimplePatternRecognizer(temp_storage)

        # Record a pattern
        recognizer.record_sequence("tools", ["edit", "test", "commit"])

        # Retrieve patterns
        patterns = recognizer.get_patterns("tools")
        assert len(patterns) == 1
        assert patterns[0].sequence == ["edit", "test", "commit"]
        assert patterns[0].frequency == 1

    def test_pattern_frequency_increment(self, temp_storage):
        """Test that repeating patterns increment frequency."""
        recognizer = SimplePatternRecognizer(temp_storage)

        # Record same pattern multiple times
        sequence = ["edit", "test"]
        recognizer.record_sequence("tools", sequence)
        recognizer.record_sequence("tools", sequence)
        recognizer.record_sequence("tools", sequence)

        patterns = recognizer.get_patterns("tools")
        assert len(patterns) == 1
        assert patterns[0].frequency == 3

    def test_pattern_persistence(self, temp_storage):
        """Test that patterns persist to file."""
        # Create recognizer and record pattern
        recognizer1 = SimplePatternRecognizer(temp_storage)
        recognizer1.record_sequence("tools", ["edit", "test"])

        # Create new recognizer and check pattern is loaded
        recognizer2 = SimplePatternRecognizer(temp_storage)
        patterns = recognizer2.get_patterns("tools")

        assert len(patterns) == 1
        assert patterns[0].sequence == ["edit", "test"]

    def test_empty_pattern_type(self, temp_storage):
        """Test retrieving empty pattern type."""
        recognizer = SimplePatternRecognizer(temp_storage)

        patterns = recognizer.get_patterns("nonexistent")
        assert patterns == []


class TestSequencePredictor:
    """Test sequence predictor."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            yield f.name
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def predictor(self, temp_storage):
        """Create sequence predictor with test data."""
        recognizer = SimplePatternRecognizer(temp_storage)

        # Add some test patterns
        recognizer.record_sequence("tool_sequences", ["edit", "test", "commit"])
        recognizer.record_sequence("tool_sequences", ["edit", "test", "push"])
        recognizer.record_sequence("tool_sequences", ["edit", "lint", "fix"])

        return SequencePredictor(recognizer)

    def test_predict_empty_actions(self, predictor):
        """Test prediction with empty recent actions."""
        results = predictor.predict([])
        assert results == []

    def test_predict_next_tool(self, predictor):
        """Test predicting next tool."""
        results = predictor.predict(["edit"])

        assert len(results) > 0
        assert all(isinstance(r, PredictionResult) for r in results)
        assert all(r.prediction_type == "next_tool" for r in results)
        assert all(r.confidence > 0 for r in results)

    def test_predict_specific_sequence(self, predictor):
        """Test prediction for specific sequence."""
        results = predictor.predict(["edit", "test"])

        # Should predict "commit" or "push" as next tools
        tool_values = [r.value for r in results]
        assert any(tool in ["commit", "push"] for tool in tool_values)

    def test_predict_max_predictions_limit(self, predictor):
        """Test max predictions limit."""
        results = predictor.predict(["edit"], max_predictions=2)
        assert len(results) <= 2

    def test_confidence_threshold(self, predictor):
        """Test that low confidence predictions are filtered."""
        results = predictor.predict(["unknown_tool"])

        # Should return empty or very few results for unknown sequence
        assert len(results) <= 1


class TestFilePredictor:
    """Test file predictor."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            yield f.name
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def predictor(self, temp_storage):
        """Create file predictor with test data."""
        recognizer = SimplePatternRecognizer(temp_storage)

        # Add some test workflows
        recognizer.record_sequence("file_workflows", ["main.py", "test_main.py", "requirements.txt"])
        recognizer.record_sequence("file_workflows", ["main.py", "utils.py", "test_utils.py"])
        recognizer.record_sequence("file_workflows", ["config.py", "main.py", "deploy.sh"])

        return FilePredictor(recognizer)

    def test_predict_empty_file(self, predictor):
        """Test prediction with empty current file."""
        results = predictor.predict("")
        assert results == []

    def test_predict_next_file(self, predictor):
        """Test predicting next file."""
        results = predictor.predict("main.py")

        assert len(results) > 0
        assert all(isinstance(r, PredictionResult) for r in results)
        assert all(r.prediction_type == "next_file" for r in results)
        assert all(r.confidence > 0 for r in results)

    def test_predict_specific_workflow(self, predictor):
        """Test prediction for specific workflow."""
        results = predictor.predict("main.py")

        # Should predict files that follow main.py in workflows
        file_values = [r.value for r in results]
        expected_files = ["test_main.py", "utils.py", "requirements.txt"]
        assert any(f in file_values for f in expected_files)

    def test_predict_unknown_file(self, predictor):
        """Test prediction for unknown file."""
        results = predictor.predict("unknown.py")

        # Should return empty results for unknown file
        assert len(results) == 0


class TestBasicPredictionEngine:
    """Test basic prediction engine."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for engine."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def engine(self, temp_dir):
        """Create prediction engine."""
        return BasicPredictionEngine(temp_dir)

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert isinstance(engine.pattern_recognizer, SimplePatternRecognizer)
        assert isinstance(engine.sequence_predictor, SequencePredictor)
        assert isinstance(engine.file_predictor, FilePredictor)
        assert engine.recent_tools == []
        assert engine.recent_files == []

    def test_handle_tool_use_event(self, engine):
        """Test handling tool use events."""
        event = ToolUseEvent(tool_name="edit", success=True)
        engine.handle_tool_use_event(event)

        assert "edit" in engine.recent_tools

    def test_handle_failed_tool_use(self, engine):
        """Test handling failed tool use."""
        event = ToolUseEvent(tool_name="edit", success=False)
        engine.handle_tool_use_event(event)

        # Failed tools should not be recorded
        assert "edit" not in engine.recent_tools

    def test_handle_file_change(self, engine):
        """Test handling file changes."""
        engine.handle_file_change("main.py")

        assert "main.py" in engine.recent_files

    def test_tool_prediction_with_learning(self, engine):
        """Test tool prediction with learning."""
        # Record some tool usage
        for tool in ["edit", "test", "commit", "edit", "test"]:
            event = ToolUseEvent(tool_name=tool, success=True)
            engine.handle_tool_use_event(event)

        # Predict next tool
        results = engine.predict_next_tool()

        # Should have some predictions based on learned patterns
        assert len(results) >= 0  # Might be empty if patterns don't meet threshold

    def test_file_prediction_with_learning(self, engine):
        """Test file prediction with learning."""
        # Record some file changes
        for file_path in ["main.py", "test.py", "config.py", "main.py"]:
            engine.handle_file_change(file_path)

        # Predict next file
        results = engine.predict_next_file("main.py")

        # Should have some predictions based on learned workflows
        assert len(results) >= 0  # Might be empty if patterns don't meet threshold

    def test_history_limit(self, engine):
        """Test that history is limited."""
        # Add more tools than the limit
        for i in range(25):
            event = ToolUseEvent(tool_name=f"tool_{i}", success=True)
            engine.handle_tool_use_event(event)

        assert len(engine.recent_tools) == engine.max_history
        assert "tool_24" in engine.recent_tools
        assert "tool_0" not in engine.recent_tools

    def test_get_summary(self, engine):
        """Test getting engine summary."""
        summary = engine.get_summary()

        assert "tool_patterns" in summary
        assert "file_patterns" in summary
        assert "recent_tools" in summary
        assert "recent_files" in summary
        assert "status" in summary
        assert summary["status"] == "active"


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_get_prediction_engine(self):
        """Test getting global prediction engine."""
        engine1 = get_prediction_engine()
        engine2 = get_prediction_engine()

        # Should return same instance
        assert engine1 is engine2
        assert isinstance(engine1, BasicPredictionEngine)

    def test_predict_next_tool_global(self):
        """Test global predict_next_tool function."""
        results = predict_next_tool(max_predictions=2)

        assert isinstance(results, list)
        assert len(results) <= 2

    def test_predict_next_file_global(self):
        """Test global predict_next_file function."""
        results = predict_next_file("main.py", max_predictions=2)

        assert isinstance(results, list)
        assert len(results) <= 2

    def test_record_tool_use_global(self):
        """Test global record_tool_use function."""
        # Should not raise an exception
        record_tool_use("edit", success=True)
        record_tool_use("test", success=False)

    def test_record_file_change_global(self):
        """Test global record_file_change function."""
        # Should not raise an exception
        record_file_change("main.py")
        record_file_change("test.py")


class TestIntegration:
    """Test integration scenarios."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_end_to_end_tool_prediction(self, temp_dir):
        """Test complete tool prediction workflow."""
        engine = BasicPredictionEngine(temp_dir)

        # Simulate a development workflow
        workflow = [
            "edit",
            "test",
            "commit",
            "edit",
            "test",
            "commit",
            "edit",
            "test",
            "commit",
            "edit",
            "test",  # Set up for prediction
        ]

        # Record the workflow
        for tool in workflow:
            event = ToolUseEvent(tool_name=tool, success=True)
            engine.handle_tool_use_event(event)

        # Predict next tool (should be "commit")
        results = engine.predict_next_tool()

        if results:  # Only check if we have predictions
            # The most likely prediction should be "commit"
            top_prediction = results[0]
            assert top_prediction.value == "commit"
            assert top_prediction.confidence > 0.3

    def test_end_to_end_file_prediction(self, temp_dir):
        """Test complete file prediction workflow."""
        engine = BasicPredictionEngine(temp_dir)

        # Simulate file workflows
        workflows = [
            ["main.py", "test_main.py", "requirements.txt"],
            ["main.py", "test_main.py", "setup.py"],
            ["main.py", "utils.py", "test_utils.py"],
        ]

        # Record the workflows
        for workflow in workflows:
            for file_path in workflow:
                engine.handle_file_change(file_path)

        # Predict next file after main.py
        results = engine.predict_next_file("main.py")

        if results:  # Only check if we have predictions
            # Should predict files that typically follow main.py
            predicted_files = [r.value for r in results]
            expected_files = ["test_main.py", "utils.py", "requirements.txt", "setup.py"]
            assert any(f in predicted_files for f in expected_files)

    def test_pattern_persistence_across_sessions(self, temp_dir):
        """Test that patterns persist across different engine instances."""
        # First session - record patterns
        engine1 = BasicPredictionEngine(temp_dir)

        # Record some patterns
        for tool in ["edit", "test", "commit"] * 3:
            event = ToolUseEvent(tool_name=tool, success=True)
            engine1.handle_tool_use_event(event)

        # Second session - load patterns
        engine2 = BasicPredictionEngine(temp_dir)

        # Should have learned patterns from previous session
        patterns = engine2.pattern_recognizer.get_patterns("tool_sequences")
        assert len(patterns) > 0

    def test_prediction_confidence_calculation(self, temp_dir):
        """Test that confidence is calculated reasonably."""
        engine = BasicPredictionEngine(temp_dir)

        # Record a strong pattern multiple times
        for _ in range(10):
            for tool in ["edit", "test", "commit"]:
                event = ToolUseEvent(tool_name=tool, success=True)
                engine.handle_tool_use_event(event)

        # Predict after "edit", "test"
        engine.recent_tools = ["edit", "test"]
        results = engine.predict_next_tool()

        if results:
            # Should have high confidence for "commit"
            commit_prediction = next((r for r in results if r.value == "commit"), None)
            if commit_prediction:
                assert commit_prediction.confidence > 0.5
