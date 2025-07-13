"""Project analyzer for determining complexity and characteristics."""

import os
from pathlib import Path
from typing import Any


class ProjectAnalyzer:
    """Analyze project characteristics to determine appropriate rules."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def analyze(self) -> dict[str, Any]:
        """Analyze project and return characteristics."""
        return {
            "project_type": self._detect_project_type(),
            "file_count": self._count_files(),
            "directory_depth": self._get_directory_depth(),
            "has_tests": self._has_tests(),
            "has_ci": self._has_ci(),
            "team_markers": self._check_team_markers(),
            "complexity_score": self._calculate_complexity_score(),
            "has_documentation": self._has_documentation(),
        }

    def _detect_project_type(self) -> str:
        """Detect the primary language/framework of the project."""
        # Check for language-specific files
        if (self.project_dir / "pyproject.toml").exists() or (self.project_dir / "requirements.txt").exists():
            return "python"
        elif (self.project_dir / "Cargo.toml").exists():
            return "rust"
        elif (self.project_dir / "package.json").exists():
            # Check if TypeScript
            if (self.project_dir / "tsconfig.json").exists():
                return "typescript"
            return "javascript"
        elif (self.project_dir / "go.mod").exists():
            return "go"
        elif (self.project_dir / "pom.xml").exists() or (self.project_dir / "build.gradle").exists():
            return "java"
        elif (self.project_dir / "Gemfile").exists():
            return "ruby"
        elif any(self.project_dir.glob("*.csproj")):
            return "csharp"
        else:
            return "unknown"

    def _count_files(self) -> int:
        """Count total number of code files."""
        extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".rs",
            ".go",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".php",
            ".dart",
        }

        count = 0
        for root, _, files in os.walk(self.project_dir):
            # Skip hidden directories and common non-code directories
            if any(part.startswith(".") for part in Path(root).parts):
                continue
            if any(skip in root for skip in ["node_modules", "venv", "env", "target", "build", "dist"]):
                continue

            for file in files:
                if Path(file).suffix in extensions:
                    count += 1

        return count

    def _get_directory_depth(self) -> int:
        """Get maximum directory depth."""
        max_depth = 0

        for root, dirs, _ in os.walk(self.project_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            depth = len(Path(root).relative_to(self.project_dir).parts)
            max_depth = max(max_depth, depth)

        return max_depth

    def _has_tests(self) -> bool:
        """Check if project has a test directory or test files."""
        # Common test directories
        test_dirs = ["tests", "test", "__tests__", "spec"]
        for test_dir in test_dirs:
            if (self.project_dir / test_dir).exists():
                return True

        # Check for test files
        test_patterns = ["*test*.py", "*test*.js", "*test*.ts", "*_test.go", "*Test.java", "*spec*.rb"]
        return any(list(self.project_dir.rglob(pattern)) for pattern in test_patterns)

    def _has_ci(self) -> bool:
        """Check if project has CI/CD configuration."""
        ci_files = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
            "Jenkinsfile",
            ".travis.yml",
            "azure-pipelines.yml",
            ".drone.yml",
        ]

        return any((self.project_dir / ci_file).exists() for ci_file in ci_files)

    def _check_team_markers(self) -> bool:
        """Check for indicators of a team project."""
        team_indicators = [
            ".github/CODEOWNERS",
            ".github/pull_request_template.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            ".github/ISSUE_TEMPLATE",
        ]

        for indicator in team_indicators:
            if (self.project_dir / indicator).exists():
                return True

        # Check if git exists and has multiple contributors
        git_dir = self.project_dir / ".git"
        if git_dir.exists():
            # This is a simple heuristic - could be enhanced
            config_file = git_dir / "config"
            if config_file.exists():
                content = config_file.read_text()
                # Look for remote origin (indicates shared repo)
                if '[remote "origin"]' in content:
                    return True

        return False

    def _has_documentation(self) -> bool:
        """Check if project has documentation."""
        doc_indicators = [
            "docs",
            "documentation",
            "README.md",
            "README.rst",
            "ARCHITECTURE.md",
            "API.md",
        ]

        for doc in doc_indicators:
            path = self.project_dir / doc
            if path.exists():
                # For directories, check if they have content
                if path.is_dir():
                    if any(path.iterdir()):
                        return True
                else:
                    # For files, check if they have substantial content
                    if path.stat().st_size > 100:  # More than 100 bytes
                        return True

        return False

    def _calculate_complexity_score(self) -> float:
        """Calculate a complexity score from 0 to 1."""
        score = 0.0

        # File count contribution (0-0.3)
        file_count = self._count_files()
        if file_count > 100:
            score += 0.3
        elif file_count > 50:
            score += 0.2
        elif file_count > 20:
            score += 0.1

        # Directory depth contribution (0-0.2)
        depth = self._get_directory_depth()
        if depth > 5:
            score += 0.2
        elif depth > 3:
            score += 0.1

        # Has tests (0.1)
        if self._has_tests():
            score += 0.1

        # Has CI (0.1)
        if self._has_ci():
            score += 0.1

        # Team markers (0.2)
        if self._check_team_markers():
            score += 0.2

        # Has documentation (0.1)
        if self._has_documentation():
            score += 0.1

        return min(score, 1.0)
