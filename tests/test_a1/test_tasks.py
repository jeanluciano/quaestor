"""Tests for task management utilities."""

import asyncio
from datetime import datetime, timedelta

import pytest

from a1.utilities.tasks import (
    Task,
    TaskManager,
    TaskPriority,
    TaskQueue,
    TaskResult,
    TaskStatus,
    Worker,
    WorkerStatus,
    Workflow,
    create_simple_task_manager,
    run_tasks,
)


class TestTaskResult:
    """Test TaskResult dataclass."""

    def test_default_creation(self):
        result = TaskResult()
        assert result.success is False
        assert result.data is None
        assert result.error is None
        assert result.duration is None
        assert result.metadata == {}

    def test_creation_with_data(self):
        result = TaskResult(success=True, data={"output": "test"}, duration=1.5, metadata={"worker": "w1"})
        assert result.success is True
        assert result.data == {"output": "test"}
        assert result.duration == 1.5
        assert result.metadata == {"worker": "w1"}


class TestTask:
    """Test Task dataclass and methods."""

    def test_default_creation(self):
        task = Task()
        assert task.id is not None
        assert task.name == ""
        assert task.priority == TaskPriority.MEDIUM
        assert task.status == TaskStatus.PENDING
        assert task.func is None
        assert task.args == ()
        assert task.kwargs == {}
        assert isinstance(task.created_at, datetime)
        assert task.depends_on == set()
        assert task.max_retries == 3
        assert task.retry_count == 0
        assert task.result is None
        assert task.progress == 0.0
        assert task.tags == set()
        assert task.metadata == {}

    def test_creation_with_params(self):
        def test_func():
            return "test"

        depends = {"task1", "task2"}
        tags = {"urgent", "backend"}

        task = Task(
            name="test_task",
            priority=TaskPriority.HIGH,
            func=test_func,
            args=(1, 2),
            kwargs={"key": "value"},
            depends_on=depends,
            max_retries=5,
            tags=tags,
        )

        assert task.name == "test_task"
        assert task.priority == TaskPriority.HIGH
        assert task.func == test_func
        assert task.args == (1, 2)
        assert task.kwargs == {"key": "value"}
        assert task.depends_on == depends
        assert task.max_retries == 5
        assert task.tags == tags

    def test_is_ready_no_dependencies(self):
        task = Task()
        completed = {"task1", "task2"}
        assert task.is_ready(completed) is True

    def test_is_ready_with_satisfied_dependencies(self):
        task = Task(depends_on={"task1", "task2"})
        completed = {"task1", "task2", "task3"}
        assert task.is_ready(completed) is True

    def test_is_ready_with_unsatisfied_dependencies(self):
        task = Task(depends_on={"task1", "task2"})
        completed = {"task1"}
        assert task.is_ready(completed) is False

    def test_is_ready_wrong_status(self):
        task = Task(status=TaskStatus.RUNNING)
        completed = set()
        assert task.is_ready(completed) is False

    def test_is_ready_with_scheduled_time_future(self):
        future_time = datetime.now() + timedelta(minutes=5)
        task = Task(scheduled_at=future_time)
        completed = set()
        assert task.is_ready(completed) is False

    def test_is_ready_with_scheduled_time_past(self):
        past_time = datetime.now() - timedelta(minutes=5)
        task = Task(scheduled_at=past_time)
        completed = set()
        assert task.is_ready(completed) is True

    def test_can_retry_success(self):
        task = Task(status=TaskStatus.FAILED, retry_count=1, max_retries=3)
        assert task.can_retry() is True

    def test_can_retry_max_retries_reached(self):
        task = Task(status=TaskStatus.FAILED, retry_count=3, max_retries=3)
        assert task.can_retry() is False

    def test_can_retry_wrong_status(self):
        task = Task(status=TaskStatus.COMPLETED, retry_count=1, max_retries=3)
        assert task.can_retry() is False


