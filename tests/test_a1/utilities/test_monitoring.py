"""Tests for performance monitoring utilities."""

import time
from datetime import datetime, timedelta

import pytest

from a1.utilities.monitoring import (
    AlertSeverity,
    Benchmark,
    BenchmarkResult,
    MetricCollector,
    MetricType,
    PerformanceMonitor,
    ResourceMonitor,
    ResourceUsage,
    benchmark_function,
    create_monitor,
    format_benchmark_result,
)


class TestMetricCollector:
    """Test MetricCollector functionality."""

    def test_record_metric(self):
        """Test recording a metric."""
        collector = MetricCollector()

        collector.record_value("test_metric", 42.0, MetricType.GAUGE, "ms")

        metrics = collector.get_metrics("test_metric")
        assert len(metrics) == 1
        assert metrics[0].value == 42.0
        assert metrics[0].metric_type == MetricType.GAUGE
        assert metrics[0].unit == "ms"

    def test_multiple_metrics(self):
        """Test recording multiple metrics."""
        collector = MetricCollector()

        for i in range(5):
            collector.record_value("counter", float(i), MetricType.COUNTER)
            collector.record_value("gauge", float(i * 2), MetricType.GAUGE)

        counter_metrics = collector.get_metrics("counter")
        gauge_metrics = collector.get_metrics("gauge")

        assert len(counter_metrics) == 5
        assert len(gauge_metrics) == 5
        assert counter_metrics[-1].value == 4.0
        assert gauge_metrics[-1].value == 8.0

    def test_time_range_filtering(self):
        """Test filtering metrics by time range."""
        collector = MetricCollector()

        # Record metrics at different times
        now = datetime.now()
        old_metric = collector.get_metrics("test")  # Empty list

        collector.record_value("test", 1.0)
        time.sleep(0.01)
        collector.record_value("test", 2.0)
        time.sleep(0.01)
        collector.record_value("test", 3.0)

        # Get all metrics
        all_metrics = collector.get_metrics("test")
        assert len(all_metrics) == 3

        # Get recent metrics only
        recent = collector.get_metrics("test", start_time=now + timedelta(seconds=0.015))
        assert len(recent) <= 2

    def test_metric_summary(self):
        """Test getting metric summary statistics."""
        collector = MetricCollector()

        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for v in values:
            collector.record_value("test", v, MetricType.GAUGE)

        summary = collector.get_summary("test")

        assert summary["count"] == 5
        assert summary["mean"] == 30.0
        assert summary["median"] == 30.0
        assert summary["min"] == 10.0
        assert summary["max"] == 50.0
        assert summary["latest"] == 50.0
        assert summary["std_dev"] > 0

    def test_empty_summary(self):
        """Test summary for non-existent metric."""
        collector = MetricCollector()

        summary = collector.get_summary("nonexistent")

        assert summary["count"] == 0
        assert summary["mean"] == 0.0

    def test_prometheus_export(self):
        """Test Prometheus format export."""
        collector = MetricCollector()

        collector.record_value(
            "http_requests_total", 1234.0, MetricType.COUNTER, tags={"method": "GET", "status": "200"}
        )

        collector.record_value("memory_usage_bytes", 1048576.0, MetricType.GAUGE, unit="bytes")

        export = collector.export_prometheus()

        assert "# TYPE http_requests_total counter" in export
        assert "# TYPE memory_usage_bytes gauge" in export
        assert "# HELP memory_usage_bytes Metric in bytes" in export
        assert 'http_requests_total{method="GET",status="200"} 1234' in export
        assert "memory_usage_bytes 1048576" in export

    def test_metric_cleanup(self):
        """Test old metric cleanup."""
        collector = MetricCollector(retention_hours=0)  # Immediate cleanup

        collector.record_value("test", 1.0)

        # Force cleanup by recording after retention period
        collector._last_cleanup = datetime.now() - timedelta(hours=2)
        collector.record_value("test2", 2.0)

        # Old metrics should be cleaned up
        assert "test" not in collector._metrics or len(collector._metrics["test"]) == 0


