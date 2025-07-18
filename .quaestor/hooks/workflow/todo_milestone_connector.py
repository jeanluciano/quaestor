#!/usr/bin/env python3
"""Connect TODO changes to milestone tracking and trigger PRs when milestones complete.

This hook is called by Claude Code when TodoWrite is used.
It updates milestone progress and creates PRs when milestones are completed.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_utils import parse_hook_input, call_automation_hook, get_project_root


def find_milestone_for_todos(todos, project_root):
    """Find which milestone contains the given TODOs.
    
    Args:
        todos: List of TODO items
        project_root: Project root path
        
    Returns:
        str: Milestone name or None
    """
    # For now, return None - could be enhanced to read milestone files
    # and match TODOs to specific milestones
    return None


def check_milestone_completion(hook_data, project_root):
    """Check if any milestones are now complete based on TODO changes.
    
    Args:
        hook_data: Parsed hook input from Claude
        project_root: Project root path
        
    Returns:
        list: Names of completed milestones
    """
    completed_milestones = []
    
    try:
        # Check if this is a TodoWrite event
        if hook_data.get('toolName') != 'TodoWrite':
            return completed_milestones
            
        # Get the todos from the output
        output = hook_data.get('output', {})
        todos = output.get('todos', [])
        
        # Count completed vs total
        total = len(todos)
        completed = sum(1 for todo in todos if todo.get('status') == 'completed')
        
        # If all TODOs are completed, we might have a completed milestone
        if total > 0 and completed == total:
            # Try to find the milestone
            milestone = find_milestone_for_todos(todos, project_root)
            if milestone:
                completed_milestones.append(milestone)
            else:
                # Generic milestone detection
                print("📊 All TODOs completed! Consider creating a milestone PR.")
                
    except Exception as e:
        print(f"Warning: Error checking milestone completion: {e}")
        
    return completed_milestones


def main():
    """Main entry point for the hook."""
    # Parse hook input
    hook_data = parse_hook_input()
    project_root = get_project_root()
    
    # First, update memory with TODO changes
    print("📝 Updating project memory...")
    memory_context = {
        'from_todos': True,
        'hook_data': hook_data,
        'project_root': str(project_root)
    }
    call_automation_hook('auto_update_memory', memory_context)
    
    # Check for milestone completion
    completed_milestones = check_milestone_completion(hook_data, project_root)
    
    if completed_milestones:
        print(f"🎉 Milestone(s) completed: {', '.join(completed_milestones)}")
        
        # Trigger milestone PR creation
        for milestone in completed_milestones:
            pr_context = {
                'milestone': milestone,
                'auto_pr': True,
                'project_root': str(project_root)
            }
            print(f"🚀 Creating PR for milestone: {milestone}")
            call_automation_hook('auto_milestone_check', pr_context)
    else:
        # Just check milestone status
        check_context = {
            'milestone': None,
            'auto_pr': False,
            'project_root': str(project_root)
        }
        call_automation_hook('auto_milestone_check', check_context)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())