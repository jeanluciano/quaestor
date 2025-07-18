"""Bidirectional communication bridge between A1 and Quaestor."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from a1.core.events import ClaudeEvent, QuaestorEvent
from a1.core.context import ContextManager


logger = logging.getLogger(__name__)


class QuaestorBridge:
    """Handles bidirectional communication with Quaestor."""
    
    def __init__(self, config: Dict):
        """Initialize bridge with configuration."""
        self.config = config
        self.quaestor_socket_path = Path.home() / ".quaestor" / "quaestor.sock"
        self.event_filters = config.get("hooks", {}).get("event_filtering", [])
        
    async def notify(self, claude_event: ClaudeEvent, intent: Dict, context: Optional[Dict]):
        """Notify Quaestor of relevant Claude events with A1 insights.
        
        Args:
            claude_event: The original Claude event
            intent: Detected intent information
            context: Current context from A1
        """
        # Don't send raw Claude events, send processed insights
        if not self._should_notify(claude_event, intent):
            return
            
        quaestor_event = QuaestorEvent(
            type="a1_insight",
            data={
                "intent": {
                    "type": intent["type"],
                    "confidence": intent["confidence"]
                },
                "context_summary": context if context else {},
                "triggered_by": {
                    "claude_event_type": claude_event.type,
                    "tool": claude_event.data.get("tool", "unknown")
                },
                "recommendations": self._get_recommendations(intent, context)
            },
            component="a1_bridge",
            source="quaestor"
        )
        
        await self._send_to_quaestor(quaestor_event)
        
    async def receive_from_quaestor(self, event: QuaestorEvent):
        """Receive and process events from Quaestor.
        
        Args:
            event: Event from Quaestor system
        """
        logger.info(f"Received Quaestor event: {event.type}")
        
        # Handle different Quaestor event types
        handlers = {
            "milestone_updated": self._handle_milestone_update,
            "config_changed": self._handle_config_change,
            "rule_updated": self._handle_rule_update,
            "context_request": self._handle_context_request,
        }
        
        handler = handlers.get(event.type)
        if handler:
            await handler(event.data)
        else:
            logger.warning(f"Unknown Quaestor event type: {event.type}")
            
    def _should_notify(self, event: ClaudeEvent, intent: Dict) -> bool:
        """Determine if this event/intent should be sent to Quaestor.
        
        Args:
            event: Claude event
            intent: Detected intent
            
        Returns:
            True if should notify Quaestor
        """
        # Check event filters
        for filter_rule in self.event_filters:
            if "include" in filter_rule:
                tools = filter_rule["include"]
                if event.data.get("tool") not in tools:
                    return False
            if "exclude" in filter_rule:
                tools = filter_rule["exclude"]
                if event.data.get("tool") in tools:
                    return False
                    
        # Always notify on high-confidence intent changes
        if intent["confidence"] > 0.8:
            return True
            
        # Notify on important events
        important_events = ["test_run", "post_file_edit", "file_change"]
        if event.type in important_events:
            return True
            
        return False
        
    def _get_recommendations(self, intent: Dict, context: Optional[Dict]) -> Dict:
        """Generate recommendations based on intent and context.
        
        Args:
            intent: Current intent
            context: Current context
            
        Returns:
            Dict of recommendations
        """
        recommendations = {}
        
        if intent["type"] == "exploring":
            recommendations["rule_relaxation"] = {
                "function_length": "inform",
                "complexity": "inform",
                "reason": "User is exploring codebase"
            }
        elif intent["type"] == "implementing":
            recommendations["rule_enforcement"] = {
                "test_coverage": "warn",
                "documentation": "warn",
                "reason": "Active implementation requires quality checks"
            }
        elif intent["type"] == "debugging":
            recommendations["assistance"] = {
                "suggest_breakpoints": True,
                "highlight_recent_changes": True,
                "reason": "Debugging mode detected"
            }
        elif intent["type"] == "refactoring":
            recommendations["rule_enforcement"] = {
                "test_coverage": "enforce",
                "breaking_changes": "warn",
                "reason": "Refactoring requires careful validation"
            }
            
        return recommendations
        
    async def _send_to_quaestor(self, event: QuaestorEvent):
        """Send event to Quaestor.
        
        Args:
            event: Event to send
        """
        try:
            # For now, log the event. In production, this would send via socket/IPC
            logger.info(f"Sending to Quaestor: {event.get_event_type()}")
            logger.debug(f"Event data: {json.dumps(event.to_dict(), indent=2)}")
            
            # TODO: Implement actual IPC/socket communication
            # async with aiofiles.open(self.quaestor_socket_path, 'w') as f:
            #     await f.write(json.dumps(event.to_dict()))
            
        except Exception as e:
            logger.error(f"Failed to send event to Quaestor: {e}")
            
    async def _handle_milestone_update(self, data: Dict):
        """Handle milestone update from Quaestor."""
        logger.info(f"Milestone updated: {data.get('milestone_id')}")
        # Update A1's understanding of project state
        # This would update context manager
        
    async def _handle_config_change(self, data: Dict):
        """Handle configuration change from Quaestor."""
        logger.info("Configuration changed")
        # Update A1 configuration
        # This might require component reinitialization
        
    async def _handle_rule_update(self, data: Dict):
        """Handle rule update from Quaestor."""
        logger.info(f"Rule updated: {data.get('rule_id')}")
        # Update A1's rule understanding
        # This affects recommendation generation
        
    async def _handle_context_request(self, data: Dict):
        """Handle context request from Quaestor."""
        logger.info("Context requested by Quaestor")
        # Send current A1 context back to Quaestor
        # This provides rich context for Quaestor operations