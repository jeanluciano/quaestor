#!/usr/bin/env python3
"""Review completion archiving hook.

This hook monitors /review command completion and automatically archives
specifications when work is completed and shipped.
"""

import re
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.core.memory_manager import MemoryManager
from quaestor.core.specifications import SpecificationManager, SpecStatus


class ReviewArchiverHook(BaseHook):
    """Hook for archiving specifications on review completion."""

    def __init__(self):
        super().__init__("review_archiver")
        self.project_root = get_project_root()
        self.spec_manager = SpecificationManager(self.project_root)
        # Use the folder manager from spec manager
        self.memory_manager = MemoryManager(self.project_root, self.spec_manager.folder_manager)

    def execute(self):
        """Execute review archiving logic."""
        # Only run for review command
        if not self._is_review_command():
            self.output_success()
            return

        # Check if PR was created (indicates completion)
        if not self._check_pr_created():
            self.output_success()
            return

        # Get active specifications
        active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)
        if not active_specs:
            self.output_success()
            return

        # Detect which specifications were completed
        completed_specs = self._detect_completed_specs(active_specs)

        if completed_specs:
            # Archive completed specifications
            archived_count = 0
            for spec in completed_specs:
                if self.spec_manager.complete_specification(spec.id):
                    archived_count += 1

                    # Create spec data for memory archiving
                    spec_data = {
                        "title": spec.title,
                        "start_date": spec.created_at.strftime("%Y-%m-%d"),
                        "acceptance_criteria": spec.acceptance_criteria,
                        "learnings": self._extract_learnings(spec),
                        "scope": spec.type.value,
                        "complexity": spec.metadata.get("complexity", "medium"),
                    }

                    # Archive in memory
                    self.memory_manager.archive_completed_specification(spec.id, spec_data)

            # Don't call update_memory_file() as it overwrites the archive

            # Provide feedback based on context
            if self.has_active_work():
                self._generate_detailed_feedback(archived_count, completed_specs)
            else:
                self._generate_minimal_feedback(archived_count)
        else:
            self.output_success()

    def _is_review_command(self) -> bool:
        """Check if this is a review command execution."""
        # Check command history or input data
        command = self.input_data.get("command", "")
        return command.startswith("/review") or "review" in command.lower()

    def _check_pr_created(self) -> bool:
        """Check if a PR was created in the review process."""
        # Look for PR creation indicators in recent tool calls
        tool_name = self.input_data.get("tool_name", "")
        if tool_name == "Bash":
            tool_input = self.input_data.get("tool_input", {})
            command = tool_input.get("command", "")

            # Check for gh pr create command
            if "gh pr create" in command:
                return True

        # Check for PR URL in output
        output = self.input_data.get("output", "")
        if isinstance(output, str) and ("github.com" in output and "/pull/" in output):
            return True

        return False

    def _detect_completed_specs(self, active_specs: list) -> list:
        """Detect which specifications were completed based on review output."""
        completed = []

        # Check review output for completion indicators
        output = self.input_data.get("output", "")
        if not isinstance(output, str):
            return completed

        # Look for specification IDs mentioned in completion context
        for spec in active_specs:
            # Check if spec is mentioned in completed context
            if self._is_spec_completed(spec, output):
                completed.append(spec)

        return completed

    def _is_spec_completed(self, spec: Any, output: str) -> bool:
        """Check if a specification appears to be completed."""
        # Look for completion indicators
        completion_patterns = [
            rf"{spec.id}.*complet",
            rf"{spec.id}.*done",
            rf"{spec.id}.*finish",
            rf"complet.*{spec.id}",
            rf"finish.*{spec.id}",
            rf"{spec.title}.*complet",
        ]

        for pattern in completion_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True

        # Check if all acceptance criteria are mentioned as complete
        if spec.acceptance_criteria:
            criteria_mentions = sum(1 for criterion in spec.acceptance_criteria if criterion.lower() in output.lower())
            if criteria_mentions >= len(spec.acceptance_criteria) * 0.8:  # 80% threshold
                return True

        return False

    def _extract_learnings(self, spec: Any) -> list[str]:
        """Extract learnings from specification metadata and review output."""
        learnings = []

        # Check spec metadata for learnings
        if spec.metadata.get("learnings"):
            learnings.extend(spec.metadata["learnings"])

        # Extract from review output
        output = self.input_data.get("output", "")
        if isinstance(output, str):
            # Look for learning patterns
            learning_patterns = [
                r"learn(?:ed|ing|t):\s*(.+?)(?:\n|$)",
                r"discover(?:ed|y):\s*(.+?)(?:\n|$)",
                r"found that:\s*(.+?)(?:\n|$)",
                r"insight:\s*(.+?)(?:\n|$)",
            ]

            for pattern in learning_patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                learnings.extend(matches)

        # Default learnings based on spec type
        if not learnings:
            if spec.type.value == "feature":
                learnings.append("Feature implementation completed successfully")
            elif spec.type.value == "bugfix":
                learnings.append("Bug resolved and regression tests added")
            elif spec.type.value == "refactor":
                learnings.append("Code structure improved without breaking changes")

        return learnings[:3]  # Limit to 3

    def _generate_detailed_feedback(self, archived_count: int, completed_specs: list):
        """Generate detailed feedback for archiving."""
        if archived_count > 0:
            spec_list = "\n".join([f"  - {spec.id}: {spec.title}" for spec in completed_specs])

            message = f"""✅ SPECIFICATIONS ARCHIVED

Successfully archived {archived_count} completed specification(s):
{spec_list}

The following actions were taken:
1. Moved specifications to completed/ folder
2. Updated MEMORY.md with completion information
3. Preserved git history through proper moves

Next steps:
- Create new specifications for upcoming work
- Review completed specifications for learnings
- Update project documentation if needed
"""
            self.output_success(message)
        else:
            self.output_error("Failed to archive completed specifications", blocking=False)

    def _generate_minimal_feedback(self, archived_count: int):
        """Generate minimal feedback."""
        if archived_count > 0:
            self.output_success(f"📁 Archived {archived_count} completed specification(s)")
        else:
            # Silent in drive mode for no action
            self.output_success()


def main():
    """Main hook entry point."""
    hook = ReviewArchiverHook()
    hook.run()


if __name__ == "__main__":
    main()
