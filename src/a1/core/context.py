"""Simplified context management for Quaestor A1."""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from uuid import uuid4


class ContextType(Enum):
    """Context types for different work modes."""

    RESEARCH = "research"
    DEVELOPMENT = "development"
    DEBUGGING = "debugging"
    TESTING = "testing"


@dataclass
class ContextState:
    """Represents the current state of a context."""

    id: str = field(default_factory=lambda: str(uuid4()))
    context_type: ContextType = ContextType.DEVELOPMENT
    relevant_files: list[str] = field(default_factory=list)
    current_task: str = ""
    relevance_scores: dict[str, float] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    def update_relevance_score(self, file_path: str, score: float) -> None:
        """Update relevance score for a file."""
        self.relevance_scores[file_path] = score
        self.last_updated = time.time()

    def add_relevant_file(self, file_path: str, score: float = 0.5) -> None:
        """Add a file to the context with relevance score."""
        if file_path not in self.relevant_files:
            self.relevant_files.append(file_path)
        self.update_relevance_score(file_path, score)

    def remove_relevant_file(self, file_path: str) -> None:
        """Remove a file from the context."""
        if file_path in self.relevant_files:
            self.relevant_files.remove(file_path)
        self.relevance_scores.pop(file_path, None)
        self.last_updated = time.time()

    def get_top_files(self, count: int = 5) -> list[str]:
        """Get top N most relevant files."""
        if not self.relevance_scores:
            return self.relevant_files[:count]

        sorted_files = sorted(self.relevance_scores.items(), key=lambda x: x[1], reverse=True)
        return [file_path for file_path, _ in sorted_files[:count]]


@dataclass
class ContextConfiguration:
    """Configuration for context management."""

    max_context_size: int = 50
    relevance_threshold: float = 0.3
    auto_optimization: bool = True
    context_switch_timeout: float = 0.5  # 500ms target
    cache_size: int = 100


@dataclass
class ContextSession:
    """Manages a context session."""

    id: str = field(default_factory=lambda: str(uuid4()))
    current_context: ContextState | None = None
    context_history: list[str] = field(default_factory=list)
    configuration: ContextConfiguration = field(default_factory=ContextConfiguration)
    created_at: float = field(default_factory=time.time)

    def switch_context(self, new_context: ContextState) -> None:
        """Switch to a new context."""
        if self.current_context:
            self.context_history.append(self.current_context.id)
        self.current_context = new_context

    def get_context_history(self, count: int = 10) -> list[str]:
        """Get recent context history."""
        return self.context_history[-count:]


class RelevanceScorer:
    """Simple relevance scoring for context files."""

    def __init__(self, config: ContextConfiguration):
        self.config = config
        self._file_access_cache: dict[str, float] = {}
        self._file_edit_cache: dict[str, int] = {}

    def score_file(self, file_path: str, context_state: ContextState) -> float:
        """Score a file's relevance to the current context.

        Scoring algorithm:
        - Recency: 40% (when was it last accessed)
        - Edit frequency: 30% (how often it's edited)
        - Task relevance: 30% (relevance to current task)
        """
        current_time = time.time()

        # Recency score (40%)
        last_access = self._file_access_cache.get(file_path, current_time - 3600)
        recency_score = max(0, 1 - (current_time - last_access) / 3600)  # 1 hour decay

        # Edit frequency score (30%)
        edit_count = self._file_edit_cache.get(file_path, 0)
        frequency_score = min(1.0, edit_count / 10.0)  # Normalize to 0-1

        # Task relevance score (30%)
        task_score = self._calculate_task_relevance(file_path, context_state)

        # Weighted combination
        final_score = recency_score * 0.4 + frequency_score * 0.3 + task_score * 0.3

        return min(1.0, max(0.0, final_score))

    def _calculate_task_relevance(self, file_path: str, context_state: ContextState) -> float:
        """Calculate task relevance based on file type and context."""
        file_ext = Path(file_path).suffix.lower()

        # Context-specific file type relevance
        if context_state.context_type == ContextType.DEVELOPMENT:
            if file_ext in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".rs"]:
                return 0.9
            elif file_ext in [".md", ".txt", ".rst"]:
                return 0.6
        elif context_state.context_type == ContextType.TESTING:
            if "test" in file_path.lower() or file_ext in [".py", ".js", ".ts"]:
                return 0.9
            elif file_ext in [".json", ".yaml", ".yml"]:
                return 0.7
        elif context_state.context_type == ContextType.DEBUGGING:
            if file_ext in [".py", ".js", ".ts", ".log"]:
                return 0.9
            elif file_ext in [".json", ".yaml", ".yml"]:
                return 0.6
        elif context_state.context_type == ContextType.RESEARCH:
            if file_ext in [".md", ".txt", ".rst", ".pdf"]:
                return 0.9
            elif file_ext in [".py", ".js", ".ts"]:
                return 0.6

        return 0.5  # Default relevance

    def update_access_time(self, file_path: str) -> None:
        """Update file access time."""
        self._file_access_cache[file_path] = time.time()

    def increment_edit_count(self, file_path: str) -> None:
        """Increment edit count for a file."""
        self._file_edit_cache[file_path] = self._file_edit_cache.get(file_path, 0) + 1


