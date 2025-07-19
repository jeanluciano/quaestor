"""Settings Screen

Configuration and preferences for the A1 dashboard.
"""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, Select, Switch


class SettingsScreen(Screen):
    """Settings screen for configuring the A1 dashboard."""

    DEFAULT_CSS = """
    SettingsScreen {
        background: $background;
    }

    SettingsScreen .settings-container {
        width: 100%;
        height: 100%;
        padding: 2;
        overflow-y: auto;
    }

    SettingsScreen .settings-section {
        margin-bottom: 2;
        padding: 1;
        border: solid $accent;
    }

    SettingsScreen .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    SettingsScreen .setting-item {
        margin-bottom: 1;
        height: auto;
    }

    SettingsScreen .setting-label {
        width: 30;
        margin-right: 2;
    }

    SettingsScreen Input {
        width: 20;
    }

    SettingsScreen Select {
        width: 30;
    }

    SettingsScreen .button-row {
        margin-top: 2;
        height: 3;
    }

    SettingsScreen Button {
        min-width: 16;
        margin-right: 1;
    }
    """

    def __init__(self):
        """Initialize the settings screen."""
        super().__init__()
        self.settings = self._load_settings()
        self.original_settings = self.settings.copy()

    def compose(self) -> ComposeResult:
        """Create the settings screen layout."""
        with Vertical(classes="settings-container"):
            # Display Settings
            with Container(classes="settings-section"):
                yield Label("Display Settings", classes="section-title")

                # Auto-scroll toggle
                with Horizontal(classes="setting-item"):
                    yield Label("Auto-scroll events:", classes="setting-label")
                    yield Switch(value=self.settings.get("auto_scroll", True), id="auto-scroll-switch")

                # Update interval
                with Horizontal(classes="setting-item"):
                    yield Label("Update interval (seconds):", classes="setting-label")
                    yield Input(
                        value=str(self.settings.get("update_interval", 1.0)), type="number", id="update-interval"
                    )

                # Theme selection
                with Horizontal(classes="setting-item"):
                    yield Label("Theme:", classes="setting-label")
                    yield Select(
                        [
                            ("Dark", "dark"),
                            ("Light", "light"),
                            ("Auto", "auto"),
                        ],
                        value=self.settings.get("theme", "dark"),
                        id="theme-select",
                    )

            # Performance Settings
            with Container(classes="settings-section"):
                yield Label("Performance Settings", classes="section-title")

                # Event buffer size
                with Horizontal(classes="setting-item"):
                    yield Label("Event buffer size:", classes="setting-label")
                    yield Input(
                        value=str(self.settings.get("event_buffer_size", 1000)), type="number", id="buffer-size"
                    )

                # History window
                with Horizontal(classes="setting-item"):
                    yield Label("Metrics history (seconds):", classes="setting-label")
                    yield Input(value=str(self.settings.get("history_window", 300)), type="number", id="history-window")

            # Alert Settings
            with Container(classes="settings-section"):
                yield Label("Alert Thresholds", classes="section-title")

                # CPU threshold
                with Horizontal(classes="setting-item"):
                    yield Label("CPU warning threshold (%):", classes="setting-label")
                    yield Input(value=str(self.settings.get("cpu_threshold", 80)), type="number", id="cpu-threshold")

                # Memory threshold
                with Horizontal(classes="setting-item"):
                    yield Label("Memory warning (MB):", classes="setting-label")
                    yield Input(
                        value=str(self.settings.get("memory_threshold", 150)), type="number", id="memory-threshold"
                    )

                # Response time threshold
                with Horizontal(classes="setting-item"):
                    yield Label("Response time warning (ms):", classes="setting-label")
                    yield Input(
                        value=str(self.settings.get("response_threshold", 100)), type="number", id="response-threshold"
                    )

            # Connection Settings
            with Container(classes="settings-section"):
                yield Label("Connection Settings", classes="section-title")

                # Socket path
                with Horizontal(classes="setting-item"):
                    yield Label("A1 socket path:", classes="setting-label")
                    yield Input(
                        value=str(self.settings.get("socket_path", "~/.quaestor/a1/service.sock")), id="socket-path"
                    )

                # Auto-reconnect
                with Horizontal(classes="setting-item"):
                    yield Label("Auto-reconnect:", classes="setting-label")
                    yield Switch(value=self.settings.get("auto_reconnect", True), id="auto-reconnect")

            # Filter Settings
            with Container(classes="settings-section"):
                yield Label("Event Filters", classes="section-title")

                # Event type filters
                yield Label("Show event types:", classes="setting-label")
                yield Checkbox("Tool Use", value=True, id="filter-tool-use")
                yield Checkbox("Intent Changes", value=True, id="filter-intent")
                yield Checkbox("Errors", value=True, id="filter-errors")
                yield Checkbox("Metrics", value=True, id="filter-metrics")
                yield Checkbox("Alerts", value=True, id="filter-alerts")

            # Action buttons
            with Horizontal(classes="button-row"):
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Reset", variant="warning", id="reset-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def _load_settings(self) -> dict[str, Any]:
        """Load settings from configuration file."""
        # In production, would load from actual config file
        # For now, return defaults
        return {
            "auto_scroll": True,
            "update_interval": 1.0,
            "theme": "dark",
            "event_buffer_size": 1000,
            "history_window": 300,
            "cpu_threshold": 80,
            "memory_threshold": 150,
            "response_threshold": 100,
            "socket_path": "~/.quaestor/a1/service.sock",
            "auto_reconnect": True,
            "event_filters": {
                "tool_use": True,
                "intent": True,
                "errors": True,
                "metrics": True,
                "alerts": True,
            },
        }

    def _save_settings(self) -> None:
        """Save settings to configuration file."""
        # Collect current values
        self.settings["auto_scroll"] = self.query_one("#auto-scroll-switch", Switch).value
        self.settings["update_interval"] = float(self.query_one("#update-interval", Input).value)
        self.settings["theme"] = self.query_one("#theme-select", Select).value
        self.settings["event_buffer_size"] = int(self.query_one("#buffer-size", Input).value)
        self.settings["history_window"] = int(self.query_one("#history-window", Input).value)
        self.settings["cpu_threshold"] = int(self.query_one("#cpu-threshold", Input).value)
        self.settings["memory_threshold"] = int(self.query_one("#memory-threshold", Input).value)
        self.settings["response_threshold"] = int(self.query_one("#response-threshold", Input).value)
        self.settings["socket_path"] = self.query_one("#socket-path", Input).value
        self.settings["auto_reconnect"] = self.query_one("#auto-reconnect", Switch).value

        # Event filters
        self.settings["event_filters"] = {
            "tool_use": self.query_one("#filter-tool-use", Checkbox).value,
            "intent": self.query_one("#filter-intent", Checkbox).value,
            "errors": self.query_one("#filter-errors", Checkbox).value,
            "metrics": self.query_one("#filter-metrics", Checkbox).value,
            "alerts": self.query_one("#filter-alerts", Checkbox).value,
        }

        # In production, would save to file
        # For now, just apply to app
        self._apply_settings()

    def _apply_settings(self) -> None:
        """Apply settings to the application."""
        # Apply theme
        if self.settings["theme"] == "dark":
            self.app.dark = True
        elif self.settings["theme"] == "light":
            self.app.dark = False

        # Apply other settings through app
        if hasattr(self.app, "apply_settings"):
            self.app.apply_settings(self.settings)

    def _reset_settings(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self._load_settings()

        # Update UI
        self.query_one("#auto-scroll-switch", Switch).value = self.settings["auto_scroll"]
        self.query_one("#update-interval", Input).value = str(self.settings["update_interval"])
        self.query_one("#theme-select", Select).value = self.settings["theme"]
        self.query_one("#buffer-size", Input).value = str(self.settings["event_buffer_size"])
        self.query_one("#history-window", Input).value = str(self.settings["history_window"])
        self.query_one("#cpu-threshold", Input).value = str(self.settings["cpu_threshold"])
        self.query_one("#memory-threshold", Input).value = str(self.settings["memory_threshold"])
        self.query_one("#response-threshold", Input).value = str(self.settings["response_threshold"])
        self.query_one("#socket-path", Input).value = self.settings["socket_path"]
        self.query_one("#auto-reconnect", Switch).value = self.settings["auto_reconnect"]

        # Reset filters
        filters = self.settings["event_filters"]
        self.query_one("#filter-tool-use", Checkbox).value = filters["tool_use"]
        self.query_one("#filter-intent", Checkbox).value = filters["intent"]
        self.query_one("#filter-errors", Checkbox).value = filters["errors"]
        self.query_one("#filter-metrics", Checkbox).value = filters["metrics"]
        self.query_one("#filter-alerts", Checkbox).value = filters["alerts"]

    @on(Button.Pressed, "#save-btn")
    def on_save_pressed(self, event: Button.Pressed) -> None:
        """Handle save button press."""
        try:
            self._save_settings()
            self.app.notify("Settings saved successfully", severity="information")
            self.app.pop_screen()
        except Exception as e:
            self.app.notify(f"Error saving settings: {e}", severity="error")

    @on(Button.Pressed, "#reset-btn")
    def on_reset_pressed(self, event: Button.Pressed) -> None:
        """Handle reset button press."""
        self._reset_settings()
        self.app.notify("Settings reset to defaults", severity="warning")

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_pressed(self, event: Button.Pressed) -> None:
        """Handle cancel button press."""
        # Restore original settings
        self.settings = self.original_settings.copy()
        self.app.pop_screen()
