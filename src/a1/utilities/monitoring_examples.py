"""Usage examples for performance monitoring utilities.

These examples demonstrate how to use the monitoring system
for performance tracking, benchmarking, and resource monitoring.
"""

import time
from datetime import datetime, timedelta

from .monitoring import (
    AlertSeverity,
    Benchmark,
    MetricCollector,
    MetricType,
    PerformanceMonitor,
    ResourceMonitor,
    benchmark_function,
    create_monitor,
    format_benchmark_result,
)


def example_basic_metrics():
    """Example: Basic metric collection."""
    collector = MetricCollector()

    print("Recording basic metrics...")

    # Record different types of metrics
    collector.record_value("requests_total", 150, MetricType.COUNTER)
    collector.record_value("active_connections", 25, MetricType.GAUGE)
    collector.record_value("response_time", 45.3, MetricType.TIMER, unit="ms")

    # Record with tags
    collector.record_value(
        "http_requests", 1, MetricType.COUNTER, tags={"method": "GET", "endpoint": "/api/users", "status": "200"}
    )

    # Get metric summary
    summary = collector.get_summary("response_time")
    print(f"\nResponse time summary: {summary}")

    # Export in Prometheus format
    print("\nPrometheus export:")
    print(collector.export_prometheus())

    return collector


def example_performance_monitoring():
    """Example: Monitoring operation performance."""
    monitor = create_monitor()

    print("Monitoring operation performance...")

    # Monitor a simple operation
    with monitor.measure("data_processing") as metadata:
        # Simulate processing
        data = [i**2 for i in range(10000)]
        metadata["records"] = len(data)

    # Monitor with resource tracking
    with monitor.measure("heavy_computation", record_resources=True):
        # Simulate heavy computation
        sum(i**3 for i in range(50000))

    # Monitor with custom tags
    for i in range(5):
        with monitor.measure("batch_processing", tags={"batch": str(i)}):
            time.sleep(0.01 * (i + 1))  # Increasing delay

    # Check metrics
    metrics = monitor.metrics.get_summary("data_processing_duration")
    print(f"\nData processing metrics: {metrics}")

    # Check for alerts
    alerts = monitor.get_alerts()
    if alerts:
        print("\nPerformance alerts:")
        for alert in alerts:
            print(f"  - {alert.metric_name}: {alert.message}")

    return monitor


def example_resource_monitoring():
    """Example: Monitoring system resources."""
    monitor = ResourceMonitor()

    print("Monitoring system resources...")

    # Get system info
    info = monitor.get_system_info()
    print("\nSystem Info:")
    print(f"  CPU cores: {info['cpu_count']}")
    print(f"  Total memory: {info['memory_total_mb']:.0f} MB")
    print(f"  Disk usage: {info['disk_usage_percent']:.1f}%")
    print(f"  Platform: {info['platform']}")

    # Monitor resource usage over time
    print("\nResource usage over 5 seconds:")

    for i in range(5):
        usage = monitor.get_current_usage()
        print(f"\n[{i+1}s] Resource snapshot:")
        print(f"  CPU: {usage.cpu_percent:.1f}%")
        print(f"  Memory: {usage.memory_mb:.1f} MB ({usage.memory_percent:.1f}%)")
        print(f"  Threads: {usage.thread_count}")
        print(f"  Open files: {usage.open_files}")

        if i < 4:
            time.sleep(1)

    return monitor


def example_benchmarking():
    """Example: Benchmarking functions."""
    print("Running benchmarks...")

    # Define functions to benchmark
    def list_comprehension(n):
        return [i**2 for i in range(n)]

    def generator_expression(n):
        return list(i**2 for i in range(n))

    def map_function(n):
        return list(map(lambda x: x**2, range(n)))

    # Run benchmarks
    n = 10000
    benchmark = Benchmark(warmup_iterations=5, benchmark_iterations=100)

    results = []
    for func in [list_comprehension, generator_expression, map_function]:
        result = benchmark.run(func.__name__, func, n)
        results.append(result)
        print(f"\n{format_benchmark_result(result)}")

    # Compare results
    print("\n" + "=" * 50)
    print("Benchmark Comparison:")
    comparison = benchmark.compare(results)

    print(f"\nBaseline: {comparison['baseline']}")
    for comp in comparison["comparisons"]:
        print(f"\n{comp['name']}:")
        print(f"  Mean speedup: {comp['mean_speedup']:.2f}x")
        print(f"  Throughput ratio: {comp['throughput_ratio']:.2f}x")
        print(f"  Mean difference: {comp['mean_difference_ms']:.3f}ms")

    return results


def example_alert_thresholds():
    """Example: Setting up performance alerts."""
    monitor = PerformanceMonitor()

    print("Setting up performance alerts...")

    # Set custom thresholds
    monitor.set_threshold("api_response_duration", 100.0, AlertSeverity.WARNING)
    monitor.set_threshold("api_response_duration", 500.0, AlertSeverity.ERROR)
    monitor.set_threshold("api_response_duration", 1000.0, AlertSeverity.CRITICAL)

    # Simulate API calls with varying response times
    response_times = [50, 80, 150, 600, 1200, 75, 90]

    for i, response_time in enumerate(response_times):
        with monitor.measure("api_response") as metadata:
            time.sleep(response_time / 1000)  # Convert to seconds
            metadata["endpoint"] = f"/api/endpoint{i}"

    # Check alerts
    alerts = monitor.get_alerts()

    print(f"\nGenerated {len(alerts)} alerts:")
    for alert in sorted(alerts, key=lambda a: a.severity.value):
        print(
            f"  [{alert.severity.value}] {alert.metric_name}: " f"{alert.current_value:.0f}ms > {alert.threshold:.0f}ms"
        )

    # Resolve some alerts
    monitor.resolve_alerts("api_response_duration")

    print(f"\nActive alerts after resolution: {len(monitor.get_alerts())}")

    return monitor


