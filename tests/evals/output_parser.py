"""Output parser for Claude CLI responses.

Extracts structured data from Claude's text output.
"""

import re
from pathlib import Path
from typing import Any

from .models import SpecificationOutput
from .utils import load_spec_as_eval_output


class OutputParser:
    """Parse Claude CLI output to extract structured information."""

    @staticmethod
    def extract_spec_id(text: str) -> str | None:
        """Extract specification ID from Claude output.

        Args:
            text: Claude CLI output text

        Returns:
            Spec ID (e.g., "spec-20250101-120000") or None
        """
        # Pattern: spec-YYYYMMDD-HHMMSS
        pattern = r"spec-\d{8}-\d{6}"
        matches = re.findall(pattern, text)

        if matches:
            # Return the last match (most recently mentioned)
            return matches[-1]

        return None

    @staticmethod
    def extract_spec_path(text: str, base_dir: Path | None = None) -> Path | None:
        """Extract specification file path from output.

        Args:
            text: Claude CLI output text
            base_dir: Base directory to resolve relative paths

        Returns:
            Path to specification file or None
        """
        # Look for .quaestor/specs/*/spec-*.md patterns
        pattern = r"\.quaestor/specs/(draft|active|completed|archived)/(spec-\d{8}-\d{6})\.md"
        match = re.search(pattern, text)

        if match:
            relative_path = match.group(0)
            if base_dir:
                return base_dir / relative_path
            return Path(relative_path)

        # Try to extract just the spec ID and construct path
        spec_id = OutputParser.extract_spec_id(text)
        if spec_id and base_dir:
            # Check common locations
            for status in ["draft", "active", "completed"]:
                spec_path = base_dir / ".quaestor/specs" / status / f"{spec_id}.md"
                if spec_path.exists():
                    return spec_path

        return None

    @staticmethod
    def parse_spec_from_output(
        text: str,
        project_dir: Path | None = None,
    ) -> SpecificationOutput | None:
        """Parse specification from Claude output and load as SpecificationOutput.

        Args:
            text: Claude CLI output text
            project_dir: Project directory to find spec files

        Returns:
            SpecificationOutput if spec found and parsed, None otherwise
        """
        # Extract spec ID
        spec_id = OutputParser.extract_spec_id(text)
        if not spec_id:
            return None

        # Find spec file
        if project_dir:
            for status in ["draft", "active", "completed", "archived"]:
                spec_path = project_dir / ".quaestor/specs" / status / f"{spec_id}.md"
                if spec_path.exists():
                    return load_spec_as_eval_output(spec_path)

        return None

    @staticmethod
    def extract_file_changes(text: str) -> list[str]:
        """Extract list of files that were changed from output.

        Args:
            text: Claude CLI output text

        Returns:
            List of file paths that were modified
        """
        files = []

        # Pattern 1: "Modified: path/to/file.py"
        pattern1 = r"Modified:\s+(.+\.(?:py|md|yaml|yml|json|txt))"
        files.extend(re.findall(pattern1, text))

        # Pattern 2: "Created: path/to/file.py"
        pattern2 = r"Created:\s+(.+\.(?:py|md|yaml|yml|json|txt))"
        files.extend(re.findall(pattern2, text))

        # Pattern 3: Git-style "+ path/to/file.py"
        pattern3 = r"^\+\s+(.+\.(?:py|md|yaml|yml|json|txt))"
        files.extend(re.findall(pattern3, text, re.MULTILINE))

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)

        return unique_files

    @staticmethod
    def extract_tests_passing(text: str) -> bool | None:
        """Determine if tests are passing from output.

        Args:
            text: Claude CLI output text

        Returns:
            True if tests passing, False if failing, None if unknown
        """
        # Look for pytest output
        if re.search(r"(\d+) passed", text):
            # Check for failures
            if re.search(r"(\d+) failed", text):
                return False
            return True

        # Look for explicit success/failure messages
        if re.search(r"(All tests? passed?|Tests? passing)", text, re.IGNORECASE):
            return True

        if re.search(r"(Tests? failed?|Tests? failing)", text, re.IGNORECASE):
            return False

        return None

    @staticmethod
    def extract_progress_percentage(text: str) -> float | None:
        """Extract progress percentage from output.

        Args:
            text: Claude CLI output text

        Returns:
            Progress percentage (0.0-100.0) or None
        """
        # Pattern: "Progress: 75%"
        pattern1 = r"Progress:\s+(\d+(?:\.\d+)?)%"
        match = re.search(pattern1, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Pattern: "75% complete"
        pattern2 = r"(\d+(?:\.\d+)?)%\s+complete"
        match = re.search(pattern2, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Pattern: "3/8 criteria met" -> 37.5%
        pattern3 = r"(\d+)/(\d+)\s+(?:criteria|tasks?|items?)"
        match = re.search(pattern3, text, re.IGNORECASE)
        if match:
            completed = int(match.group(1))
            total = int(match.group(2))
            if total > 0:
                return (completed / total) * 100.0

        return None

    @staticmethod
    def extract_metadata(text: str) -> dict[str, Any]:
        """Extract misc metadata from output.

        Args:
            text: Claude CLI output text

        Returns:
            Dictionary of extracted metadata
        """
        metadata: dict[str, Any] = {}

        # Extract duration if present
        duration_pattern = r"Duration:\s+(\d+(?:\.\d+)?)\s*(seconds?|s|minutes?|m)"
        match = re.search(duration_pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower()
            if "m" in unit:
                value *= 60  # Convert minutes to seconds
            metadata["duration_seconds"] = value

        # Extract error messages
        error_pattern = r"Error:\s+(.+)"
        errors = re.findall(error_pattern, text)
        if errors:
            metadata["errors"] = errors

        # Extract warnings
        warning_pattern = r"Warning:\s+(.+)"
        warnings = re.findall(warning_pattern, text)
        if warnings:
            metadata["warnings"] = warnings

        # Extract success indicators
        if re.search(r"✓|✅|Success|Complete", text):
            metadata["has_success_indicator"] = True

        return metadata
