"""Main predictive engine for A1 Phase 5.

This module orchestrates pattern recognition, prediction, and suggestion
generation based on user behavior and system events.
"""

import logging
import time
from pathlib import Path
from typing import Any

from a1.core.event_bus import EventBus
from a1.core.events import Event, LearningEvent

from .pattern_matcher import MatchContext, PatternMatcher
from .pattern_store import PatternStore
from .patterns import PatternType
from .sequence_miner import SequenceMiner

logger = logging.getLogger(__name__)


class PredictiveEngine:
    """Main predictive engine that coordinates pattern learning and prediction."""

    def __init__(self, event_bus: EventBus, storage_path: Path | None = None):
        """Initialize predictive engine.

        Args:
            event_bus: Event bus for receiving events
            storage_path: Path for storing patterns
        """
        self.event_bus = event_bus
        self.storage_path = storage_path or Path(".quaestor/.a1")

        # Initialize components
        self.pattern_store = PatternStore(self.storage_path)
        self.sequence_miner = SequenceMiner(min_support=2, max_gap=300)
        self.pattern_matcher = PatternMatcher(self.pattern_store)

        # Event buffer for context
        self.event_buffer: list[Event] = []
        self.max_buffer_size = 100

        # Performance tracking
        self.last_mining_time = 0
        self.mining_interval = 300  # Mine patterns every 5 minutes
        self.events_since_mining = 0

        # Subscribe to events
        self._subscribe_to_events()

        logger.info("Predictive engine initialized")

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        # Subscribe to all event types we care about
        event_types = [
            "claude_event",
            "quaestor_event",
            "file_change",
            "tool_use",
            "user_action",
            "system",
            "learning",
        ]

        for event_type in event_types:
            self.event_bus.subscribe(event_type, self._handle_event)

    def _handle_event(self, event: Event) -> None:
        """Handle incoming events."""
        # Add to event buffer
        self.event_buffer.append(event)
        if len(self.event_buffer) > self.max_buffer_size:
            self.event_buffer.pop(0)

        # Add to sequence miner
        self.sequence_miner.add_event(event)
        self.events_since_mining += 1

        # Mine patterns periodically
        current_time = time.time()
        if current_time - self.last_mining_time > self.mining_interval and self.events_since_mining >= 10:
            self._mine_patterns()

        # Real-time prediction for certain events
        if self._should_predict(event):
            self._generate_predictions(event)

    def _should_predict(self, event: Event) -> bool:
        """Determine if we should generate predictions for this event."""
        # Predict on user actions and certain tool uses
        event_type = event.get_event_type() if hasattr(event, "get_event_type") else ""
        return event_type in [
            "user_action",
            "tool_use",
            "file_change",
        ]

    def _mine_patterns(self) -> None:
        """Mine patterns from recent events."""
        logger.debug("Mining patterns from event stream")

        # Mine patterns
        patterns = self.sequence_miner.mine_patterns()

        # Store/merge patterns
        self.pattern_store.merge_patterns(patterns)

        # Publish learning event
        if patterns:
            self.event_bus.publish(
                LearningEvent(
                    learning_type="pattern_discovered",
                    confidence=0.8,  # High confidence for discovered patterns
                )
            )

        # Update tracking
        self.last_mining_time = time.time()
        self.events_since_mining = 0

        # Prune old patterns
        pruned = self.pattern_store.prune_old_patterns(days_inactive=30)
        if pruned > 0:
            logger.info(f"Pruned {pruned} inactive patterns")

    def _generate_predictions(self, trigger_event: Event) -> None:
        """Generate predictions based on current context."""
        # Build context
        context = self._build_match_context(trigger_event)

        # Get predictions
        predictions = self.pattern_matcher.get_next_actions(context, limit=5)

        if predictions:
            # Publish prediction event
            self.event_bus.publish(
                LearningEvent(
                    learning_type="prediction_generated", confidence=max(p["pattern_confidence"] for p in predictions)
                )
            )

    def get_suggestions(self, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Get suggestions for current context.

        Args:
            context: Optional context override

        Returns:
            List of suggestions with confidence scores
        """
        # Build context
        match_context = self._build_match_context(user_context=context)

        # Get matches
        matches = self.pattern_matcher.match_context(match_context)

        # Convert to suggestions
        suggestions = []
        seen = set()

        for match in matches[:10]:
            if match.next_actions:
                for action in match.next_actions:
                    # Create suggestion
                    suggestion = {
                        "type": action["type"],
                        "confidence": match.confidence * match.match_score,
                        "pattern_type": match.pattern.pattern_type.value,
                        "pattern_id": match.pattern.id,
                        "action": action,
                    }

                    # Deduplicate
                    key = (action["type"], action.get("target", action.get("command", "")))
                    if key not in seen:
                        seen.add(key)
                        suggestions.append(suggestion)

        # Sort by confidence
        suggestions.sort(key=lambda s: s["confidence"], reverse=True)
        return suggestions[:5]

    def get_workflow_status(self) -> dict[str, Any]:
        """Get status of active workflows."""
        # Find active workflow patterns
        _ = self.pattern_store.get_patterns_by_type(PatternType.WORKFLOW)  # Available for future use
        active_workflows = []

        context = self._build_match_context()
        matches = self.pattern_matcher.match_context(context)

        for match in matches:
            if match.pattern.pattern_type == PatternType.WORKFLOW and match.partial_match:
                workflow = match.pattern
                if hasattr(workflow, "workflow_steps"):
                    # Calculate progress
                    completed = 0
                    for step in workflow.workflow_steps:
                        # Check if step appears in recent events
                        if any(step["id"] in str(e) for e in self.event_buffer[-20:]):
                            completed += 1

                    active_workflows.append(
                        {
                            "name": workflow.workflow_name,
                            "progress": completed / len(workflow.workflow_steps),
                            "completed_steps": completed,
                            "total_steps": len(workflow.workflow_steps),
                            "confidence": match.confidence,
                            "next_step": match.next_actions[0] if match.next_actions else None,
                        }
                    )

        return {
            "active_workflows": active_workflows,
            "total_patterns": len(self.pattern_store.patterns),
            "last_mining": self.last_mining_time,
        }

    def get_pattern_statistics(self) -> dict[str, Any]:
        """Get statistics about learned patterns."""
        stats = {
            "total_patterns": len(self.pattern_store.patterns),
            "by_type": {},
            "high_confidence": 0,
            "recent_discoveries": 0,
        }

        # Count by type
        for pattern_type in PatternType:
            patterns = self.pattern_store.get_patterns_by_type(pattern_type)
            stats["by_type"][pattern_type.value] = len(patterns)

        # High confidence patterns
        stats["high_confidence"] = len(self.pattern_store.get_high_confidence_patterns(min_confidence=0.8))

        # Recent discoveries (last 24 hours)
        cutoff = time.time() - 86400
        stats["recent_discoveries"] = len([p for p in self.pattern_store.patterns.values() if p.first_seen > cutoff])

        return stats

    def export_patterns(self, output_path: Path) -> None:
        """Export learned patterns to file."""
        self.pattern_store.export_patterns(output_path)
        logger.info(f"Exported patterns to {output_path}")

    def _build_match_context(
        self, trigger_event: Event | None = None, user_context: dict[str, Any] | None = None
    ) -> MatchContext:
        """Build context for pattern matching."""
        context = MatchContext(
            current_events=list(self.event_buffer),
            user_context=user_context or {},
        )

        # Extract current state from recent events
        for event in reversed(self.event_buffer):
            if hasattr(event, "file_path") and not context.current_file:
                context.current_file = event.file_path
            if hasattr(event, "command") and not context.current_command:
                context.current_command = event.command
            if hasattr(event, "error") and not context.error_state:
                context.error_state = {
                    "type": getattr(event, "error_type", "unknown"),
                    "message": str(event.error),
                }

        # Add trigger event info
        if trigger_event:
            if hasattr(trigger_event, "file_path"):
                context.current_file = trigger_event.file_path
            if hasattr(trigger_event, "command"):
                context.current_command = trigger_event.command

        # Add time context
        current_time = time.localtime()
        context.time_context = {
            "hour": current_time.tm_hour,
            "day_of_week": current_time.tm_wday,
            "is_weekend": current_time.tm_wday >= 5,
        }

        return context

    def _event_to_dict(self, event: Event) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": event.__class__.__name__,
            "timestamp": getattr(event, "timestamp", time.time()),
            "data": {k: v for k, v in event.__dict__.items() if not k.startswith("_") and k != "timestamp"},
        }
