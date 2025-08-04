# Quaestor Mode Detection System

## Overview

Quaestor now uses a simple, reliable mode detection system that distinguishes between:

- **Drive Mode**: Default mode where users have full control with no workflow enforcement
- **Framework Mode**: Active only when executing Quaestor commands, enforces workflow patterns

## How It Works

### Drive Mode (Default)
- Active when users are working directly without using Quaestor commands
- No workflow enforcement
- No specification requirements
- Full freedom to edit any files
- Compliance hooks are bypassed

### Framework Mode
- Active ONLY when executing a Quaestor command (`/research`, `/plan`, `/impl`, `/review`, `/debug`)
- Enforces Research → Plan → Implement workflow
- Requires active specifications for implementation work
- Provides helpful guidance and agent suggestions
- Tracks progress and provides phase-appropriate feedback

## Implementation Details

### Mode Detection (`mode_detector.py`)
- Uses a simple marker file approach (`/tmp/.quaestor_command_active`)
- Commands set the marker when they start
- Marker is removed when command completes
- Includes timeout protection (5 minutes) to prevent stale markers

### Hook Integration
- `compliance_pre_edit.py`: Checks mode before enforcing rules
- `workflow_tracker.py`: Only tracks progress in framework mode
- `base.py`: Provides mode detection methods for all hooks

### Key Benefits
1. **No brittle state files**: Removed complex `.workflow_state` file
2. **Clear mode switching**: Based on command execution, not persistent state
3. **User control**: Drive mode gives complete freedom
4. **Framework guidance**: Commands provide structured workflow when needed

## Usage

For users:
- Work normally for direct edits (drive mode)
- Use Quaestor commands for structured work (framework mode)

For developers:
- Check mode with `is_drive_mode()` or `is_framework_mode()`
- Commands should set framework mode when appropriate
- Hooks should respect mode when enforcing rules

## Migration Notes

The old workflow state file (`.quaestor/.workflow_state`) is no longer used and can be safely deleted. The new system is much simpler and more reliable.