class TestResourceMonitor:
    """Test ResourceMonitor functionality."""

    def test_get_current_usage(self):
        """Test getting current resource usage."""
        monitor = ResourceMonitor()

        usage = monitor.get_current_usage()

        assert isinstance(usage, ResourceUsage)
        assert usage.cpu_percent >= 0
        assert usage.memory_percent >= 0
        assert usage.memory_mb > 0
        assert usage.thread_count > 0

    def test_resource_deltas(self):
        """Test resource usage deltas."""
        monitor = ResourceMonitor()

        # First call establishes baseline
        usage1 = monitor.get_current_usage()

        # Do some work
        data = [i**2 for i in range(1000)]
        time.sleep(0.1)

        # Second call should show deltas
        usage2 = monitor.get_current_usage()

        # Network and disk I/O might be 0 but should not be negative
        assert usage2.disk_read_mb >= 0
        assert usage2.disk_write_mb >= 0
        assert usage2.network_sent_mb >= 0
        assert usage2.network_recv_mb >= 0

    def test_get_system_info(self):
        """Test getting system information."""
        monitor = ResourceMonitor()

        info = monitor.get_system_info()

        assert "cpu_count" in info
        assert "memory_total_mb" in info
        assert "disk_usage_percent" in info
        assert "platform" in info
        assert info["cpu_count"] > 0
        assert info["memory_total_mb"] > 0


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""

    def test_measure_operation(self):
        """Test measuring operation performance."""
        monitor = PerformanceMonitor()

        with monitor.measure("test_operation") as metadata:
            time.sleep(0.01)  # 10ms operation
            metadata["custom"] = "value"

        # Check that duration was recorded
        metrics = monitor.metrics.get_metrics("test_operation_duration")
        assert len(metrics) == 1
        assert metrics[0].value >= 10.0  # At least 10ms
        assert metrics[0].metric_type == MetricType.TIMER

    def test_measure_with_resources(self):
        """Test measuring with resource tracking."""
        monitor = PerformanceMonitor()

        with monitor.measure("resource_test", record_resources=True):
            # Do some work
            data = [i**2 for i in range(10000)]

        # Check metrics were recorded
        duration_metrics = monitor.metrics.get_metrics("resource_test_duration")
        cpu_metrics = monitor.metrics.get_metrics("resource_test_cpu_percent")
        memory_metrics = monitor.metrics.get_metrics("resource_test_memory_mb")

        assert len(duration_metrics) == 1
        assert len(cpu_metrics) == 1
        assert len(memory_metrics) == 1

    def test_measure_with_exception(self):
        """Test measuring operation that fails."""
        monitor = PerformanceMonitor()

        with pytest.raises(ValueError):
            with monitor.measure("failing_operation") as metadata:
                raise ValueError("Test error")

        # Duration should still be recorded with success=False
        metrics = monitor.metrics.get_metrics("failing_operation_duration")
        assert len(metrics) == 1
        assert metrics[0].tags["success"] == "False"

    def test_threshold_alerts(self):
        """Test threshold-based alerting."""
        monitor = PerformanceMonitor()

        # Set a low threshold
        monitor.set_threshold("slow_operation_duration", 5.0, AlertSeverity.WARNING)

        # Perform slow operation
        with monitor.measure("slow_operation"):
            time.sleep(0.01)  # 10ms > 5ms threshold

        # Check alerts
        alerts = monitor.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].metric_name == "slow_operation_duration"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert not alerts[0].resolved

    def test_resolve_alerts(self):
        """Test resolving alerts."""
        monitor = PerformanceMonitor()

        # Create an alert
        monitor.set_threshold("test_duration", 1.0)
        with monitor.measure("test"):
            time.sleep(0.002)

        alerts = monitor.get_alerts()
        assert len(alerts) == 1

        # Resolve alerts
        monitor.resolve_alerts("test_duration")

        active_alerts = monitor.get_alerts(active_only=True)
        assert len(active_alerts) == 0

        all_alerts = monitor.get_alerts(active_only=False)
        assert len(all_alerts) == 1
        assert all_alerts[0].resolved

    def test_performance_report(self):
        """Test generating performance report."""
        monitor = PerformanceMonitor()

        # Record some metrics
        for i in range(5):
            with monitor.measure("operation", tags={"iteration": str(i)}):
                time.sleep(0.001)

        report = monitor.get_performance_report(window_minutes=5)

        assert "timestamp" in report
        assert "metrics" in report
        assert "alerts" in report
        assert "resource_usage" in report
        assert "system_info" in report

        assert "operation_duration" in report["metrics"]
        assert report["metrics"]["operation_duration"]["count"] == 5


