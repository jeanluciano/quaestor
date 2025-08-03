#!/usr/bin/env python3
"""UserPromptSubmit hook - simplified version.

Simply logs the user prompt for debugging and passes through.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook


class UserPromptSubmitHook(BaseHook):
    """Simple hook that logs user prompts."""

    def __init__(self):
        super().__init__("UserPromptSubmit")

    def execute(self):
        """Process user prompt - just log and pass through."""
        try:
            # Get user prompt from input
            user_prompt = self.input_data.get("user_prompt", "")
            session_id = self.input_data.get("sessionId", "unknown")

            # Log the prompt (truncated for safety)
            prompt_preview = user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
            self.logger.info(f"User prompt: {prompt_preview}")

            # Simple output with context info
            output = {
                "session_id": session_id,
                "has_active_work": self.has_active_work(),
                "message": "Ready to assist!",
            }

            self.output_success(data=output)

        except Exception as e:
            self.logger.error(f"Error in UserPromptSubmit: {e}")
            self.output_error(f"Hook execution failed: {e}")


def main():
    """Entry point for the hook."""
    hook = UserPromptSubmitHook()
    hook.run()


if __name__ == "__main__":
    main()
