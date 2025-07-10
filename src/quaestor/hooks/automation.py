"""Automation hooks for repetitive tasks.

These hooks handle automatic commits, memory updates, and quality checks.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from . import HookResult, detect_project_type, get_project_root


def run_automation_hook(hook_name: str, context: dict[str, Any]) -> HookResult:
    """Run an automation hook."""
    if hook_name == "auto_update_memory":
        return update_memory_from_todos(context.get("milestone"))
    elif hook_name == "auto_quality_check":
        return run_quality_checks(context.get("fix", False))
    elif hook_name == "auto_milestone_check":
        return check_milestone_completion(context.get("milestone"), context.get("auto_pr", False))
    elif hook_name == "auto_commit":
        return create_atomic_commit(context.get("message"), context.get("files"))
    else:
        return HookResult(False, f"Unknown automation hook: {hook_name}")


def update_memory_from_todos(milestone: str | None = None) -> HookResult:
    """Update MEMORY.md based on completed TODOs."""
    root = get_project_root()
    memory_path = root / ".quaestor" / "MEMORY.md"

    if not memory_path.exists():
        return HookResult(False, "MEMORY.md not found")

    try:
        # Read current memory
        with open(memory_path) as f:
            memory_content = f.read()

        # Extract TODO sections
        todos_completed = extract_completed_todos(memory_content)
        if not todos_completed:
            return HookResult(True, "No completed TODOs found to update")

        # Update progress section
        updated_content = update_progress_section(memory_content, todos_completed)

        # Update milestone status if specified
        if milestone:
            updated_content = update_milestone_status(updated_content, milestone, todos_completed)

        # Write back
        with open(memory_path, "w") as f:
            f.write(updated_content)

        return HookResult(
            True,
            f"✅ Updated MEMORY.md with {len(todos_completed)} completed items",
            {"completed_todos": todos_completed},
        )

    except Exception as e:
        return HookResult(False, f"Failed to update MEMORY.md: {e}")


def extract_completed_todos(content: str) -> list[dict[str, str]]:
    """Extract completed TODOs from memory content."""
    completed = []

    # Look for checked items (✅ or [x])
    patterns = [
        r"✅\s+(.+?)(?:\n|$)",
        r"\[x\]\s+(.+?)(?:\n|$)",
        r"- \[x\]\s+(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            completed.append({"task": match.strip(), "status": "completed"})

    return completed


def update_progress_section(content: str, completed_todos: list[dict[str, str]]) -> str:
    """Update the progress tracking section."""
    # Find progress section
    progress_pattern = r"(<!-- SECTION:memory:status:START -->.*?<!-- SECTION:memory:status:END -->)"
    match = re.search(progress_pattern, content, re.DOTALL)

    if not match:
        # Add progress section if not found
        progress_section = generate_progress_section(completed_todos)
        return content + "\n\n" + progress_section

    # Update existing section
    old_section = match.group(1)
    new_section = update_progress_data(old_section, completed_todos)
    return content.replace(old_section, new_section)


def generate_progress_section(completed_todos: list[dict[str, str]]) -> str:
    """Generate a new progress section."""
    return f"""<!-- SECTION:memory:status:START -->
## Current Status

