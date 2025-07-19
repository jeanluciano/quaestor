"""Alerts Widget

Display and management of system alerts and notifications.
"""

from datetime import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static


class AlertsWidget(Widget):
    """Widget for displaying and managing A1 system alerts.

    Features:
    - Real-time alert display
    - Alert severity levels
    - Acknowledgment functionality
    - Alert history
    """

    DEFAULT_CSS = """
    AlertsWidget {
        height: 100%;
        padding: 1;
        border: solid $accent;
    }

    AlertsWidget .alerts-header {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
        width: 100%;
    }

    AlertsWidget .alert-count {
        text-align: center;
        margin-bottom: 1;
        padding: 1;
        width: 100%;
    }

    AlertsWidget .alert-count.none {
        color: $success;
        background: $success-darken-3;
    }

    AlertsWidget .alert-count.active {
        color: $error;
        background: $error-darken-3;
    }

    AlertsWidget .alert-item {
        margin-bottom: 1;
        padding: 1;
        border: solid;
        width: 100%;
    }

    AlertsWidget .alert-item.info {
        border-color: $primary;
        background: $primary-darken-3;
    }

    AlertsWidget .alert-item.warning {
        border-color: $warning;
        background: $warning-darken-3;
    }

    AlertsWidget .alert-item.error {
        border-color: $error;
        background: $error-darken-3;
    }

    AlertsWidget .alert-item.critical {
        border-color: $error;
        background: $error-darken-2;
        text-style: bold;
    }

    AlertsWidget .alert-timestamp {
        color: $text-muted;
        text-style: italic;
    }

    AlertsWidget .alert-actions {
        margin-top: 1;
    }

    AlertsWidget Button {
        min-width: 12;
        margin-right: 1;
    }
    """

    # Reactive properties
    active_alerts = reactive(0)
    total_alerts = reactive(0)

    def __init__(self, **kwargs):
        """Initialize the alerts widget."""
        super().__init__(**kwargs)

        # Alert storage
        self.alerts: list[dict[str, Any]] = []
        self.acknowledged_alerts: set[str] = set()
        self.max_alerts = 100

    def compose(self) -> ComposeResult:
        """Create the widget layout."""
        yield Vertical(
            Label("System Alerts", classes="alerts-header"),
            Label("No active alerts", id="alert-count", classes="alert-count none"),
            VerticalScroll(id="alerts-container"),
        )

    def add_alert(self, alert: dict[str, Any]) -> None:
        """Add a new alert to the system.

        Args:
            alert: Alert dictionary with type, severity, message, etc.
        """
        # Add unique ID if not present
        if "id" not in alert:
            alert["id"] = f"alert_{datetime.now().timestamp()}"

        # Add timestamp if not present
        if "timestamp" not in alert:
            alert["timestamp"] = datetime.now()

        # Add to alerts list
        self.alerts.append(alert)

        # Trim if too many
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)

        # Update counts
        self._update_counts()

        # Refresh display
        self._refresh_display()

    def acknowledge_alert(self, alert_id: str) -> None:
        """Acknowledge an alert.

        Args:
            alert_id: ID of the alert to acknowledge
        """
        self.acknowledged_alerts.add(alert_id)
        self._update_counts()
        self._refresh_display()

    def clear_acknowledged(self) -> None:
        """Clear all acknowledged alerts."""
        self.alerts = [a for a in self.alerts if a["id"] not in self.acknowledged_alerts]
        self.acknowledged_alerts.clear()
        self._update_counts()
        self._refresh_display()

    def _update_counts(self) -> None:
        """Update alert counts."""
        self.total_alerts = len(self.alerts)
        self.active_alerts = len([a for a in self.alerts if a["id"] not in self.acknowledged_alerts])

        # Update count display
        count_label = self.query_one("#alert-count", Label)
        if self.active_alerts == 0:
            count_label.update("No active alerts")
            count_label.remove_class("active")
            count_label.add_class("none")
        else:
            count_label.update(f"{self.active_alerts} active alert{'s' if self.active_alerts != 1 else ''}")
            count_label.remove_class("none")
            count_label.add_class("active")

    def _refresh_display(self) -> None:
        """Refresh the alerts display."""
        container = self.query_one("#alerts-container", VerticalScroll)
        container.remove_children()

        # Show active alerts first, then acknowledged
        active_alerts = [a for a in reversed(self.alerts) if a["id"] not in self.acknowledged_alerts]
        acknowledged = [a for a in reversed(self.alerts) if a["id"] in self.acknowledged_alerts]

        # Display active alerts
        for alert in active_alerts[:20]:  # Show max 20 active
            container.mount(self._create_alert_widget(alert, acknowledged=False))

        # Display some acknowledged alerts
        if acknowledged and len(active_alerts) < 10:
            container.mount(Label("─── Acknowledged ───", classes="separator"))
            for alert in acknowledged[:5]:
                container.mount(self._create_alert_widget(alert, acknowledged=True))

    def _create_alert_widget(self, alert: dict[str, Any], acknowledged: bool) -> Widget:
        """Create a widget for displaying a single alert."""
        severity = alert.get("severity", "info")
        message = alert.get("message", "Unknown alert")
        timestamp = alert.get("timestamp", datetime.now())
        source = alert.get("source", "system")

        # Format timestamp
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        time_str = timestamp.strftime("%H:%M:%S")

        # Create container
        container = Vertical(classes=f"alert-item {severity}")

        with container:
            # Header with severity and timestamp
            header = f"[{severity.upper()}] {time_str} - {source}"
            container.mount(Label(header, classes="alert-timestamp"))

            # Message
            container.mount(Static(message))

            # Actions (if not acknowledged)
            if not acknowledged:
                actions = Horizontal(classes="alert-actions")
                with actions:
                    ack_btn = Button("Acknowledge", variant="primary", id=f"ack-{alert['id']}")
                    actions.mount(ack_btn)

                    # Add specific actions based on alert type
                    if severity == "error":
                        view_btn = Button("View Details", variant="default", id=f"view-{alert['id']}")
                        actions.mount(view_btn)

                container.mount(actions)

        return container

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id

        if button_id and button_id.startswith("ack-"):
            # Extract alert ID and acknowledge
            alert_id = button_id[4:]  # Remove "ack-" prefix
            self.acknowledge_alert(alert_id)

        elif button_id and button_id.startswith("view-"):
            # Extract alert ID and show details
            alert_id = button_id[5:]  # Remove "view-" prefix
            self._show_alert_details(alert_id)

    def _show_alert_details(self, alert_id: str) -> None:
        """Show detailed information about an alert."""
        # Find the alert
        alert = next((a for a in self.alerts if a["id"] == alert_id), None)

        if alert:
            # Show detailed view (could open a modal or switch screens)
            details = f"""
Alert Details:
ID: {alert["id"]}
Severity: {alert.get("severity", "info")}
Source: {alert.get("source", "unknown")}
Time: {alert.get("timestamp", "unknown")}

Message:
{alert.get("message", "No message")}

Additional Data:
{alert.get("data", "None")}
            """
            self.app.notify(details, title="Alert Details", timeout=10)

    def get_alerts_summary(self) -> dict[str, Any]:
        """Get a summary of current alerts."""
        severity_counts = {
            "info": 0,
            "warning": 0,
            "error": 0,
            "critical": 0,
        }

        for alert in self.alerts:
            if alert["id"] not in self.acknowledged_alerts:
                severity = alert.get("severity", "info")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_alerts": self.total_alerts,
            "active_alerts": self.active_alerts,
            "acknowledged": len(self.acknowledged_alerts),
            "by_severity": severity_counts,
            "oldest_alert": self.alerts[0]["timestamp"].isoformat() if self.alerts else None,
        }

    def export_alerts(self) -> list[dict[str, Any]]:
        """Export all alerts for external processing."""
        return [
            {
                **alert,
                "acknowledged": alert["id"] in self.acknowledged_alerts,
                "timestamp": (
                    alert["timestamp"].isoformat() if isinstance(alert["timestamp"], datetime) else alert["timestamp"]
                ),
            }
            for alert in self.alerts
        ]
