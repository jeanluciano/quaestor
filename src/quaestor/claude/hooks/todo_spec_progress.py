#!/usr/bin/env python3
"""Hook that automatically updates specification progress when TODOs are completed.

This hook monitors TODO completions and updates the corresponding specification
YAML files, marking acceptance criteria as completed when all related TODOs
are done.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root
from quaestor.core.specifications import SpecificationManager, SpecStatus


class TodoSpecProgressHook(BaseHook):
    """Update specification progress when TODOs are completed."""

    def __init__(self):
        super().__init__("todo_spec_progress")
        self.project_root = get_project_root()
        self.spec_manager = SpecificationManager(self.project_root)

    def execute(self):
        """Track progress after TodoWrite operations."""
        event_name = self.input_data.get("hook_event_name", "")
        if event_name != "PostToolUse":
            self.output_success("Not a PostToolUse event")
            return

        tool_name = self.input_data.get("tool_name", "")
        if tool_name != "TodoWrite":
            self.output_success("Not a TodoWrite operation")
            return

        # Get the updated TODO list
        tool_input = self.input_data.get("tool_input", {})
        todos = tool_input.get("todos", [])

        if not todos:
            self.output_success("No TODOs to process")
            return

        # Get active specifications
        active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)
        if not active_specs:
            self.output_success("No active specifications")
            return

        # Track which specs were updated
        updated_specs = []

        # Check for completed TODOs that relate to specifications
        for spec in active_specs:
            spec_updated = self._check_spec_progress(spec, todos)
            if spec_updated:
                updated_specs.append(spec.id)

        # Provide feedback about updates
        if updated_specs:
            message = f"Updated specifications: {', '.join(updated_specs)}"
            self.output_success(message)
        else:
            self.output_success("No specification updates needed")

    def _check_spec_progress(self, spec: Any, todos: list[dict[str, Any]]) -> bool:
        """Check if any completed TODOs satisfy spec criteria."""
        # Find TODOs that might relate to this spec
        spec_todos = self._find_spec_related_todos(spec, todos)

        if not spec_todos:
            return False

        # Check if any criteria can be marked as completed
        updated = False
        spec_data = self._load_spec_yaml(spec.id)

        if not spec_data:
            return False

        # Check each acceptance criterion
        criteria = spec_data.get("acceptance_criteria", [])
        for i, criterion in enumerate(criteria):
            # Skip if already completed
            if "✓" in criterion:
                continue

            # Check if this criterion is satisfied by completed TODOs
            if self._is_criterion_satisfied(criterion, spec_todos):
                # Update the criterion
                criteria[i] = f"✓ {criterion.replace('[ ]', '').strip()}"
                updated = True
                self.logger.info(f"Marked criterion as completed: {criterion}")

        if updated:
            # Update progress and save
            spec_data["acceptance_criteria"] = criteria
            spec_data["progress"] = self._calculate_progress(spec_data)
            spec_data["updated_at"] = datetime.now().isoformat()

            # Add implementation note
            notes = spec_data.get("implementation_notes", "")
            new_note = f"\n- {datetime.now().strftime('%Y-%m-%d')}: Updated progress via TODO completion"
            spec_data["implementation_notes"] = (notes + new_note).strip()

            self._save_spec_yaml(spec.id, spec_data)

        return updated

    def _find_spec_related_todos(self, spec: Any, todos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Find TODOs that relate to the given specification."""
        spec_todos = []

        # Look for TODOs that mention the spec ID or criteria
        for todo in todos:
            content = todo.get("content", "").lower()
            status = todo.get("status", "")

            # Only consider completed TODOs
            if status != "completed":
                continue

            # Check if TODO mentions spec ID
            if spec.id.lower() in content:
                spec_todos.append(todo)
                continue

            # Check if TODO content matches any criterion keywords
            for criterion in spec.acceptance_criteria:
                criterion_keywords = self._extract_keywords(criterion)
                if any(keyword in content for keyword in criterion_keywords):
                    spec_todos.append(todo)
                    break

        return spec_todos

    def _extract_keywords(self, criterion: str) -> list[str]:
        """Extract meaningful keywords from a criterion."""
        # Remove common words and extract key terms
        criterion_clean = criterion.replace("✓", "").replace("[ ]", "").lower()

        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = criterion_clean.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords

    def _is_criterion_satisfied(self, criterion: str, completed_todos: list[dict[str, Any]]) -> bool:
        """Check if completed TODOs satisfy the criterion."""
        # Extract key terms from criterion
        criterion_keywords = self._extract_keywords(criterion)

        if not criterion_keywords:
            return False

        # Count how many keywords are covered by completed TODOs
        covered_keywords = set()
        for todo in completed_todos:
            content = todo.get("content", "").lower()
            for keyword in criterion_keywords:
                if keyword in content:
                    covered_keywords.add(keyword)

        # Consider criterion satisfied if >70% of keywords are covered
        coverage = len(covered_keywords) / len(criterion_keywords)
        return coverage > 0.7

    def _load_spec_yaml(self, spec_id: str) -> dict[str, Any] | None:
        """Load specification YAML file."""
        spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec_id}.yaml"

        if not spec_path.exists():
            return None

        try:
            import yaml

            with open(spec_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load spec {spec_id}: {e}")
            return None

    def _save_spec_yaml(self, spec_id: str, spec_data: dict[str, Any]):
        """Save updated specification YAML file."""
        spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec_id}.yaml"

        try:
            import yaml

            with open(spec_path, "w") as f:
                yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Updated specification: {spec_id}")
        except Exception as e:
            self.logger.error(f"Failed to save spec {spec_id}: {e}")

    def _calculate_progress(self, spec_data: dict[str, Any]) -> float:
        """Calculate overall progress based on completed criteria."""
        criteria = spec_data.get("acceptance_criteria", [])
        if not criteria:
            return 0.0

        completed = sum(1 for c in criteria if "✓" in c)
        total = len(criteria)

        # Simple percentage for now (can be enhanced with weights)
        return round(completed / total, 2)


def main():
    """Main hook entry point."""
    hook = TodoSpecProgressHook()
    hook.run()


if __name__ == "__main__":
    main()
