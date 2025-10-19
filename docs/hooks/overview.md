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


**Features:**
- Zero manual intervention required
- Intelligent keyword matching
- Automatic YAML updates
- Natural workflow integration

## Hook Configuration

Hooks are provided by the Quaestor Claude Code plugin and automatically configured when you:

1. Install the Quaestor plugin from Claude Code marketplace
2. Initialize your project with `uvx quaestor init`

### How Plugin-based Hooks Work

1. **No Manual Configuration**: Hooks are part of the plugin, not your project files
2. **Always Up-to-Date**: Plugin updates bring the latest hook improvements
3. **Project Context**: Hooks read your local `.quaestor/` files for context
4. **Zero Maintenance**: No files to update or maintain in your repository

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
4. **Manual Updates**: Update specifications manually as needed
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

Hooks are automatically available when you:

```bash
# 1. Install the Quaestor plugin from Claude Code marketplace

# 2. Initialize your project
uvx quaestor init
```

**Note**: Hooks are provided by the Quaestor Claude Code plugin, not stored in your project directory.

## Customization

The default hooks are designed to work well for most projects. Hook behavior can be customized through:

1. **Specification Structure**: Organize specs in `.quaestor/specs/` to control what's loaded
2. **Project Configuration**: Use `.quaestor/AGENT.md` and `.quaestor/RULES.md` to guide behavior
3. **Future Plugin Settings**: Customization options coming in future plugin releases

## Troubleshooting

### Hooks Not Running
1. Verify the Quaestor plugin is installed in Claude Code
2. Check that `.quaestor/` directory exists in your project
3. Ensure you've run `uvx quaestor init` in your project
4. Restart Claude Code to reload the plugin

### Context Not Loading
1. Verify `.quaestor/AGENT.md` exists
2. Check that active specifications are in `.quaestor/specs/active/`
3. Ensure specification files are valid Markdown

### Performance Issues
1. Reduce number of active specifications (move some to draft or archive)
2. Keep specifications focused and concise
3. Report persistent issues to the Quaestor GitHub repository

## Next Steps

- Learn about [Session Context Loading](session-context-loader.md)
- Explore the [Specification Workflow](../specs/workflow.md)