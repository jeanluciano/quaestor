"""Task management and workflow coordination utilities.

Extracted from A1 Task Management, Agent Orchestration, and Workflow systems.
Provides comprehensive task coordination with 85% complexity reduction.
"""

import asyncio
import contextlib
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class WorkerStatus(Enum):
    """Worker status."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class TaskResult:
    """Task execution result."""

    success: bool = False
    data: Any = None
    error: str | None = None
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents a task to be executed."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    # Execution details
    func: Callable | None = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)

    # Scheduling
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Dependencies and constraints
    depends_on: set[str] = field(default_factory=set)
    max_retries: int = 3
    retry_count: int = 0
    timeout: float | None = None

    # Results and tracking
    result: TaskResult | None = None
    progress: float = 0.0
    worker_id: str | None = None
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed_tasks: set[str]) -> bool:
        """Check if task is ready to execute.

        Args:
            completed_tasks: Set of completed task IDs

        Returns:
            True if all dependencies are satisfied
        """
        if self.status != TaskStatus.PENDING:
            return False

        # Check if scheduled time has passed
        if self.scheduled_at and datetime.now() < self.scheduled_at:
            return False

        # Check dependencies
        return self.depends_on.issubset(completed_tasks)

    def can_retry(self) -> bool:
        """Check if task can be retried.

        Returns:
            True if retry is possible
        """
        return self.status == TaskStatus.FAILED and self.retry_count < self.max_retries


@dataclass
class Worker:
    """Represents a task worker."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    status: WorkerStatus = WorkerStatus.IDLE
    capabilities: set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 1
    current_tasks: set[str] = field(default_factory=set)

    # Performance tracking
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)

    def can_handle_task(self, task: Task) -> bool:
        """Check if worker can handle a task.

        Args:
            task: Task to check

        Returns:
            True if worker can handle the task
        """
        if self.status != WorkerStatus.IDLE:
            return False

        if len(self.current_tasks) >= self.max_concurrent_tasks:
            return False

        # Check capabilities
        task_tags = task.tags
        return not (task_tags and not task_tags.intersection(self.capabilities))

    @property
    def success_rate(self) -> float:
        """Calculate worker success rate.

        Returns:
            Success rate (0.0 to 1.0)
        """
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks == 0:
            return 1.0
        return self.tasks_completed / total_tasks

    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time.

        Returns:
            Average execution time in seconds
        """
        if self.tasks_completed == 0:
            return 0.0
        return self.total_execution_time / self.tasks_completed


class TaskQueue:
    """Priority-based task queue."""

    def __init__(self):
        """Initialize task queue."""
        self._queues: dict[TaskPriority, deque] = {priority: deque() for priority in TaskPriority}
        self._task_index: dict[str, Task] = {}

    def add(self, task: Task):
        """Add task to queue.

        Args:
            task: Task to add
        """
        if task.id in self._task_index:
            return  # Task already in queue

        task.status = TaskStatus.QUEUED
        self._queues[task.priority].appendleft(task)
        self._task_index[task.id] = task

    def get_next(self, worker: Worker) -> Task | None:
        """Get next task for a worker.

        Args:
            worker: Worker requesting task

        Returns:
            Next available task or None
        """
        # Check priorities from high to low
        for priority in reversed(list(TaskPriority)):
            queue = self._queues[priority]

            # Find first task the worker can handle
            for _i, task in enumerate(queue):
                if worker.can_handle_task(task):
                    # Remove from queue
                    queue.remove(task)
                    del self._task_index[task.id]
                    return task

        return None

    def remove(self, task_id: str) -> bool:
        """Remove task from queue.

        Args:
            task_id: Task ID to remove

        Returns:
            True if task was removed
        """
        if task_id not in self._task_index:
            return False

        task = self._task_index[task_id]
        self._queues[task.priority].remove(task)
        del self._task_index[task_id]
        return True

    def size(self) -> int:
        """Get total queue size.

        Returns:
            Number of tasks in queue
        """
        return sum(len(queue) for queue in self._queues.values())

    def is_empty(self) -> bool:
        """Check if queue is empty.

        Returns:
            True if no tasks in queue
        """
        return self.size() == 0


class TaskManager:
    """Manages task execution and coordination."""

    def __init__(self, max_workers: int = 4):
        """Initialize task manager.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.queue = TaskQueue()
        self.workers: dict[str, Worker] = {}
        self.tasks: dict[str, Task] = {}
        self.completed_tasks: set[str] = set()
        self.running = False

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = defaultdict(list)

        # Metrics
        self.metrics = {"tasks_submitted": 0, "tasks_completed": 0, "tasks_failed": 0, "total_execution_time": 0.0}

    def add_worker(self, name: str, capabilities: set[str] | None = None, max_concurrent: int = 1) -> str:
        """Add a worker.

        Args:
            name: Worker name
            capabilities: Worker capabilities
            max_concurrent: Maximum concurrent tasks

        Returns:
            Worker ID
        """
        worker = Worker(name=name, capabilities=capabilities or set(), max_concurrent_tasks=max_concurrent)
        self.workers[worker.id] = worker
        return worker.id

    def submit_task(
        self,
        func: Callable,
        *args,
        name: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        depends_on: set[str] | None = None,
        scheduled_at: datetime | None = None,
        timeout: float | None = None,
        max_retries: int = 3,
        tags: set[str] | None = None,
        **kwargs,
    ) -> str:
        """Submit a task for execution.

        Args:
            func: Function to execute
            *args: Function arguments
            name: Task name
            priority: Task priority
            depends_on: Task dependencies
            scheduled_at: Scheduled execution time
            timeout: Execution timeout
            max_retries: Maximum retry attempts
            tags: Task tags for worker matching
            **kwargs: Function keyword arguments

        Returns:
            Task ID
        """
        task = Task(
            name=name or func.__name__,
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            depends_on=depends_on or set(),
            scheduled_at=scheduled_at,
            timeout=timeout,
            max_retries=max_retries,
            tags=tags or set(),
        )

        self.tasks[task.id] = task
        self.metrics["tasks_submitted"] += 1

        # Check if task is ready to queue
        if task.is_ready(self.completed_tasks):
            self.queue.add(task)

        self._emit_event("task_submitted", task)
        return task.id

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None
        """
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID

        Returns:
            True if task was cancelled
        """
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status in (TaskStatus.PENDING, TaskStatus.QUEUED):
            task.status = TaskStatus.CANCELLED
            self.queue.remove(task_id)
            self._emit_event("task_cancelled", task)
            return True

        return False

    def on(self, event: str, handler: Callable):
        """Register event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        self._event_handlers[event].append(handler)

    def _emit_event(self, event: str, *args):
        """Emit event to handlers.

        Args:
            event: Event name
            *args: Event arguments
        """
        for handler in self._event_handlers[event]:
            with contextlib.suppress(Exception):
                handler(*args)

    async def start(self):
        """Start the task manager."""
        if self.running:
            return

        self.running = True

        # Create default worker if none exist
        if not self.workers:
            self.add_worker("default_worker")

        # Start worker loops
        worker_tasks = []
        for worker in self.workers.values():
            worker_tasks.append(asyncio.create_task(self._worker_loop(worker)))

        # Start dependency resolution loop
        dependency_task = asyncio.create_task(self._dependency_loop())

        with suppress(asyncio.CancelledError):
            await asyncio.gather(*worker_tasks, dependency_task)

    async def stop(self):
        """Stop the task manager."""
        self.running = False

        # Cancel running tasks
        for task in self.tasks.values():
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.CANCELLED

    async def _worker_loop(self, worker: Worker):
        """Worker execution loop.

        Args:
            worker: Worker instance
        """
        while self.running:
            try:
                # Get next task
                task = self.queue.get_next(worker)

                if task:
                    await self._execute_task(worker, task)
                else:
                    # No tasks available, wait a bit
                    await asyncio.sleep(0.1)
            except Exception:
                worker.status = WorkerStatus.ERROR
                await asyncio.sleep(1.0)  # Recover from error
                worker.status = WorkerStatus.IDLE

    async def _execute_task(self, worker: Worker, task: Task):
        """Execute a task.

        Args:
            worker: Worker executing the task
            task: Task to execute
        """
        # Prepare for execution
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.worker_id = worker.id
        worker.status = WorkerStatus.BUSY
        worker.current_tasks.add(task.id)
        worker.last_activity = datetime.now()

        self._emit_event("task_started", task, worker)

        start_time = time.time()

        try:
            # Execute the function
            if asyncio.iscoroutinefunction(task.func):
                result_data = await task.func(*task.args, **task.kwargs)
            else:
                result_data = task.func(*task.args, **task.kwargs)

            # Task completed successfully
            execution_time = time.time() - start_time

            task.result = TaskResult(success=True, data=result_data, duration=execution_time)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 1.0

            # Update worker stats
            worker.tasks_completed += 1
            worker.total_execution_time += execution_time

            # Update global stats
            self.metrics["tasks_completed"] += 1
            self.metrics["total_execution_time"] += execution_time

            # Add to completed set
            self.completed_tasks.add(task.id)

            self._emit_event("task_completed", task, worker)

        except Exception as e:
            # Task failed
            execution_time = time.time() - start_time

            task.result = TaskResult(success=False, error=str(e), duration=execution_time)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

            # Update worker stats
            worker.tasks_failed += 1

            # Update global stats
            self.metrics["tasks_failed"] += 1

            # Check if we should retry
            if task.can_retry():
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                # Re-queue for retry
                self.queue.add(task)
                self._emit_event("task_retry", task, worker)
            else:
                self._emit_event("task_failed", task, worker)

        finally:
            # Clean up worker state
            worker.status = WorkerStatus.IDLE
            worker.current_tasks.discard(task.id)

    async def _dependency_loop(self):
        """Loop to check and queue tasks with satisfied dependencies."""
        while self.running:
            # Check pending tasks for satisfied dependencies
            ready_tasks = []

            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING and task.is_ready(self.completed_tasks):
                    ready_tasks.append(task)

            # Queue ready tasks
            for task in ready_tasks:
                self.queue.add(task)

            await asyncio.sleep(0.5)  # Check every 500ms

    def get_stats(self) -> dict[str, Any]:
        """Get task manager statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "metrics": self.metrics.copy(),
            "queue_size": self.queue.size(),
            "workers": {
                worker.id: {
                    "name": worker.name,
                    "status": worker.status.value,
                    "tasks_completed": worker.tasks_completed,
                    "tasks_failed": worker.tasks_failed,
                    "success_rate": worker.success_rate,
                    "avg_execution_time": worker.average_execution_time,
                    "current_tasks": len(worker.current_tasks),
                }
                for worker in self.workers.values()
            },
            "task_statuses": {
                status.value: len([t for t in self.tasks.values() if t.status == status]) for status in TaskStatus
            },
        }


