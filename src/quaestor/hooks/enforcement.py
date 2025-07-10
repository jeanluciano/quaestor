"""Enforcement hooks for CRITICAL_RULES compliance.

These hooks ensure that Claude follows the mandatory workflow patterns
defined in CRITICAL_RULES.md.
"""

import re
from datetime import datetime, timedelta
from typing import Any

from . import HookResult, get_project_root

# Track workflow state
WORKFLOW_STATE_FILE = ".quaestor/.workflow_state"


class WorkflowState:
    """Track the current workflow state."""

    def __init__(self):
        self.root = get_project_root()
        self.state_file = self.root / WORKFLOW_STATE_FILE
        self.state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        """Load workflow state from file."""
        if not self.state_file.exists():
            return {
                "phase": "idle",
                "last_research": None,
                "last_plan": None,
                "research_files": [],
                "complexity_level": "simple",
            }

        try:
            import json

            with open(self.state_file) as f:
                return json.load(f)
        except Exception:
            return {"phase": "idle"}

    def _save_state(self):
        """Save workflow state to file."""
        try:
            import json

            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception:
            pass

    def mark_research_done(self, files: list[str]):
        """Mark that research phase is complete."""
        self.state["phase"] = "planning"
        self.state["last_research"] = datetime.now().isoformat()
        self.state["research_files"] = files
        self._save_state()

    def mark_plan_done(self):
        """Mark that planning phase is complete."""
        self.state["phase"] = "implementing"
        self.state["last_plan"] = datetime.now().isoformat()
        self._save_state()

    def reset_workflow(self):
        """Reset workflow to idle state."""
        self.state["phase"] = "idle"
        self.state["last_research"] = None
        self.state["last_plan"] = None
        self.state["research_files"] = []
        self._save_state()

    def is_research_valid(self) -> bool:
        """Check if research is still valid (within 2 hours)."""
        if not self.state.get("last_research"):
            return False

        try:
            last_research = datetime.fromisoformat(self.state["last_research"])
            return datetime.now() - last_research < timedelta(hours=2)
        except Exception:
            return False


def run_enforcement_hook(hook_name: str, context: dict[str, Any]) -> HookResult:
    """Run an enforcement hook."""
    if hook_name == "enforce_research_before_code":
        return check_research_before_implementation(context.get("tool", ""))
    elif hook_name == "enforce_complexity_check":
        return check_complexity_triggers(context)
    elif hook_name == "enforce_agent_usage":
        return check_agent_usage(context)
    else:
        return HookResult(False, f"Unknown enforcement hook: {hook_name}")


def check_research_before_implementation(tool: str) -> HookResult:
    """Ensure research is done before writing code."""
    # Tools that indicate implementation
    implementation_tools = ["Write", "Edit", "MultiEdit"]

    if tool not in implementation_tools:
        return HookResult(True, "Tool allowed")

    state = WorkflowState()

    # Check if we're in the right phase
    if state.state["phase"] == "idle":
        return HookResult(
            False,
            "❌ BLOCKED: You must research the codebase before implementing.\n"
            "Required: Use Grep/Read tools to examine at least 5 relevant files.\n"
            "Say: 'Let me research the codebase and create a plan before implementing.'",
        )

    if state.state["phase"] == "planning" and not state.state.get("last_plan"):
        return HookResult(
            False,
            "❌ BLOCKED: You must create and get approval for a plan before implementing.\n"
            "Required: Present a structured implementation plan.\n"
            "Say: 'Based on my research, here's my implementation plan...'",
        )

    if not state.is_research_valid():
        return HookResult(
            False,
            "⚠️ WARNING: Your research is stale (>2 hours old).\n"
            "Recommended: Re-examine the codebase before continuing.\n"
            "Say: 'Let me refresh my understanding of the codebase.'",
        )

    # Check if enough files were examined
    if len(state.state.get("research_files", [])) < 5:
        files_examined = len(state.state.get("research_files", []))
        return HookResult(
            False,
            f"❌ BLOCKED: Insufficient research. You've only examined {files_examined} files.\n"
            "Required: Examine at least 5 relevant files before implementing.\n"
            "Use: Grep, Read, or Task tools to explore the codebase.",
        )

    return HookResult(True, "✅ Research validated - implementation allowed")


