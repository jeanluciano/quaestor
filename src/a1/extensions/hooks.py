"""Simplified hook system for A1 - extracted from V2.0 complexity.

Provides file-based hook execution with 92% code reduction from A1.
Focuses on practical functionality with simple JSON configuration.
"""

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.events import ToolUseEvent


@dataclass
class HookDefinition:
    """Simple hook definition."""

    type: str  # "command", "python", "shell"
    command: str
    name: str = ""
    description: str = ""
    timeout: int = 30  # seconds

    def matches_tool(self, tool_name: str) -> bool:
        """Check if this hook should run for the given tool."""
        # Simple pattern matching - no complex event filters
        return bool(re.search(self.pattern, tool_name, re.IGNORECASE))


@dataclass
class HookResult:
    """Result of hook execution."""

    success: bool
    duration_ms: float
    output: str = ""
    error: str = ""
    exit_code: int = 0


class SimpleHookManager:
    """Simplified hook manager for A1."""

    def __init__(self, config_file: str = ".quaestor/hooks.json", project_root: str = "."):
        self.config_file = Path(config_file)
        self.project_root = Path(project_root)
        self.hooks: dict[str, list[tuple[str, HookDefinition]]] = {}
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load hook configuration from JSON file."""
        if not self.config_file.exists():
            self.hooks = {}
            return

        try:
            with open(self.config_file) as f:
                config = json.load(f)

            self.hooks = {}
            for event_type, matchers in config.get("hooks", {}).items():
                self.hooks[event_type] = []

                for matcher_config in matchers:
                    pattern = matcher_config.get("matcher", ".*")
                    hook_configs = matcher_config.get("hooks", [])

                    for hook_config in hook_configs:
                        hook = HookDefinition(
                            type=hook_config.get("type", "command"),
                            command=hook_config.get("command", ""),
                            name=hook_config.get("name", ""),
                            description=hook_config.get("description", ""),
                            timeout=hook_config.get("timeout", 30),
                        )
                        self.hooks[event_type].append((pattern, hook))

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to load hook configuration: {e}")
            self.hooks = {}

    def _substitute_variables(self, command: str, context: dict[str, Any]) -> str:
        """Substitute variables in command string."""
        substitutions = {
            "{python_path}": sys.executable,
            "{project_root}": str(self.project_root.absolute()),
        }

        # Add context variables
        for key, value in context.items():
            substitutions[f"{{{key}}}"] = str(value)

        result = command
        for placeholder, value in substitutions.items():
            result = result.replace(placeholder, value)

        return result

    def _execute_hook(self, hook: HookDefinition, context: dict[str, Any]) -> HookResult:
        """Execute a single hook."""
        start_time = time.time()

        try:
            # Substitute variables in command
            command = self._substitute_variables(hook.command, context)

            if hook.type == "command":
                # Execute as shell command
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=hook.timeout, cwd=self.project_root
                )

                duration_ms = (time.time() - start_time) * 1000

                return HookResult(
                    success=result.returncode == 0,
                    duration_ms=duration_ms,
                    output=result.stdout,
                    error=result.stderr,
                    exit_code=result.returncode,
                )

            elif hook.type == "python":
                # Execute Python script directly
                # Split command and args properly
                cmd_parts = command.split()
                script_path = cmd_parts[0]
                script_args = cmd_parts[1:] + context.get("args", [])

                result = subprocess.run(
                    [sys.executable, script_path] + script_args,
                    capture_output=True,
                    text=True,
                    timeout=hook.timeout,
                    cwd=self.project_root,
                )

                duration_ms = (time.time() - start_time) * 1000

                return HookResult(
                    success=result.returncode == 0,
                    duration_ms=duration_ms,
                    output=result.stdout,
                    error=result.stderr,
                    exit_code=result.returncode,
                )

            else:
                return HookResult(success=False, duration_ms=0, error=f"Unknown hook type: {hook.type}")

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            return HookResult(
                success=False, duration_ms=duration_ms, error=f"Hook timed out after {hook.timeout} seconds"
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HookResult(success=False, duration_ms=duration_ms, error=str(e))

    def execute_hooks(self, event_type: str, tool_name: str = "", **context) -> list[HookResult]:
        """Execute all matching hooks for an event type and tool."""
        if event_type not in self.hooks:
            return []

        results = []
        execution_context = {"tool_name": tool_name, "event_type": event_type, **context}

        for pattern, hook in self.hooks[event_type]:
            # Check if pattern matches tool name
            if tool_name and not re.search(pattern, tool_name, re.IGNORECASE):
                continue

            result = self._execute_hook(hook, execution_context)
            results.append(result)

            # Log result
            status = "✅" if result.success else "❌"
            print(f"{status} Hook {hook.name or hook.command[:50]}... ({result.duration_ms:.1f}ms)")

            if not result.success and result.error:
                print(f"   Error: {result.error}")

        return results

    def handle_tool_use_event(self, event: ToolUseEvent) -> list[HookResult]:
        """Handle tool use event by executing pre/post hooks."""
        results = []

        # Execute pre-tool hooks
        pre_results = self.execute_hooks(
            "PreToolUse", event.tool_name, success=event.success, duration_ms=event.duration_ms
        )
        results.extend(pre_results)

        # Execute post-tool hooks
        post_results = self.execute_hooks(
            "PostToolUse", event.tool_name, success=event.success, duration_ms=event.duration_ms
        )
        results.extend(post_results)

        return results

    def register_hook(self, event_type: str, pattern: str, hook: HookDefinition) -> None:
        """Register a new hook programmatically."""
        if event_type not in self.hooks:
            self.hooks[event_type] = []

        self.hooks[event_type].append((pattern, hook))

    def reload_configuration(self) -> None:
        """Reload hook configuration from file."""
        self._load_configuration()

    def get_hooks_summary(self) -> dict[str, Any]:
        """Get summary of loaded hooks."""
        summary = {}

        for event_type, hook_list in self.hooks.items():
            summary[event_type] = []
            for pattern, hook in hook_list:
                summary[event_type].append(
                    {
                        "pattern": pattern,
                        "name": hook.name or "Unnamed hook",
                        "type": hook.type,
                        "command": hook.command[:100] + "..." if len(hook.command) > 100 else hook.command,
                    }
                )

        return summary


# Global instance for easy access
_hook_manager: SimpleHookManager | None = None


def get_hook_manager() -> SimpleHookManager:
    """Get global hook manager instance."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = SimpleHookManager()
    return _hook_manager


