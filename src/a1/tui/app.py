"""Main A1 Dashboard Application

The central Textual application that coordinates all dashboard components
and manages the connection to the A1 service.
"""

import asyncio
import contextlib
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Header

from ..service.client import A1Client
from ..utilities import MetricCollector, PerformanceMonitor
from .screens.events import EventDetailScreen
from .screens.main import MainDashboard
from .screens.settings import SettingsScreen


class A1Dashboard(App):
    """Main A1 Dashboard Application.

    Provides real-time monitoring and control of the A1 intelligent context system.
    Features include event streaming, metrics visualization, intent tracking, and alerts.
    """

    CSS_PATH = "styles/dashboard.css"
    TITLE = "Quaestor A1 Dashboard"
    SUB_TITLE = "Intelligent Context Monitoring"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("e", "show_events", "Events"),
        Binding("m", "show_main", "Main"),
        Binding("s", "show_settings", "Settings"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "show_help", "Help"),
    ]

    # Reactive attributes
    connection_status = reactive("disconnected")
    event_count = reactive(0)
    active_intent = reactive("IDLE")
    alert_count = reactive(0)

    def __init__(self, socket_path: Path | None = None):
        """Initialize the dashboard application.

        Args:
            socket_path: Path to A1 service socket (defaults to ~/.quaestor/a1/service.sock)
        """
        super().__init__()

        # Set up socket path
        if socket_path is None:
            socket_path = Path.home() / ".quaestor" / "a1" / "service.sock"
        self.socket_path = socket_path

        # Initialize components
        self.client: A1Client | None = None
        self.metric_collector = MetricCollector()
        self.performance_monitor = PerformanceMonitor()

        # Event buffer for display
        self.event_buffer: list[dict[str, Any]] = []
        self.max_events = 1000

        # Update task
        self._update_task: asyncio.Task | None = None

    async def on_mount(self) -> None:
        """Set up the dashboard when the app starts."""
        # Connect to A1 service
        await self._connect_to_service()

        # Start update loop
        self._update_task = asyncio.create_task(self._update_loop())

        # Push main screen
        self.push_screen(MainDashboard())

    async def on_unmount(self) -> None:
        """Clean up when the app stops."""
        # Cancel update task
        if self._update_task:
            self._update_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._update_task

        # Disconnect from service
        if self.client:
            await self.client.disconnect()

    async def _connect_to_service(self) -> None:
        """Connect to the A1 service."""
        try:
            self.client = A1Client(socket_path=self.socket_path)
            connected = await self.client.connect()

            if connected:
                self.connection_status = "connected"
                self.notify("Connected to A1 service", severity="information")
            else:
                self.connection_status = "disconnected"
                self.notify("Failed to connect to A1 service", severity="warning")
        except Exception as e:
            self.connection_status = "error"
            self.notify(f"Connection error: {e}", severity="error")

    async def _update_loop(self) -> None:
        """Main update loop for fetching data from A1 service."""
        while True:
            try:
                if self.client and self.connection_status == "connected":
                    # Fetch latest events
                    events = await self.client.get_recent_events(limit=50)
                    if events:
                        self._process_events(events)

                    # Get current intent
                    intent_info = await self.client.get_current_intent()
                    if intent_info:
                        self.active_intent = intent_info.get("intent", "IDLE")

                    # Get metrics
                    metrics = await self.client.get_metrics()
                    if metrics:
                        self._update_metrics(metrics)

                # Wait before next update
                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log.error(f"Update loop error: {e}")
                await asyncio.sleep(5.0)  # Back off on error

    def _process_events(self, events: list[dict[str, Any]]) -> None:
        """Process incoming events from A1 service."""
        # Add new events to buffer
        self.event_buffer.extend(events)

        # Trim buffer if too large
        if len(self.event_buffer) > self.max_events:
            self.event_buffer = self.event_buffer[-self.max_events :]

        # Update event count
        self.event_count = len(self.event_buffer)

        # Check for alerts in events
        alert_events = [e for e in events if e.get("type") == "alert"]
        if alert_events:
            self.alert_count += len(alert_events)

    def _update_metrics(self, metrics: dict[str, Any]) -> None:
        """Update dashboard metrics from A1 service data."""
        # This will be used by the metrics widget
        # Store metrics for access by screens
        self.app_metrics = metrics

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()
        yield Container(id="main-container")
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_show_main(self) -> None:
        """Show the main dashboard screen."""
        self.pop_screen()
        self.push_screen(MainDashboard())

    def action_show_events(self) -> None:
        """Show the events detail screen."""
        self.pop_screen()
        self.push_screen(EventDetailScreen())

    def action_show_settings(self) -> None:
        """Show the settings screen."""
        self.pop_screen()
        self.push_screen(SettingsScreen())

    def action_refresh(self) -> None:
        """Refresh the current screen."""
        # Force immediate update
        if self.client and self.connection_status == "connected":
            asyncio.create_task(self._update_loop())

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
        A1 Dashboard Help

        Keyboard Shortcuts:
        - q: Quit
        - d: Toggle dark mode
        - e: Show events screen
        - m: Show main dashboard
        - s: Show settings
        - r: Refresh data
        - ?: Show this help

        Navigation:
        - Tab/Shift+Tab: Navigate widgets
        - Arrow keys: Navigate within widgets
        - Enter: Activate/select
        - Escape: Go back
        """
        self.notify(help_text, title="Help", timeout=10)


def run_dashboard(socket_path: Path | None = None) -> None:
    """Run the A1 dashboard application.

    Args:
        socket_path: Optional path to A1 service socket
    """
    app = A1Dashboard(socket_path=socket_path)
    app.run()