def check_complexity_triggers(context: dict[str, Any]) -> HookResult:
    """Check for complexity triggers that require special handling."""
    tool = context.get("tool", "")
    args = context.get("args", {})

    # Check for complex code patterns
    if tool in ["Write", "Edit", "MultiEdit"]:
        content = args.get("content", "") or args.get("new_string", "")

        # Complexity indicators
        complexity_checks = [
            (r"class.*:\n(?:.*\n){50,}", "Class with >50 lines"),
            (r"def.*:\n(?:.*\n){30,}", "Function with >30 lines"),
            (r"(?:if|for|while).*:\n(?:.*(?:if|for|while).*:\n){3,}", "Nesting depth >3"),
            (r"(?:try|except).*:\n(?:.*\n){20,}", "Complex error handling"),
        ]

        triggers = []
        for pattern, description in complexity_checks:
            if re.search(pattern, content, re.MULTILINE):
                triggers.append(description)

        if triggers:
            return HookResult(
                False,
                f"⚠️ COMPLEXITY DETECTED:\n"
                f"Found: {', '.join(triggers)}\n\n"
                f"Required actions:\n"
                f"1. Use 'ultrathink' for complex reasoning\n"
                f"2. Break down into smaller functions\n"
                f"3. Consider using multiple agents\n\n"
                f"Say: 'Let me ultrathink about this architecture before implementing.'",
            )

    return HookResult(True, "Complexity check passed")


def check_agent_usage(context: dict[str, Any]) -> HookResult:
    """Check if multiple agents should be used."""
    task_description = context.get("task_description", "").lower()

    # Triggers for multi-agent usage
    multi_agent_triggers = [
        "multiple files",
        "refactor",
        "new feature",
        "performance",
        "analyze",
        "complex",
        "architecture",
        "integrate",
    ]

    triggered = [trigger for trigger in multi_agent_triggers if trigger in task_description]

    if len(triggered) >= 2:
        return HookResult(
            False,
            f"🤖 MULTI-AGENT REQUIRED:\n"
            f"Detected triggers: {', '.join(triggered)}\n\n"
            f"Required: Spawn multiple agents for parallel work\n"
            f"Example: 'I'll spawn agents to tackle different aspects:'\n"
            f"- Agent 1: Analyze existing patterns\n"
            f"- Agent 2: Write implementation\n"
            f"- Agent 3: Create tests\n\n"
            f"Use the Task tool with appropriate prompts.",
        )

    return HookResult(True, "Agent check passed")


def validate_critical_rules_loaded() -> HookResult:
    """Ensure CRITICAL_RULES.md has been loaded."""
    root = get_project_root()
    critical_rules = root / ".quaestor" / "CRITICAL_RULES.md"

    if not critical_rules.exists():
        return HookResult(
            False,
            "⚠️ WARNING: CRITICAL_RULES.md not found!\n"
            "This file defines mandatory workflow patterns.\n"
            "Run: quaestor init --force to regenerate.",
        )

    # Check if file was recently modified (could indicate it wasn't loaded)
    try:
        import os

        stat = os.stat(critical_rules)
        modified = datetime.fromtimestamp(stat.st_mtime)
        if datetime.now() - modified < timedelta(minutes=5):
            return HookResult(
                False,
                "📋 REMINDER: CRITICAL_RULES.md was recently updated.\n"
                "Required: Re-read CRITICAL_RULES.md to ensure compliance.\n"
                "Say: 'Let me review the updated CRITICAL_RULES.'",
            )
    except Exception:
        pass

    return HookResult(True, "CRITICAL_RULES check passed")
