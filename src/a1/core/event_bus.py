"""Simplified event bus for Quaestor A1 event system."""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from .event_store import EventStore
from .events import Event

logger = logging.getLogger(__name__)

# Type aliases
EventHandler = Callable[[Event], None] | Callable[[Event], Awaitable[None]]


class EventBus:
    """Simple event bus for Quaestor A1 with async processing."""

    def __init__(self, event_store: EventStore | None = None):
        """Initialize the event bus.

        Args:
            event_store: Optional event store for persistence
        """
        self.event_store = event_store
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the event bus processing."""
        if self._processing_task and not self._processing_task.done():
            return

        if self.event_store:
            await self.event_store.initialize()

        self._shutdown_event.clear()
        self._processing_task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")

    async def stop(self) -> None:
        """Stop the event bus processing."""
        self._shutdown_event.set()

        if self._processing_task:
            await self._processing_task

        # Process remaining events
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                await self._handle_event(event)
            except asyncio.QueueEmpty:
                break

        if self.event_store:
            await self.event_store.close()

        logger.info("EventBus stopped")

    def subscribe(self, handler: EventHandler, event_type: str | None = None) -> None:
        """Subscribe to events.

        Args:
            handler: Function to handle events (can be sync or async)
            event_type: Event type to subscribe to (None for all)
        """
        key = event_type or "*"
        self._handlers[key].append(handler)

    def unsubscribe(self, handler: EventHandler, event_type: str | None = None) -> None:
        """Unsubscribe from events.

        Args:
            handler: Handler to remove
            event_type: Event type to unsubscribe from (None for all)
        """
        key = event_type or "*"
        if key in self._handlers and handler in self._handlers[key]:
            self._handlers[key].remove(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to the bus.

        Args:
            event: Event to publish
        """
        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning(f"Event queue full, dropping event: {event.id}")

    async def _process_events(self) -> None:
        """Process events from the queue."""
        while not self._shutdown_event.is_set():
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._handle_event(event)
            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _handle_event(self, event: Event) -> None:
        """Handle a single event."""
        # Store event if store is available
        if self.event_store:
            try:
                await self.event_store.store_event(event)
            except Exception as e:
                logger.error(f"Error storing event {event.id}: {e}")

        # Find handlers for this event type
        handlers = []
        event_type = event.get_event_type()

        # Add specific handlers
        handlers.extend(self._handlers.get(event_type, []))
        # Add wildcard handlers
        handlers.extend(self._handlers.get("*", []))

        # Execute handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def get_stats(self) -> dict[str, int]:
        """Get basic statistics about the event bus."""
        return {
            "queue_size": self._event_queue.qsize(),
            "handler_count": sum(len(handlers) for handlers in self._handlers.values()),
        }
