"""Performance monitoring and benchmarking utilities.

Extracted from A1 Performance Monitor, Benchmark, and Resource Optimizer.
Provides comprehensive performance tracking with 80% complexity reduction.
"""

import os
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean, median, stdev
from typing import Any

import psutil


class MetricType(Enum):
    """Types of metrics that can be collected."""

    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"  # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Duration measurements


class AlertSeverity(Enum):
    """Severity levels for performance alerts."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Represents a performance metric."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceUsage:
    """System resource usage snapshot."""

    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    open_files: int = 0
    thread_count: int = 0


@dataclass
class PerformanceAlert:
    """Performance alert information."""

    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""

    name: str
    iterations: int
    total_duration: float
    mean_duration: float
    median_duration: float
    min_duration: float
    max_duration: float
    std_deviation: float
    percentiles: dict[int, float]  # 50th, 90th, 95th, 99th
    throughput: float  # Operations per second
    resource_usage: ResourceUsage | None = None


class MetricCollector:
    """Collects and stores performance metrics."""

    def __init__(self, retention_hours: int = 24):
        """Initialize metric collector.

        Args:
            retention_hours: How long to retain metrics
        """
        self._metrics: dict[str, list[Metric]] = {}
        self._retention_hours = retention_hours
        self._last_cleanup = datetime.now()

    def record(self, metric: Metric):
        """Record a metric.

        Args:
            metric: Metric to record
        """
        if metric.name not in self._metrics:
            self._metrics[metric.name] = []

        self._metrics[metric.name].append(metric)

        # Periodic cleanup
        if datetime.now() - self._last_cleanup > timedelta(hours=1):
            self._cleanup_old_metrics()

    def record_value(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        unit: str = "",
        tags: dict[str, str] | None = None,
    ):
        """Convenience method to record a metric value.

        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            unit: Unit of measurement
            tags: Optional tags
        """
        metric = Metric(name=name, value=value, metric_type=metric_type, unit=unit, tags=tags or {})
        self.record(metric)

    def get_metrics(
        self, name: str, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> list[Metric]:
        """Get metrics by name and time range.

        Args:
            name: Metric name
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of metrics
        """
        if name not in self._metrics:
            return []

        metrics = self._metrics[name]

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]

        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics

    def get_summary(self, name: str, window_minutes: int = 60) -> dict[str, Any]:
        """Get statistical summary of a metric.

        Args:
            name: Metric name
            window_minutes: Time window to analyze

        Returns:
            Summary statistics
        """
        start_time = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(name, start_time=start_time)

        if not metrics:
            return {"count": 0, "mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "mean": mean(values),
            "median": median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": stdev(values) if len(values) > 1 else 0.0,
            "latest": values[-1],
            "first_timestamp": metrics[0].timestamp.isoformat(),
            "last_timestamp": metrics[-1].timestamp.isoformat(),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            Prometheus-formatted metrics
        """
        lines = []

        for name, metrics in self._metrics.items():
            if not metrics:
                continue

            latest = metrics[-1]
            metric_type = latest.metric_type.value

            # Type declaration
            lines.append(f"# TYPE {name} {metric_type}")

            # Help text
            if latest.unit:
                lines.append(f"# HELP {name} Metric in {latest.unit}")

            # Metric value with tags
            tag_str = ""
            if latest.tags:
                tag_parts = [f'{k}="{v}"' for k, v in latest.tags.items()]
                tag_str = "{" + ",".join(tag_parts) + "}"

            lines.append(f"{name}{tag_str} {latest.value}")

        return "\n".join(lines)

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self._retention_hours)

        for name in list(self._metrics.keys()):
            self._metrics[name] = [m for m in self._metrics[name] if m.timestamp > cutoff]

            if not self._metrics[name]:
                del self._metrics[name]

        self._last_cleanup = datetime.now()


