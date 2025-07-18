"""Event queue system for A1 service with IPC communication."""

import asyncio
import json
import logging
import socket
import struct
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from a1.core.events import ClaudeEvent, Event, QuaestorEvent

logger = logging.getLogger(__name__)


class EventQueue:
    """Async event queue with prioritization and overflow handling."""
    
    def __init__(self, max_size: int = 10000, overflow_policy: str = "drop_oldest"):
        """Initialize event queue.
        
        Args:
            max_size: Maximum queue size
            overflow_policy: Policy when queue is full (drop_oldest, drop_newest, block)
        """
        self.max_size = max_size
        self.overflow_policy = overflow_policy
        self._queue = asyncio.Queue(maxsize=max_size)
        self._priority_queue = asyncio.PriorityQueue(maxsize=max_size)
        self._metrics = {
            "events_received": 0,
            "events_processed": 0,
            "events_dropped": 0,
            "queue_overflows": 0
        }
        
    async def put(self, event: Event, priority: int = 5) -> bool:
        """Add event to queue with priority.
        
        Args:
            event: Event to add
            priority: Priority (0=highest, 10=lowest)
            
        Returns:
            True if event was queued
        """
        self._metrics["events_received"] += 1
        
        try:
            # Use priority queue for prioritized events
            if priority != 5:
                self._priority_queue.put_nowait((priority, datetime.now(), event))
            else:
                self._queue.put_nowait(event)
            return True
            
        except asyncio.QueueFull:
            self._metrics["queue_overflows"] += 1
            
            if self.overflow_policy == "drop_oldest":
                # Remove oldest event and retry
                try:
                    self._queue.get_nowait()
                    await self._queue.put(event)
                    return True
                except:
                    pass
                    
            elif self.overflow_policy == "drop_newest":
                # Drop this event
                self._metrics["events_dropped"] += 1
                return False
                
            elif self.overflow_policy == "block":
                # Wait for space
                await self._queue.put(event)
                return True
                
        return False
        
    async def get(self, timeout: Optional[float] = None) -> Optional[Event]:
        """Get next event from queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Next event or None if timeout
        """
        try:
            # Check priority queue first
            if not self._priority_queue.empty():
                _, _, event = await asyncio.wait_for(
                    self._priority_queue.get(), 
                    timeout=timeout
                )
                self._metrics["events_processed"] += 1
                return event
                
            # Then regular queue
            event = await asyncio.wait_for(
                self._queue.get(),
                timeout=timeout
            )
            self._metrics["events_processed"] += 1
            return event
            
        except asyncio.TimeoutError:
            return None
            
    def get_metrics(self) -> Dict[str, int]:
        """Get queue metrics.
        
        Returns:
            Metrics dictionary
        """
        return {
            **self._metrics,
            "queue_size": self._queue.qsize(),
            "priority_queue_size": self._priority_queue.qsize()
        }


class IPCEventTransport:
    """IPC transport for events using Unix domain sockets."""
    
    def __init__(self, socket_path: Union[str, Path]):
        """Initialize IPC transport.
        
        Args:
            socket_path: Path to Unix domain socket
        """
        self.socket_path = Path(socket_path)
        self.server = None
        self.clients = []
        self._handlers = {}
        
    async def start_server(self, handler: Callable[[Event], None]):
        """Start IPC server to receive events.
        
        Args:
            handler: Callback for received events
        """
        # Ensure socket directory exists
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing socket
        if self.socket_path.exists():
            self.socket_path.unlink()
            
        # Create Unix domain socket server
        self.server = await asyncio.start_unix_server(
            lambda r, w: self._handle_client(r, w, handler),
            path=str(self.socket_path)
        )
        
        logger.info(f"IPC server started at {self.socket_path}")
        
    async def _handle_client(self, reader, writer, handler):
        """Handle client connection.
        
        Args:
            reader: AsyncIO stream reader
            writer: AsyncIO stream writer
            handler: Event handler callback
        """
        client_addr = writer.get_extra_info('peername', 'unknown')
        logger.debug(f"Client connected: {client_addr}")
        
        try:
            while True:
                # Read message length (4 bytes)
                length_bytes = await reader.readexactly(4)
                if not length_bytes:
                    break
                    
                length = struct.unpack('!I', length_bytes)[0]
                
                # Read message data
                data = await reader.readexactly(length)
                
                # Deserialize event
                event_data = json.loads(data.decode('utf-8'))
                event = self._deserialize_event(event_data)
                
                # Handle event
                await handler(event)
                
                # Send acknowledgment
                writer.write(b'\x00')
                await writer.drain()
                
        except asyncio.IncompleteReadError:
            logger.debug(f"Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            
    async def send_event(self, event: Event) -> bool:
        """Send event to IPC server.
        
        Args:
            event: Event to send
            
        Returns:
            True if sent successfully
        """
        try:
            # Connect to server
            reader, writer = await asyncio.open_unix_connection(str(self.socket_path))
            
            # Serialize event
            data = json.dumps(self._serialize_event(event)).encode('utf-8')
            
            # Send length prefix
            writer.write(struct.pack('!I', len(data)))
            
            # Send data
            writer.write(data)
            await writer.drain()
            
            # Wait for acknowledgment
            ack = await reader.read(1)
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            return ack == b'\x00'
            
        except FileNotFoundError:
            logger.error(f"IPC server not found at {self.socket_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return False
            
    def _serialize_event(self, event: Event) -> Dict[str, Any]:
        """Serialize event to dictionary.
        
        Args:
            event: Event to serialize
            
        Returns:
            Serialized event data
        """
        if isinstance(event, ClaudeEvent):
            return {
                "__type__": "ClaudeEvent",
                "type": event.type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source
            }
        elif isinstance(event, QuaestorEvent):
            return {
                "__type__": "QuaestorEvent",
                "type": event.type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source
            }
        else:
            return {
                "__type__": "Event",
                "type": event.type,
                "data": getattr(event, "data", {}),
                "timestamp": event.timestamp.isoformat()
            }
            
    def _deserialize_event(self, data: Dict[str, Any]) -> Event:
        """Deserialize event from dictionary.
        
        Args:
            data: Serialized event data
            
        Returns:
            Event instance
        """
        event_type = data.get("__type__", "Event")
        timestamp = datetime.fromisoformat(data["timestamp"])
        
        if event_type == "ClaudeEvent":
            return ClaudeEvent(
                type=data["type"],
                data=data["data"],
                timestamp=timestamp,
                source=data["source"]
            )
        elif event_type == "QuaestorEvent":
            return QuaestorEvent(
                type=data["type"],
                data=data["data"],
                timestamp=timestamp,
                source=data["source"]
            )
        else:
            event = Event()
            event.type = data.get("type", "")
            event.timestamp = timestamp
            if hasattr(event, "data"):
                event.data = data.get("data", {})
            return event
            
    async def stop_server(self):
        """Stop IPC server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
            # Remove socket file
            if self.socket_path.exists():
                self.socket_path.unlink()
                
            logger.info("IPC server stopped")