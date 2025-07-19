"""Events Detail Screen

Detailed view and analysis of system events.
"""

from datetime import datetime, timedelta
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Label, Select, Static


class EventDetailScreen(Screen):
    """Detailed event view with filtering and analysis capabilities."""

    DEFAULT_CSS = """
    EventDetailScreen {
        background: $background;
    }

    EventDetailScreen #filters-container {
        height: 5;
        padding: 1;
        background: $surface;
        border-bottom: solid $accent;
    }

    EventDetailScreen #event-table {
        height: 1fr;
    }

    EventDetailScreen #event-details {
        height: 40%;
        padding: 1;
        background: $surface;
        border-top: solid $accent;
    }

    EventDetailScreen .filter-control {
        margin-right: 2;
    }

    EventDetailScreen Button {
        min-width: 16;
        margin-left: 1;
    }
    """

    def __init__(self):
        """Initialize the event detail screen."""
        super().__init__()
        self.filtered_events: list[dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        """Create the event detail screen layout."""
        # Filters section
        with Container(id="filters-container"), Horizontal():
            # Event type filter
            yield Select(
                [
                    ("All Types", "all"),
                    ("Tool Use", "tool_use"),
                    ("Intent Change", "intent_change"),
                    ("Error", "error"),
                    ("Alert", "alert"),
                    ("Metric", "metric"),
                ],
                prompt="Event Type",
                value="all",
                id="type-filter",
                classes="filter-control",
            )

            # Time range filter
            yield Select(
                [
                    ("Last 5 min", "5m"),
                    ("Last 15 min", "15m"),
                    ("Last hour", "1h"),
                    ("Last 24 hours", "24h"),
                    ("All", "all"),
                ],
                prompt="Time Range",
                value="15m",
                id="time-filter",
                classes="filter-control",
            )

            # Search input
            yield Input(
                placeholder="Search events...",
                id="search-input",
                classes="filter-control",
            )

            # Action buttons
            yield Button("Refresh", variant="primary", id="refresh-btn")
            yield Button("Export", variant="default", id="export-btn")
            yield Button("Clear", variant="warning", id="clear-btn")

        # Event table
        yield DataTable(id="event-table", cursor_type="row")

        # Event details panel
        with Container(id="event-details"):
            yield Label("Event Details", classes="details-title")
            yield VerticalScroll(
                Static("Select an event to view details", id="details-content"),
            )

    async def on_mount(self) -> None:
        """Set up the screen when mounted."""
        # Configure the data table
        table = self.query_one("#event-table", DataTable)
        table.add_columns("Time", "Type", "Source", "Summary")
        table.zebra_stripes = True

        # Load initial events
        self.refresh_events()

    def refresh_events(self) -> None:
        """Refresh the events display with current filters."""
        # Get filter values
        type_filter = self.query_one("#type-filter", Select).value
        time_filter = self.query_one("#time-filter", Select).value
        search_text = self.query_one("#search-input", Input).value

        # Get events from app
        events = self.app.event_buffer.copy() if hasattr(self.app, "event_buffer") else []

        # Apply filters
        self.filtered_events = self._apply_filters(events, type_filter, time_filter, search_text)

        # Update table
        self._update_table()

    def _apply_filters(
        self,
        events: list[dict[str, Any]],
        type_filter: str,
        time_filter: str,
        search_text: str,
    ) -> list[dict[str, Any]]:
        """Apply filters to the event list."""
        filtered = events

        # Type filter
        if type_filter != "all":
            filtered = [e for e in filtered if e.get("type") == type_filter]

        # Time filter
        if time_filter != "all":
            cutoff_time = self._get_cutoff_time(time_filter)
            filtered = [e for e in filtered if self._parse_timestamp(e.get("timestamp")) >= cutoff_time]

        # Search filter
        if search_text:
            search_lower = search_text.lower()
            filtered = [e for e in filtered if search_lower in str(e).lower()]

        return filtered

    def _get_cutoff_time(self, time_filter: str) -> datetime:
        """Get the cutoff time for the time filter."""
        now = datetime.now()

        if time_filter == "5m":
            return now - timedelta(minutes=5)
        elif time_filter == "15m":
            return now - timedelta(minutes=15)
        elif time_filter == "1h":
            return now - timedelta(hours=1)
        elif time_filter == "24h":
            return now - timedelta(days=1)
        else:
            return datetime.min

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse a timestamp to datetime."""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp)
            except:
                return datetime.min
        else:
            return datetime.min

    def _update_table(self) -> None:
        """Update the data table with filtered events."""
        table = self.query_one("#event-table", DataTable)
        table.clear()

        # Add rows for filtered events (most recent first)
        for event in reversed(self.filtered_events[-100:]):  # Show max 100
            timestamp = self._parse_timestamp(event.get("timestamp"))
            time_str = timestamp.strftime("%H:%M:%S")

            event_type = event.get("type", "unknown")
            source = event.get("source", "system")

            # Create summary based on event type
            summary = self._create_event_summary(event)

            table.add_row(time_str, event_type, source, summary)

    def _create_event_summary(self, event: dict[str, Any]) -> str:
        """Create a brief summary of an event."""
        event_type = event.get("type", "unknown")
        data = event.get("data", {})

        if event_type == "tool_use":
            tool = data.get("tool", "unknown")
            if tool in ["Read", "Write", "Edit"]:
                file_path = data.get("parameters", {}).get("file_path", "")
                return f"{tool}: {file_path}"
            else:
                return f"Tool: {tool}"

        elif event_type == "intent_change":
            old_intent = data.get("old_intent", "?")
            new_intent = data.get("new_intent", "?")
            return f"{old_intent} → {new_intent}"

        elif event_type == "error":
            return data.get("message", "Error occurred")[:50]

        else:
            # Generic summary
            if isinstance(data, dict) and data:
                first_key = list(data.keys())[0]
                return f"{first_key}: {data[first_key]}"[:50]
            else:
                return str(data)[:50]

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the event table."""
        # Get the selected event
        if 0 <= event.row_index < len(self.filtered_events):
            selected_event = self.filtered_events[-(event.row_index + 1)]  # Reverse index
            self._show_event_details(selected_event)

    def _show_event_details(self, event: dict[str, Any]) -> None:
        """Show detailed information about an event."""
        details_content = self.query_one("#details-content", Static)

        # Format the event details
        details = []

        # Basic info
        details.append(f"Type: {event.get('type', 'unknown')}")
        details.append(f"Timestamp: {event.get('timestamp', 'unknown')}")
        details.append(f"Source: {event.get('source', 'system')}")

        # Event data
        data = event.get("data", {})
        if isinstance(data, dict):
            details.append("\nData:")
            for key, value in data.items():
                if isinstance(value, dict):
                    details.append(f"  {key}:")
                    for k, v in value.items():
                        details.append(f"    {k}: {v}")
                else:
                    details.append(f"  {key}: {value}")
        else:
            details.append(f"\nData: {data}")

        # Additional metadata
        for key, value in event.items():
            if key not in ["type", "timestamp", "source", "data"]:
                details.append(f"{key}: {value}")

        # Update the display
        details_content.update("\n".join(details))

    @on(Select.Changed)
    def on_filter_changed(self, event: Select.Changed) -> None:
        """Handle filter changes."""
        self.refresh_events()

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.refresh_events()

    @on(Button.Pressed, "#refresh-btn")
    def on_refresh_pressed(self, event: Button.Pressed) -> None:
        """Handle refresh button press."""
        self.refresh_events()
        self.app.notify("Events refreshed", severity="information")

    @on(Button.Pressed, "#export-btn")
    def on_export_pressed(self, event: Button.Pressed) -> None:
        """Handle export button press."""
        # In production, would export to file
        self.app.notify(f"Would export {len(self.filtered_events)} events to file", severity="information")

    @on(Button.Pressed, "#clear-btn")
    def on_clear_pressed(self, event: Button.Pressed) -> None:
        """Handle clear button press."""
        if hasattr(self.app, "event_buffer"):
            self.app.event_buffer.clear()
            self.refresh_events()
            self.app.notify("Event buffer cleared", severity="warning")
