"""Main Dashboard Screen

The primary dashboard view combining all widgets.
"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static

from ..widgets import AlertsWidget, EventStreamWidget, IntentVisualizationWidget, MetricsWidget


class MainDashboard(Screen):
    """Main dashboard screen combining all monitoring widgets."""

    DEFAULT_CSS = """
    MainDashboard {
        layout: grid;
        grid-size: 3 2;
        grid-rows: 1fr 1fr;
        grid-columns: 1fr 1fr 1fr;
    }

    MainDashboard #metrics-panel {
        column-span: 2;
        row-span: 1;
        border: solid $accent;
        margin: 1;
    }

    MainDashboard #intent-panel {
        column-span: 1;
        row-span: 1;
        border: solid $accent;
        margin: 1;
    }

    MainDashboard #events-panel {
        column-span: 2;
        row-span: 1;
        border: solid $accent;
        margin: 1;
    }

    MainDashboard #alerts-panel {
        column-span: 1;
        row-span: 1;
        border: solid $accent;
        margin: 1;
    }

    MainDashboard .panel-title {
        text-style: bold;
        text-align: center;
        background: $accent;
        color: $text;
        padding: 0 1;
        dock: top;
        height: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the main dashboard layout."""
        # Top row: Metrics (2 cols) + Intent (1 col)
        with Container(id="metrics-panel"):
            yield Static("System Metrics", classes="panel-title")
            yield MetricsWidget(id="metrics-widget")

        with Container(id="intent-panel"):
            yield Static("Intent Detection", classes="panel-title")
            yield IntentVisualizationWidget(id="intent-widget")

        # Bottom row: Events (2 cols) + Alerts (1 col)
        with Container(id="events-panel"):
            yield Static("Event Stream", classes="panel-title")
            yield EventStreamWidget(id="events-widget")

        with Container(id="alerts-panel"):
            yield Static("Alerts", classes="panel-title")
            yield AlertsWidget(id="alerts-widget")

    async def on_mount(self) -> None:
        """Set up the dashboard when mounted."""
        # Set up periodic updates
        self.set_interval(1.0, self.update_widgets)

    async def update_widgets(self) -> None:
        """Update all widgets with latest data from the app."""
        app = self.app

        # Update metrics if available
        if hasattr(app, "app_metrics"):
            metrics_widget = self.query_one("#metrics-widget", MetricsWidget)
            metrics_widget.update_metrics(app.app_metrics)

        # Update events from buffer
        if hasattr(app, "event_buffer"):
            events_widget = self.query_one("#events-widget", EventStreamWidget)

            # Only add new events (simple approach - in production would track last seen)
            current_count = len(events_widget.events)
            if len(app.event_buffer) > current_count:
                new_events = app.event_buffer[current_count:]
                for event in new_events:
                    events_widget.add_event(event)

        # Update intent if available
        if hasattr(app, "active_intent"):
            intent_widget = self.query_one("#intent-widget", IntentVisualizationWidget)

            # Get more detailed intent info if available from client
            if hasattr(app, "client") and app.client:
                try:
                    intent_info = await app.client.get_current_intent()
                    if intent_info:
                        intent_widget.update_intent(intent_info)
                except Exception:
                    # Fall back to simple intent
                    intent_widget.update_intent(
                        {
                            "intent": app.active_intent,
                            "confidence": 0.8,  # Default confidence
                            "evidence": [],
                        }
                    )

        # Update alerts count
        if hasattr(app, "alert_count"):
            # In production, would fetch actual alerts from service
            # For now, just show count changes
            pass

    def action_focus_metrics(self) -> None:
        """Focus on the metrics panel."""
        self.query_one("#metrics-widget").focus()

    def action_focus_intent(self) -> None:
        """Focus on the intent panel."""
        self.query_one("#intent-widget").focus()

    def action_focus_events(self) -> None:
        """Focus on the events panel."""
        self.query_one("#events-widget").focus()

    def action_focus_alerts(self) -> None:
        """Focus on the alerts panel."""
        self.query_one("#alerts-widget").focus()
