"""Event Stream Widget

Real-time display of A1 system events with filtering and search capabilities.
"""

from datetime import datetime
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, Static


class EventStreamWidget(Widget):
    """Widget for displaying a real-time stream of A1 events.

    Features:
    - Auto-scrolling event display
    - Event type filtering
    - Search functionality
    - Syntax highlighting for code events
    """

    DEFAULT_CSS = """
    EventStreamWidget {
        height: 100%;
        border: solid $accent;
    }

    EventStreamWidget > VerticalScroll {
        height: 1fr;
        background: $surface;
        padding: 1;
    }

    EventStreamWidget .event-item {
        margin-bottom: 1;
        padding: 1;
        background: $panel;
    }

    EventStreamWidget .event-header {
        text-style: bold;
        margin-bottom: 0;
    }

    EventStreamWidget .event-body {
        margin-left: 2;
    }

    EventStreamWidget .event-timestamp {
        color: $text-muted;
        text-style: italic;
    }

    EventStreamWidget Input {
        dock: top;
        margin: 1;
    }
    """

    # Reactive properties
    filter_text = reactive("")
    auto_scroll = reactive(True)

    def __init__(self, **kwargs):
        """Initialize the event stream widget."""
        super().__init__(**kwargs)
        self.events: list[dict[str, Any]] = []
        self.filtered_events: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        """Create the widget layout."""
        yield Input(placeholder="Filter events...", id="event-filter")
        yield VerticalScroll(id="event-container")

    def on_mount(self) -> None:
        """Set up the widget when mounted."""
        # Focus on the filter input by default
        self.query_one("#event-filter", Input).focus()

    @on(Input.Changed, "#event-filter")
    def on_filter_changed(self, event: Input.Changed) -> None:
        """Handle filter text changes."""
        self.filter_text = event.value
        self._apply_filter()

    def add_event(self, event: dict[str, Any]) -> None:
        """Add a new event to the stream.

        Args:
            event: Event dictionary with type, data, timestamp, etc.
        """
        self.events.append(event)

        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events.pop(0)

        self._apply_filter()

        if self.auto_scroll:
            self._scroll_to_bottom()

    def _apply_filter(self) -> None:
        """Apply the current filter to events."""
        if not self.filter_text:
            self.filtered_events = self.events
        else:
            filter_lower = self.filter_text.lower()
            self.filtered_events = [e for e in self.events if filter_lower in str(e).lower()]

        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh the event display."""
        container = self.query_one("#event-container", VerticalScroll)
        container.remove_children()

        for event in self.filtered_events[-50:]:  # Show last 50 events
            container.mount(self._create_event_widget(event))

    def _create_event_widget(self, event: dict[str, Any]) -> Widget:
        """Create a widget for displaying a single event."""
        # Create container for the event
        event_container = Static(classes="event-item")

        # Format timestamp
        timestamp = event.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds

        # Create header with event type and timestamp
        event_type = event.get("type", "unknown")
        header_text = f"[{event_type}] {time_str}"
        header = Label(header_text, classes="event-header event-timestamp")

        # Create body based on event type
        body = self._format_event_body(event)

        # Compose the event widget
        with event_container:
            event_container.mount(header)
            event_container.mount(body)

        return event_container

    def _format_event_body(self, event: dict[str, Any]) -> Widget:
        """Format the event body based on event type."""
        event_type = event.get("type", "unknown")
        data = event.get("data", {})

        # Special formatting for different event types
        if event_type == "tool_use":
            tool_name = data.get("tool", "unknown")
            params = data.get("parameters", {})

            if tool_name in ["Read", "Write", "Edit"]:
                # Show file operations with syntax highlighting
                file_path = params.get("file_path", "")
                content = f"File: {file_path}"

                if tool_name == "Edit" and "old_string" in params:
                    # Show diff-like view for edits
                    old = params.get("old_string", "")[:50] + "..."
                    new = params.get("new_string", "")[:50] + "..."
                    content += f"\n- {old}\n+ {new}"

                return Static(content, classes="event-body")

            else:
                # Generic tool display
                content = f"Tool: {tool_name}\n"
                if params:
                    content += f"Params: {list(params.keys())}"
                return Static(content, classes="event-body")

        elif event_type == "intent_change":
            old_intent = data.get("old_intent", "IDLE")
            new_intent = data.get("new_intent", "IDLE")
            confidence = data.get("confidence", 0.0)

            content = f"Intent: {old_intent} → {new_intent}\n"
            content += f"Confidence: {confidence:.2%}"
            return Static(content, classes="event-body")

        elif event_type == "error":
            error_msg = data.get("message", "Unknown error")
            return Static(f"Error: {error_msg}", classes="event-body error")

        else:
            # Default formatting
            if isinstance(data, dict):
                content = "\n".join(f"{k}: {v}" for k, v in list(data.items())[:5])
            else:
                content = str(data)[:200]

            return Static(content, classes="event-body")

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the event list."""
        container = self.query_one("#event-container", VerticalScroll)
        container.scroll_end()

    def clear_events(self) -> None:
        """Clear all events from the display."""
        self.events.clear()
        self.filtered_events.clear()
        self._refresh_display()

    def set_auto_scroll(self, enabled: bool) -> None:
        """Enable or disable auto-scrolling."""
        self.auto_scroll = enabled

    def export_events(self) -> list[dict[str, Any]]:
        """Export the current filtered events."""
        return self.filtered_events.copy()
