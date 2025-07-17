"""Tests for simplified context management system."""

import time

from a1.core.context import (
    ContextConfiguration,
    ContextManager,
    ContextSession,
    ContextState,
    ContextSwitcher,
    ContextType,
    RelevanceScorer,
)


class TestContextState:
    """Test cases for ContextState."""

    def test_context_state_creation(self):
        """Test basic context state creation."""
        context = ContextState(context_type=ContextType.DEVELOPMENT, current_task="implementing feature")

        assert context.context_type == ContextType.DEVELOPMENT
        assert context.current_task == "implementing feature"
        assert context.relevant_files == []
        assert context.relevance_scores == {}
        assert context.id is not None
        assert context.created_at > 0

    def test_add_relevant_file(self):
        """Test adding files to context."""
        context = ContextState()

        context.add_relevant_file("/path/to/file.py", 0.8)

        assert "/path/to/file.py" in context.relevant_files
        assert context.relevance_scores["/path/to/file.py"] == 0.8

    def test_remove_relevant_file(self):
        """Test removing files from context."""
        context = ContextState()
        context.add_relevant_file("/path/to/file.py", 0.8)

        context.remove_relevant_file("/path/to/file.py")

        assert "/path/to/file.py" not in context.relevant_files
        assert "/path/to/file.py" not in context.relevance_scores

    def test_get_top_files(self):
        """Test getting top relevant files."""
        context = ContextState()
        context.add_relevant_file("file1.py", 0.9)
        context.add_relevant_file("file2.py", 0.7)
        context.add_relevant_file("file3.py", 0.8)

        top_files = context.get_top_files(count=2)

        assert len(top_files) == 2
        assert top_files[0] == "file1.py"  # Highest score
        assert top_files[1] == "file3.py"  # Second highest

    def test_update_relevance_score(self):
        """Test updating relevance scores."""
        context = ContextState()
        context.add_relevant_file("file.py", 0.5)

        old_updated = context.last_updated
        time.sleep(0.01)  # Ensure time difference
        context.update_relevance_score("file.py", 0.9)

        assert context.relevance_scores["file.py"] == 0.9
        assert context.last_updated > old_updated


class TestContextConfiguration:
    """Test cases for ContextConfiguration."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = ContextConfiguration()

        assert config.max_context_size == 50
        assert config.relevance_threshold == 0.3
        assert config.auto_optimization is True
        assert config.context_switch_timeout == 0.5
        assert config.cache_size == 100

    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = ContextConfiguration(max_context_size=25, relevance_threshold=0.5, auto_optimization=False)

        assert config.max_context_size == 25
        assert config.relevance_threshold == 0.5
        assert config.auto_optimization is False


class TestContextSession:
    """Test cases for ContextSession."""

    def test_session_creation(self):
        """Test session creation."""
        session = ContextSession()

        assert session.id is not None
        assert session.current_context is None
        assert session.context_history == []
        assert isinstance(session.configuration, ContextConfiguration)

    def test_switch_context(self):
        """Test context switching in session."""
        session = ContextSession()
        context1 = ContextState(context_type=ContextType.DEVELOPMENT)
        context2 = ContextState(context_type=ContextType.TESTING)

        session.switch_context(context1)
        assert session.current_context == context1
        assert len(session.context_history) == 0

        session.switch_context(context2)
        assert session.current_context == context2
        assert session.context_history == [context1.id]

    def test_context_history(self):
        """Test context history tracking."""
        session = ContextSession()
        contexts = [ContextState() for _ in range(5)]

        for context in contexts:
            session.switch_context(context)

        history = session.get_context_history(count=3)
        assert len(history) == 3
        # Should get most recent 3 (excluding current)
        assert history == [contexts[1].id, contexts[2].id, contexts[3].id]


class TestRelevanceScorer:
    """Test cases for RelevanceScorer."""

    def test_scorer_creation(self):
        """Test scorer creation."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)

        assert scorer.config == config
        assert scorer._file_access_cache == {}
        assert scorer._file_edit_cache == {}

    def test_score_file_basic(self):
        """Test basic file scoring."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)
        context = ContextState(context_type=ContextType.DEVELOPMENT)

        score = scorer.score_file("/path/to/file.py", context)

        assert 0 <= score <= 1
        assert isinstance(score, float)

    def test_task_relevance_development(self):
        """Test task relevance for development context."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)
        context = ContextState(context_type=ContextType.DEVELOPMENT)

        # Python files should have high relevance in development
        py_score = scorer._calculate_task_relevance("/path/file.py", context)
        md_score = scorer._calculate_task_relevance("/path/file.md", context)

        assert py_score > md_score
        assert py_score == 0.9
        assert md_score == 0.6

    def test_task_relevance_testing(self):
        """Test task relevance for testing context."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)
        context = ContextState(context_type=ContextType.TESTING)

        # Test files should have high relevance in testing
        test_score = scorer._calculate_task_relevance("/path/test_file.py", context)
        config_score = scorer._calculate_task_relevance("/path/config.json", context)

        assert test_score == 0.9
        assert config_score == 0.7

    def test_update_access_time(self):
        """Test updating file access time."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)

        file_path = "/path/to/file.py"
        before_time = time.time()
        scorer.update_access_time(file_path)
        after_time = time.time()

        access_time = scorer._file_access_cache[file_path]
        assert before_time <= access_time <= after_time

    def test_increment_edit_count(self):
        """Test incrementing edit count."""
        config = ContextConfiguration()
        scorer = RelevanceScorer(config)

        file_path = "/path/to/file.py"

        scorer.increment_edit_count(file_path)
        assert scorer._file_edit_cache[file_path] == 1

        scorer.increment_edit_count(file_path)
        assert scorer._file_edit_cache[file_path] == 2