def execute_hooks(event_type: str, tool_name: str = "", **context) -> list[HookResult]:
    """Execute hooks for an event type and tool."""
    return get_hook_manager().execute_hooks(event_type, tool_name, **context)


def execute_pre_tool_hooks(tool_name: str, **context) -> list[HookResult]:
    """Execute pre-tool hooks."""
    return execute_hooks("PreToolUse", tool_name, **context)


def execute_post_tool_hooks(tool_name: str, success: bool = True, **context) -> list[HookResult]:
    """Execute post-tool hooks."""
    return execute_hooks("PostToolUse", tool_name, success=success, **context)


def register_hook(event_type: str, pattern: str, command: str, hook_type: str = "command") -> None:
    """Register a new hook."""
    hook = HookDefinition(type=hook_type, command=command)
    get_hook_manager().register_hook(event_type, pattern, hook)


def reload_hooks() -> None:
    """Reload hook configuration from file."""
    get_hook_manager().reload_configuration()


def create_default_config(config_file: str = ".quaestor/hooks.json") -> None:
    """Create a default hook configuration file."""
    config_path = Path(config_file)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "name": "Pre-implementation check",
                            "command": "echo 'Starting implementation...'",
                            "description": "Log implementation start",
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Read|Grep",
                    "hooks": [
                        {
                            "type": "python",
                            "name": "Track research",
                            "command": "{project_root}/.quaestor/hooks/track-research.py {project_root}",
                            "description": "Track research activities",
                        }
                    ],
                },
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [
                        {
                            "type": "python",
                            "name": "Track implementation",
                            "command": "{project_root}/.quaestor/hooks/track-implementation.py {project_root}",
                            "description": "Track implementation progress",
                        }
                    ],
                },
                {
                    "matcher": "TodoWrite",
                    "hooks": [
                        {
                            "type": "python",
                            "name": "Update memory",
                            "command": "{project_root}/.quaestor/hooks/update-memory.py {project_root} --from-todos",
                            "description": "Update project memory from todos",
                        }
                    ],
                },
            ],
        }
    }

    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=2)

    print(f"Created default hook configuration at {config_path}")
