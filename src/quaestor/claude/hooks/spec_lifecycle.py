#!/usr/bin/env python3
"""Handle automatic spec lifecycle transitions (draft → active → completed)."""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from quaestor.claude.hooks.base import BaseHook, get_project_root


class SpecLifecycleHook(BaseHook):
    """Manage specification lifecycle transitions automatically."""

    def __init__(self):
        super().__init__("spec_lifecycle")
        self.project_root = get_project_root()

    def execute(self):
        """Check for spec activation opportunities."""
        # Get tool details
        tool_name = self.input_data.get("toolName", "")
        tool_input = self.input_data.get("tool_input", {})
        
        # Only process Task tool calls (for /impl command)
        if tool_name != "Task":
            self.output_success("Not a Task tool call")
            return
            
        # Check if this is an implementation task
        description = tool_input.get("description", "").lower()
        prompt = tool_input.get("prompt", "").lower()
        
        # Keywords that indicate implementation
        impl_keywords = ["implement", "execute", "build", "create feature", "develop", "code"]
        
        is_implementation = any(keyword in description or keyword in prompt for keyword in impl_keywords)
        
        if not is_implementation:
            self.output_success("Not an implementation task")
            return
            
        # Check for matching spec in draft folder
        draft_dir = self.project_root / ".quaestor" / "specs" / "draft"
        active_dir = self.project_root / ".quaestor" / "specs" / "active"
        
        if not draft_dir.exists():
            self.output_success("No draft folder found")
            return
            
        # Extract potential spec ID from prompt
        spec_match = self._find_matching_spec(prompt, draft_dir)
        
        if spec_match:
            # Check if active folder has space
            active_specs = list(active_dir.glob("*.yaml")) if active_dir.exists() else []
            
            if len(active_specs) >= 3:
                message = f"📋 Found matching spec '{spec_match.stem}' in draft folder, but active folder is full (3/3 slots). Please complete or archive an active spec first."
                self.output_suggestion(message)
                return
                
            # Suggest activation
            message = f"""📋 Found matching specification '{spec_match.stem}' in draft folder!

Would you like to activate it? This will:
1. Move the spec to active/ folder
2. Update status to 'active'
3. Link to current work

Please run: Move {spec_match} to {active_dir / spec_match.name}"""
            
            self.output_suggestion(message)
        else:
            self.output_success("No matching draft spec found")
            
    def _find_matching_spec(self, text: str, draft_dir: Path) -> Path | None:
        """Find a spec in draft folder that matches the task description."""
        text_lower = text.lower()
        
        # Look for spec IDs mentioned directly
        for spec_file in draft_dir.glob("*.yaml"):
            spec_id = spec_file.stem
            if spec_id in text or spec_id.replace("-", " ") in text_lower:
                return spec_file
                
        # Look for keyword matches in spec titles
        for spec_file in draft_dir.glob("*.yaml"):
            try:
                with open(spec_file) as f:
                    content = f.read()
                    # Simple title extraction
                    for line in content.split("\n"):
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip().lower()
                            # Check if significant words from title appear in text
                            title_words = [w for w in title.split() if len(w) > 3]
                            if len(title_words) > 0:
                                matches = sum(1 for word in title_words if word in text_lower)
                                if matches >= len(title_words) * 0.5:  # 50% word match
                                    return spec_file
            except Exception:
                continue
                
        return None


if __name__ == "__main__":
    hook = SpecLifecycleHook()
    hook.run()