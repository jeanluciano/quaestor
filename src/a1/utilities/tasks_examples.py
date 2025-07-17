"""Usage examples for task management utilities.

This module demonstrates how to use the task management system
extracted from V2.0 with 85% complexity reduction.
"""

import asyncio
import time
from datetime import datetime, timedelta

from src.a1.utilities.tasks import (
    TaskManager,
    TaskPriority,
    Workflow,
    create_simple_task_manager,
    run_tasks,
)


def example_1_basic_task_submission():
    """Example 1: Basic task submission and execution."""
    print("=== Example 1: Basic Task Submission ===")

    async def run_example():
        # Create a simple task manager
        manager = create_simple_task_manager(num_workers=2)

        # Define some tasks
        def calculate_sum(a, b):
            time.sleep(0.1)  # Simulate work
            return a + b

        def calculate_product(x, y):
            time.sleep(0.1)
            return x * y

        # Submit tasks
        task1_id = manager.submit_task(calculate_sum, 5, 10, name="sum_task", priority=TaskPriority.HIGH)

        task2_id = manager.submit_task(calculate_product, 3, 7, name="product_task", priority=TaskPriority.MEDIUM)

        # Start the manager
        manager_task = asyncio.create_task(manager.start())

        # Wait for tasks to complete
        await asyncio.sleep(1.0)

        # Get results
        task1 = manager.get_task(task1_id)
        task2 = manager.get_task(task2_id)

        print(f"Task 1 result: {task1.result.data if task1.result else 'None'}")
        print(f"Task 2 result: {task2.result.data if task2.result else 'None'}")

        # Stop manager
        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_2_task_dependencies():
    """Example 2: Tasks with dependencies."""
    print("\n=== Example 2: Task Dependencies ===")

    async def run_example():
        manager = TaskManager()
        manager.add_worker("dependency_worker", max_concurrent=1)

        results_store = {}

        def step1():
            print("Executing step 1...")
            result = "data_from_step1"
            results_store["step1"] = result
            return result

        def step2():
            print("Executing step 2...")
            step1_data = results_store.get("step1", "missing")
            result = f"processed_{step1_data}"
            results_store["step2"] = result
            return result

        def step3():
            print("Executing step 3...")
            step2_data = results_store.get("step2", "missing")
            return f"final_{step2_data}"

        # Submit tasks with dependencies
        task1_id = manager.submit_task(step1, name="step1")
        task2_id = manager.submit_task(step2, name="step2", depends_on={task1_id})
        task3_id = manager.submit_task(step3, name="step3", depends_on={task2_id})

        # Start manager
        manager_task = asyncio.create_task(manager.start())

        # Wait for completion
        await asyncio.sleep(2.0)

        # Check results
        for task_id, name in [(task1_id, "step1"), (task2_id, "step2"), (task3_id, "step3")]:
            task = manager.get_task(task_id)
            if task and task.result:
                print(f"{name}: {task.result.data}")
            else:
                print(f"{name}: Not completed")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_3_worker_capabilities():
    """Example 3: Worker capabilities and task matching."""
    print("\n=== Example 3: Worker Capabilities ===")

    async def run_example():
        manager = TaskManager()

        # Add workers with different capabilities
        manager.add_worker("python_worker", {"python", "data"})
        manager.add_worker("js_worker", {"javascript", "web"})
        manager.add_worker("general_worker", set())

        def python_task():
            return "Python task completed"

        def js_task():
            return "JavaScript task completed"

        def general_task():
            return "General task completed"

        # Submit tasks with tags
        python_task_id = manager.submit_task(python_task, name="python_work", tags={"python"})

        js_task_id = manager.submit_task(js_task, name="js_work", tags={"javascript"})

        general_task_id = manager.submit_task(general_task, name="general_work")

        # Start manager
        manager_task = asyncio.create_task(manager.start())

        await asyncio.sleep(1.0)

        # Check which worker handled each task
        for task_id, name in [(python_task_id, "Python"), (js_task_id, "JavaScript"), (general_task_id, "General")]:
            task = manager.get_task(task_id)
            if task and task.worker_id:
                worker = manager.workers[task.worker_id]
                print(f"{name} task handled by: {worker.name}")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_4_workflow_orchestration():
    """Example 4: Workflow orchestration."""
    print("\n=== Example 4: Workflow Orchestration ===")

    async def run_example():
        # Create a data processing workflow
        workflow = Workflow("data_processing")

        def extract_data():
            print("Extracting data...")
            return {"records": 100, "source": "database"}

        def transform_data(data_info):
            print(f"Transforming {data_info}")
            return {"transformed_records": 95, "quality": "high"}

        def load_data(transformed_info):
            print(f"Loading {transformed_info}")
            return {"loaded": True, "timestamp": datetime.now().isoformat()}

        # Add workflow steps
        workflow.add_step("extract", "Extract Data", extract_data)
        workflow.add_step("transform", "Transform Data", transform_data, depends_on={"extract"})
        workflow.add_step("load", "Load Data", load_data, depends_on={"transform"})

        # Execute workflow
        manager = create_simple_task_manager(num_workers=1)

        step_to_task = await workflow.execute(manager)

        # Start manager
        manager_task = asyncio.create_task(manager.start())

        await asyncio.sleep(2.0)

        # Check results
        for step_id, task_id in step_to_task.items():
            task = manager.get_task(task_id)
            if task and task.result:
                print(f"{step_id}: {task.result.data}")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_5_error_handling_and_retries():
    """Example 5: Error handling and retries."""
    print("\n=== Example 5: Error Handling and Retries ===")

    async def run_example():
        manager = TaskManager()
        manager.add_worker("retry_worker")

        attempt_count = {"value": 0}

        def flaky_task():
            attempt_count["value"] += 1
            print(f"Attempt {attempt_count['value']}")

            if attempt_count["value"] < 3:
                raise ValueError(f"Simulated failure on attempt {attempt_count['value']}")

            return "Success after retries!"

        # Submit task with retries
        task_id = manager.submit_task(flaky_task, name="flaky_task", max_retries=3)

        manager_task = asyncio.create_task(manager.start())

        await asyncio.sleep(2.0)

        task = manager.get_task(task_id)
        if task:
            print(f"Final status: {task.status}")
            if task.result:
                if task.result.success:
                    print(f"Result: {task.result.data}")
                else:
                    print(f"Error: {task.result.error}")
            print(f"Retry count: {task.retry_count}")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_6_scheduled_tasks():
    """Example 6: Scheduled tasks."""
    print("\n=== Example 6: Scheduled Tasks ===")

    async def run_example():
        manager = TaskManager()
        manager.add_worker("scheduler_worker")

        def immediate_task():
            return f"Executed immediately at {datetime.now()}"

        def delayed_task():
            return f"Executed after delay at {datetime.now()}"

        # Submit immediate task
        immediate_id = manager.submit_task(immediate_task, name="immediate")

        # Submit delayed task (2 seconds from now)
        future_time = datetime.now() + timedelta(seconds=2)
        delayed_id = manager.submit_task(delayed_task, name="delayed", scheduled_at=future_time)

        print(f"Current time: {datetime.now()}")
        print(f"Delayed task scheduled for: {future_time}")

        manager_task = asyncio.create_task(manager.start())

        # Wait for both tasks
        await asyncio.sleep(4.0)

        for task_id, name in [(immediate_id, "immediate"), (delayed_id, "delayed")]:
            task = manager.get_task(task_id)
            if task and task.result:
                print(f"{name}: {task.result.data}")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_7_monitoring_and_metrics():
    """Example 7: Task monitoring and metrics."""
    print("\n=== Example 7: Monitoring and Metrics ===")

    async def run_example():
        manager = TaskManager()
        manager.add_worker("monitor_worker", max_concurrent=2)

        # Event handler for monitoring
        def task_completed_handler(task, worker):
            duration = task.result.duration if task.result else 0
            print(f"Task {task.name} completed by {worker.name} in {duration:.3f}s")

        def task_failed_handler(task, worker):
            error = task.result.error if task.result else "Unknown error"
            print(f"Task {task.name} failed: {error}")

        manager.on("task_completed", task_completed_handler)
        manager.on("task_failed", task_failed_handler)

        # Submit various tasks
        def fast_task():
            time.sleep(0.1)
            return "fast"

        def slow_task():
            time.sleep(0.5)
            return "slow"

        def failing_task():
            raise RuntimeError("This task always fails")

        for i in range(3):
            manager.submit_task(fast_task, name=f"fast_{i}")
            manager.submit_task(slow_task, name=f"slow_{i}")

        manager.submit_task(failing_task, name="failing", max_retries=1)

        manager_task = asyncio.create_task(manager.start())

        await asyncio.sleep(3.0)

        # Get final statistics
        stats = manager.get_stats()
        print("\nFinal Statistics:")
        print(f"Tasks submitted: {stats['metrics']['tasks_submitted']}")
        print(f"Tasks completed: {stats['metrics']['tasks_completed']}")
        print(f"Tasks failed: {stats['metrics']['tasks_failed']}")
        print(f"Total execution time: {stats['metrics']['total_execution_time']:.3f}s")

        await manager.stop()
        manager_task.cancel()

    asyncio.run(run_example())


