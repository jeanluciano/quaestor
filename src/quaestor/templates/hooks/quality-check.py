#!/usr/bin/env python3
"""Run quality checks based on project type."""

import subprocess
import sys
from pathlib import Path


def detect_project_type():
    """Detect project type from files."""
    if Path("pyproject.toml").exists() or Path("requirements.txt").exists():
        return "python"
    elif Path("Cargo.toml").exists():
        return "rust"
    elif Path("package.json").exists():
        return "javascript"
    return "unknown"


def run_quality_checks():
    """Run appropriate quality checks for project type."""
    project_type = detect_project_type()

    if project_type == "python":
        checks = [("ruff", ["ruff", "check", "."]), ("ruff format", ["ruff", "format", "--check", "."])]
    elif project_type == "rust":
        checks = [("clippy", ["cargo", "clippy", "--", "-D", "warnings"]), ("fmt", ["cargo", "fmt", "--check"])]
    elif project_type == "javascript":
        checks = [("eslint", ["npx", "eslint", "."]), ("prettier", ["npx", "prettier", "--check", "."])]
    else:
        print(f"ℹ️  No quality checks configured for {project_type} project")
        return True

    all_passed = True
    for name, cmd in checks:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name} passed")
            else:
                print(f"❌ {name} failed")
                all_passed = False
        except FileNotFoundError:
            print(f"⚠️  {name} not found - skipping")

    return all_passed


if __name__ == "__main__":
    block_on_fail = "--block-on-fail" in sys.argv
    success = run_quality_checks()

    if not success and block_on_fail:
        print("\n❌ Quality checks failed - blocking commit")
        sys.exit(1)
    sys.exit(0)
