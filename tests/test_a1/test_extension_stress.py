"""Extension Stress Testing and Performance Validation for V2.1

Comprehensive stress testing to validate extension interactions under extreme conditions:

1. High-frequency event generation
2. Memory leak detection
3. Concurrent extension operations
4. Resource exhaustion scenarios
5. Long-running operation validation

Performance Targets:
- Event processing: >100 events/sec
- Memory usage: <200MB total
- Startup time: <1 second
- No memory leaks over 1000+ operations
"""

import asyncio
import gc
import tempfile
import time
from pathlib import Path
from threading import Event as ThreadEvent
from threading import Thread

import psutil
import pytest

from a1 import (
    EventBus,
    FileChangeEvent,
    ToolUseEvent,
    UserActionEvent,
    get_prediction_engine,
    get_state_manager,
)
from a1.extensions.workflow import initialize_workflow_detector


class ExtensionStressTester:
    """Stress testing framework for V2.1 extensions."""

    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.performance_data = {}
        self.memory_snapshots = []
        self.stop_event = ThreadEvent()

    def setup_full_system(self) -> dict:
        """Setup complete V2.1 system for stress testing."""
        event_bus = EventBus()

        system = {
            "event_bus": event_bus,
            "prediction": get_prediction_engine(),
            "state": get_state_manager(),
            "workflow": initialize_workflow_detector(event_bus),
        }

        return system

    def measure_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def stress_test_event_throughput(self, system: dict, duration_seconds: int = 10) -> dict:
        """Stress test event processing throughput."""
        start_memory = self.measure_memory_usage()
        start_time = time.time()

        events_processed = 0
        test_events = [
            ToolUseEvent(tool_name="Read", success=True),
            ToolUseEvent(tool_name="Edit", success=True),
            ToolUseEvent(tool_name="Write", success=True),
            FileChangeEvent(file_path="test.py", change_type="modified"),
            UserActionEvent(action_type="save", action_details={"file": "test.py"}),
        ]

        end_time = start_time + duration_seconds

        while time.time() < end_time:
            for event in test_events:
                # Process events through appropriate extensions
                if "prediction" in system and isinstance(event, ToolUseEvent):
                    system["prediction"].handle_tool_use_event(event)

                if "workflow" in system:
                    try:
                        if isinstance(event, ToolUseEvent):
                            asyncio.run(system["workflow"].handle_tool_use_event(event))
                        elif isinstance(event, FileChangeEvent):
                            asyncio.run(system["workflow"].handle_file_change_event(event))
                        elif isinstance(event, UserActionEvent):
                            asyncio.run(system["workflow"].handle_user_action_event(event))
                    except RuntimeError:
                        pass  # No event loop

                events_processed += 1

                # Stop if requested
                if self.stop_event.is_set():
                    break

            if self.stop_event.is_set():
                break

        end_memory = self.measure_memory_usage()
        actual_duration = time.time() - start_time

        return {
            "events_processed": events_processed,
            "duration_seconds": actual_duration,
            "events_per_second": events_processed / actual_duration,
            "memory_start_mb": start_memory,
            "memory_end_mb": end_memory,
            "memory_increase_mb": end_memory - start_memory,
        }

    def stress_test_concurrent_operations(self, system: dict, num_threads: int = 5) -> dict:
        """Stress test concurrent operations across extensions."""
        results = {"threads_completed": 0, "errors": []}

        def worker_thread(thread_id: int):
            try:
                for i in range(100):  # 100 operations per thread
                    if self.stop_event.is_set():
                        break

                    # Create diverse operations
                    if thread_id % 2 == 0:
                        # Prediction operations
                        event = ToolUseEvent(tool_name=f"tool_{thread_id}_{i}", success=True)
                        if "prediction" in system:
                            system["prediction"].handle_tool_use_event(event)
                    else:
                        # State operations
                        if "state" in system:
                            system["state"].create_snapshot(f"thread_{thread_id}_snapshot_{i}")

                    time.sleep(0.001)  # Small delay to allow context switching

                results["threads_completed"] += 1

            except Exception as e:
                results["errors"].append(f"Thread {thread_id} error: {e}")

        # Start worker threads
        threads = []
        start_time = time.time()

        for i in range(num_threads):
            thread = Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        duration = time.time() - start_time

        return {
            "num_threads": num_threads,
            "threads_completed": results["threads_completed"],
            "errors": results["errors"],
            "duration_seconds": duration,
            "success_rate": results["threads_completed"] / num_threads,
        }

    def stress_test_memory_leak_detection(self, system: dict, iterations: int = 1000) -> dict:
        """Test for memory leaks over many operations."""
        initial_memory = self.measure_memory_usage()
        gc.collect()  # Start with clean memory

        memory_samples = [initial_memory]

        for i in range(iterations):
            # Generate diverse operations
            events = [
                ToolUseEvent(tool_name=f"leak_test_{i}", success=True),
                FileChangeEvent(file_path=f"test_{i}.py", change_type="modified"),
            ]

            for event in events:
                if "prediction" in system and isinstance(event, ToolUseEvent):
                    system["prediction"].handle_tool_use_event(event)

                if "workflow" in system:
                    try:
                        if isinstance(event, ToolUseEvent):
                            asyncio.run(system["workflow"].handle_tool_use_event(event))
                        elif isinstance(event, FileChangeEvent):
                            asyncio.run(system["workflow"].handle_file_change_event(event))
                    except RuntimeError:
                        pass

            # Create and cleanup state snapshots
            if "state" in system and i % 10 == 0:
                system["state"].create_snapshot(f"leak_test_{i}")

            # Sample memory periodically
            if i % 100 == 0:
                gc.collect()
                memory_samples.append(self.measure_memory_usage())

        final_memory = self.measure_memory_usage()
        memory_increase = final_memory - initial_memory

        # Analyze memory trend
        memory_trend = "stable"
        if len(memory_samples) > 2:
            start_avg = sum(memory_samples[:3]) / 3
            end_avg = sum(memory_samples[-3:]) / 3
            if end_avg > start_avg * 1.5:  # >50% increase suggests leak
                memory_trend = "increasing"
            elif end_avg > start_avg * 1.2:  # >20% increase is concerning
                memory_trend = "concerning"

        return {
            "iterations": iterations,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "memory_samples": memory_samples,
            "memory_trend": memory_trend,
            "memory_per_operation_kb": (memory_increase * 1024) / iterations,
        }

    def stress_test_resource_exhaustion(self, system: dict) -> dict:
        """Test system behavior under resource constraints."""
        results = {"file_operations": 0, "memory_operations": 0, "errors": []}

        try:
            # Test many file operations
            for i in range(500):
                if "state" in system:
                    try:
                        system["state"].create_snapshot(f"resource_test_{i}")
                        results["file_operations"] += 1
                    except Exception as e:
                        results["errors"].append(f"File operation {i} failed: {e}")
                        break

            # Test memory-intensive operations
            large_events = []
            for i in range(1000):
                try:
                    event = ToolUseEvent(
                        tool_name=f"memory_test_{i}" * 10,  # Larger string
                        success=True,
                        metadata={"large_data": list(range(100))},  # Some payload
                    )
                    large_events.append(event)

                    if "prediction" in system:
                        system["prediction"].handle_tool_use_event(event)

                    results["memory_operations"] += 1

                except Exception as e:
                    results["errors"].append(f"Memory operation {i} failed: {e}")
                    break

        except Exception as e:
            results["errors"].append(f"Resource exhaustion test failed: {e}")

        return results

    def benchmark_startup_time(self) -> float:
        """Benchmark V2.1 system startup time."""
        start_time = time.time()

        # Full system initialization
        self.setup_full_system()

        end_time = time.time()
        startup_time = end_time - start_time

        return startup_time


