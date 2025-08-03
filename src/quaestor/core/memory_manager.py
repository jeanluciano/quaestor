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

from ..utils.yaml_utils import load_yaml, save_yaml
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

    def archive_completed_specification(self, spec_id: str) -> bool:
        """
        Archive memory content for a completed specification.

        Args:
            spec_id: Specification identifier to archive

        Returns:
            True if archiving successful, False otherwise
        """
        try:
            # Find specification in completed folder
            completed_path = self.folder_manager.base_path / "completed" / f"{spec_id}.yaml"
            if not completed_path.exists():
                logger.warning(f"Completed specification {spec_id} not found")
                return False

            # Extract progress information
            spec_data = load_yaml(completed_path)

            # Create archive entry
            archive_entry = {
                "spec_id": spec_id,
                "title": spec_data.get("title", "Unknown"),
                "completed_at": datetime.now().isoformat(),
                "implementation_summary": self._extract_implementation_summary(spec_data),
                "files_created": spec_data.get("implementation_details", {}).get("files_to_create", []),
                "files_modified": spec_data.get("implementation_details", {}).get("files_to_modify", []),
            }

            # Append to specification file as completion metadata
            if "completion_metadata" not in spec_data:
                spec_data["completion_metadata"] = archive_entry
                save_yaml(completed_path, spec_data)

            # Remove from active memory
            self.update_memory_file()

            logger.info(f"Archived memory for specification {spec_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to archive specification {spec_id}: {e}")
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

    def _extract_implementation_summary(self, spec_data: dict[str, Any]) -> str:
        """Extract implementation summary from specification."""
        # Try to get from completion metadata first
        if "completion_metadata" in spec_data:
            return spec_data["completion_metadata"].get("summary", "")

        # Otherwise, use description
        return spec_data.get("description", "No summary available")[:200]

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
