#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Project type detection and analysis utilities.

Detects project language/framework and analyzes complexity indicators.
Self-contained with no external dependencies.

Usage:
    # As a standalone script
    uv run scripts/project-detector.py detect .
    uv run scripts/project-detector.py analyze .

    # As an imported module
    from scripts.project_detector import detect_project_type, analyze_project_complexity
"""

from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=128)
def detect_project_type(project_dir: Path) -> str:
    """Detect the primary language/framework of the project.

    Args:
        project_dir: Path to the project directory

    Returns:
        String indicating the project type (python, rust, javascript, typescript, go, etc.)
        Returns "unknown" if type cannot be determined.
    """
    # Convert to Path if string
    if isinstance(project_dir, str):
        project_dir = Path(project_dir)

    # Python projects
    if (project_dir / "pyproject.toml").exists() or (project_dir / "requirements.txt").exists():
        return "python"

    # Rust projects
    elif (project_dir / "Cargo.toml").exists():
        return "rust"

    # JavaScript/TypeScript projects
    elif (project_dir / "package.json").exists():
        # Check if TypeScript
        if (project_dir / "tsconfig.json").exists():
            return "typescript"
        return "javascript"

    # Go projects
    elif (project_dir / "go.mod").exists():
        return "go"

    # Java projects
    elif (project_dir / "pom.xml").exists() or (project_dir / "build.gradle").exists():
        return "java"

    # Ruby projects
    elif (project_dir / "Gemfile").exists():
        return "ruby"

    # C# projects
    elif any(project_dir.glob("*.csproj")):
        return "csharp"

    # PHP projects
    elif (project_dir / "composer.json").exists():
        return "php"

    # Swift projects
    elif (project_dir / "Package.swift").exists():
        return "swift"

    # Kotlin projects
    elif any(project_dir.glob("*.gradle.kts")) or (project_dir / "build.gradle.kts").exists():
        return "kotlin"

    else:
        return "unknown"


def get_project_files_by_type(project_dir: Path, project_type: str | None = None) -> dict[str, list[Path]]:
    """Get lists of files organized by type for the project.

    Args:
        project_dir: Path to the project directory
        project_type: Optional project type (auto-detected if not provided)

    Returns:
        Dictionary with file categories as keys and lists of paths as values
    """
    if project_type is None:
        project_type = detect_project_type(project_dir)

    # Define file patterns for each project type
    patterns = {
        "python": {
            "source": ["**/*.py"],
            "tests": ["**/test_*.py", "**/tests/**/*.py", "**/*_test.py"],
            "config": ["pyproject.toml", "setup.py", "requirements*.txt", "Pipfile", "poetry.lock"],
        },
        "javascript": {
            "source": ["**/*.js", "**/*.jsx"],
            "tests": ["**/*.test.js", "**/*.spec.js", "**/tests/**/*.js"],
            "config": ["package.json", "package-lock.json", "yarn.lock", ".eslintrc*", "babel.config.*"],
        },
        "typescript": {
            "source": ["**/*.ts", "**/*.tsx"],
            "tests": ["**/*.test.ts", "**/*.spec.ts", "**/tests/**/*.ts"],
            "config": ["package.json", "tsconfig.json", "package-lock.json", "yarn.lock", ".eslintrc*"],
        },
        "rust": {
            "source": ["**/*.rs"],
            "tests": ["**/tests/**/*.rs"],
            "config": ["Cargo.toml", "Cargo.lock"],
        },
        "go": {
            "source": ["**/*.go"],
            "tests": ["**/*_test.go"],
            "config": ["go.mod", "go.sum"],
        },
        "java": {
            "source": ["**/*.java"],
            "tests": ["**/src/test/**/*.java"],
            "config": ["pom.xml", "build.gradle", "build.gradle.kts"],
        },
    }

    result = {"source": [], "tests": [], "config": [], "other": []}

    if project_type in patterns:
        for category, file_patterns in patterns[project_type].items():
            for pattern in file_patterns:
                result[category].extend(project_dir.glob(pattern))

    # Find other files (non-hidden, non-binary)
    common_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java", ".rb", ".php", ".swift", ".kt"}
    for file_path in project_dir.rglob("*"):
        if (
            file_path.is_file()
            and not file_path.name.startswith(".")
            and file_path.suffix.lower() in common_extensions
            and file_path not in result["source"]
            and file_path not in result["tests"]
            and file_path not in result["config"]
        ):
            result["other"].append(file_path)

    return result


def is_test_file(file_path: Path, project_type: str | None = None) -> bool:
    """Check if a file is a test file based on naming conventions.

    Args:
        file_path: Path to the file
        project_type: Optional project type (auto-detected if not provided)

    Returns:
        True if the file appears to be a test file
    """
    if project_type is None:
        project_type = detect_project_type(file_path.parent)

    file_name = file_path.name.lower()

    # Common test patterns across languages
    test_patterns = [
        "test_",  # Python convention
        "_test.",  # Go/Python convention
        ".test.",  # JavaScript/TypeScript convention
        ".spec.",  # JavaScript/TypeScript spec files
        "tests/",  # In tests directory
    ]

    return any(pattern in file_name or pattern in str(file_path).lower() for pattern in test_patterns)


def get_project_complexity_indicators(project_dir: Path, project_type: str | None = None) -> dict[str, Any]:
    """Analyze project complexity indicators.

    Args:
        project_dir: Path to the project directory
        project_type: Optional project type (auto-detected if not provided)

    Returns:
        Dictionary with complexity metrics
    """
    if project_type is None:
        project_type = detect_project_type(project_dir)

    files = get_project_files_by_type(project_dir, project_type)

    total_files = len(files["source"]) + len(files["tests"]) + len(files["other"])

    # Calculate directory depth
    max_depth = 0
    for file_path in project_dir.rglob("*"):
        if file_path.is_file():
            depth = len(file_path.relative_to(project_dir).parts)
            max_depth = max(max_depth, depth)

    # Check for various complexity indicators
    has_ci = any(
        [
            (project_dir / ".github" / "workflows").exists(),
            (project_dir / ".gitlab-ci.yml").exists(),
            (project_dir / "Jenkinsfile").exists(),
            (project_dir / ".travis.yml").exists(),
        ]
    )

    has_docker = (project_dir / "Dockerfile").exists() or (project_dir / "docker-compose.yml").exists()

    has_docs = any(
        [
            (project_dir / "docs").exists(),
            (project_dir / "README.md").exists(),
            (project_dir / "README.rst").exists(),
        ]
    )

    # Team collaboration indicators
    has_team_markers = any(
        [
            (project_dir / ".gitignore").exists(),
            (project_dir / "CONTRIBUTING.md").exists(),
            (project_dir / "CODE_OF_CONDUCT.md").exists(),
            (project_dir / ".pre-commit-config.yaml").exists(),
        ]
    )

    return {
        "project_type": project_type,
        "total_files": total_files,
        "source_files": len(files["source"]),
        "test_files": len(files["tests"]),
        "config_files": len(files["config"]),
        "max_directory_depth": max_depth,
        "has_ci": has_ci,
        "has_docker": has_docker,
        "has_documentation": has_docs,
        "has_team_markers": has_team_markers,
        "test_coverage_ratio": len(files["tests"]) / max(len(files["source"]), 1),
    }


def analyze_project_complexity(project_dir: Path) -> dict[str, Any]:
    """Complete project analysis including type detection and complexity scoring.

    Args:
        project_dir: Path to the project directory

    Returns:
        Dictionary with complete analysis results
    """
    project_type = detect_project_type(project_dir)
    indicators = get_project_complexity_indicators(project_dir, project_type)

    # Calculate complexity score from 0 to 1
    score = 0.0

    # File count contribution (0-0.3)
    file_count = indicators["total_files"]
    if file_count > 100:
        score += 0.3
    elif file_count > 50:
        score += 0.2
    elif file_count > 20:
        score += 0.1

    # Directory depth contribution (0-0.2)
    depth = indicators["max_directory_depth"]
    if depth > 5:
        score += 0.2
    elif depth > 3:
        score += 0.1

    # Has tests (0.1)
    if indicators["test_files"] > 0:
        score += 0.1

    # Has CI (0.1)
    if indicators["has_ci"]:
        score += 0.1

    # Team markers (0.2)
    if indicators["has_team_markers"]:
        score += 0.2

    # Has documentation (0.1)
    if indicators["has_documentation"]:
        score += 0.1

    indicators["complexity_score"] = min(score, 1.0)

    return indicators


def main():
    """CLI interface for project-detector."""
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/project-detector.py <command> [path]")
        print()
        print("Commands:")
        print("  detect [path]   - Detect project type (default: current directory)")
        print("  analyze [path]  - Full project analysis (default: current directory)")
        print("  files [path]    - List files by category")
        sys.exit(1)

    command = sys.argv[1]
    project_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()

    if command == "detect":
        project_type = detect_project_type(project_path)
        print(f"Project type: {project_type}")

    elif command == "analyze":
        analysis = analyze_project_complexity(project_path)
        print(json.dumps(analysis, indent=2, default=str))

    elif command == "files":
        project_type = detect_project_type(project_path)
        files = get_project_files_by_type(project_path, project_type)
        print(f"Project type: {project_type}")
        print(f"\nSource files: {len(files['source'])}")
        print(f"Test files: {len(files['tests'])}")
        print(f"Config files: {len(files['config'])}")
        print(f"Other files: {len(files['other'])}")

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