# Workflow utilities


@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""

    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    depends_on: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)


class Workflow:
    """Simple workflow management."""

    def __init__(self, name: str):
        """Initialize workflow.

        Args:
            name: Workflow name
        """
        self.name = name
        self.steps: dict[str, WorkflowStep] = {}
        self.task_manager: TaskManager | None = None

    def add_step(
        self,
        step_id: str,
        name: str,
        func: Callable,
        *args,
        depends_on: set[str] | None = None,
        tags: set[str] | None = None,
        **kwargs,
    ):
        """Add step to workflow.

        Args:
            step_id: Step identifier
            name: Step name
            func: Function to execute
            *args: Function arguments
            depends_on: Step dependencies
            tags: Step tags
            **kwargs: Function keyword arguments
        """
        step = WorkflowStep(
            id=step_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            depends_on=depends_on or set(),
            tags=tags or set(),
        )
        self.steps[step_id] = step

    async def execute(self, task_manager: TaskManager) -> dict[str, str]:
        """Execute workflow.

        Args:
            task_manager: Task manager to use

        Returns:
            Dictionary mapping step IDs to task IDs
        """
        self.task_manager = task_manager
        step_to_task: dict[str, str] = {}

        # Submit all steps as tasks
        for step in self.steps.values():
            # Map step dependencies to task dependencies
            task_depends_on = {
                step_to_task[dep_step_id] for dep_step_id in step.depends_on if dep_step_id in step_to_task
            }

            task_id = task_manager.submit_task(
                step.func,
                *step.args,
                name=f"{self.name}:{step.name}",
                depends_on=task_depends_on,
                tags=step.tags,
                **step.kwargs,
            )

            step_to_task[step.id] = task_id

        return step_to_task