class ResourceMonitor:
    """Monitors system resource usage."""

    def __init__(self):
        """Initialize resource monitor."""
        self._process = psutil.Process()
        self._last_disk_io = None
        self._last_net_io = None
        self._last_check = None

    def get_current_usage(self) -> ResourceUsage:
        """Get current resource usage.

        Returns:
            ResourceUsage snapshot
        """
        # CPU and memory
        cpu_percent = self._process.cpu_percent(interval=0.1)
        memory_info = self._process.memory_info()
        memory_percent = self._process.memory_percent()
        memory_mb = memory_info.rss / (1024 * 1024)

        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = 0.0
        disk_write_mb = 0.0

        if disk_io and self._last_disk_io and self._last_check:
            time_delta = (datetime.now() - self._last_check).total_seconds()
            if time_delta > 0:
                disk_read_mb = (disk_io.read_bytes - self._last_disk_io.read_bytes) / (1024 * 1024) / time_delta
                disk_write_mb = (disk_io.write_bytes - self._last_disk_io.write_bytes) / (1024 * 1024) / time_delta

        self._last_disk_io = disk_io

        # Network I/O
        net_io = psutil.net_io_counters()
        network_sent_mb = 0.0
        network_recv_mb = 0.0

        if net_io and self._last_net_io and self._last_check:
            time_delta = (datetime.now() - self._last_check).total_seconds()
            if time_delta > 0:
                network_sent_mb = (net_io.bytes_sent - self._last_net_io.bytes_sent) / (1024 * 1024) / time_delta
                network_recv_mb = (net_io.bytes_recv - self._last_net_io.bytes_recv) / (1024 * 1024) / time_delta

        self._last_net_io = net_io
        self._last_check = datetime.now()

        # File descriptors and threads
        try:
            open_files = len(self._process.open_files())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            open_files = 0

        try:
            thread_count = self._process.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            thread_count = 0

        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_read_mb=max(0, disk_read_mb),
            disk_write_mb=max(0, disk_write_mb),
            network_sent_mb=max(0, network_sent_mb),
            network_recv_mb=max(0, network_recv_mb),
            open_files=open_files,
            thread_count=thread_count,
        )

    def get_system_info(self) -> dict[str, Any]:
        """Get system information.

        Returns:
            System information dictionary
        """
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "memory_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "python_version": os.sys.version,
            "platform": os.sys.platform,
        }