class TestWorker:
    """Test Worker dataclass and methods."""

    def test_default_creation(self):
        worker = Worker()
        assert worker.id is not None
        assert worker.name == ""
        assert worker.status == WorkerStatus.IDLE
        assert worker.capabilities == set()
        assert worker.max_concurrent_tasks == 1
        assert worker.current_tasks == set()
        assert worker.tasks_completed == 0
        assert worker.tasks_failed == 0
        assert worker.total_execution_time == 0.0
        assert isinstance(worker.last_activity, datetime)

    def test_creation_with_params(self):
        capabilities = {"python", "testing"}
        worker = Worker(name="test_worker", capabilities=capabilities, max_concurrent_tasks=3)

        assert worker.name == "test_worker"
        assert worker.capabilities == capabilities
        assert worker.max_concurrent_tasks == 3

    def test_can_handle_task_success(self):
        worker = Worker(capabilities={"python", "testing"})
        task = Task(tags={"python"})

        assert worker.can_handle_task(task) is True

    def test_can_handle_task_wrong_status(self):
        worker = Worker(status=WorkerStatus.BUSY)
        task = Task()

        assert worker.can_handle_task(task) is False

    def test_can_handle_task_too_many_tasks(self):
        worker = Worker(max_concurrent_tasks=1, current_tasks={"task1"})
        task = Task()

        assert worker.can_handle_task(task) is False

    def test_can_handle_task_missing_capabilities(self):
        worker = Worker(capabilities={"python"})
        task = Task(tags={"java", "testing"})

        assert worker.can_handle_task(task) is False

    def test_can_handle_task_no_tags(self):
        worker = Worker(capabilities={"python"})
        task = Task()  # No tags

        assert worker.can_handle_task(task) is True

    def test_success_rate_no_tasks(self):
        worker = Worker()
        assert worker.success_rate == 1.0

    def test_success_rate_with_tasks(self):
        worker = Worker(tasks_completed=8, tasks_failed=2)
        assert worker.success_rate == 0.8

    def test_average_execution_time_no_tasks(self):
        worker = Worker()
        assert worker.average_execution_time == 0.0

    def test_average_execution_time_with_tasks(self):
        worker = Worker(tasks_completed=4, total_execution_time=8.0)
        assert worker.average_execution_time == 2.0


class TestTaskQueue:
    """Test TaskQueue functionality."""

    def test_creation(self):
        queue = TaskQueue()
        assert queue.size() == 0
        assert queue.is_empty() is True

    def test_add_task(self):
        queue = TaskQueue()
        task = Task(name="test")

        queue.add(task)

        assert queue.size() == 1
        assert queue.is_empty() is False
        assert task.status == TaskStatus.QUEUED

    def test_add_duplicate_task(self):
        queue = TaskQueue()
        task = Task(name="test")

        queue.add(task)
        queue.add(task)  # Should not add duplicate

        assert queue.size() == 1

    def test_get_next_no_tasks(self):
        queue = TaskQueue()
        worker = Worker()

        result = queue.get_next(worker)
        assert result is None

    def test_get_next_priority_order(self):
        queue = TaskQueue()
        worker = Worker()

        low_task = Task(name="low", priority=TaskPriority.LOW)
        high_task = Task(name="high", priority=TaskPriority.HIGH)
        critical_task = Task(name="critical", priority=TaskPriority.CRITICAL)

        queue.add(low_task)
        queue.add(high_task)
        queue.add(critical_task)

        # Should get critical first
        result = queue.get_next(worker)
        assert result.name == "critical"
        assert queue.size() == 2

    def test_get_next_worker_cannot_handle(self):
        queue = TaskQueue()
        worker = Worker(capabilities={"python"})
        task = Task(tags={"java"})

        queue.add(task)

        result = queue.get_next(worker)
        assert result is None
        assert queue.size() == 1  # Task should remain in queue

    def test_remove_task(self):
        queue = TaskQueue()
        task = Task(name="test")

        queue.add(task)
        removed = queue.remove(task.id)

        assert removed is True
        assert queue.size() == 0

    def test_remove_nonexistent_task(self):
        queue = TaskQueue()
        removed = queue.remove("nonexistent")

        assert removed is False


