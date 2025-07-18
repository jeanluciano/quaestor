#!/usr/bin/env python3
"""A1 Claude Code Hook Receiver - Receives ALL Claude Code hook events directly."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from a1.core.events import ClaudeEvent
from a1.service.client import A1ServiceClient


class ClaudeHookReceiver:
    """Receives ALL Claude Code hook events directly and forwards to A1 service."""

    def __init__(self):
        self.service_client = A1ServiceClient()

    def process_hook(self, hook_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process raw Claude Code hook data.

        Args:
            hook_type: Type of hook (pre_tool_use, post_tool_use, etc.)
            data: Raw hook data from Claude Code

        Returns:
            Response dict for Claude Code
        """
        try:
            # Create Claude event from hook data
            event = ClaudeEvent(type=hook_type, data=data, timestamp=datetime.now(), source="claude_code")

            # Send to A1 service asynchronously (non-blocking)
            # We need to run in event loop since hooks are sync
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.service_client.send_event(event))

            # Return quickly to not block Claude
            return {"status": "received", "a1": "processing"}

        except Exception as e:
            # Don't fail Claude operations if A1 has issues
            return {"status": "error", "error": str(e), "a1": "failed"}

    def handle_pre_stop(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle preStopHook."""
        return self.process_hook("pre_stop", data)

    def handle_stop(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle stopHook."""
        return self.process_hook("stop", data)

    def handle_pre_tool_use(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle preToolUseHook."""
        return self.process_hook("pre_tool_use", data)

    def handle_post_tool_use(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle postToolUseHook."""
        return self.process_hook("post_tool_use", data)

    def handle_pre_file_edit(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle preFileEditHook."""
        return self.process_hook("pre_file_edit", data)

    def handle_post_file_edit(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle postFileEditHook."""
        return self.process_hook("post_file_edit", data)

    def handle_pre_user_prompt(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle preUserPromptSubmitHook."""
        return self.process_hook("pre_user_prompt_submit", data)

    def handle_pre_text_gen(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle preProcessTextGenerationHook."""
        return self.process_hook("pre_process_text_generation", data)

    def handle_file_change(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle fileChangeHook."""
        return self.process_hook("file_change", data)

    def handle_test_run(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle testRunHook."""
        return self.process_hook("test_run", data)


def main():
    """Main entry point for hook script."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Hook type not specified"}))
        sys.exit(1)

    hook_type = sys.argv[1]

    # Read hook data from stdin
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"error": f"Failed to parse input: {str(e)}"}))
        sys.exit(1)

    # Create receiver and handle hook
    receiver = ClaudeHookReceiver()

    handlers = {
        "pre_stop": receiver.handle_pre_stop,
        "stop": receiver.handle_stop,
        "pre_tool_use": receiver.handle_pre_tool_use,
        "post_tool_use": receiver.handle_post_tool_use,
        "pre_file_edit": receiver.handle_pre_file_edit,
        "post_file_edit": receiver.handle_post_file_edit,
        "pre_user_prompt": receiver.handle_pre_user_prompt,
        "pre_text_gen": receiver.handle_pre_text_gen,
        "file_change": receiver.handle_file_change,
        "test_run": receiver.handle_test_run,
    }

    handler = handlers.get(hook_type)
    if not handler:
        print(json.dumps({"error": f"Unknown hook type: {hook_type}"}))
        sys.exit(1)

    # Process hook and return response
    try:
        result = handler(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e), "a1": "failed"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