class PerformanceMonitor:
    """Monitors application performance."""

    def __init__(self, metric_collector: MetricCollector | None = None):
        """Initialize performance monitor.

        Args:
            metric_collector: Optional metric collector to use
        """
        self.metrics = metric_collector or MetricCollector()
        self.resource_monitor = ResourceMonitor()
        self._alerts: list[PerformanceAlert] = []
        self._thresholds: dict[str, tuple[float, AlertSeverity]] = {}

    @contextmanager
    def measure(self, operation_name: str, tags: dict[str, str] | None = None, record_resources: bool = False):
        """Context manager to measure operation performance.

        Args:
            operation_name: Name of the operation
            tags: Optional tags
            record_resources: Whether to record resource usage

        Yields:
            Dict that can be used to add metadata
        """
        start_time = time.time()
        start_resources = self.resource_monitor.get_current_usage() if record_resources else None
        metadata = {}

        try:
            yield metadata
            success = True
        except Exception:
            success = False
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms

            # Record timing metric
            self.metrics.record_value(
                name=f"{operation_name}_duration",
                value=duration,
                metric_type=MetricType.TIMER,
                unit="ms",
                tags={**(tags or {}), "success": str(success)},
            )

            # Record resource usage if requested
            if record_resources:
                end_resources = self.resource_monitor.get_current_usage()

                # Calculate deltas
                self.metrics.record_value(
                    name=f"{operation_name}_cpu_percent",
                    value=end_resources.cpu_percent,
                    metric_type=MetricType.GAUGE,
                    unit="%",
                    tags=tags,
                )

                self.metrics.record_value(
                    name=f"{operation_name}_memory_mb",
                    value=end_resources.memory_mb - (start_resources.memory_mb if start_resources else 0),
                    metric_type=MetricType.GAUGE,
                    unit="MB",
                    tags=tags,
                )

            # Check thresholds
            self._check_threshold(f"{operation_name}_duration", duration)

    def set_threshold(self, metric_name: str, threshold: float, severity: AlertSeverity = AlertSeverity.WARNING):
        """Set an alert threshold for a metric.

        Args:
            metric_name: Name of the metric
            threshold: Threshold value
            severity: Alert severity
        """
        self._thresholds[metric_name] = (threshold, severity)

    def get_alerts(self, active_only: bool = True) -> list[PerformanceAlert]:
        """Get performance alerts.

        Args:
            active_only: Only return unresolved alerts

        Returns:
            List of alerts
        """
        if active_only:
            return [a for a in self._alerts if not a.resolved]
        return self._alerts.copy()

    def resolve_alerts(self, metric_name: str):
        """Resolve alerts for a metric.

        Args:
            metric_name: Metric name
        """
        for alert in self._alerts:
            if alert.metric_name == metric_name and not alert.resolved:
                alert.resolved = True

    def _check_threshold(self, metric_name: str, value: float):
        """Check if a metric exceeds its threshold.

        Args:
            metric_name: Metric name
            value: Current value
        """
        if metric_name not in self._thresholds:
            return

        threshold, severity = self._thresholds[metric_name]

        if value > threshold:
            alert = PerformanceAlert(
                metric_name=metric_name,
                current_value=value,
                threshold=threshold,
                severity=severity,
                message=f"{metric_name} exceeded threshold: {value:.2f} > {threshold}",
            )
            self._alerts.append(alert)

    def get_performance_report(self, window_minutes: int = 60) -> dict[str, Any]:
        """Generate a performance report.

        Args:
            window_minutes: Time window for the report

        Returns:
            Performance report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "window_minutes": window_minutes,
            "metrics": {},
            "alerts": [],
            "resource_usage": asdict(self.resource_monitor.get_current_usage()),
            "system_info": self.resource_monitor.get_system_info(),
        }

        # Collect all metric summaries
        datetime.now() - timedelta(minutes=window_minutes)

        for metric_name in self.metrics._metrics:
            summary = self.metrics.get_summary(metric_name, window_minutes)
            if summary["count"] > 0:
                report["metrics"][metric_name] = summary

        # Include active alerts
        report["alerts"] = [asdict(alert) for alert in self.get_alerts(active_only=True)]

        return report


class Benchmark:
    """Simple benchmarking utility."""

    def __init__(self, warmup_iterations: int = 5, benchmark_iterations: int = 100):
        """Initialize benchmark.

        Args:
            warmup_iterations: Number of warmup runs
            benchmark_iterations: Number of benchmark runs
        """
        self.warmup_iterations = warmup_iterations
        self.benchmark_iterations = benchmark_iterations
        self.resource_monitor = ResourceMonitor()

    def run(self, name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run a benchmark.

        Args:
            name: Benchmark name
            func: Function to benchmark
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Benchmark results
        """
        # Warmup
        for _ in range(self.warmup_iterations):
            func(*args, **kwargs)

        # Record initial resources
        self.resource_monitor.get_current_usage()

        # Benchmark runs
        durations = []
        start_total = time.time()

        for _ in range(self.benchmark_iterations):
            start = time.time()
            func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # Convert to ms
            durations.append(duration)

        total_duration = (time.time() - start_total) * 1000

        # Record final resources
        end_resources = self.resource_monitor.get_current_usage()

        # Calculate statistics
        durations.sort()

        return BenchmarkResult(
            name=name,
            iterations=self.benchmark_iterations,
            total_duration=total_duration,
            mean_duration=mean(durations),
            median_duration=median(durations),
            min_duration=min(durations),
            max_duration=max(durations),
            std_deviation=stdev(durations) if len(durations) > 1 else 0.0,
            percentiles={
                50: durations[int(len(durations) * 0.5)],
                90: durations[int(len(durations) * 0.9)],
                95: durations[int(len(durations) * 0.95)],
                99: durations[int(len(durations) * 0.99)],
            },
            throughput=1000.0 / mean(durations) if mean(durations) > 0 else 0.0,  # Operations per second
            resource_usage=end_resources,
        )

    def compare(self, benchmarks: list[BenchmarkResult]) -> dict[str, Any]:
        """Compare multiple benchmark results.

        Args:
            benchmarks: List of benchmark results

        Returns:
            Comparison report
        """
        if not benchmarks:
            return {}

        baseline = benchmarks[0]
        comparison = {"baseline": baseline.name, "comparisons": []}

        for benchmark in benchmarks[1:]:
            comp = {
                "name": benchmark.name,
                "mean_speedup": baseline.mean_duration / benchmark.mean_duration,
                "median_speedup": baseline.median_duration / benchmark.median_duration,
                "throughput_ratio": benchmark.throughput / baseline.throughput,
                "mean_difference_ms": benchmark.mean_duration - baseline.mean_duration,
                "percentile_comparison": {},
            }

            for p in [50, 90, 95, 99]:
                if p in baseline.percentiles and p in benchmark.percentiles:
                    comp["percentile_comparison"][f"p{p}_speedup"] = baseline.percentiles[p] / benchmark.percentiles[p]

            comparison["comparisons"].append(comp)

        return comparison


