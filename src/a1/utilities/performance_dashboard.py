"""Performance Monitoring Dashboard for A1

Real-time performance monitoring and visualization for the A1 system.
Provides insights into system performance, resource usage, and bottlenecks.
"""

import asyncio
import json
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..utilities import MetricCollector, PerformanceMonitor, ResourceMonitor


class PerformanceDashboard:
    """Real-time performance monitoring dashboard for A1."""

    def __init__(self, history_window: int = 300):  # 5 minutes default
        self.performance_monitor = PerformanceMonitor()
        self.resource_monitor = ResourceMonitor()
        self.metric_collector = MetricCollector()
        self.console = Console()

        # History tracking
        self.history_window = history_window
        self.cpu_history: deque[float] = deque(maxlen=history_window)
        self.memory_history: deque[float] = deque(maxlen=history_window)
        self.event_rate_history: deque[float] = deque(maxlen=history_window)
        self.response_time_history: deque[float] = deque(maxlen=history_window)

        # Current metrics
        self.current_metrics = {
            "startup_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "event_rate": 0.0,
            "avg_response_time": 0.0,
            "active_operations": 0,
            "total_events": 0,
            "errors": 0,
        }

        # Thresholds for alerts
        self.thresholds = {
            "memory_mb": 150,
            "cpu_percent": 80,
            "response_ms": 100,
            "event_rate_min": 50,
        }

        self.start_time = time.time()

    def update_metrics(self):
        """Update current performance metrics."""
        # Get resource usage
        usage = self.resource_monitor.get_current_usage()
        self.current_metrics["cpu_usage"] = usage["cpu_percent"]
        self.current_metrics["memory_usage"] = usage["memory_mb"]

        # Update history
        self.cpu_history.append(usage["cpu_percent"])
        self.memory_history.append(usage["memory_mb"])

        # Get recent metrics
        recent_metrics = self.metric_collector.get_metrics(start_time=datetime.now() - timedelta(seconds=1))

        # Calculate event rate
        event_count = len([m for m in recent_metrics if m["name"].startswith("event_")])
        self.current_metrics["event_rate"] = event_count
        self.event_rate_history.append(event_count)

        # Calculate average response time
        response_times = [m["value"] for m in recent_metrics if m["name"].endswith("_time")]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            self.current_metrics["avg_response_time"] = avg_response
            self.response_time_history.append(avg_response)

        # Get active operations from performance monitor
        active_ops = len(self.performance_monitor._active_operations)
        self.current_metrics["active_operations"] = active_ops

        # Count errors
        errors = len([m for m in recent_metrics if m["name"] == "error"])
        self.current_metrics["errors"] = errors

    def create_header_panel(self) -> Panel:
        """Create header panel with system info."""
        uptime = timedelta(seconds=int(time.time() - self.start_time))

        content = Text()
        content.append("A1 Performance Dashboard\n", style="bold cyan")
        content.append(f"Uptime: {uptime} | ", style="dim")
        content.append(f"Last Update: {datetime.now().strftime('%H:%M:%S')}", style="dim")

        return Panel(content, title="[bold]Quaestor A1[/bold]", border_style="cyan")

    def create_metrics_panel(self) -> Panel:
        """Create panel with current metrics."""
        table = Table(show_header=False, box=None, padding=(0, 2))

        # Add metric rows with color coding
        metrics = [
            (
                "CPU Usage",
                f"{self.current_metrics['cpu_usage']:.1f}%",
                self.current_metrics["cpu_usage"] > self.thresholds["cpu_percent"],
            ),
            (
                "Memory",
                f"{self.current_metrics['memory_usage']:.1f}MB",
                self.current_metrics["memory_usage"] > self.thresholds["memory_mb"],
            ),
            (
                "Event Rate",
                f"{self.current_metrics['event_rate']}/s",
                self.current_metrics["event_rate"] < self.thresholds["event_rate_min"],
            ),
            (
                "Avg Response",
                f"{self.current_metrics['avg_response_time']:.2f}ms",
                self.current_metrics["avg_response_time"] > self.thresholds["response_ms"],
            ),
            ("Active Ops", str(self.current_metrics["active_operations"]), False),
            ("Errors", str(self.current_metrics["errors"]), self.current_metrics["errors"] > 0),
        ]

        for name, value, is_alert in metrics:
            color = "red" if is_alert else "green"
            table.add_row(Text(name, style="cyan"), Text(value, style=f"bold {color}"))

        return Panel(table, title="[bold]Current Metrics[/bold]", border_style="green")

    def create_history_panel(self) -> Panel:
        """Create panel with performance history graphs."""
        content = Text()

        # CPU history graph
        content.append("CPU Usage History:\n", style="bold")
        content.append(self._create_sparkline(self.cpu_history, max_val=100))
        content.append("\n\n")

        # Memory history graph
        content.append("Memory Usage History:\n", style="bold")
        content.append(self._create_sparkline(self.memory_history, max_val=200))
        content.append("\n\n")

        # Event rate history
        content.append("Event Rate History:\n", style="bold")
        content.append(self._create_sparkline(self.event_rate_history))
        content.append("\n\n")

        # Response time history
        content.append("Response Time History:\n", style="bold")
        content.append(self._create_sparkline(self.response_time_history, max_val=100))

        return Panel(content, title="[bold]Performance History[/bold]", border_style="blue")

    def create_alerts_panel(self) -> Panel:
        """Create panel with active alerts."""
        alerts = []

        # Check thresholds
        if self.current_metrics["cpu_usage"] > self.thresholds["cpu_percent"]:
            alerts.append(("HIGH CPU", f"CPU usage at {self.current_metrics['cpu_usage']:.1f}%", "red"))

        if self.current_metrics["memory_usage"] > self.thresholds["memory_mb"]:
            alerts.append(("HIGH MEMORY", f"Memory usage at {self.current_metrics['memory_usage']:.1f}MB", "red"))

        if self.current_metrics["avg_response_time"] > self.thresholds["response_ms"]:
            alerts.append(
                ("SLOW RESPONSE", f"Avg response time {self.current_metrics['avg_response_time']:.2f}ms", "yellow")
            )

        if self.current_metrics["event_rate"] < self.thresholds["event_rate_min"]:
            alerts.append(("LOW THROUGHPUT", f"Event rate only {self.current_metrics['event_rate']}/s", "yellow"))

        if self.current_metrics["errors"] > 0:
            alerts.append(("ERRORS", f"{self.current_metrics['errors']} errors detected", "red"))

        if not alerts:
            content = Text("✓ All systems operating normally", style="green")
        else:
            content = Text()
            for alert_type, message, color in alerts:
                content.append(f"⚠ {alert_type}: ", style=f"bold {color}")
                content.append(f"{message}\n", style=color)

        return Panel(content, title="[bold]System Alerts[/bold]", border_style="red" if alerts else "green")

    def _create_sparkline(self, data: deque[float], max_val: float | None = None) -> str:
        """Create a sparkline graph from data."""
        if not data:
            return "No data"

        # Sparkline characters
        chars = " ▁▂▃▄▅▆▇█"

        # Normalize data
        if max_val is None:
            max_val = max(data) if data else 1

        if max_val == 0:
            max_val = 1

        # Create sparkline
        sparkline = ""
        for value in data:
            index = int((value / max_val) * (len(chars) - 1))
            index = max(0, min(index, len(chars) - 1))
            sparkline += chars[index]

        # Add min/max labels
        return f"{sparkline} (max: {max(data):.1f})"

    def create_layout(self) -> Layout:
        """Create dashboard layout."""
        layout = Layout()

        layout.split_column(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=6))

        layout["main"].split_row(Layout(name="metrics", ratio=1), Layout(name="history", ratio=2))

        return layout

    async def run_dashboard(self, refresh_rate: float = 1.0):
        """Run the performance dashboard."""
        layout = self.create_layout()

        with Live(layout, refresh_per_second=1 / refresh_rate, screen=True):
            try:
                while True:
                    # Update metrics
                    self.update_metrics()

                    # Update layout panels
                    layout["header"].update(self.create_header_panel())
                    layout["metrics"].update(self.create_metrics_panel())
                    layout["history"].update(self.create_history_panel())
                    layout["footer"].update(self.create_alerts_panel())

                    # Wait for next update
                    await asyncio.sleep(refresh_rate)

            except KeyboardInterrupt:
                pass

    def export_metrics(self, output_path: Path) -> None:
        """Export current metrics to JSON file."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "current_metrics": self.current_metrics,
            "history": {
                "cpu": list(self.cpu_history),
                "memory": list(self.memory_history),
                "event_rate": list(self.event_rate_history),
                "response_time": list(self.response_time_history),
            },
            "thresholds": self.thresholds,
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

    def get_health_status(self) -> dict[str, Any]:
        """Get overall system health status."""
        # Check all thresholds
        issues = []

        if self.current_metrics["cpu_usage"] > self.thresholds["cpu_percent"]:
            issues.append("high_cpu")

        if self.current_metrics["memory_usage"] > self.thresholds["memory_mb"]:
            issues.append("high_memory")

        if self.current_metrics["avg_response_time"] > self.thresholds["response_ms"]:
            issues.append("slow_response")

        if self.current_metrics["event_rate"] < self.thresholds["event_rate_min"]:
            issues.append("low_throughput")

        if self.current_metrics["errors"] > 0:
            issues.append("errors_detected")

        # Determine overall status
        if not issues:
            status = "healthy"
            score = 100
        elif len(issues) == 1:
            status = "warning"
            score = 75
        elif len(issues) == 2:
            status = "degraded"
            score = 50
        else:
            status = "critical"
            score = 25

        return {
            "status": status,
            "score": score,
            "issues": issues,
            "metrics": self.current_metrics,
            "timestamp": datetime.now().isoformat(),
        }


def run_performance_dashboard():
    """Entry point to run the performance dashboard."""
    dashboard = PerformanceDashboard()

    try:
        asyncio.run(dashboard.run_dashboard())
    except KeyboardInterrupt:
        print("\nDashboard stopped.")

        # Export final metrics
        export_path = Path(".quaestor/performance_metrics.json")
        export_path.parent.mkdir(exist_ok=True)
        dashboard.export_metrics(export_path)
        print(f"Metrics exported to {export_path}")


if __name__ == "__main__":
    run_performance_dashboard()
