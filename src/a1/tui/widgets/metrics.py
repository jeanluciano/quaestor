"""Metrics Display Widget

Real-time metrics visualization for A1 system performance.
"""

from collections import deque
from typing import Any

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar, Sparkline


class MetricsWidget(Widget):
    """Widget for displaying real-time A1 system metrics.

    Shows:
    - CPU and memory usage
    - Event processing rate
    - Response times
    - Active operations
    - Error rates
    """

    DEFAULT_CSS = """
    MetricsWidget {
        height: 100%;
        padding: 1;
    }

    MetricsWidget .metric-card {
        border: solid $accent;
        padding: 1;
        margin: 1;
        height: auto;
    }

    MetricsWidget .metric-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    MetricsWidget .metric-value {
        text-style: bold;
        text-align: center;
        width: 100%;
    }

    MetricsWidget .metric-value.good {
        color: $success;
    }

    MetricsWidget .metric-value.warning {
        color: $warning;
    }

    MetricsWidget .metric-value.critical {
        color: $error;
    }

    MetricsWidget Sparkline {
        height: 5;
        margin-top: 1;
    }

    MetricsWidget ProgressBar {
        margin-top: 1;
    }
    """

    # Reactive metrics
    cpu_usage = reactive(0.0)
    memory_usage = reactive(0.0)
    event_rate = reactive(0.0)
    response_time = reactive(0.0)
    active_operations = reactive(0)
    error_count = reactive(0)

    def __init__(self, history_size: int = 60, **kwargs):
        """Initialize the metrics widget.

        Args:
            history_size: Number of historical data points to keep
        """
        super().__init__(**kwargs)

        # Historical data for sparklines
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.event_rate_history = deque(maxlen=history_size)
        self.response_time_history = deque(maxlen=history_size)

        # Thresholds for status coloring
        self.thresholds = {
            "cpu_percent": {"good": 50, "warning": 75, "critical": 90},
            "memory_mb": {"good": 100, "warning": 150, "critical": 200},
            "response_ms": {"good": 50, "warning": 100, "critical": 200},
            "event_rate": {"good": 10, "warning": 5, "critical": 1},
        }

    def compose(self) -> ComposeResult:
        """Create the widget layout."""
        yield Grid(
            self._create_metric_card("CPU Usage", "cpu"),
            self._create_metric_card("Memory", "memory"),
            self._create_metric_card("Event Rate", "events"),
            self._create_metric_card("Response Time", "response"),
            self._create_metric_card("Active Ops", "operations"),
            self._create_metric_card("Errors", "errors"),
            id="metrics-grid",
        )

    def _create_metric_card(self, title: str, metric_type: str) -> Vertical:
        """Create a metric display card."""
        card = Vertical(classes="metric-card")

        with card:
            # Title
            card.mount(Label(title, classes="metric-title"))

            # Value display
            value_label = Label("--", classes="metric-value", id=f"value-{metric_type}")
            card.mount(value_label)

            # Add appropriate visualization
            if metric_type in ["cpu", "memory"]:
                # Progress bar for resource usage
                progress = ProgressBar(total=100, id=f"progress-{metric_type}")
                card.mount(progress)

            elif metric_type in ["events", "response"]:
                # Sparkline for rates
                sparkline = Sparkline([], id=f"sparkline-{metric_type}")
                card.mount(sparkline)

            # For operations and errors, just show the number

        return card

    def update_metrics(self, metrics: dict[str, Any]) -> None:
        """Update all metrics from A1 service data.

        Args:
            metrics: Dictionary of metric values
        """
        # Update values
        self.cpu_usage = metrics.get("cpu_usage", 0.0)
        self.memory_usage = metrics.get("memory_usage", 0.0)
        self.event_rate = metrics.get("event_rate", 0.0)
        self.response_time = metrics.get("avg_response_time", 0.0)
        self.active_operations = metrics.get("active_operations", 0)
        self.error_count = metrics.get("errors", 0)

        # Update history
        self.cpu_history.append(self.cpu_usage)
        self.memory_history.append(self.memory_usage)
        self.event_rate_history.append(self.event_rate)
        self.response_time_history.append(self.response_time)

        # Refresh display
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh all metric displays."""
        # Update CPU
        cpu_label = self.query_one("#value-cpu", Label)
        cpu_label.update(f"{self.cpu_usage:.1f}%")
        cpu_label.remove_class("good", "warning", "critical")
        cpu_label.add_class(self._get_status_class(self.cpu_usage, "cpu_percent"))

        cpu_progress = self.query_one("#progress-cpu", ProgressBar)
        cpu_progress.progress = self.cpu_usage

        # Update Memory
        mem_label = self.query_one("#value-memory", Label)
        mem_label.update(f"{self.memory_usage:.1f} MB")
        mem_label.remove_class("good", "warning", "critical")
        mem_label.add_class(self._get_status_class(self.memory_usage, "memory_mb"))

        mem_progress = self.query_one("#progress-memory", ProgressBar)
        mem_progress.progress = min(self.memory_usage / 2, 100)  # Scale to 200MB max

        # Update Event Rate
        event_label = self.query_one("#value-events", Label)
        event_label.update(f"{self.event_rate:.1f}/s")
        event_label.remove_class("good", "warning", "critical")
        event_label.add_class(self._get_status_class(self.event_rate, "event_rate", reverse=True))

        event_sparkline = self.query_one("#sparkline-events", Sparkline)
        event_sparkline.data = list(self.event_rate_history)

        # Update Response Time
        response_label = self.query_one("#value-response", Label)
        response_label.update(f"{self.response_time:.1f} ms")
        response_label.remove_class("good", "warning", "critical")
        response_label.add_class(self._get_status_class(self.response_time, "response_ms"))

        response_sparkline = self.query_one("#sparkline-response", Sparkline)
        response_sparkline.data = list(self.response_time_history)

        # Update Active Operations
        ops_label = self.query_one("#value-operations", Label)
        ops_label.update(str(self.active_operations))
        ops_label.remove_class("good", "warning", "critical")
        ops_label.add_class("good" if self.active_operations < 10 else "warning")

        # Update Errors
        error_label = self.query_one("#value-errors", Label)
        error_label.update(str(self.error_count))
        error_label.remove_class("good", "warning", "critical")
        error_label.add_class("good" if self.error_count == 0 else "critical")

    def _get_status_class(self, value: float, metric_type: str, reverse: bool = False) -> str:
        """Get the CSS class for a metric value based on thresholds.

        Args:
            value: The metric value
            metric_type: Type of metric for threshold lookup
            reverse: If True, lower values are worse (e.g., event rate)

        Returns:
            CSS class name: "good", "warning", or "critical"
        """
        thresholds = self.thresholds.get(metric_type, {})

        if not thresholds:
            return "good"

        if reverse:
            # For metrics where lower is worse
            if value >= thresholds["good"]:
                return "good"
            elif value >= thresholds["warning"]:
                return "warning"
            else:
                return "critical"
        else:
            # For metrics where higher is worse
            if value <= thresholds["good"]:
                return "good"
            elif value <= thresholds["warning"]:
                return "warning"
            else:
                return "critical"

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "event_rate": self.event_rate,
            "response_time": self.response_time,
            "active_operations": self.active_operations,
            "error_count": self.error_count,
            "status": self._calculate_overall_status(),
        }

    def _calculate_overall_status(self) -> str:
        """Calculate overall system status based on all metrics."""
        statuses = []

        statuses.append(self._get_status_class(self.cpu_usage, "cpu_percent"))
        statuses.append(self._get_status_class(self.memory_usage, "memory_mb"))
        statuses.append(self._get_status_class(self.event_rate, "event_rate", reverse=True))
        statuses.append(self._get_status_class(self.response_time, "response_ms"))

        if self.error_count > 0:
            statuses.append("critical")

        # Overall status is the worst individual status
        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        else:
            return "good"