# Convenience functions


def create_monitor(thresholds: dict[str, tuple[float, AlertSeverity]] | None = None) -> PerformanceMonitor:
    """Create a performance monitor with default thresholds.

    Args:
        thresholds: Optional custom thresholds

    Returns:
        Configured PerformanceMonitor
    """
    monitor = PerformanceMonitor()

    # Set default thresholds
    default_thresholds = {
        "api_call_duration": (1000.0, AlertSeverity.WARNING),  # 1 second
        "database_query_duration": (500.0, AlertSeverity.WARNING),  # 500ms
        "file_operation_duration": (2000.0, AlertSeverity.WARNING),  # 2 seconds
        "memory_usage_mb": (500.0, AlertSeverity.ERROR),  # 500MB
        "cpu_percent": (80.0, AlertSeverity.WARNING),  # 80%
    }

    default_thresholds.update(thresholds or {})

    for metric, (threshold, severity) in default_thresholds.items():
        monitor.set_threshold(metric, threshold, severity)

    return monitor


def benchmark_function(
    func: Callable, *args, name: str | None = None, iterations: int = 100, **kwargs
) -> BenchmarkResult:
    """Convenience function to benchmark a function.

    Args:
        func: Function to benchmark
        *args: Function arguments
        name: Benchmark name (defaults to function name)
        iterations: Number of iterations
        **kwargs: Function keyword arguments

    Returns:
        Benchmark results
    """
    benchmark = Benchmark(benchmark_iterations=iterations)
    return benchmark.run(name or func.__name__, func, *args, **kwargs)


def format_benchmark_result(result: BenchmarkResult) -> str:
    """Format benchmark result as a readable string.

    Args:
        result: Benchmark result

    Returns:
        Formatted string
    """
    lines = [
        f"Benchmark: {result.name}",
        f"Iterations: {result.iterations}",
        f"Mean: {result.mean_duration:.2f}ms",
        f"Median: {result.median_duration:.2f}ms",
        f"Min: {result.min_duration:.2f}ms",
        f"Max: {result.max_duration:.2f}ms",
        f"Std Dev: {result.std_deviation:.2f}ms",
        f"Throughput: {result.throughput:.2f} ops/sec",
        "Percentiles:",
        f"  50th: {result.percentiles[50]:.2f}ms",
        f"  90th: {result.percentiles[90]:.2f}ms",
        f"  95th: {result.percentiles[95]:.2f}ms",
        f"  99th: {result.percentiles[99]:.2f}ms",
    ]

    if result.resource_usage:
        lines.extend(
            [
                "Resource Usage:",
                f"  CPU: {result.resource_usage.cpu_percent:.1f}%",
                f"  Memory: {result.resource_usage.memory_mb:.1f}MB",
            ]
        )

    return "\n".join(lines)