def example_performance_report():
    """Example: Generating comprehensive performance reports."""
    monitor = create_monitor()

    print("Generating performance report...")

    # Simulate various operations
    operations = [
        ("database_query", 50, {"table": "users"}),
        ("cache_lookup", 5, {"hit": "true"}),
        ("file_read", 200, {"size_mb": "10"}),
        ("api_call", 300, {"endpoint": "/external"}),
        ("computation", 150, {"algorithm": "sort"}),
    ]

    # Run operations multiple times
    for _ in range(3):
        for op_name, duration_ms, tags in operations:
            with monitor.measure(op_name, tags=tags, record_resources=True):
                time.sleep(duration_ms / 1000)

    # Generate report
    report = monitor.get_performance_report(window_minutes=5)

    print("\n" + "=" * 50)
    print("PERFORMANCE REPORT")
    print("=" * 50)
    print(f"Generated at: {report['timestamp']}")
    print(f"Window: {report['window_minutes']} minutes")

    print("\nMetrics Summary:")
    for metric_name, summary in report["metrics"].items():
        if "_duration" in metric_name:
            op_name = metric_name.replace("_duration", "")
            print(f"\n{op_name}:")
            print(f"  Count: {summary['count']}")
            print(f"  Mean: {summary['mean']:.2f}ms")
            print(f"  Median: {summary['median']:.2f}ms")
            print(f"  Min/Max: {summary['min']:.2f}ms / {summary['max']:.2f}ms")

    print("\nResource Usage:")
    resources = report["resource_usage"]
    print(f"  CPU: {resources['cpu_percent']:.1f}%")
    print(f"  Memory: {resources['memory_mb']:.1f}MB")
    print(f"  Threads: {resources['thread_count']}")

    if report["alerts"]:
        print(f"\nActive Alerts: {len(report['alerts'])}")

    return report


def example_continuous_monitoring():
    """Example: Continuous monitoring with metric aggregation."""
    collector = MetricCollector()
    monitor = ResourceMonitor()

    print("Starting continuous monitoring for 10 seconds...")
    print("(Simulating real-time metrics collection)")

    start_time = datetime.now()
    iteration = 0

    while datetime.now() - start_time < timedelta(seconds=10):
        iteration += 1

        # Collect resource metrics
        usage = monitor.get_current_usage()

        # Record metrics
        collector.record_value("cpu_usage", usage.cpu_percent, MetricType.GAUGE, unit="%")
        collector.record_value("memory_usage", usage.memory_mb, MetricType.GAUGE, unit="MB")
        collector.record_value("iterations", iteration, MetricType.COUNTER)

        # Simulate some work
        [i**2 for i in range(1000)]

        # Print periodic updates
        if iteration % 5 == 0:
            cpu_summary = collector.get_summary("cpu_usage", window_minutes=1)
            mem_summary = collector.get_summary("memory_usage", window_minutes=1)

            print(f"\n[{iteration}] Metrics Update:")
            print(f"  CPU: {cpu_summary['latest']:.1f}% " f"(avg: {cpu_summary['mean']:.1f}%)")
            print(f"  Memory: {mem_summary['latest']:.1f}MB " f"(avg: {mem_summary['mean']:.1f}MB)")

        time.sleep(0.2)

    # Final summary
    print("\n" + "=" * 50)
    print("MONITORING SUMMARY")
    print("=" * 50)

    for metric_name in ["cpu_usage", "memory_usage"]:
        summary = collector.get_summary(metric_name)
        print(f"\n{metric_name}:")
        print(f"  Samples: {summary['count']}")
        print(f"  Mean: {summary['mean']:.2f}")
        print(f"  Min/Max: {summary['min']:.2f} / {summary['max']:.2f}")
        print(f"  Std Dev: {summary['std_dev']:.2f}")

    return collector


def example_custom_benchmark():
    """Example: Custom benchmarking scenarios."""
    print("Running custom benchmarks...")

    # Benchmark different sorting algorithms
    import random

    def bubble_sort(arr):
        arr = arr.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)

    # Test data
    sizes = [50, 100, 200]

    for size in sizes:
        print(f"\n{'='*50}")
        print(f"Array size: {size}")
        print("=" * 50)

        # Generate random array
        test_array = [random.randint(1, 1000) for _ in range(size)]

        # Benchmark each algorithm
        for sort_func in [sorted, bubble_sort, quick_sort]:
            result = benchmark_function(sort_func, test_array, name=f"{sort_func.__name__}_{size}", iterations=20)

            print(f"\n{sort_func.__name__}:")
            print(f"  Mean: {result.mean_duration:.3f}ms")
            print(f"  Throughput: {result.throughput:.0f} ops/sec")


if __name__ == "__main__":
    print("=== Performance Monitoring Examples ===\n")

    print("1. Basic Metrics Collection:")
    example_basic_metrics()

    print("\n\n2. Performance Monitoring:")
    example_performance_monitoring()

    print("\n\n3. Resource Monitoring:")
    example_resource_monitoring()

    print("\n\n4. Benchmarking:")
    example_benchmarking()

    print("\n\n5. Alert Thresholds:")
    example_alert_thresholds()

    print("\n\n6. Performance Reports:")
    example_performance_report()

    print("\n\n7. Continuous Monitoring:")
    example_continuous_monitoring()

    print("\n\n8. Custom Benchmarks:")
    example_custom_benchmark()