<!-- DATA:project-status:START -->
```yaml
last_updated: "{datetime.now().strftime("%Y-%m-%d")}"
completed_today: {len(completed_todos)}
recent_completions:
{chr(10).join(f'  - "{todo["task"]}"' for todo in completed_todos[:5])}
```
<!-- DATA:project-status:END -->
<!-- SECTION:memory:status:END -->"""


def update_progress_data(section: str, completed_todos: list[dict[str, str]]) -> str:
    """Update progress data in existing section."""
    # Update last_updated
    section = re.sub(
        r'last_updated:\s*"[^"]*"',
        f'last_updated: "{datetime.now().strftime("%Y-%m-%d")}"',
        section,
    )

    # Update completed count
    count_match = re.search(r"completed_today:\s*(\d+)", section)
    if count_match:
        old_count = int(count_match.group(1))
        new_count = old_count + len(completed_todos)
        section = re.sub(r"completed_today:\s*\d+", f"completed_today: {new_count}", section)

    return section


def update_milestone_status(content: str, milestone: str, completed_todos: list[dict[str, str]]) -> str:
    """Update specific milestone status."""
    # Find milestone section
    milestone_pattern = rf"(###\s*{re.escape(milestone)}.*?)(?=###|\Z)"
    match = re.search(milestone_pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        milestone_section = match.group(1)

        # Count total and completed items
        total_items = len(re.findall(r"[-*]\s*\[.\]", milestone_section))
        completed_items = len(re.findall(r"[-*]\s*\[x\]|✅", milestone_section))

        # Calculate percentage
        progress = int((completed_items / total_items * 100) if total_items > 0 else 0)

        # Update progress indicator
        milestone_section = re.sub(
            r"\((?:CURRENT|IN PROGRESS|COMPLETE).*?\)",
            f"({progress}% complete)",
            milestone_section,
        )

        # Mark as complete if 100%
        if progress == 100:
            milestone_section = re.sub(
                rf"(###\s*{re.escape(milestone)})",
                r"\1 ✅",
                milestone_section,
            )

        content = content.replace(match.group(1), milestone_section)

    return content


def run_quality_checks(fix: bool = False) -> HookResult:
    """Run project-appropriate quality checks."""
    root = get_project_root()
    project_type = detect_project_type(root)

    results = []
    all_passed = True

    # Python project checks
    if project_type == "python":
        # Run ruff
        ruff_result = run_python_checks(root, fix)
        results.append(ruff_result)
        all_passed &= ruff_result["success"]

        # Run tests
        test_result = run_python_tests(root)
        results.append(test_result)
        all_passed &= test_result["success"]

    # Rust project checks
    elif project_type == "rust":
        # Run clippy
        clippy_result = run_rust_checks(root, fix)
        results.append(clippy_result)
        all_passed &= clippy_result["success"]

        # Run tests
        test_result = run_rust_tests(root)
        results.append(test_result)
        all_passed &= test_result["success"]

    # JavaScript/TypeScript checks
    elif project_type == "javascript":
        # Run eslint
        lint_result = run_js_checks(root, fix)
        results.append(lint_result)
        all_passed &= lint_result["success"]

        # Run tests
        test_result = run_js_tests(root)
        results.append(test_result)
        all_passed &= test_result["success"]

    else:
        return HookResult(True, f"No quality checks configured for {project_type} projects")

    # Format results
    summary = "\n".join([f"{'✅' if r['success'] else '❌'} {r['name']}: {r['message']}" for r in results])

    return HookResult(
        all_passed,
        f"Quality Check Results:\n{summary}",
        {"results": results},
    )


def run_python_checks(root: Path, fix: bool) -> dict[str, Any]:
    """Run Python quality checks."""
    try:
        cmd = ["ruff", "check", str(root / "src"), str(root / "tests")]
        if fix:
            cmd.append("--fix")

        result = subprocess.run(cmd, capture_output=True, text=True)
        success = result.returncode == 0

        return {
            "name": "Ruff (linting)",
            "success": success,
            "message": "All checks passed" if success else f"Found issues:\n{result.stdout}",
        }
    except FileNotFoundError:
        return {
            "name": "Ruff (linting)",
            "success": False,
            "message": "Ruff not found. Install with: pip install ruff",
        }


def run_python_tests(root: Path) -> dict[str, Any]:
    """Run Python tests."""
    try:
        result = subprocess.run(["pytest", str(root / "tests"), "-v"], capture_output=True, text=True)
        success = result.returncode == 0

        # Extract test summary
        summary_match = re.search(r"(\d+) passed", result.stdout)
        summary = summary_match.group(0) if summary_match else "See output"

        return {
            "name": "Pytest",
            "success": success,
            "message": summary if success else f"Tests failed:\n{result.stdout}",
        }
    except FileNotFoundError:
        return {
            "name": "Pytest",
            "success": False,
            "message": "Pytest not found. Install with: pip install pytest",
        }


def run_rust_checks(root: Path, fix: bool) -> dict[str, Any]:
    """Run Rust quality checks."""
    try:
        cmd = ["cargo", "clippy"]
        if fix:
            cmd.extend(["--fix", "--allow-dirty"])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
        success = result.returncode == 0

        return {
            "name": "Clippy",
            "success": success,
            "message": "All checks passed" if success else "Found warnings/errors",
        }
    except FileNotFoundError:
        return {
            "name": "Clippy",
            "success": False,
            "message": "Cargo not found. Install Rust toolchain.",
        }


def run_rust_tests(root: Path) -> dict[str, Any]:
    """Run Rust tests."""
    try:
        result = subprocess.run(["cargo", "test"], capture_output=True, text=True, cwd=root)
        success = result.returncode == 0

        # Extract test summary
        summary_match = re.search(r"test result:.*?(\d+) passed", result.stdout)
        summary = summary_match.group(0) if summary_match else "See output"

        return {
            "name": "Cargo Test",
            "success": success,
            "message": summary if success else "Tests failed",
        }
    except FileNotFoundError:
        return {
            "name": "Cargo Test",
            "success": False,
            "message": "Cargo not found",
        }


def run_js_checks(root: Path, fix: bool) -> dict[str, Any]:
    """Run JavaScript/TypeScript checks."""
    try:
        cmd = ["npm", "run", "lint"]
        if fix:
            cmd.append("--", "--fix")

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
        success = result.returncode == 0

        return {
            "name": "ESLint",
            "success": success,
            "message": "All checks passed" if success else "Found issues",
        }
    except FileNotFoundError:
        return {
            "name": "ESLint",
            "success": False,
            "message": "npm not found",
        }


def run_js_tests(root: Path) -> dict[str, Any]:
    """Run JavaScript tests."""
    try:
        result = subprocess.run(["npm", "test"], capture_output=True, text=True, cwd=root)
        success = result.returncode == 0

        return {
            "name": "npm test",
            "success": success,
            "message": "All tests passed" if success else "Tests failed",
        }
    except FileNotFoundError:
        return {
            "name": "npm test",
            "success": False,
            "message": "npm not found",
        }


def check_milestone_completion(milestone: str | None, auto_pr: bool = False) -> HookResult:
    """Check if a milestone is complete and optionally create a PR."""
    root = get_project_root()
    memory_path = root / ".quaestor" / "MEMORY.md"

    if not memory_path.exists():
        return HookResult(False, "MEMORY.md not found")

    try:
        with open(memory_path) as f:
            content = f.read()

        # Find milestone section
        pattern = rf"###\s*{re.escape(milestone)}.*?(?=###|\Z)" if milestone else r"###.*?\(CURRENT\).*?(?=###|\Z)"

        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return HookResult(False, f"Milestone '{milestone or 'CURRENT'}' not found")

        milestone_section = match.group(0)
        milestone_name = re.search(r"###\s*(.+?)(?:\s*\(|$)", milestone_section).group(1).strip()

        # Count items
        total_items = len(re.findall(r"[-*]\s*\[.\]", milestone_section))
        completed_items = len(re.findall(r"[-*]\s*\[x\]|✅", milestone_section))

        if total_items == 0:
            return HookResult(False, f"No items found in milestone '{milestone_name}'")

        progress = int(completed_items / total_items * 100)
        is_complete = progress == 100

        result_message = f"Milestone '{milestone_name}': {completed_items}/{total_items} items ({progress}%)"

        if is_complete:
            result_message += " ✅ COMPLETE!"

            if auto_pr:
                # Create PR
                pr_result = create_milestone_pr(milestone_name, milestone_section)
                if pr_result["success"]:
                    result_message += f"\n🚀 Created PR: {pr_result['pr_url']}"
                else:
                    result_message += f"\n❌ Failed to create PR: {pr_result['error']}"

        return HookResult(
            True,
            result_message,
            {
                "milestone": milestone_name,
                "progress": progress,
                "complete": is_complete,
                "items": {"total": total_items, "completed": completed_items},
            },
        )

    except Exception as e:
        return HookResult(False, f"Failed to check milestone: {e}")


def create_milestone_pr(milestone_name: str, milestone_content: str) -> dict[str, Any]:
    """Create a pull request for completed milestone."""
    try:
        # Extract completed items for PR description
        completed_items = re.findall(r"[-*]\s*\[x\]\s*(.+?)(?:\n|$)", milestone_content)

        # Create PR body
        pr_body = f"""## 🎯 Milestone Complete: {milestone_name}

