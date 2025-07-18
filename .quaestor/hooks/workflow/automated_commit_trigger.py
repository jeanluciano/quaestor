#!/usr/bin/env python3
"""Trigger auto-commit when TODO items are marked as completed.

This hook is called by Claude Code when TodoWrite is used.
It parses the output to find completed items and creates commits.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared_utils import parse_hook_input, call_automation_hook, get_project_root


def parse_todo_changes(hook_data):
    """Parse TodoWrite output to find completed items.
    
    Args:
        hook_data: Parsed hook input from Claude
        
    Returns:
        list: Completed TODO items with their descriptions
    """
    completed_todos = []
    
    try:
        # Check if this is a TodoWrite event
        if hook_data.get('toolName') != 'TodoWrite':
            return completed_todos
            
        # Get the todos from the output
        output = hook_data.get('output', {})
        todos = output.get('todos', [])
        
        # Find completed items
        for todo in todos:
            if todo.get('status') == 'completed':
                # Check if this was just marked completed
                # (This is a simple check - could be enhanced to track state changes)
                completed_todos.append({
                    'id': todo.get('id'),
                    'content': todo.get('content', 'Completed task'),
                    'priority': todo.get('priority', 'medium')
                })
                
    except Exception as e:
        print(f"Warning: Error parsing TODO changes: {e}")
        
    return completed_todos


def generate_commit_message(todos):
    """Generate a commit message from completed TODOs.
    
    Args:
        todos: List of completed TODO items
        
    Returns:
        str: Formatted commit message
    """
    if not todos:
        return None
        
    if len(todos) == 1:
        # Single todo - use its content as the message
        content = todos[0]['content']
        # Clean up the message
        if len(content) > 50:
            # Truncate to 50 chars for commit title
            return f"feat: {content[:47]}..."
        return f"feat: {content}"
    else:
        # Multiple todos - create a summary
        message = f"feat: complete {len(todos)} tasks\n\n"
        for todo in todos:
            priority = todo.get('priority', 'medium')
            content = todo['content']
            message += f"- [{priority}] {content}\n"
        return message


def main():
    """Main entry point for the hook."""
    # Parse hook input
    hook_data = parse_hook_input()
    
    # Find completed TODOs
    completed_todos = parse_todo_changes(hook_data)
    
    if not completed_todos:
        # No completed TODOs, nothing to do
        return 0
        
    print(f"✅ Found {len(completed_todos)} completed TODO(s)")
    
    # Generate commit message
    commit_message = generate_commit_message(completed_todos)
    
    # Prepare context for automation hook
    context = {
        'message': commit_message,
        'files': None,  # Let the hook determine which files to commit
        'todos': completed_todos,
        'project_root': str(get_project_root())
    }
    
    # Call the automation hook
    print("🚀 Creating auto-commit...")
    return call_automation_hook('auto_commit', context)


if __name__ == "__main__":
    sys.exit(main())