class TestBenchmark:
    """Test Benchmark functionality."""

    def test_basic_benchmark(self):
        """Test basic benchmarking."""
        benchmark = Benchmark(warmup_iterations=2, benchmark_iterations=10)

        def test_func(n):
            return sum(range(n))

        result = benchmark.run("sum_benchmark", test_func, 1000)

        assert isinstance(result, BenchmarkResult)
        assert result.name == "sum_benchmark"
        assert result.iterations == 10
        assert result.mean_duration > 0
        assert result.median_duration > 0
        assert result.min_duration <= result.mean_duration <= result.max_duration
        assert result.throughput > 0
        assert 50 in result.percentiles
        assert 99 in result.percentiles

    def test_benchmark_comparison(self):
        """Test comparing benchmark results."""
        benchmark = Benchmark(warmup_iterations=2, benchmark_iterations=10)

        def fast_func():
            return sum(range(100))

        def slow_func():
            return sum(range(1000))

        fast_result = benchmark.run("fast", fast_func)
        slow_result = benchmark.run("slow", slow_func)

        comparison = benchmark.compare([fast_result, slow_result])

        assert comparison["baseline"] == "fast"
        assert len(comparison["comparisons"]) == 1

        comp = comparison["comparisons"][0]
        assert comp["name"] == "slow"
        assert comp["mean_speedup"] < 1.0  # Slow is slower than fast
        assert comp["mean_difference_ms"] > 0  # Slow takes more time

    def test_benchmark_function_convenience(self):
        """Test convenience benchmark function."""

        def test_func(x, y):
            return x + y

        result = benchmark_function(test_func, 10, 20, iterations=50)

        assert result.name == "test_func"
        assert result.iterations == 50
        assert result.mean_duration > 0

    def test_format_benchmark_result(self):
        """Test formatting benchmark results."""
        result = BenchmarkResult(
            name="test",
            iterations=100,
            total_duration=100.0,
            mean_duration=1.0,
            median_duration=0.9,
            min_duration=0.5,
            max_duration=2.0,
            std_deviation=0.3,
            percentiles={50: 0.9, 90: 1.5, 95: 1.7, 99: 1.9},
            throughput=1000.0,
            resource_usage=ResourceUsage(cpu_percent=50.0, memory_mb=100.0),
        )

        formatted = format_benchmark_result(result)

        assert "Benchmark: test" in formatted
        assert "Mean: 1.00ms" in formatted
        assert "Throughput: 1000.00 ops/sec" in formatted
        assert "CPU: 50.0%" in formatted
        assert "Memory: 100.0MB" in formatted


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_monitor(self):
        """Test creating monitor with default thresholds."""
        monitor = create_monitor()

        # Check default thresholds are set
        assert "api_call_duration" in monitor._thresholds
        assert "database_query_duration" in monitor._thresholds
        assert "memory_usage_mb" in monitor._thresholds

        # Test custom thresholds
        custom = {"custom_metric": (100.0, AlertSeverity.CRITICAL)}
        monitor2 = create_monitor(custom)

        assert "custom_metric" in monitor2._thresholds
        assert monitor2._thresholds["custom_metric"][1] == AlertSeverity.CRITICAL
