"""Build enforcement context from various sources."""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..enforcement.rule_enforcer import EnforcementContext


class ContextBuilder:
    """Build rich enforcement context from multiple sources."""

    def __init__(self, workflow_state: Any):
        self.workflow_state = workflow_state
        self._developer_experience_cache: float | None = None
        self._time_pressure_cache: float | None = None

    def build(self, input_data: dict[str, Any], workflow_state: Any, project_root: Path) -> EnforcementContext:
        """Build complete enforcement context."""
        # Extract basic info from input
        user_intent = self._detect_intent(input_data)
        workflow_phase = workflow_state.state.get("phase", "idle")
        file_path = input_data.get("filePath") or input_data.get("file_path")
        tool_name = input_data.get("toolName") or input_data.get("tool_name")

        # Calculate experience and pressure
        developer_experience = self._calculate_developer_experience(project_root)
        time_pressure = self._detect_time_pressure(input_data, workflow_state)

        # Count previous violations
        previous_violations = self._count_recent_violations(workflow_state)

        # Build metadata
        metadata = {
            "session_id": input_data.get("sessionId"),
            "timestamp": datetime.now().isoformat(),
            "files_examined": len(workflow_state.state.get("research_files", [])),
            "content": input_data.get("content", ""),
            "args": input_data.get("args", []),
        }

        return EnforcementContext(
            user_intent=user_intent,
            workflow_phase=workflow_phase,
            file_path=file_path,
            tool_name=tool_name,
            developer_experience=developer_experience,
            time_pressure=time_pressure,
            previous_violations=previous_violations,
            metadata=metadata,
        )

    def _detect_intent(self, input_data: dict[str, Any]) -> str:
        """Detect user intent from input data."""
        # Check explicit intent
        if "intent" in input_data:
            return input_data["intent"]

        # Infer from tool and context
        tool_name = input_data.get("toolName", "").lower()
        file_path = input_data.get("filePath", "").lower()

        # Intent patterns
        if "test" in file_path or "test" in tool_name:
            return "testing"
        elif "doc" in file_path or "readme" in file_path:
            return "documentation"
        elif tool_name in ["grep", "read", "search"]:
            return "research"
        elif tool_name in ["write", "edit", "multiedit"]:
            return "implementation"
        elif "plan" in str(input_data.get("args", [])):
            return "planning"
        else:
            return "unknown"

    def _calculate_developer_experience(self, project_root: Path) -> float:
        """Calculate developer experience based on git history."""
        if self._developer_experience_cache is not None:
            return self._developer_experience_cache

        try:
            # Get commit count (simplified metric)
            result = subprocess.run(
                ["git", "log", "--oneline", "--author", "@"],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=5,
            )

            if result.returncode == 0:
                commit_count = len(result.stdout.strip().split("\n"))
                # Simple mapping: 0-10 commits = 0.3, 10-50 = 0.5, 50-200 = 0.7, 200+ = 0.9
                if commit_count < 10:
                    experience = 0.3
                elif commit_count < 50:
                    experience = 0.5
                elif commit_count < 200:
                    experience = 0.7
                else:
                    experience = 0.9
            else:
                experience = 0.5  # Default medium experience

            self._developer_experience_cache = experience
            return experience

        except Exception:
            # Default to medium experience on error
            return 0.5

    def _detect_time_pressure(self, input_data: dict[str, Any], workflow_state: Any) -> float:
        """Detect time pressure from various signals."""
        if self._time_pressure_cache is not None:
            return self._time_pressure_cache

        pressure_score = 0.5  # Default medium pressure

        # Check for rush indicators in args
        args_str = " ".join(str(arg) for arg in input_data.get("args", []))
        rush_words = ["quick", "fast", "asap", "urgent", "hurry", "now"]
        if any(word in args_str.lower() for word in rush_words):
            pressure_score = 0.8

        # Check workflow velocity
        last_research = workflow_state.state.get("last_research")
        if last_research:
            try:
                research_time = datetime.fromisoformat(last_research)
                time_since_research = datetime.now() - research_time
                if time_since_research < timedelta(minutes=5):
                    # Very fast progression through phases
                    pressure_score = max(pressure_score, 0.7)
            except Exception:
                pass

        # Check for skip flags
        if "--skip-checks" in input_data.get("args", []):
            pressure_score = 0.9

        self._time_pressure_cache = pressure_score
        return pressure_score

    def _count_recent_violations(self, workflow_state: Any) -> int:
        """Count recent rule violations from workflow state."""
        # Simple implementation - could be enhanced with actual violation tracking
        violations = workflow_state.state.get("violations", {})

        # Count violations in last 24 hours
        count = 0
        cutoff_time = datetime.now() - timedelta(hours=24)

        for _rule_id, violation_times in violations.items():
            if isinstance(violation_times, list):
                for violation_time in violation_times:
                    try:
                        if datetime.fromisoformat(violation_time) > cutoff_time:
                            count += 1
                    except Exception:
                        pass

        return count

    def to_dict(self, context: EnforcementContext) -> dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "user_intent": context.user_intent,
            "workflow_phase": context.workflow_phase,
            "file_path": context.file_path,
            "tool_name": context.tool_name,
            "developer_experience": context.developer_experience,
            "time_pressure": context.time_pressure,
            "previous_violations": context.previous_violations,
            "metadata": context.metadata,
        }
