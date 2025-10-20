#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Load active specifications into session context at startup.

This hook injects the full content of active specifications into Claude's
context at session start, ensuring important project context survives
chat compaction and is immediately available in new sessions.
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Import from quaestor package for spec management
from quaestor.specifications import Specification, SpecificationManager, SpecStatus

# Configure logging
LOG_DIR = Path.home() / ".quaestor" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"hooks_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()  # Fallback to current directory


class SessionContextLoaderHook:
    """Inject active specifications as context at session start."""

    def __init__(self):
        self.hook_name = "session_context_loader"
        self.logger = logging.getLogger(f"quaestor.hooks.{self.hook_name}")
        self.start_time = time.time()
        self.input_data = {}
        self.project_root = get_project_root()
        self.spec_manager = SpecificationManager(self.project_root)
        self.performance_target_ms = 50  # Target: <50ms

    def read_input(self) -> dict:
        """Read JSON input from stdin."""
        try:
            raw_input = sys.stdin.read()
            if not raw_input:
                self.logger.warning("No input received from stdin")
                return {}
            data = json.loads(raw_input)
            if not isinstance(data, dict):
                self.logger.error("Input must be a JSON object")
                return {}
            self.input_data = data
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON input: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error reading input: {e}")
            return {}

    def output_json(self, data: dict, exit_code: int = 0):
        """Output JSON response and exit."""
        try:
            # Add execution metadata
            data["_metadata"] = {
                "hook": self.hook_name,
                "execution_time": time.time() - self.start_time,
                "timestamp": datetime.now().isoformat(),
            }
            json.dump(data, sys.stdout, indent=2)
            sys.stdout.flush()
            sys.exit(exit_code)
        except Exception as e:
            self.logger.error(f"Error outputting JSON: {e}")
            sys.exit(1)

    def output_error(self, message: str):
        """Output error response."""
        self.output_json({"error": message, "blocking": False}, 1)

    def output_success(self, message: str):
        """Output success response."""
        self.output_json({"message": message}, 0)

    def execute(self):
        """Load and inject active specifications into session context."""
        start_time = time.time()

        # Support both SessionStart and PostCompact events
        event_name = self.input_data.get("hook_event_name", "")
        if event_name not in ["SessionStart", "PostCompact"]:
            self.output_success(f"Not a session event: {event_name}")
            return

        # Track source for context customization
        source = self.input_data.get("source", "startup")  # startup, resume, compact

        try:
            # Generate context with event awareness
            context = self.generate_specification_context(event_name, source)

            # Performance tracking
            execution_time = (time.time() - start_time) * 1000
            if execution_time > self.performance_target_ms:
                self.logger.warning(
                    f"Performance target missed: {execution_time:.1f}ms > {self.performance_target_ms}ms"
                )

            # Output as additional context for session
            output = {
                "hookSpecificOutput": {
                    "hookEventName": event_name,
                    "additionalContext": context,
                    "metadata": {
                        "execution_time_ms": execution_time,
                        "performance_target_met": execution_time <= self.performance_target_ms,
                    },
                }
            }

            self.output_json(output, exit_code=0)

        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}")
            self.output_error(f"Session context loader failed: {str(e)}")

    def generate_specification_context(self, event_name: str, source: str) -> str:
        """Generate context containing full active specifications."""
        try:
            context_parts = []

            # Add consistent header for all sessions
            context_parts.append("<!-- QUAESTOR SESSION CONTEXT -->")

            # Header similar to CLAUDE.md
            context_parts.extend(
                [
                    "",
                    "<!-- QUAESTOR ACTIVE SPECIFICATIONS -->",
                    "> [!IMPORTANT]",
                    "> **Active Specifications**: The following specifications are currently being worked on.",
                    "> These define the current implementation tasks and acceptance criteria.",
                    "",
                ]
            )
            # Get active specifications
            active_specs = self.spec_manager.list_specifications(status=SpecStatus.ACTIVE)

            if active_specs:
                context_parts.append(f"## 📋 Active Specifications ({len(active_specs)})")
                context_parts.append("")

                # Load and inject each active specification with enhanced formatting
                for i, spec in enumerate(active_specs, 1):
                    spec_content = self._format_specification(spec, i)
                    context_parts.extend(spec_content)

                    # Add collapsible Markdown content
                    spec_path = self.project_root / ".quaestor" / "specs" / "active" / f"{spec.id}.md"
                    if spec_path.exists():
                        context_parts.extend(
                            ["<details>", "<summary>View Full Specification</summary>", "", "```markdown"]
                        )
                        with open(spec_path) as f:
                            context_parts.append(f.read().strip())
                        context_parts.extend(["```", "</details>", "", "---", ""])
            else:
                context_parts.extend(
                    [
                        "## 📋 No Active Specifications",
                        "",
                        "No specifications are currently active. Use `/plan` to create new specifications.",
                        "",
                    ]
                )

            context_parts.append("<!-- END QUAESTOR CONTEXT -->")

            return "\n".join(context_parts)

        except Exception as e:
            self.logger.error(f"Failed to generate context: {e}")
            return self._generate_fallback_context(str(e))

    def _format_specification(self, spec: Specification, index: int) -> list[str]:
        """Format specification with detailed progress breakdown."""
        content = []

        # Calculate detailed progress
        criteria_completed = sum(1 for c in spec.acceptance_criteria if "✓" in c or "completed" in c.lower())
        criteria_total = len(spec.acceptance_criteria)
        progress = (criteria_completed / criteria_total * 100) if criteria_total > 0 else 0

        content.extend(
            [
                f"### 📋 Specification {index}: {spec.title}",
                f"**ID**: {spec.id}",
                f"**Progress**: {progress:.0%}",
                f"├─ Criteria: {criteria_completed}/{criteria_total} completed",
                f"├─ Status: {spec.status.value}",
                f"├─ Priority: {spec.priority.value}",
                f"└─ Branch: {spec.branch or 'Not set'}",
                "",
            ]
        )

        # Add reminder about automatic tracking
        if progress < 1.0:
            content.extend(
                [
                    "<!-- AUTOMATIC TRACKING REMINDER -->",
                    "💡 **Progress tracks automatically**: Complete TODOs to update acceptance criteria",
                    "<!-- END REMINDER -->",
                    "",
                ]
            )

        # Show acceptance criteria with visual status
        if spec.acceptance_criteria:
            content.append("**Acceptance Criteria:**")
            for i, criterion in enumerate(spec.acceptance_criteria, 1):
                # Check if criterion is completed
                if "✓" in criterion or "completed" in criterion.lower():
                    content.append(f"  {i}. [x] ~~{criterion}~~")
                else:
                    content.append(f"  {i}. [ ] {criterion}")
            content.append("")

        # Test status summary if available
        if hasattr(spec, "test_scenarios") and spec.test_scenarios:
            passed = sum(1 for t in spec.test_scenarios if getattr(t, "passed", False))
            total = len(spec.test_scenarios)
            content.append(f"**Test Status**: {passed}/{total} passing")
            content.append("")

        # Show next actionable items if not complete
        if progress < 1.0:
            next_items = self._get_next_actionable_items(spec)
            if next_items:
                content.append("**🎯 Next Steps:**")
                for item in next_items[:3]:  # Show top 3
                    content.append(f"  → {item}")
                content.append("")

        return content

    def _get_next_actionable_items(self, spec: Specification) -> list[str]:
        """Get next actionable items for the specification."""
        next_items = []

        # Find uncompleted acceptance criteria
        for criterion in spec.acceptance_criteria:
            if "✓" not in criterion and "completed" not in criterion.lower():
                # Clean up the criterion text
                clean_criterion = criterion.replace("[ ]", "").strip()
                next_items.append(clean_criterion)

        # Add test-related items if criteria are mostly done
        if hasattr(spec, "test_scenarios") and spec.test_scenarios:
            failed_tests = [t for t in spec.test_scenarios if not getattr(t, "passed", False)]
            if failed_tests and len(next_items) < 3:
                next_items.append(f"Fix failing tests ({len(failed_tests)} remaining)")

        # Add generic items if needed
        if not next_items:
            if spec.status.value == "ACTIVE":
                next_items.append("Review implementation against spec")
                next_items.append("Run tests and verify functionality")

        return next_items

    def _generate_fallback_context(self, error: str) -> str:
        """Generate minimal fallback context on error."""
        return f"""<!-- QUAESTOR SESSION CONTEXT (FALLBACK MODE) -->
<!-- Error: {error} -->

## ⚠️ Context Loading Error

Could not load active specifications. Operating in fallback mode.

**Error**: {error}

**Quick Actions**:
- Check specs directory: `.quaestor/specs/active/`
- Use `/plan` to create new specifications
- Review existing specs: `/plan --list`

<!-- END FALLBACK CONTEXT -->"""

    def run(self):
        """Main entry point for hook execution."""
        try:
            self.read_input()
            self.execute()
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.hook_name}: {e}", exc_info=True)
            self.output_error(f"Unexpected error: {e}")


def main():
    """Main hook entry point."""
    hook = SessionContextLoaderHook()
    hook.run()


if __name__ == "__main__":
    main()
