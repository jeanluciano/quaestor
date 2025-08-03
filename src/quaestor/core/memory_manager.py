"""
Memory management for Quaestor's specification-driven development.

This module provides memory file generation, minimization, and lifecycle
management integrated with the folder-based specification system.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ..utils.yaml_utils import load_yaml
from .folder_manager import FolderManager

logger = logging.getLogger(__name__)


@dataclass
class MemoryContent:
    """Structured memory content for MEMORY.md generation."""

    project_status: dict[str, Any]
    active_specifications: list[dict[str, Any]]
    recent_progress: list[str]
    next_actions: list[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MemoryManager:
    """
    Manages MEMORY.md generation and lifecycle for specification tracking.

    Generates minimal, focused memory files based on active specifications
    while archiving historical context with completed specifications.
    """

    MAX_MEMORY_LINES = 50
    MAX_PROGRESS_ENTRIES = 5

    def __init__(self, project_path: Path, folder_manager: FolderManager):
        """
        Initialize MemoryManager with project path and folder manager.

        Args:
            project_path: Root project path containing .quaestor
            folder_manager: FolderManager instance for specification access
        """
        self.project_path = Path(project_path)
        self.folder_manager = folder_manager
        self.memory_file = self.project_path / ".quaestor" / "MEMORY.md"
        self.template_file = Path(__file__).parent.parent / "claude" / "templates" / "minimal_memory.md"

    def generate_minimal_memory(self) -> str:
        """
        Generate minimal MEMORY.md content from active specifications.

        Returns:
            Minimal memory content as markdown string (<50 lines)
        """
        # Gather active specifications
        active_specs = self._get_active_specifications()

        # Extract project status
        project_status = self._extract_project_status(active_specs)

        # Get recent progress
        recent_progress = self._extract_recent_progress()

        # Determine next actions
        next_actions = self._extract_next_actions(active_specs)

        # Create memory content
        memory_content = MemoryContent(
            project_status=project_status,
            active_specifications=active_specs,
            recent_progress=recent_progress,
            next_actions=next_actions,
        )

        # Generate markdown
        return self._render_memory_template(memory_content)

    def update_memory_file(self) -> bool:
        """
        Update MEMORY.md with current active specification state.

        Returns:
            True if update successful, False otherwise
        """
        try:
            # Generate new content
            content = self.generate_minimal_memory()

            # Ensure content is within limits
            lines = content.split("\n")
            if len(lines) > self.MAX_MEMORY_LINES:
                logger.warning(f"Memory content exceeds {self.MAX_MEMORY_LINES} lines, truncating")
                content = "\n".join(lines[: self.MAX_MEMORY_LINES])

            # Write to file
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text(content)

            logger.info(f"Updated MEMORY.md with {len(lines)} lines")
            return True

        except Exception as e:
            logger.error(f"Failed to update memory file: {e}")
            return False

    def _get_active_specifications(self) -> list[dict[str, Any]]:
        """Get all specifications in active folder."""
        active_specs = []
        active_path = self.folder_manager.base_path / "active"

        if not active_path.exists():
            return active_specs

        for spec_file in active_path.glob("*.yaml"):
            try:
                spec_data = load_yaml(spec_file)
                # Extract minimal info for memory
                active_specs.append(
                    {
                        "id": spec_data.get("id", spec_file.stem),
                        "title": spec_data.get("title", "Unknown"),
                        "type": spec_data.get("type", "feature"),
                        "priority": spec_data.get("priority", "medium"),
                        "progress": self._calculate_progress(spec_data),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to read specification {spec_file}: {e}")

        return active_specs

    def _extract_project_status(self, active_specs: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract overall project status from active specifications."""
        if not active_specs:
            return {"phase": "idle", "active_count": 0, "overall_progress": "No active specifications"}

        # Calculate average progress
        progress_values = [spec.get("progress", 0) for spec in active_specs]
        avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0

        # Determine phase
        if avg_progress < 20:
            phase = "planning"
        elif avg_progress < 80:
            phase = "implementing"
        else:
            phase = "finalizing"

        return {
            "phase": phase,
            "active_count": len(active_specs),
            "overall_progress": f"{int(avg_progress)}% complete across {len(active_specs)} active specifications",
        }

    def _extract_recent_progress(self) -> list[str]:
        """Extract recent progress entries from workflow state."""
        try:
            # Read workflow state if available
            workflow_file = self.project_path / ".quaestor" / ".workflow_state"
            if workflow_file.exists():
                workflow_data = load_yaml(workflow_file)
                # Extract last N implementation files
                impl_files = workflow_data.get("implementation_files", [])[-self.MAX_PROGRESS_ENTRIES :]
                return [f"Implemented: {Path(f).name}" for f in impl_files]
        except Exception:
            pass

        return ["No recent progress tracked"]

    def _extract_next_actions(self, active_specs: list[dict[str, Any]]) -> list[str]:
        """Extract next actions from active specifications."""
        actions = []

        for spec in active_specs[:3]:  # Top 3 priorities
            spec_id = spec.get("id", "unknown")
            progress = spec.get("progress", 0)

            if progress < 30:
                actions.append(f"Complete implementation for {spec_id}")
            elif progress < 70:
                actions.append(f"Write tests for {spec_id}")
            else:
                actions.append(f"Finalize and review {spec_id}")

        if not actions:
            actions.append("No active specifications - create new specification with /plan")

        return actions

    def _calculate_progress(self, spec_data: dict[str, Any]) -> int:
        """Calculate specification progress percentage."""
        # Simple heuristic based on phases
        phases = spec_data.get("phases", {})
        if not phases:
            return 0

        completed_phases = sum(
            1 for phase in phases.values() if isinstance(phase, dict) and phase.get("status") == "completed"
        )
        total_phases = len(phases)

        return int((completed_phases / total_phases) * 100) if total_phases > 0 else 0

    def _render_memory_template(self, content: MemoryContent) -> str:
        """Render memory content using minimal template."""
        # If template exists, use it; otherwise use embedded template
        template = self.template_file.read_text() if self.template_file.exists() else self._get_default_template()

        # Simple template substitution
        return template.format(
            timestamp=content.timestamp,
            phase=content.project_status.get("phase", "unknown"),
            active_count=content.project_status.get("active_count", 0),
            overall_progress=content.project_status.get("overall_progress", "Unknown"),
            active_specs=self._format_active_specs(content.active_specifications),
            recent_progress=self._format_list(content.recent_progress),
            next_actions=self._format_list(content.next_actions),
        )

    def _format_active_specs(self, specs: list[dict[str, Any]]) -> str:
        """Format active specifications for display."""
        if not specs:
            return "  - No active specifications"

        lines = []
        for spec in specs:
            lines.append(f"  - {spec['id']}: {spec['title']} ({spec['progress']}%)")
        return "\n".join(lines)

    def _format_list(self, items: list[str]) -> str:
        """Format list items for display."""
        if not items:
            return "  - None"
        return "\n".join(f"  - {item}" for item in items)

    def _get_default_template(self) -> str:
        """Get default minimal memory template."""
        return """# Project Memory

## Status
- **Last Updated**: {timestamp}
- **Phase**: {phase}
- **Active Specifications**: {active_count}
- **Progress**: {overall_progress}

## Active Work
{active_specs}

## Recent Progress
{recent_progress}

## Next Actions
{next_actions}

---
*Auto-generated from active specifications. See .quaestor/specifications/active/ for details.*
"""

    def archive_completed_specification(self, spec_id: str, spec_data: dict[str, Any]) -> bool:
        """Archive a completed specification in memory.

        Args:
            spec_id: Specification ID
            spec_data: Specification data including title, dates, achievements

        Returns:
            True if successful
        """
        memory_file = self.memory_file
        if not memory_file.exists():
            # Create initial memory file if it doesn't exist
            self.update_memory_file()

        try:
            # Read current memory
            current_content = memory_file.read_text()

            # Create completion entry
            completion_date = datetime.now().strftime("%Y-%m-%d")
            completion_entry = f"""
### {completion_date} - Specification Completed: {spec_id}

**Completed**: {spec_data.get("title", "Unknown")}
**Duration**: {spec_data.get("start_date", "Unknown")} to {completion_date}
**Key Achievements**:
{self._format_achievements(spec_data.get("acceptance_criteria", []))}

**Learnings**:
{self._format_learnings(spec_data.get("learnings", []))}

**Metrics**:
- Implementation scope: {spec_data.get("scope", "Unknown")}
- Complexity: {spec_data.get("complexity", "Unknown")}
- Status: ✅ Completed
"""

            # Find insertion point (after active specifications section)
            lines = current_content.split("\n")
            insert_index = self._find_completion_section(lines)

            # Insert completion entry
            if insert_index >= 0:
                lines.insert(insert_index, completion_entry)
                updated_content = "\n".join(lines)
            else:
                # Append at end if section not found
                updated_content = current_content + "\n" + completion_entry

            # Ensure content stays under limit
            updated_content = self._trim_old_completions(updated_content)

            # Write back
            memory_file.write_text(updated_content)
            return True

        except Exception as e:
            logger.error(f"Failed to archive specification {spec_id}: {e}")
            return False

    def _format_achievements(self, criteria: list[str]) -> str:
        """Format acceptance criteria as achievements."""
        if not criteria:
            return "- Specification requirements met"
        return "\n".join([f"- ✅ {criterion}" for criterion in criteria[:5]])  # Limit to 5

    def _format_learnings(self, learnings: list[str]) -> str:
        """Format learnings list."""
        if not learnings:
            return "- Implementation completed successfully"
        return "\n".join([f"- {learning}" for learning in learnings[:3]])  # Limit to 3

    def _find_completion_section(self, lines: list[str]) -> int:
        """Find where to insert completion entries."""
        # Look for completions section or end of active specs
        for i, line in enumerate(lines):
            if "## Completed Specifications" in line or "## Recent Completions" in line:
                return i + 1

        # Find end of active specifications section
        for i, line in enumerate(lines):
            if line.startswith("## Active Specifications"):
                # Find next section or end
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("##"):
                        return j
                return len(lines)

        # Default to end
        return len(lines)

    def _trim_old_completions(self, content: str) -> str:
        """Trim old completion entries to stay under line limit."""
        lines = content.split("\n")

        # Count completion entries
        completion_starts = []
        for i, line in enumerate(lines):
            if "Specification Completed:" in line:
                completion_starts.append(i)

        # If too many completions, remove oldest
        if len(completion_starts) > 5:  # Keep only 5 most recent
            # Find the end of the oldest completion
            oldest_start = completion_starts[0]
            oldest_end = completion_starts[1] if len(completion_starts) > 1 else len(lines)

            # Remove oldest completion
            del lines[oldest_start:oldest_end]

        # Ensure total lines under limit
        if len(lines) > self.MAX_MEMORY_LINES:
            # Trim from the middle (old progress entries)
            trim_start = self.MAX_MEMORY_LINES // 2
            trim_count = len(lines) - self.MAX_MEMORY_LINES + 5
            del lines[trim_start : trim_start + trim_count]
            lines.insert(trim_start, "... (older entries trimmed) ...")

        return "\n".join(lines)