class TestContextSwitcher:
    """Test cases for ContextSwitcher."""

    def test_switcher_creation(self):
        """Test switcher creation."""
        config = ContextConfiguration()
        switcher = ContextSwitcher(config)

        assert switcher.config == config
        assert isinstance(switcher.scorer, RelevanceScorer)

    def test_switch_context_new_session(self):
        """Test switching context in new session."""
        config = ContextConfiguration()
        switcher = ContextSwitcher(config)
        session = ContextSession(configuration=config)

        new_context = switcher.switch_context(session, ContextType.TESTING, "running tests")

        assert new_context.context_type == ContextType.TESTING
        assert new_context.current_task == "running tests"
        assert session.current_context == new_context

    def test_switch_context_with_file_transfer(self):
        """Test context switching with file transfer."""
        config = ContextConfiguration()
        switcher = ContextSwitcher(config)
        session = ContextSession(configuration=config)

        # Create initial context with files
        initial_context = ContextState(context_type=ContextType.DEVELOPMENT)
        initial_context.add_relevant_file("file1.py", 0.9)
        initial_context.add_relevant_file("file2.py", 0.4)  # Below threshold
        session.switch_context(initial_context)

        # Switch to testing context
        new_context = switcher.switch_context(session, ContextType.TESTING, "running tests")

        # Should transfer high-relevance files
        assert "file1.py" in new_context.relevant_files
        # Low relevance files might not transfer depending on re-scoring

    def test_add_file_to_context(self):
        """Test adding file to context."""
        config = ContextConfiguration()
        switcher = ContextSwitcher(config)
        context = ContextState(context_type=ContextType.DEVELOPMENT)

        switcher.add_file_to_context(context, "/path/to/file.py")

        assert "/path/to/file.py" in context.relevant_files
        assert "/path/to/file.py" in context.relevance_scores

    def test_remove_file_from_context(self):
        """Test removing file from context."""
        config = ContextConfiguration()
        switcher = ContextSwitcher(config)
        context = ContextState(context_type=ContextType.DEVELOPMENT)
        context.add_relevant_file("/path/to/file.py", 0.8)

        switcher.remove_file_from_context(context, "/path/to/file.py")

        assert "/path/to/file.py" not in context.relevant_files
        assert "/path/to/file.py" not in context.relevance_scores

    def test_optimize_context(self):
        """Test context optimization."""
        config = ContextConfiguration(max_context_size=2, relevance_threshold=0.5, auto_optimization=True)
        switcher = ContextSwitcher(config)
        context = ContextState()

        # Add files with different scores
        context.add_relevant_file("high_score.py", 0.9)
        context.add_relevant_file("medium_score.py", 0.6)
        context.add_relevant_file("low_score.py", 0.3)  # Below threshold

        switcher.optimize_context(context)

        # Should remove low score file and limit to max size
        assert "low_score.py" not in context.relevant_files
        assert len(context.relevant_files) <= config.max_context_size

    def test_optimize_context_disabled(self):
        """Test context optimization when disabled."""
        config = ContextConfiguration(auto_optimization=False)
        switcher = ContextSwitcher(config)
        context = ContextState()
        context.add_relevant_file("file.py", 0.1)  # Very low score

        switcher.optimize_context(context)

        # Should not remove file when optimization disabled
        assert "file.py" in context.relevant_files