def example_8_utility_functions():
    """Example 8: Using utility functions."""
    print("\n=== Example 8: Utility Functions ===")

    async def run_example():
        # Simple task execution with run_tasks
        def task1():
            time.sleep(0.1)
            return "Task 1 result"

        def task2():
            time.sleep(0.2)
            return "Task 2 result"

        def task3():
            time.sleep(0.1)
            return "Task 3 result"

        tasks = [task1, task2, task3]

        print("Running tasks concurrently...")
        start_time = time.time()
        results = await run_tasks(tasks, max_workers=2)
        duration = time.time() - start_time

        print(f"All tasks completed in {duration:.3f}s")

        for i, result in enumerate(results):
            if result.success:
                print(f"Task {i+1}: {result.data}")
            else:
                print(f"Task {i+1} failed: {result.error}")

    asyncio.run(run_example())


def main():
    """Run all examples."""
    print("Task Management Utilities - Usage Examples")
    print("==========================================")

    example_1_basic_task_submission()
    example_2_task_dependencies()
    example_3_worker_capabilities()
    example_4_workflow_orchestration()
    example_5_error_handling_and_retries()
    example_6_scheduled_tasks()
    example_7_monitoring_and_metrics()
    example_8_utility_functions()

    print("\n=== All Examples Completed ===")


if __name__ == "__main__":
    main()
