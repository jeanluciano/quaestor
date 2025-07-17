"""Performance Baseline Measurement for V2.1 System

This script measures the current performance characteristics of the V2.1 system
to establish a baseline and identify optimization opportunities.

Performance Targets:
- Startup time: < 1 second
- Memory usage: < 150MB
- Response times: < 100ms
- Event processing: > 100 events/sec
"""

import asyncio
import gc
import time
from typing import Any

import psutil
import pytest

# Import V2.1 components
from v2_1 import (
    AnalysisEngine,
    ContextManager,
    # Core components
    EventBus,
    FileChangeEvent,
    LearningManager,
    QualityGuardian,
    # Events
    ToolUseEvent,
    UserActionEvent,
    # System creation
    create_basic_system,
    get_hook_manager,
    get_persistence_manager,
    # Extensions
    get_prediction_engine,
    get_state_manager,
)
from a1.extensions.workflow import initialize_workflow_detector
from a1.utilities import PerformanceMonitor, ResourceMonitor


class V21PerformanceBaseline:
    """Comprehensive performance baseline measurement for V2.1."""

    def __init__(self):
        self.results = {}
        self.performance_monitor = PerformanceMonitor()
        self.resource_monitor = ResourceMonitor()

    def measure_startup_time(self, with_extensions: bool = True) -> dict[str, float]:
        """Measure V2.1 system startup time."""
        gc.collect()  # Clean slate

        # Measure core system startup
        start_time = time.time()

        # Initialize core components
        event_bus = EventBus()
        context_manager = ContextManager()
        quality_guardian = QualityGuardian()
        learning_manager = LearningManager()
        analysis_engine = AnalysisEngine()

        core_startup_time = time.time() - start_time

        # Measure extension startup
        extension_times = {}

        if with_extensions:
            # Prediction engine
            ext_start = time.time()
            prediction = get_prediction_engine()
            extension_times["prediction"] = time.time() - ext_start

            # Hook manager
            ext_start = time.time()
            hooks = get_hook_manager()
            extension_times["hooks"] = time.time() - ext_start

            # State manager
            ext_start = time.time()
            state = get_state_manager()
            extension_times["state"] = time.time() - ext_start

            # Workflow detector
            ext_start = time.time()
            workflow = initialize_workflow_detector(event_bus)
            extension_times["workflow"] = time.time() - ext_start

            # Persistence manager
            ext_start = time.time()
            persistence = get_persistence_manager()
            extension_times["persistence"] = time.time() - ext_start

        total_startup_time = time.time() - start_time

        return {
            "core_startup_time": core_startup_time,
            "extension_times": extension_times,
            "total_startup_time": total_startup_time,
            "extensions_total": sum(extension_times.values()),
        }

    def measure_memory_usage(self) -> dict[str, float]:
        """Measure memory usage of V2.1 system."""
        process = psutil.Process()

        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create full system
        system = create_basic_system(enable_extensions=True)

        # Memory after system creation
        system_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate some activity
        event_bus = system["event_bus"]
        for i in range(100):
            event = ToolUseEvent(tool_name=f"test_tool_{i}", success=True)
            asyncio.run(event_bus.publish(event))

        # Memory after activity
        gc.collect()
        active_memory = process.memory_info().rss / 1024 / 1024  # MB

        return {
            "baseline_memory_mb": baseline_memory,
            "system_memory_mb": system_memory,
            "active_memory_mb": active_memory,
            "system_overhead_mb": system_memory - baseline_memory,
            "activity_overhead_mb": active_memory - system_memory,
        }

    def measure_response_times(self) -> dict[str, float]:
        """Measure response times for common operations."""
        system = create_basic_system(enable_extensions=True)
        event_bus = system["event_bus"]

        response_times = {}

        # Event publishing response time
        events = [
            ToolUseEvent(tool_name="test", success=True),
            FileChangeEvent(file_path="test.py", change_type="modified"),
            UserActionEvent(action_type="save", action_details={}),
        ]

        for event in events:
            start = time.time()
            asyncio.run(event_bus.publish(event))
            response_times[f"publish_{event.get_event_type()}"] = (time.time() - start) * 1000  # ms

        # Context switching response time
        if "context" in system:
            start = time.time()
            system["context"].switch_context("test_context", "task")
            response_times["context_switch"] = (time.time() - start) * 1000  # ms

        # Quality check response time
        if "quality" in system:
            start = time.time()
            system["quality"].analyze_quality([__file__])
            response_times["quality_check"] = (time.time() - start) * 1000  # ms

        # Prediction response time
        if "prediction" in system:
            start = time.time()
            predictions = system["prediction"].predict_next_tool()
            response_times["predict_tool"] = (time.time() - start) * 1000  # ms

        # State snapshot response time
        if "state" in system:
            start = time.time()
            system["state"].create_snapshot("perf_test")
            response_times["create_snapshot"] = (time.time() - start) * 1000  # ms

        return response_times

    def measure_throughput(self) -> dict[str, float]:
        """Measure event processing throughput."""
        system = create_basic_system(enable_extensions=True)
        event_bus = system["event_bus"]

        # Measure events per second
        event_count = 1000
        events = [ToolUseEvent(tool_name=f"tool_{i}", success=True) for i in range(event_count)]

        start_time = time.time()
        for event in events:
            asyncio.run(event_bus.publish(event))
        duration = time.time() - start_time

        events_per_second = event_count / duration

        # Measure with async handlers
        async_count = 0

        async def async_handler(event):
            nonlocal async_count
            async_count += 1
            await asyncio.sleep(0.001)  # Simulate async work

        event_bus.subscribe(ToolUseEvent, async_handler)

        start_time = time.time()
        for event in events[:100]:  # Test with 100 async events
            asyncio.run(event_bus.publish(event))

        # Wait for async completion
        asyncio.run(asyncio.sleep(0.2))
        async_duration = time.time() - start_time

        return {
            "events_per_second": events_per_second,
            "event_processing_time_ms": (duration / event_count) * 1000,
            "async_events_per_second": 100 / async_duration,
            "async_completion_ratio": async_count / 100,
        }

    def measure_resource_usage(self) -> dict[str, Any]:
        """Measure CPU and resource usage patterns."""
        system = create_basic_system(enable_extensions=True)

        # Get system info
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Measure under load
        process = psutil.Process()

        # CPU usage before load
        process.cpu_percent()  # First call to initialize
        time.sleep(0.1)
        cpu_before = process.cpu_percent()

        # Generate load
        event_bus = system["event_bus"]
        start_time = time.time()

        for i in range(500):
            event = ToolUseEvent(tool_name=f"load_test_{i}", success=True)
            asyncio.run(event_bus.publish(event))

            if "prediction" in system:
                system["prediction"].predict_next_tool()

            if "quality" in system and i % 10 == 0:
                system["quality"].analyze_quality([__file__])

        duration = time.time() - start_time

        # CPU usage after load
        cpu_after = process.cpu_percent()

        # File handles
        open_files = len(process.open_files())

        # Thread count
        thread_count = process.num_threads()

        return {
            "cpu_count": cpu_count,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else 0,
            "cpu_usage_before": cpu_before,
            "cpu_usage_during": cpu_after,
            "open_files": open_files,
            "thread_count": thread_count,
            "operations_per_second": 500 / duration,
        }

    def generate_baseline_report(self) -> str:
        """Generate comprehensive performance baseline report."""
        print("\n" + "=" * 60)
        print("V2.1 PERFORMANCE BASELINE MEASUREMENT")
        print("=" * 60)

        # Startup time
        print("\n1. STARTUP TIME MEASUREMENT")
        startup_results = self.measure_startup_time()
        self.results["startup"] = startup_results

        print(f"   Core startup: {startup_results['core_startup_time']*1000:.1f}ms")
        print(f"   Extensions total: {startup_results['extensions_total']*1000:.1f}ms")
        for ext, time_taken in startup_results["extension_times"].items():
            print(f"     - {ext}: {time_taken*1000:.1f}ms")
        print(f"   TOTAL STARTUP: {startup_results['total_startup_time']*1000:.1f}ms")
        print(f"   Target: <1000ms | Status: {'✓ PASS' if startup_results['total_startup_time'] < 1.0 else '✗ FAIL'}")

        # Memory usage
        print("\n2. MEMORY USAGE MEASUREMENT")
        memory_results = self.measure_memory_usage()
        self.results["memory"] = memory_results

        print(f"   Baseline: {memory_results['baseline_memory_mb']:.1f}MB")
        print(f"   With system: {memory_results['system_memory_mb']:.1f}MB")
        print(f"   After activity: {memory_results['active_memory_mb']:.1f}MB")
        print(f"   System overhead: {memory_results['system_overhead_mb']:.1f}MB")
        print(f"   Target: <150MB | Status: {'✓ PASS' if memory_results['active_memory_mb'] < 150 else '✗ FAIL'}")

        # Response times
        print("\n3. RESPONSE TIME MEASUREMENT")
        response_results = self.measure_response_times()
        self.results["response"] = response_results

        max_response = max(response_results.values())
        for operation, time_ms in response_results.items():
            print(f"   {operation}: {time_ms:.2f}ms")
        print(f"   Max response: {max_response:.2f}ms")
        print(f"   Target: <100ms | Status: {'✓ PASS' if max_response < 100 else '✗ FAIL'}")

        # Throughput
        print("\n4. THROUGHPUT MEASUREMENT")
        throughput_results = self.measure_throughput()
        self.results["throughput"] = throughput_results

        print(f"   Events/second: {throughput_results['events_per_second']:.1f}")
        print(f"   Event processing: {throughput_results['event_processing_time_ms']:.3f}ms/event")
        print(f"   Async events/sec: {throughput_results['async_events_per_second']:.1f}")
        print(
            f"   Target: >100 events/sec | Status: {'✓ PASS' if throughput_results['events_per_second'] > 100 else '✗ FAIL'}"
        )

        # Resource usage
        print("\n5. RESOURCE USAGE MEASUREMENT")
        resource_results = self.measure_resource_usage()
        self.results["resources"] = resource_results

        print(f"   CPU cores: {resource_results['cpu_count']}")
        print(f"   CPU usage (idle): {resource_results['cpu_usage_before']:.1f}%")
        print(f"   CPU usage (load): {resource_results['cpu_usage_during']:.1f}%")
        print(f"   Open files: {resource_results['open_files']}")
        print(f"   Threads: {resource_results['thread_count']}")
        print(f"   Ops/second: {resource_results['operations_per_second']:.1f}")

        # Summary
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)

        targets_met = {
            "Startup < 1s": startup_results["total_startup_time"] < 1.0,
            "Memory < 150MB": memory_results["active_memory_mb"] < 150,
            "Response < 100ms": max_response < 100,
            "Throughput > 100/s": throughput_results["events_per_second"] > 100,
        }

        for target, met in targets_met.items():
            print(f"   {target}: {'✓ PASS' if met else '✗ FAIL'}")

        all_passed = all(targets_met.values())
        print(f"\n   Overall: {'✓ ALL TARGETS MET' if all_passed else '✗ OPTIMIZATION NEEDED'}")

        return self.results


@pytest.fixture
def baseline_tester():
    """Create performance baseline tester."""
    return V21PerformanceBaseline()


class TestV21PerformanceBaseline:
    """Run performance baseline tests."""

    def test_run_baseline_measurement(self, baseline_tester):
        """Run complete baseline measurement."""
        results = baseline_tester.generate_baseline_report()

        # Assertions based on targets
        assert results["startup"]["total_startup_time"] < 2.0, "Startup time significantly exceeds target"

        assert results["memory"]["active_memory_mb"] < 200, "Memory usage significantly exceeds target"

        assert results["throughput"]["events_per_second"] > 50, "Throughput significantly below target"


if __name__ == "__main__":
    # Run baseline measurement directly
    tester = V21PerformanceBaseline()
    tester.generate_baseline_report()
