# Hooks Overview

Quaestor's hook system provides automated triggers that execute at specific points in your development workflow. The system is designed to be minimal and helpful, not intrusive.

## What are Hooks?

Hooks are automated commands that execute when specific Claude Code events occur. With Quaestor's uvx-based system, hooks run without requiring any Python installation in your project:

- **Session Events**: When a Claude session starts
- **Tool Events**: When specific tools are used (like TodoWrite)
- **Zero Dependencies**: Hooks execute via `uvx` - no local Quaestor installation needed

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

Hooks are configured in `.claude/settings.json` and execute via `uvx`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uvx --from quaestor quaestor hook session-context-loader",
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
            "command": "uvx --from quaestor quaestor hook todo-spec-progress",
            "description": "Update specification progress when TODOs are completed"
          }
        ]
      }
    ]
  }
}
```

### How uvx-based Hooks Work

1. **No Installation Required**: Hooks run via `uvx` without installing Quaestor in your project
2. **Always Up-to-Date**: Uses the latest published version of Quaestor
3. **Project Context**: Hooks read your local `.quaestor/` files while running remotely
4. **Clean Dependencies**: Your project stays free of Quaestor dependencies

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

Hooks are automatically configured during initialization:

```bash
# Using uvx (recommended - no installation)
uvx quaestor init
# Creates .claude/settings.json with uvx commands

# Team mode
uvx quaestor init --mode team
# Creates shared .claude/settings.json

# Traditional installation
pip install quaestor
quaestor init
```

**Note**: No hook files are copied to your project. Hooks run via `uvx` commands configured in `.claude/settings.json`.

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
2. Verify `uvx` is installed (comes with `uv`)
3. Check internet connection (uvx downloads Quaestor on first run)
4. Try running manually: `echo '{}' | uvx --from quaestor quaestor hook session-context-loader`

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