### ✅ Completed Items
{chr(10).join(f"- {item.strip()}" for item in completed_items)}

### 📊 Summary
- Total items: {len(completed_items)}
- All tasks completed successfully
- Quality checks passed

---
*This PR was automatically generated by Quaestor hooks upon milestone completion.*
"""

        # Create PR using gh CLI
        cmd = [
            "gh",
            "pr",
            "create",
            "--title",
            f"feat: Complete milestone - {milestone_name}",
            "--body",
            pr_body,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Extract PR URL from output
            pr_url = result.stdout.strip()
            return {"success": True, "pr_url": pr_url}
        else:
            return {"success": False, "error": result.stderr}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_atomic_commit(message: str | None, files: list[str] | None = None) -> HookResult:
    """Create an atomic commit with proper message."""
    try:
        # Stage files
        cmd = ["git", "add"] + files if files else ["git", "add", "-A"]

        subprocess.run(cmd, check=True)

        # Generate commit message if not provided
        if not message:
            # Get staged changes
            diff_result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
            changed_files = diff_result.stdout.strip().split("\n")

            # Determine commit type
            if any("test" in f for f in changed_files):
                commit_type = "test"
            elif any("fix" in f for f in changed_files):
                commit_type = "fix"
            elif any("docs" in f for f in changed_files):
                commit_type = "docs"
            else:
                commit_type = "feat"

            message = f"{commit_type}: Update {len(changed_files)} files"

        # Create commit
        subprocess.run(["git", "commit", "-m", message], check=True)

        return HookResult(True, f"✅ Created commit: {message}")

    except subprocess.CalledProcessError as e:
        return HookResult(False, f"Failed to create commit: {e}")
    except Exception as e:
        return HookResult(False, f"Unexpected error: {e}")