class TestTaskManager:
    """Test TaskManager functionality."""

    def test_creation(self):
        manager = TaskManager(max_workers=2)

        assert manager.max_workers == 2
        assert len(manager.workers) == 0
        assert len(manager.tasks) == 0
        assert len(manager.completed_tasks) == 0
        assert manager.running is False
        assert manager.metrics["tasks_submitted"] == 0

    def test_add_worker(self):
        manager = TaskManager()

        worker_id = manager.add_worker("test_worker", {"python"}, 2)

        assert worker_id in manager.workers
        worker = manager.workers[worker_id]
        assert worker.name == "test_worker"
        assert worker.capabilities == {"python"}
        assert worker.max_concurrent_tasks == 2

    def test_submit_task(self):
        manager = TaskManager()

        def test_func():
            return "result"

        task_id = manager.submit_task(test_func, name="test_task", priority=TaskPriority.HIGH)

        assert task_id in manager.tasks
        task = manager.tasks[task_id]
        assert task.name == "test_task"
        assert task.priority == TaskPriority.HIGH
        assert task.func == test_func
        assert manager.metrics["tasks_submitted"] == 1

    def test_submit_task_with_dependencies(self):
        manager = TaskManager()

        task_id = manager.submit_task(lambda: "result", depends_on={"missing_dep"})

        task = manager.tasks[task_id]
        assert task.status == TaskStatus.PENDING  # Should not be queued yet
        assert manager.queue.size() == 0

    def test_submit_task_ready_to_queue(self):
        manager = TaskManager()
        manager.completed_tasks.add("dep1")

        task_id = manager.submit_task(lambda: "result", depends_on={"dep1"})

        assert manager.queue.size() == 1

    def test_get_task(self):
        manager = TaskManager()
        task_id = manager.submit_task(lambda: "result")

        task = manager.get_task(task_id)
        assert task is not None
        assert task.id == task_id

        nonexistent = manager.get_task("nonexistent")
        assert nonexistent is None

    def test_cancel_task_pending(self):
        manager = TaskManager()
        task_id = manager.submit_task(lambda: "result")

        cancelled = manager.cancel_task(task_id)

        assert cancelled is True
        task = manager.tasks[task_id]
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_task_running(self):
        manager = TaskManager()
        task_id = manager.submit_task(lambda: "result")
        task = manager.tasks[task_id]
        task.status = TaskStatus.RUNNING

        cancelled = manager.cancel_task(task_id)

        assert cancelled is False

    def test_cancel_nonexistent_task(self):
        manager = TaskManager()
        cancelled = manager.cancel_task("nonexistent")

        assert cancelled is False

    def test_event_handlers(self):
        manager = TaskManager()
        events = []

        def handler(event_type, *args):
            events.append((event_type, args))

        manager.on("task_submitted", handler)
        manager.submit_task(lambda: "result")

        # Note: Event emission happens in _emit_event which uses different signature
        # This test mainly checks that handlers are registered
        assert len(manager._event_handlers["task_submitted"]) == 1

    def test_get_stats(self):
        manager = TaskManager()
        manager.add_worker("worker1")
        manager.submit_task(lambda: "result")

        stats = manager.get_stats()

        assert "metrics" in stats
        assert "queue_size" in stats
        assert "workers" in stats
        assert "task_statuses" in stats
        assert stats["metrics"]["tasks_submitted"] == 1
        assert len(stats["workers"]) == 1