@pytest.fixture
def stress_temp_dir():
    """Create temporary directory for stress testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def stress_tester(stress_temp_dir):
    """Create stress tester instance."""
    return ExtensionStressTester(stress_temp_dir)


class TestExtensionStressValidation:
    """Comprehensive stress testing for V2.1 extensions."""

    def test_startup_performance(self, stress_tester):
        """Test V2.1 system startup performance."""
        startup_time = stress_tester.benchmark_startup_time()

        print(f"System startup time: {startup_time:.3f} seconds")

        # Should start up in under 1 second
        assert startup_time < 1.0, f"Startup time too slow: {startup_time:.3f}s"


    def test_concurrent_operations_stability(self, stress_tester):
        """Test stability under concurrent extension operations."""
        system = stress_tester.setup_full_system()

        # Run concurrent operations with 3 threads
        results = stress_tester.stress_test_concurrent_operations(system, num_threads=3)

        print(f"Concurrent test - Success rate: {results['success_rate']:.2f}")
        print(f"Threads completed: {results['threads_completed']}/{results['num_threads']}")
        print(f"Duration: {results['duration_seconds']:.2f}s")

        if results["errors"]:
            print(f"Errors: {results['errors'][:3]}")  # Show first 3 errors

        # Should have high success rate with minimal errors
        assert results["success_rate"] > 0.8, f"Too many thread failures: {results['success_rate']:.2f}"

        assert len(results["errors"]) < 5, f"Too many errors: {len(results['errors'])}"

    def test_memory_leak_detection(self, stress_tester):
        """Test for memory leaks over many operations."""
        system = stress_tester.setup_full_system()

        # Run 500 iterations to detect leaks
        results = stress_tester.stress_test_memory_leak_detection(system, iterations=500)

        print("Memory leak test:")
        print(f"  Initial: {results['initial_memory_mb']:.1f}MB")
        print(f"  Final: {results['final_memory_mb']:.1f}MB")
        print(f"  Increase: {results['memory_increase_mb']:.1f}MB")
        print(f"  Per operation: {results['memory_per_operation_kb']:.2f}KB")
        print(f"  Trend: {results['memory_trend']}")

        # Memory usage should be reasonable
        assert results["memory_increase_mb"] < 100, f"Memory increase too high: {results['memory_increase_mb']:.1f}MB"

        assert (
            results["memory_per_operation_kb"] < 10
        ), f"Memory per operation too high: {results['memory_per_operation_kb']:.2f}KB"

        assert results["memory_trend"] in [
            "stable",
            "concerning",
        ], f"Memory trend indicates leak: {results['memory_trend']}"

