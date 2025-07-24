"""Pattern matching engine for the predictive system.

This module matches current context and events against discovered patterns
to enable prediction and suggestion capabilities.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

from a1.core.events import Event

from .pattern_store import PatternStore
from .patterns import (
    CommandPattern,
    ErrorRecoveryPattern,
    FilePattern,
    Pattern,
    PatternType,
    TimeBasedPattern,
    WorkflowPattern,
)

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of pattern matching."""

    pattern: Pattern
    confidence: float
    match_score: float
    context_match: bool = True
    partial_match: bool = False
    next_actions: list[dict[str, Any]] | None = None


@dataclass
class MatchContext:
    """Context for pattern matching."""

    current_events: list[Event]
    current_file: str | None = None
    current_command: str | None = None
    error_state: dict[str, Any] | None = None
    time_context: dict[str, Any] | None = None
    user_context: dict[str, Any] | None = None


class PatternMatcher:
    """Matches patterns against current context."""

    def __init__(self, pattern_store: PatternStore):
        """Initialize pattern matcher.

        Args:
            pattern_store: Store containing patterns to match against
        """
        self.pattern_store = pattern_store
        self.match_cache: dict[str, MatchResult] = {}
        self.cache_ttl = 300  # 5 minutes

    def match_context(self, context: MatchContext) -> list[MatchResult]:
        """Match current context against all patterns.

        Args:
            context: Current context to match

        Returns:
            List of matching patterns sorted by relevance
        """
        matches = []

        # Match each pattern type
        matches.extend(self._match_command_patterns(context))
        matches.extend(self._match_workflow_patterns(context))
        matches.extend(self._match_file_patterns(context))
        matches.extend(self._match_error_patterns(context))
        matches.extend(self._match_time_patterns(context))

        # Sort by combined score (confidence * match_score)
        matches.sort(key=lambda m: m.confidence * m.match_score, reverse=True)

        # Update pattern observations
        for match in matches[:5]:  # Top 5 matches
            self.pattern_store.update_pattern_observation(match.pattern.id)

        return matches

    def get_next_actions(self, context: MatchContext, limit: int = 5) -> list[dict[str, Any]]:
        """Get predicted next actions based on patterns.

        Args:
            context: Current context
            limit: Maximum number of suggestions

        Returns:
            List of suggested next actions
        """
        matches = self.match_context(context)
        suggestions = []

        for match in matches[: limit * 2]:  # Look at more matches than limit
            if match.next_actions:
                for action in match.next_actions:
                    # Add pattern confidence to action
                    action_with_confidence = action.copy()
                    action_with_confidence["pattern_confidence"] = match.confidence
                    action_with_confidence["pattern_id"] = match.pattern.id
                    suggestions.append(action_with_confidence)

        # Deduplicate and sort by confidence
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = (suggestion.get("type"), suggestion.get("target"))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)

        unique_suggestions.sort(key=lambda s: s["pattern_confidence"], reverse=True)
        return unique_suggestions[:limit]

    def _match_command_patterns(self, context: MatchContext) -> list[MatchResult]:
        """Match command sequence patterns."""
        matches = []
        command_patterns = self.pattern_store.get_patterns_by_type(PatternType.COMMAND_SEQUENCE)

        # Extract recent commands from context
        recent_commands = []
        for event in context.current_events[-10:]:  # Last 10 events
            if hasattr(event, "tool"):
                recent_commands.append(event.tool)
            elif hasattr(event, "command"):
                recent_commands.append(event.command)

        if not recent_commands:
            return matches

        for pattern in command_patterns:
            if not isinstance(pattern, CommandPattern):
                continue

            # Check if recent commands match pattern prefix
            match_score = self._calculate_sequence_match(recent_commands, pattern.command_sequence)

            if match_score > 0.5:
                # Check context requirements
                context_match = pattern.matches_context(context.user_context or {})

                # Predict next commands
                next_actions = []
                if match_score < 1.0:  # Partial match
                    # Find where we are in the sequence
                    match_len = int(len(pattern.command_sequence) * match_score)
                    if match_len < len(pattern.command_sequence):
                        next_cmd = pattern.command_sequence[match_len]
                        next_actions.append(
                            {
                                "type": "command",
                                "command": next_cmd,
                                "confidence": pattern.success_rate,
                                "parameters": pattern.common_parameters.get(next_cmd, {}),
                            }
                        )

                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=pattern.confidence,
                        match_score=match_score,
                        context_match=context_match,
                        partial_match=match_score < 1.0,
                        next_actions=next_actions if next_actions else None,
                    )
                )

        return matches

    def _match_workflow_patterns(self, context: MatchContext) -> list[MatchResult]:
        """Match workflow patterns."""
        matches = []
        workflow_patterns = self.pattern_store.get_patterns_by_type(PatternType.WORKFLOW)

        # Extract workflow indicators from recent events
        event_signatures = []
        for event in context.current_events[-20:]:  # More events for workflows
            sig = self._get_event_signature(event)
            if sig:
                event_signatures.append(sig)

        for pattern in workflow_patterns:
            if not isinstance(pattern, WorkflowPattern):
                continue

            # Check if we're in this workflow
            match_score = self._calculate_workflow_match(event_signatures, pattern.workflow_steps)

            if match_score > 0.3:  # Lower threshold for workflows
                # Get next steps
                completed_steps = []
                for step in pattern.workflow_steps:
                    if any(step["id"] in sig for sig in event_signatures):
                        completed_steps.append(step["id"])

                next_step = pattern.get_next_step(completed_steps)
                next_actions = []
                if next_step:
                    next_actions.append(
                        {
                            "type": "workflow_step",
                            "step": next_step,
                            "workflow": pattern.workflow_name,
                            "confidence": pattern.completion_rate,
                        }
                    )

                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=pattern.confidence,
                        match_score=match_score,
                        partial_match=len(completed_steps) < len(pattern.workflow_steps),
                        next_actions=next_actions if next_actions else None,
                    )
                )

        return matches

    def _match_file_patterns(self, context: MatchContext) -> list[MatchResult]:
        """Match file access patterns."""
        matches = []
        file_patterns = self.pattern_store.get_patterns_by_type(PatternType.FILE_ACCESS)

        if not context.current_file:
            return matches

        for pattern in file_patterns:
            if not isinstance(pattern, FilePattern):
                continue

            match_score = 0.0
            next_actions = []

            # Check if current file is in pattern
            if context.current_file in pattern.file_sequence:
                match_score = 0.8
                # Suggest next files
                suggestions = pattern.suggest_next_files(context.current_file)
                for file_path, correlation in suggestions:
                    next_actions.append(
                        {
                            "type": "file_access",
                            "file": file_path,
                            "confidence": correlation,
                            "operation": "read",  # Most common
                        }
                    )

            # Check file groups
            for group in pattern.file_groups:
                if context.current_file in group:
                    match_score = max(match_score, 0.7)
                    for file in group:
                        if file != context.current_file:
                            next_actions.append(
                                {"type": "file_access", "file": file, "confidence": 0.7, "operation": "read"}
                            )

            if match_score > 0:
                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=pattern.confidence,
                        match_score=match_score,
                        next_actions=next_actions if next_actions else None,
                    )
                )

        return matches

    def _match_error_patterns(self, context: MatchContext) -> list[MatchResult]:
        """Match error recovery patterns."""
        matches = []

        if not context.error_state:
            return matches

        error_patterns = self.pattern_store.get_patterns_by_type(PatternType.ERROR_RECOVERY)

        for pattern in error_patterns:
            if not isinstance(pattern, ErrorRecoveryPattern):
                continue

            # Check if error matches
            if pattern.error_type == context.error_state.get("type"):
                match_score = 0.9

                # Get recovery suggestions
                recovery_actions = pattern.get_recovery_suggestion(context.error_state)
                next_actions = []
                for action in recovery_actions[:3]:
                    next_actions.append(
                        {"type": "error_recovery", "action": action, "confidence": pattern.success_rate}
                    )

                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=pattern.confidence,
                        match_score=match_score,
                        next_actions=next_actions if next_actions else None,
                    )
                )

        return matches

    def _match_time_patterns(self, context: MatchContext) -> list[MatchResult]:
        """Match time-based patterns."""
        matches = []

        current_time = time.localtime()
        hour = current_time.tm_hour
        day_of_week = current_time.tm_wday

        time_patterns = self.pattern_store.get_patterns_by_type(PatternType.TIME_BASED)

        for pattern in time_patterns:
            if not isinstance(pattern, TimeBasedPattern):
                continue

            if pattern.is_active_time(hour, day_of_week):
                match_score = 0.7

                # Suggest common activities for this time
                next_actions = []
                for activity in pattern.common_activities[:3]:
                    next_actions.append({"type": "time_based_suggestion", "activity": activity, "confidence": 0.6})

                matches.append(
                    MatchResult(
                        pattern=pattern,
                        confidence=pattern.confidence,
                        match_score=match_score,
                        next_actions=next_actions if next_actions else None,
                    )
                )

        return matches

    def _calculate_sequence_match(self, current: list[str], pattern: list[str]) -> float:
        """Calculate how well current sequence matches pattern."""
        if not current or not pattern:
            return 0.0

        # Check if current is a prefix of pattern
        if len(current) <= len(pattern):
            matching = 0
            for i, cmd in enumerate(current):
                if i < len(pattern) and cmd == pattern[i]:
                    matching += 1
                else:
                    break
            return matching / len(pattern)

        # Check if pattern appears in current
        for i in range(len(current) - len(pattern) + 1):
            if current[i : i + len(pattern)] == pattern:
                return 1.0

        return 0.0

    def _calculate_workflow_match(self, events: list[str], steps: list[dict[str, Any]]) -> float:
        """Calculate workflow match score."""
        if not events or not steps:
            return 0.0

        matched_steps = 0
        for step in steps:
            step_id = step["id"]
            if any(step_id in event for event in events):
                matched_steps += 1

        return matched_steps / len(steps)

    def _get_event_signature(self, event: Event) -> str:
        """Get signature for an event."""
        if hasattr(event, "tool"):
            return f"tool:{event.tool}"
        elif hasattr(event, "command"):
            return f"cmd:{event.command}"
        elif hasattr(event, "file_path"):
            return f"file:{event.file_path}"
        else:
            return event.__class__.__name__
