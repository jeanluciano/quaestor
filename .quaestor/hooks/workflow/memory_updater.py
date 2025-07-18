#!/usr/bin/env python3
"""Update MEMORY.md based on TODO completions and project progress.

This hook is called by Claude Code when TodoWrite is used.
It delegates to the automation module to update project memory.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_utils import parse_hook_input, call_automation_hook, get_project_root


def main():
    """Main entry point for the hook."""
    # Parse hook input
    hook_data = parse_hook_input()
    
    # Check if this is a TodoWrite event
    if hook_data.get('toolName') != 'TodoWrite':
        return 0
    
    print("📝 Updating MEMORY.md based on TODO changes...")
    
    # Prepare context for automation hook
    context = {
        'from_todos': True,
        'milestone': None,  # Could be enhanced to detect specific milestone
        'hook_data': hook_data,
        'project_root': str(get_project_root())
    }
    
    # Call the automation hook
    return call_automation_hook('auto_update_memory', context)


if __name__ == "__main__":
    sys.exit(main())