class TestWorkflow:
    """Test Workflow functionality."""

    def test_creation(self):
        workflow = Workflow("test_workflow")

        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 0
        assert workflow.task_manager is None

    def test_add_step(self):
        workflow = Workflow("test")

        def test_func(x):
            return x * 2

        workflow.add_step("step1", "First Step", test_func, 5, depends_on=set(), tags={"math"}, multiplier=2)

        assert "step1" in workflow.steps
        step = workflow.steps["step1"]
        assert step.name == "First Step"
        assert step.func == test_func
        assert step.args == (5,)
        assert step.kwargs == {"multiplier": 2}
        assert step.tags == {"math"}

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        workflow = Workflow("test")
        manager = TaskManager()

        def step1():
            return "result1"

        def step2():
            return "result2"

        workflow.add_step("step1", "Step 1", step1)
        workflow.add_step("step2", "Step 2", step2, depends_on={"step1"})

        step_to_task = await workflow.execute(manager)

        assert len(step_to_task) == 2
        assert "step1" in step_to_task
        assert "step2" in step_to_task

        # Check that step2 depends on step1's task
        step2_task = manager.get_task(step_to_task["step2"])
        assert step_to_task["step1"] in step2_task.depends_on


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_simple_task_manager(self):
        manager = create_simple_task_manager(3)

        assert manager.max_workers == 3
        assert len(manager.workers) == 3

        # Check worker names
        worker_names = [w.name for w in manager.workers.values()]
        assert "worker_0" in worker_names
        assert "worker_1" in worker_names
        assert "worker_2" in worker_names

    @pytest.mark.asyncio
    async def test_run_tasks_simple(self):
        def task1():
            return "result1"

        def task2():
            return "result2"

        tasks = [task1, task2]
        results = await run_tasks(tasks, max_workers=2)

        assert len(results) == 2
        # Results should contain task results
        result_data = [r.data for r in results if r.success]
        assert "result1" in result_data
        assert "result2" in result_data

    @pytest.mark.asyncio
    async def test_run_tasks_with_failure(self):
        def task1():
            return "success"

        def task2():
            raise ValueError("Test error")

        tasks = [task1, task2]
        results = await run_tasks(tasks, max_workers=2)

        assert len(results) == 2

        success_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        assert len(success_results) == 1
        assert len(failed_results) == 1
        assert "Test error" in failed_results[0].error


class TestAsyncIntegration:
    """Test async functionality."""

    @pytest.mark.asyncio
    async def test_task_manager_lifecycle(self):
        manager = TaskManager()
        manager.add_worker("test_worker")

        # Start manager
        start_task = asyncio.create_task(manager.start())
        await asyncio.sleep(0.1)  # Let it start

        assert manager.running is True

        # Submit a task
        def simple_task():
            return "completed"

        task_id = manager.submit_task(simple_task)

        # Wait for task completion
        for _ in range(10):  # Max 1 second wait
            task = manager.get_task(task_id)
            if task and task.status == TaskStatus.COMPLETED:
                break
            await asyncio.sleep(0.1)

        task = manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result.success is True
        assert task.result.data == "completed"

        # Stop manager
        await manager.stop()
        start_task.cancel()

        assert manager.running is False

    @pytest.mark.asyncio
    async def test_async_task_execution(self):
        manager = TaskManager()
        manager.add_worker("async_worker")

        # Start manager
        start_task = asyncio.create_task(manager.start())
        await asyncio.sleep(0.1)

        async def async_task():
            await asyncio.sleep(0.1)
            return "async_result"

        task_id = manager.submit_task(async_task)

        # Wait for completion
        for _ in range(10):
            task = manager.get_task(task_id)
            if task and task.status == TaskStatus.COMPLETED:
                break
            await asyncio.sleep(0.1)

        task = manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result.data == "async_result"

        # Cleanup
        await manager.stop()
        start_task.cancel()

    @pytest.mark.asyncio
    async def test_task_dependencies(self):
        manager = TaskManager()
        manager.add_worker("dep_worker")

        start_task = asyncio.create_task(manager.start())
        await asyncio.sleep(0.1)

        results = {}

        def task1():
            results["task1"] = "done"
            return "task1_result"

        def task2():
            return f"task2_result_with_{results.get('task1', 'missing')}"

        # Submit tasks with dependency
        task1_id = manager.submit_task(task1)
        task2_id = manager.submit_task(task2, depends_on={task1_id})

        # Wait for both to complete
        for _ in range(20):
            task1_obj = manager.get_task(task1_id)
            task2_obj = manager.get_task(task2_id)

            if (
                task1_obj
                and task1_obj.status == TaskStatus.COMPLETED
                and task2_obj
                and task2_obj.status == TaskStatus.COMPLETED
            ):
                break
            await asyncio.sleep(0.1)

        task1_obj = manager.get_task(task1_id)
        task2_obj = manager.get_task(task2_id)

        assert task1_obj.status == TaskStatus.COMPLETED
        assert task2_obj.status == TaskStatus.COMPLETED
        assert "task2_result_with_done" in task2_obj.result.data

        # Cleanup
        await manager.stop()
        start_task.cancel()


if __name__ == "__main__":
    pytest.main([__file__])
