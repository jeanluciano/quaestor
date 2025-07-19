# Auto-Commit Hook Enhancement Requirements

## Current Issue
The `automated_commit_trigger.py` hook exists but cannot detect newly completed TODOs because it lacks state tracking. It receives the current state of all TODOs but has no way to know which ones were just marked as completed.

## Required Enhancement

### 1. State Tracking Mechanism
The hook needs to track the previous state of TODOs to detect changes:

```python
# Option 1: File-based state tracking
STATE_FILE = Path(".quaestor/.todo_state.json")

def load_previous_state():
    """Load the previous TODO state from disk."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_current_state(todos):
    """Save the current TODO state to disk."""
    state = {todo['id']: todo['status'] for todo in todos}
    STATE_FILE.parent.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
```

### 2. Change Detection Logic
Compare previous and current states to find newly completed items:

```python
def find_newly_completed_todos(current_todos, previous_state):
    """Identify TODOs that were just marked as completed."""
    newly_completed = []
    
    for todo in current_todos:
        todo_id = todo.get('id')
        current_status = todo.get('status')
        previous_status = previous_state.get(todo_id, 'pending')
        
        # Check if status changed to completed
        if current_status == 'completed' and previous_status != 'completed':
            newly_completed.append(todo)
    
    return newly_completed
```

### 3. Enhanced Hook Flow
Update the main function to use state tracking:

```python
def main():
    """Main entry point for the hook."""
    # Parse hook input
    hook_data = parse_hook_input()
    
    # Get current TODOs from TodoWrite output
    current_todos = hook_data.get("output", {}).get("todos", [])
    
    # Load previous state
    previous_state = load_previous_state()
    
    # Find newly completed TODOs
    newly_completed = find_newly_completed_todos(current_todos, previous_state)
    
    # Save current state for next time
    save_current_state(current_todos)
    
    if not newly_completed:
        return 0
    
    # Generate commit message and trigger auto-commit
    commit_message = generate_commit_message(newly_completed)
    # ... rest of the implementation
```

### 4. Alternative Approach: Event-Based
Instead of state tracking, modify TodoWrite to emit events when status changes:

```python
# In TodoWrite tool implementation
if old_status != new_status and new_status == 'completed':
    emit_event('todo_completed', {
        'todo': todo,
        'old_status': old_status,
        'new_status': new_status
    })
```

### 5. Considerations
- **Concurrency**: Handle multiple Claude instances updating TODOs
- **State file location**: Use `.quaestor/` directory (gitignored)
- **Error handling**: Gracefully handle corrupted/missing state files
- **Performance**: Keep state file small (only IDs and status)

## Implementation Priority
1. Add state tracking to existing hook (quickest fix)
2. Test with various TODO operations
3. Consider event-based approach for v2
4. Add configuration options for auto-commit behavior

## Testing Scenarios
- Single TODO completion
- Multiple TODO completions in one update
- TODO status changes (completed → pending → completed)
- State file corruption/deletion
- Concurrent updates from multiple sessions