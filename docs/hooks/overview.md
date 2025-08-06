# Hooks Overview

Quaestor's hook system provides automated triggers that execute at specific points in your development workflow. The system is designed to be minimal and helpful, not intrusive.

## What are Hooks?

Hooks are Python scripts that execute automatically when specific Claude Code events occur:

- **Session Events**: When a Claude session starts
- **Tool Events**: When specific tools are used (like TodoWrite)

## Current Hooks

Quaestor includes two essential hooks that work together to provide automatic specification tracking:

### 📋 Session Context Loader
Loads active specifications and project context when a session starts:

```python
# .quaestor/hooks/session_context_loader.py
def on_session_start():
    """Load active specifications into session context."""
    - Display active specifications with progress bars
    - Show git branch information
    - Highlight next steps
    - Performance tracking (<50ms target)
```

**Features:**
- Visual progress bars for specification completion
- Tree-structured display of acceptance criteria
- Git branch alignment checking
- Performance monitoring
- Supports both SessionStart and PostCompact events

### 🎯 TODO-Based Specification Progress
Automatically tracks specification progress through TODO completion:

```python
# .quaestor/hooks/todo_spec_progress.py
def on_todo_completed(todos):
    """Update specification progress when TODOs are completed."""
    - Match completed TODOs to specification criteria
    - Update YAML files automatically
    - Add progress notes
    - Calculate completion percentage
```

**Features:**
- Zero manual intervention required
- Intelligent keyword matching
- Automatic YAML updates
- Natural workflow integration

## Hook Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/session_context_loader.py",
            "description": "Load active specifications into session context"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/todo_spec_progress.py",
            "description": "Update specification progress when TODOs are completed"
          }
        ]
      }
    ]
  }
}
```

## Hook Events

### SessionStart
Triggered when a new Claude session begins:
- Loads project context
- Displays active specifications
- Shows current progress

### PostToolUse
Triggered after specific tools are used:
- Currently monitors TodoWrite operations
- Updates specification progress automatically

## How They Work Together

1. **Session Starts**: The session context loader displays your active specifications
2. **You Work**: Create TODOs that relate to specification criteria
3. **Complete TODOs**: Mark TODOs as completed as you work
4. **Automatic Updates**: The todo_spec_progress hook updates specifications
5. **See Progress**: Next session shows updated progress

## Benefits

### Minimal and Helpful
- Only two hooks to maintain
- No intrusive enforcement
- Natural workflow integration
- Zero configuration needed

### Automatic Progress Tracking
- No manual YAML editing
- Progress updates as you work
- Clear visibility into what's done
- Maintains focus on implementation

### Performance
- Session loading optimized for <50ms
- Lightweight TODO monitoring
- No impact on development speed

## Installation

Hooks are automatically installed during `quaestor init`:

```bash
# Team mode
quaestor init --mode team
# Hooks installed to: .quaestor/hooks/

# Personal mode  
quaestor init
# Hooks installed to: .quaestor/hooks/
```

## Customization

While the default hooks cover most needs, you can:

1. **Adjust Performance Target**:
   ```python
   self.performance_target_ms = 100  # Allow more time for larger projects
   ```

2. **Customize Progress Display**:
   ```python
   # In session_context_loader.py
   self.show_completed_criteria = False  # Hide completed items
   ```

3. **Add Custom Hooks**:
   Create new hooks by following the pattern in `base.py`

## Troubleshooting

### Hooks Not Running
1. Check `.claude/settings.json` exists and is valid JSON
2. Verify Python path in hook commands
3. Check hook files have execute permissions

### Progress Not Updating
1. Ensure TODOs are marked as "completed" status
2. Check TODO content relates to specification criteria
3. Verify specification is in "ACTIVE" status

### Performance Issues
1. Check session_context_loader.py logs for timing
2. Reduce number of active specifications
3. Consider disabling visual progress bars

## Next Steps

- Learn about [Session Context Loading](session-context-loader.md)
- Understand [Specification Progress Tracking](spec-tracking.md)
- Explore the [Specification Workflow](../specs/workflow.md)