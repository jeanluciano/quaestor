"""A1 Service Core - Main service that processes all events."""

import asyncio
import logging
from pathlib import Path

from a1.analysis.engine import AnalysisEngine
from a1.core.context import ContextManager
from a1.core.event_bus import EventBus
from a1.core.events import ClaudeEvent, Event, QuaestorEvent
from a1.core.intent import Intent, IntentDetector
from a1.core.queue import EventQueue, IPCEventTransport
from a1.learning.learning_manager import LearningManager

logger = logging.getLogger(__name__)


class A1Service:
    """Main A1 service that processes all events."""

    def __init__(self, config: dict | None = None):
        """Initialize A1 service with optional configuration."""
        self.config = config or {}

        # Core components
        self.event_bus = EventBus()
        self.intent_detector = IntentDetector()
        self.context_manager = ContextManager()

        # Optional components (based on config)
        self.analysis_engine = None
        self.learning_manager = None
        self.quaestor_bridge = None

        # Event queue and IPC transport
        self.event_queue = EventQueue(
            max_size=self.config.get("queue_size", 10000),
            overflow_policy=self.config.get("overflow_policy", "drop_oldest"),
        )

        # IPC transport for receiving events
        socket_path = Path.home() / ".quaestor" / "a1" / "service.sock"
        self.ipc_transport = IPCEventTransport(socket_path)

        self.running = False

    async def initialize(self):
        """Initialize A1 components based on configuration."""
        logger.info("Initializing A1 service...")

        # Initialize components based on config
        components = self.config.get("components", {})

        if components.get("analysis_engine", {}).get("enabled", True):
            self.analysis_engine = AnalysisEngine()
            logger.info("Analysis engine initialized")

        if components.get("learning_manager", {}).get("enabled", False):
            self.learning_manager = LearningManager()
            logger.info("Learning manager initialized")

        # Initialize Quaestor bridge if bidirectional communication enabled
        if self.config.get("hooks", {}).get("receive_from_a1", True):
            from .quaestor_bridge import QuaestorBridge

            self.quaestor_bridge = QuaestorBridge(self.config)
            logger.info("Quaestor bridge initialized")

    async def start(self):
        """Start the A1 service."""
        logger.info("Starting A1 service...")
        self.running = True

        # Start IPC server to receive events
        await self.ipc_transport.start_server(self.process_event)

        # Start event processing loop
        asyncio.create_task(self._process_events())

        logger.info("A1 service started")

    async def stop(self):
        """Stop the A1 service."""
        logger.info("Stopping A1 service...")
        self.running = False

        # Stop IPC server
        await self.ipc_transport.stop_server()

        # Process any remaining events
        while True:
            event = await self.event_queue.get(timeout=0.1)
            if event is None:
                break
            await self._process_single_event(event)

        logger.info("A1 service stopped")

    async def process_event(self, event: Event):
        """Process any A1 event (Claude or Quaestor).

        Args:
            event: Event to process
        """
        # Add to queue for async processing
        priority = self._get_event_priority(event)
        await self.event_queue.put(event, priority)

    async def _process_events(self):
        """Main event processing loop."""
        while self.running:
            try:
                # Get event from queue
                event = await self.event_queue.get(timeout=1.0)

                if event:
                    await self._process_single_event(event)

            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _process_single_event(self, event: Event):
        """Process a single event."""
        try:
            # Route based on event type
            if isinstance(event, ClaudeEvent):
                await self._process_claude_event(event)
            elif isinstance(event, QuaestorEvent):
                await self._process_quaestor_event(event)
            else:
                await self._process_generic_event(event)
        except Exception as e:
            logger.error(f"Error processing {type(event).__name__}: {e}")

    async def _process_claude_event(self, event: ClaudeEvent):
        """Handle Claude Code hook events."""
        logger.debug(f"Processing Claude event: {event.type}")

        # Update intent detection
        intent = await self.intent_detector.update(event)
        logger.info(f"Detected intent: {intent.type} (confidence: {intent.confidence})")

        # Update context manager
        await self.context_manager.process_event(event)

        # Run analysis if enabled
        if self.analysis_engine:
            await self.analysis_engine.analyze_event(event)

        # Update learning if enabled
        if self.learning_manager:
            await self.learning_manager.learn_from_event(event)

        # Notify Quaestor if relevant
        if self.quaestor_bridge and self.should_notify_quaestor(event, intent):
            await self.quaestor_bridge.notify(event, intent.to_dict(), self.context_manager.get_current_context())

    async def _process_quaestor_event(self, event: QuaestorEvent):
        """Handle Quaestor system events."""
        logger.debug(f"Processing Quaestor event: {event.type}")

        # Update context based on Quaestor event
        if event.type == "milestone_updated":
            await self.context_manager.update_milestone(event.data)
        elif event.type == "config_changed":
            await self._handle_config_change(event.data)

    async def _process_generic_event(self, event: Event):
        """Handle other event types."""
        logger.debug(f"Processing generic event: {event.get_event_type()}")

        # Emit to event bus for any listeners
        await self.event_bus.emit(event)

    def should_notify_quaestor(self, event: ClaudeEvent, intent: Intent) -> bool:
        """Determine if Quaestor should be notified about this event.

        Args:
            event: The Claude event
            intent: Detected intent info

        Returns:
            True if Quaestor should be notified
        """
        # High confidence intent changes
        if intent.confidence > 0.8 and intent.type != "idle":
            return True

        # Important tool uses
        if event.type == "post_tool_use" and event.data.get("tool") in ["Write", "MultiEdit"]:
            return True

        # Test results
        if event.type == "test_run":
            return True

        return False

    async def _handle_config_change(self, new_config: dict):
        """Handle configuration changes."""
        logger.info("Handling configuration change")
        self.config.update(new_config)

        # Reinitialize components if needed
        # TODO: Implement component reinitialization logic

    def _get_event_priority(self, event: Event) -> int:
        """Get priority for an event (0=highest, 10=lowest).

        Args:
            event: Event to prioritize

        Returns:
            Priority value
        """
        if isinstance(event, ClaudeEvent):
            # High priority for test results and errors
            if event.type == "test_run" or "error" in event.type:
                return 1
            # Medium priority for file edits
            elif "file_edit" in event.type:
                return 3
            # Normal priority for most events
            else:
                return 5

        elif isinstance(event, QuaestorEvent):
            # High priority for milestone updates
            if event.type == "milestone_updated":
                return 2
            # Medium priority for config changes
            elif event.type == "config_changed":
                return 4
            else:
                return 5

        # Default priority
        return 5