class TestContextManager:
    """Test cases for ContextManager."""

    def test_manager_creation(self):
        """Test manager creation."""
        manager = ContextManager()

        assert isinstance(manager.config, ContextConfiguration)
        assert isinstance(manager.switcher, ContextSwitcher)
        assert manager.sessions == {}

    def test_create_session(self):
        """Test session creation."""
        manager = ContextManager()

        session = manager.create_session(ContextType.DEVELOPMENT)

        assert session.id in manager.sessions
        assert session.current_context is not None
        assert session.current_context.context_type == ContextType.DEVELOPMENT

    def test_get_session(self):
        """Test getting session by ID."""
        manager = ContextManager()
        session = manager.create_session()

        retrieved_session = manager.get_session(session.id)
        assert retrieved_session == session

        # Test non-existent session
        assert manager.get_session("nonexistent") is None

    def test_switch_context_type(self):
        """Test switching context type."""
        manager = ContextManager()
        session = manager.create_session(ContextType.DEVELOPMENT)

        new_context = manager.switch_context_type(session.id, ContextType.TESTING, "running tests")

        assert new_context is not None
        assert new_context.context_type == ContextType.TESTING
        assert session.current_context == new_context

    def test_add_remove_file(self):
        """Test adding and removing files."""
        manager = ContextManager()
        session = manager.create_session()

        # Add file
        success = manager.add_file(session.id, "/path/to/file.py")
        assert success is True
        assert "/path/to/file.py" in session.current_context.relevant_files

        # Remove file
        success = manager.remove_file(session.id, "/path/to/file.py")
        assert success is True
        assert "/path/to/file.py" not in session.current_context.relevant_files

    def test_add_file_invalid_session(self):
        """Test adding file to invalid session."""
        manager = ContextManager()

        success = manager.add_file("nonexistent", "/path/to/file.py")
        assert success is False

    def test_optimize_context(self):
        """Test context optimization."""
        manager = ContextManager()
        session = manager.create_session()

        success = manager.optimize_context(session.id)
        assert success is True

    def test_get_context_info(self):
        """Test getting context information."""
        manager = ContextManager()
        session = manager.create_session(ContextType.DEVELOPMENT)
        manager.add_file(session.id, "/path/to/file.py")

        info = manager.get_context_info(session.id)

        assert info is not None
        assert info["context_type"] == "development"
        assert info["file_count"] == 1
        assert "/path/to/file.py" in info["top_files"]
        assert "context_id" in info
        assert "created_at" in info

    def test_get_context_info_invalid_session(self):
        """Test getting context info for invalid session."""
        manager = ContextManager()

        info = manager.get_context_info("nonexistent")
        assert info is None

    def test_get_stats(self):
        """Test getting context statistics."""
        manager = ContextManager()

        # No sessions
        stats = manager.get_stats()
        assert stats["total_sessions"] == 0
        assert stats["active_sessions"] == 0

        # Create sessions
        session1 = manager.create_session()
        session2 = manager.create_session()
        manager.add_file(session1.id, "/file1.py")
        manager.add_file(session2.id, "/file2.py")

        stats = manager.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 2
        assert stats["avg_files_per_context"] == 1.0


class TestPerformance:
    """Test performance requirements."""

    def test_context_switch_performance(self):
        """Test context switch performance (<500ms)."""
        config = ContextConfiguration()
        manager = ContextManager(config)
        session = manager.create_session(ContextType.DEVELOPMENT)

        # Add some files to make switching more realistic
        for i in range(10):
            manager.add_file(session.id, f"/path/to/file{i}.py")

        start_time = time.time()
        manager.switch_context_type(session.id, ContextType.TESTING, "performance test")
        switch_time = (time.time() - start_time) * 1000  # Convert to ms

        assert switch_time < 500  # Should be under 500ms

    def test_file_addition_performance(self):
        """Test file addition performance."""
        manager = ContextManager()
        session = manager.create_session()

        start_time = time.time()
        for i in range(50):
            manager.add_file(session.id, f"/path/to/file{i}.py")
        add_time = (time.time() - start_time) * 1000

        # Should be fast for bulk operations
        assert add_time < 1000  # Under 1 second for 50 files

    def test_context_optimization_performance(self):
        """Test context optimization performance."""
        config = ContextConfiguration(max_context_size=20)
        manager = ContextManager(config)
        session = manager.create_session()

        # Add many files
        for i in range(100):
            manager.add_file(session.id, f"/path/to/file{i}.py")

        start_time = time.time()
        manager.optimize_context(session.id)
        opt_time = (time.time() - start_time) * 1000

        assert opt_time < 100  # Optimization should be very fast
        assert len(session.current_context.relevant_files) <= config.max_context_size


class TestIntegration:
    """Integration tests for context management."""

    def test_full_workflow(self):
        """Test complete context management workflow."""
        manager = ContextManager()

        # Create session
        session = manager.create_session(ContextType.RESEARCH)

        # Add research files
        manager.add_file(session.id, "/docs/requirements.md")
        manager.add_file(session.id, "/docs/architecture.md")

        # Switch to development
        dev_context = manager.switch_context_type(session.id, ContextType.DEVELOPMENT, "implementing feature")

        # Add development files
        manager.add_file(session.id, "/src/main.py")
        manager.add_file(session.id, "/src/utils.py")

        # Switch to testing
        test_context = manager.switch_context_type(session.id, ContextType.TESTING, "running tests")

        # Verify context transitions
        assert len(session.context_history) == 2  # research -> dev -> test
        assert test_context.context_type == ContextType.TESTING

        # Verify relevant files carried over
        info = manager.get_context_info(session.id)
        assert info["file_count"] > 0

        # Optimize and check
        manager.optimize_context(session.id)
        assert len(session.current_context.relevant_files) <= manager.config.max_context_size
