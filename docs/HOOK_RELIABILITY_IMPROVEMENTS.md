# Hook Reliability Improvements

This document describes the reliability improvements made to the Quaestor hooks system based on Claude Code's best practices.

## Overview

The improvements focus on making hooks more reliable without adding new features:

1. **Timeout Protection** - Prevent hooks from hanging indefinitely
2. **Structured JSON I/O** - Better communication with Claude Code
3. **Comprehensive Error Handling** - Replace generic exceptions with specific handling
4. **Execution Logging** - Enable debugging and monitoring
5. **Input Validation** - Prevent security issues and crashes
6. **Retry Logic** - Handle transient failures gracefully
7. **Atomic Operations** - Prevent state corruption

## Implementation Details

### Base Hook Class (`src/quaestor/hooks/base.py`)

A new base class provides common functionality for all hooks:

```python
class BaseHook:
    """Base class for all Quaestor hooks."""
    
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.logger = logging.getLogger(f"quaestor.hooks.{hook_name}")
        self.start_time = time.time()
```

Key features:
- Automatic logging setup
- JSON input/output handling
- Timeout protection (55s to stay under Claude's 60s limit)
- Path validation and sanitization
- Structured error responses

### Timeout Protection

All subprocess calls now have timeout protection:

```python
# Before (could hang forever)
result = subprocess.run(cmd, capture_output=True, text=True)

# After (times out after specified seconds)
result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
```

Timeouts are configured based on operation type:
- Quick commands (git status, diff): 10-30 seconds
- Linting/formatting: 60-120 seconds  
- Test runs: 300 seconds (5 minutes)

### Error Handling Improvements

Replaced generic exception handling with specific handlers:

```python
# Before
try:
    # operation
except Exception:
    pass

# After
try:
    # operation
except subprocess.TimeoutExpired:
    return {"success": False, "message": "Operation timed out after X seconds"}
except FileNotFoundError:
    return {"success": False, "message": "Command not found. Install with: ..."}
except subprocess.CalledProcessError as e:
    return {"success": False, "message": f"Command failed: {e}"}
except Exception as e:
    return {"success": False, "message": f"Unexpected error: {str(e)[:200]}"}
```

### Retry Logic

Added retry decorator for transient failures:

```python
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def flaky_operation():
    # Operation that might fail temporarily
    pass
```

Git operations now retry automatically:
```python
for attempt in range(3):
    try:
        result = subprocess.run(["git", "log", ...], timeout=10)
        if result.returncode == 0:
            return process_result(result)
    except subprocess.TimeoutExpired:
        if attempt < 2:
            sleep(1)  # Wait before retry
            continue
```

### Atomic File Operations

State files are now written atomically to prevent corruption:

```python
def atomic_write(file_path: Path, content: str):
    """Write file atomically to prevent corruption."""
    temp_path = file_path.with_suffix('.tmp')
    try:
        # Write to temporary file
        temp_path.write_text(content, encoding='utf-8')
        
        # Atomic rename
        temp_path.replace(file_path)
        
    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise
```

### Input Validation

All hooks now validate inputs:

```python
def validate_path(self, path: str) -> Path:
    """Validate and sanitize file paths."""
    p = Path(path).resolve()
    
    # Check for path traversal attempts
    if ".." in path:
        raise ValidationError(f"Path traversal detected: {path}")
    
    # Ensure path is within project or home directory
    if not (p.is_relative_to(cwd) or p.is_relative_to(home)):
        raise ValidationError(f"Path outside allowed directories: {path}")
    
    return p
```

### Structured JSON Communication

Hooks can now return structured JSON responses:

```python
# Success response
{
    "message": "Research phase complete",
    "phase": "planning",
    "files_examined": 5,
    "next_action": "Create implementation plan",
    "_metadata": {
        "hook": "track-research",
        "execution_time": 1.23,
        "timestamp": "2025-01-16T10:30:00"
    }
}

# Error response (exit code 2 for blocking)
{
    "error": "Validation failed: Path outside project",
    "blocking": true,
    "_metadata": {...}
}
```

### Logging System

All hooks now log to:
- `~/.quaestor/logs/hooks_YYYYMMDD.log` - Daily rotating logs
- Console output for immediate feedback

Log entries include:
- Timestamp
- Hook name
- Log level
- Message
- Stack traces for errors

## Usage Examples

### Creating a New Hook with Base Class

```python
#!/usr/bin/env python3
from quaestor.hooks.base import BaseHook

class MyHook(BaseHook):
    def __init__(self):
        super().__init__("my-hook")
        
    def execute(self):
        # Read input from Claude
        input_data = self.input_data
        
        # Validate paths if needed
        if "filePath" in input_data:
            file_path = self.validate_path(input_data["filePath"])
        
        # Do work with timeout protection
        def do_work():
            # Your hook logic here
            return {"status": "complete"}
            
        result = self.run_with_timeout(do_work, timeout_seconds=30)
        
        # Return structured response
        self.output_success("Operation complete", data=result)

if __name__ == "__main__":
    hook = MyHook()
    hook.run()
```

### Updated Hook Template

See `src/quaestor/templates/hooks/track-research-v2.py` for a complete example of a refactored hook using all the new reliability features.

## Testing

Comprehensive tests are provided in `tests/test_hooks_reliability.py`:

- Timeout functionality
- Retry logic
- JSON I/O
- Path validation
- Atomic writes
- Error handling

Run tests with:
```bash
uv run pytest tests/test_hooks_reliability.py -v
```

## Benefits

1. **No More Hanging** - Hooks can't block Claude Code indefinitely
2. **Better Debugging** - Clear error messages and logs
3. **Graceful Degradation** - Retries handle temporary failures
4. **Data Integrity** - Atomic writes prevent corruption
5. **Security** - Input validation prevents malicious paths
6. **Performance Tracking** - Execution time in metadata

## Migration Guide

To update existing hooks:

1. Add timeout to subprocess calls
2. Replace generic exception handlers
3. Use atomic_write for state files
4. Consider inheriting from BaseHook for new hooks
5. Add retry logic for network/git operations

The improvements are backward compatible - existing hooks continue to work but won't benefit from the reliability features until updated.