class ContextSwitcher:
    """Handles context switching operations."""

    def __init__(self, config: ContextConfiguration):
        self.config = config
        self.scorer = RelevanceScorer(config)

    def switch_context(self, session: ContextSession, new_type: ContextType, reason: str = "") -> ContextState:
        """Switch to a new context type."""
        switch_start = time.time()

        # Create new context
        new_context = ContextState(context_type=new_type, current_task=reason)

        # Transfer relevant files from old context
        if session.current_context:
            self._transfer_relevant_files(session.current_context, new_context)

        # Update session
        session.switch_context(new_context)

        # Performance validation
        switch_time = time.time() - switch_start
        if switch_time > self.config.context_switch_timeout:
            # Log warning but don't fail
            pass

        return new_context

    def _transfer_relevant_files(self, old_context: ContextState, new_context: ContextState) -> None:
        """Transfer relevant files between contexts."""
        # Get top files from old context
        top_files = old_context.get_top_files(count=5)

        # Re-score files for new context and transfer relevant ones
        for file_path in top_files:
            # Use original score if high enough, or re-score
            old_score = old_context.relevance_scores.get(file_path, 0.5)
            if old_score >= 0.7:  # High relevance files transfer directly
                new_context.add_relevant_file(file_path, old_score * 0.9)  # Slight decay
            else:
                # Re-score for new context
                new_score = self.scorer.score_file(file_path, new_context)
                if new_score >= self.config.relevance_threshold:
                    new_context.add_relevant_file(file_path, new_score)

    def add_file_to_context(self, context_state: ContextState, file_path: str) -> None:
        """Add a file to the current context."""
        score = self.scorer.score_file(file_path, context_state)
        context_state.add_relevant_file(file_path, score)
        self.scorer.update_access_time(file_path)

    def remove_file_from_context(self, context_state: ContextState, file_path: str) -> None:
        """Remove a file from the current context."""
        context_state.remove_relevant_file(file_path)

    def optimize_context(self, context_state: ContextState) -> None:
        """Basic context optimization."""
        if not self.config.auto_optimization:
            return

        # Remove files below threshold
        files_to_remove = []
        for file_path in context_state.relevant_files:
            score = context_state.relevance_scores.get(file_path, 0)
            if score < self.config.relevance_threshold:
                files_to_remove.append(file_path)

        for file_path in files_to_remove:
            context_state.remove_relevant_file(file_path)

        # Limit context size
        if len(context_state.relevant_files) > self.config.max_context_size:
            # Keep only top files
            top_files = context_state.get_top_files(self.config.max_context_size)
            files_to_remove = [f for f in context_state.relevant_files if f not in top_files]
            for file_path in files_to_remove:
                context_state.remove_relevant_file(file_path)


class ContextManager:
    """Main context management orchestrator."""

    def __init__(self, config: ContextConfiguration | None = None):
        self.config = config or ContextConfiguration()
        self.switcher = ContextSwitcher(self.config)
        self.sessions: dict[str, ContextSession] = {}

    def create_session(self, initial_context_type: ContextType = ContextType.DEVELOPMENT) -> ContextSession:
        """Create a new context session."""
        session = ContextSession(configuration=self.config)

        # Create initial context
        initial_context = ContextState(context_type=initial_context_type)
        session.switch_context(initial_context)

        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> ContextSession | None:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def switch_context_type(self, session_id: str, new_type: ContextType, reason: str = "") -> ContextState | None:
        """Switch context type for a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        return self.switcher.switch_context(session, new_type, reason)

    def add_file(self, session_id: str, file_path: str) -> bool:
        """Add a file to the current context."""
        session = self.get_session(session_id)
        if not session or not session.current_context:
            return False

        self.switcher.add_file_to_context(session.current_context, file_path)
        return True

    def remove_file(self, session_id: str, file_path: str) -> bool:
        """Remove a file from the current context."""
        session = self.get_session(session_id)
        if not session or not session.current_context:
            return False

        self.switcher.remove_file_from_context(session.current_context, file_path)
        return True

    def optimize_context(self, session_id: str) -> bool:
        """Optimize the current context."""
        session = self.get_session(session_id)
        if not session or not session.current_context:
            return False

        self.switcher.optimize_context(session.current_context)
        return True

    def get_context_info(self, session_id: str) -> dict | None:
        """Get context information for a session."""
        session = self.get_session(session_id)
        if not session or not session.current_context:
            return None

        context = session.current_context
        return {
            "context_id": context.id,
            "context_type": context.context_type.value,
            "current_task": context.current_task,
            "file_count": len(context.relevant_files),
            "top_files": context.get_top_files(),
            "created_at": context.created_at,
            "last_updated": context.last_updated,
        }

    def get_stats(self) -> dict:
        """Get context management statistics."""
        total_contexts = len(self.sessions)
        active_contexts = sum(1 for s in self.sessions.values() if s.current_context)

        return {
            "total_sessions": total_contexts,
            "active_sessions": active_contexts,
            "avg_files_per_context": sum(
                len(s.current_context.relevant_files) for s in self.sessions.values() if s.current_context
            )
            / max(1, active_contexts),
        }
