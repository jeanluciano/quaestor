#!/usr/bin/env python3
"""Coordinate agent usage based on TODO changes.

This hook analyzes TODO patterns and completion rates to suggest appropriate
agents for different workflow phases. It helps maintain momentum by guiding
Claude to the right specialist agent based on task progress.
"""

import json
import sys
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def parse_hook_input() -> dict[str, Any]:
    """Parse Claude hook input from stdin."""
    try:
        input_data = sys.stdin.read()
        if input_data:
            return json.loads(input_data)
        return {}
    except Exception:
        return {}


def analyze_todo_patterns(todos: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze TODO patterns to determine workflow state and needs."""
    analysis = {
        "total": len(todos),
        "completed": 0,
        "in_progress": 0,
        "pending": 0,
        "high_priority_complete": 0,
        "high_priority_pending": 0,
        "completion_rate": 0,
        "has_testing_todos": False,
        "has_documentation_todos": False,
        "has_implementation_todos": False,
    }

    for todo in todos:
        status = todo.get("status", "pending")
        priority = todo.get("priority", "medium")
        content = todo.get("content", "").lower()

        # Count by status
        if status == "completed":
            analysis["completed"] += 1
            if priority == "high":
                analysis["high_priority_complete"] += 1
        elif status == "in_progress":
            analysis["in_progress"] += 1
        else:
            analysis["pending"] += 1
            if priority == "high":
                analysis["high_priority_pending"] += 1

        # Categorize by content
        if any(word in content for word in ["test", "spec", "coverage", "qa"]):
            analysis["has_testing_todos"] = True
        if any(word in content for word in ["doc", "readme", "comment", "update memory"]):
            analysis["has_documentation_todos"] = True
        if any(word in content for word in ["implement", "create", "add", "build", "feature"]):
            analysis["has_implementation_todos"] = True

    # Calculate completion rate
    if analysis["total"] > 0:
        analysis["completion_rate"] = int((analysis["completed"] / analysis["total"]) * 100)

    return analysis


def get_milestone_progress(project_root: Path) -> dict[str, Any]:
    """Get current milestone progress from MEMORY.md."""
    memory_file = project_root / ".quaestor" / "MEMORY.md"

    if not memory_file.exists():
        return {"has_milestone": False}

    try:
        content = memory_file.read_text()
        import re

        milestone_match = re.search(r"current_milestone:\s*['\"]?([^'\"]+)['\"]?", content)
        progress_match = re.search(r"progress:\s*(\d+)%", content)

        if milestone_match and progress_match:
            return {"has_milestone": True, "name": milestone_match.group(1), "progress": int(progress_match.group(1))}
    except Exception:
        pass

    return {"has_milestone": False}


def generate_agent_suggestion(
    analysis: dict[str, Any], milestone: dict[str, Any], recent_completions: list[dict[str, Any]]
) -> tuple[bool, str]:
    """Generate agent suggestion based on TODO analysis.

    Returns:
        Tuple of (should_block, message)
    """

    # Scenario 1: Multiple high-priority TODOs completed
    if analysis["high_priority_complete"] >= 3:
        return (
            True,
            f"""
🎯 Significant Progress Detected: {analysis["high_priority_complete"]} high-priority TODOs completed!

This indicates major implementation progress that needs quality review.

Please run: Use the qa agent to review the completed implementation and ensure quality

The QA agent should:
1. Review code changes for all completed high-priority TODOs
2. Check test coverage for new implementations
3. Validate error handling and edge cases
4. Ensure documentation is updated
5. Run integration tests if applicable

Recent completions:
{chr(10).join(f"- {todo['content']}" for todo in recent_completions[:5])}
""",
        )

    # Scenario 2: High completion rate approaching milestone completion
    if analysis["completion_rate"] >= 80 and milestone.get("has_milestone") and milestone.get("progress", 0) >= 80:
        return (
            True,
            f"""
🏁 Approaching Milestone Completion: {analysis["completion_rate"]}% TODOs done, Milestone '{milestone["name"]}' at {milestone["progress"]}%

You're close to completing this milestone!

Please run: Use the milestone-manager agent to prepare for milestone completion

The milestone-manager should:
1. Review all completed work against milestone objectives
2. Update final progress percentages
3. Prepare PR description with completed features
4. Document any deferred items for next milestone
5. Create comprehensive completion summary
""",
        )

    # Scenario 3: Testing TODOs pending after implementation
    if analysis["completed"] > 5 and analysis["has_testing_todos"] and analysis["has_implementation_todos"]:
        completed_impl = sum(
            1
            for todo in recent_completions
            if any(word in todo.get("content", "").lower() for word in ["implement", "create", "add", "build"])
        )
        pending_tests = sum(
            1
            for todo in recent_completions
            if todo.get("status") == "pending" and "test" in todo.get("content", "").lower()
        )

        if completed_impl > 3 and pending_tests > 0:
            return (
                True,
                f"""
🧪 Implementation Complete - Testing Required!

Detected {completed_impl} completed implementation tasks with {pending_tests} pending test tasks.

Please run: Use the qa agent to implement comprehensive tests for the completed features

The QA agent should:
1. Write unit tests for all new functions/methods
2. Add integration tests for feature workflows  
3. Ensure edge cases are covered
4. Validate error handling paths
5. Update test documentation

This ensures code quality before moving forward.
""",
            )

    # Scenario 4: Documentation lag
    if analysis["completed"] > 10 and analysis["has_documentation_todos"] and analysis["completion_rate"] > 60:
        return (
            True,
            f"""
📚 Documentation Update Required!

You've completed {analysis["completed"]} TODOs ({analysis["completion_rate"]}% done) but documentation tasks remain.

Please run: Use the architect agent to update project documentation

The architect should:
1. Update MEMORY.md with architectural decisions
2. Document new patterns or conventions introduced
3. Update component diagrams if structure changed
4. Add inline documentation for complex logic
5. Update README if user-facing changes were made

Good documentation ensures maintainability.
""",
        )

    # Scenario 5: Stalled progress - need planning
    if analysis["in_progress"] == 0 and analysis["pending"] > 5 and analysis["completion_rate"] < 30:
        return (
            True,
            f"""
📋 Planning Assistance Needed!

No TODOs currently in progress with {analysis["pending"]} tasks pending.

Please run: Use the planner agent to reorganize and prioritize remaining work

The planner should:
1. Review all pending TODOs
2. Identify dependencies and blockers
3. Re-prioritize based on milestone goals
4. Break down complex tasks into smaller steps
5. Create an execution plan for next phase

This will help restore momentum.
""",
        )

    # No blocking suggestion needed
    if analysis["completion_rate"] == 100:
        message = """
✅ All TODOs Complete! Great job!

Consider:
1. Creating a PR if milestone is complete
2. Planning the next milestone
3. Celebrating your progress! 🎉
"""
        return False, message

    # Provide non-blocking progress update
    message = f"""
📊 TODO Progress: {analysis["completed"]}/{analysis["total"]} ({analysis["completion_rate"]}%)
• In Progress: {analysis["in_progress"]}
• Pending: {analysis["pending"]} ({analysis["high_priority_pending"]} high priority)
"""

    if milestone.get("has_milestone"):
        message += f"\n📍 Milestone '{milestone['name']}': {milestone['progress']}% complete"

    return False, message


def main():
    """Main hook entry point."""
    # Parse input
    hook_data = parse_hook_input()
    project_root = get_project_root()

    # Check if this is a TodoWrite event
    if hook_data.get("tool_name") != "TodoWrite":
        sys.exit(0)

    # Get TODOs from tool input
    tool_input = hook_data.get("tool_input", {})
    todos = tool_input.get("todos", [])

    if not todos:
        sys.exit(0)

    # Analyze TODO patterns
    analysis = analyze_todo_patterns(todos)

    # Get recent completions for context
    recent_completions = [todo for todo in todos if todo.get("status") == "completed"][-5:]  # Last 5 completed

    # Get milestone progress
    milestone = get_milestone_progress(project_root)

    # Generate agent suggestion
    should_block, message = generate_agent_suggestion(analysis, milestone, recent_completions)

    if should_block:
        # Block and suggest agent
        print(message.strip(), file=sys.stderr)
        sys.exit(2)
    else:
        # Just provide informational output
        print(message.strip())
        sys.exit(0)


if __name__ == "__main__":
    main()