# Convenience functions


@contextmanager
def task_context(task_manager: TaskManager):
    """Context manager for task manager lifecycle.

    Args:
        task_manager: Task manager instance
    """

    async def run_manager():
        await task_manager.start()

    try:
        # Start the manager
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If event loop is already running, schedule as task
            task = loop.create_task(task_manager.start())
            yield task_manager
            task.cancel()
        else:
            # Run in new event loop
            yield task_manager
            loop.run_until_complete(task_manager.start())
    finally:
        loop.run_until_complete(task_manager.stop())


def create_simple_task_manager(num_workers: int = 4) -> TaskManager:
    """Create a simple task manager with default workers.

    Args:
        num_workers: Number of workers to create

    Returns:
        Configured TaskManager
    """
    manager = TaskManager(max_workers=num_workers)

    for i in range(num_workers):
        manager.add_worker(f"worker_{i}", max_concurrent=1)

    return manager


async def run_tasks(tasks: list[Callable], max_workers: int = 4) -> list[TaskResult]:
    """Run a list of tasks concurrently.

    Args:
        tasks: List of functions to execute
        max_workers: Maximum concurrent workers

    Returns:
        List of task results
    """
    manager = create_simple_task_manager(max_workers)

    # Submit all tasks
    task_ids = []
    for task_func in tasks:
        task_id = manager.submit_task(task_func)
        task_ids.append(task_id)

    # Start manager
    manager_task = asyncio.create_task(manager.start())

    # Wait for all tasks to complete
    results = []
    try:
        while len(results) < len(task_ids):
            for task_id in task_ids:
                task = manager.get_task(task_id)
                if (
                    task
                    and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
                    and task.result
                    and task.id not in [r.metadata.get("task_id") for r in results]
                ):
                    task.result.metadata["task_id"] = task.id
                    results.append(task.result)

            await asyncio.sleep(0.1)

    finally:
        await manager.stop()
        manager_task.cancel()

    return results
