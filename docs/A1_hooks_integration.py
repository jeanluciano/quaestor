"""
Example A1 hook integration for Quaestor.

This shows how A1 would intercept Claude Code hooks and process them
for automatic context management.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

# A1 would send events to its processing engine
def send_to_a1(event_data: Dict[str, Any]):
    """Send event to A1 processing engine via IPC/file queue."""
    # In real implementation, this would use proper IPC
    event_file = Path(".quaestor/a1/events/pending") / f"{event_data['timestamp']}.json"
    event_file.parent.mkdir(parents=True, exist_ok=True)
    event_file.write_text(json.dumps(event_data, indent=2))


def pre_tool_use_hook(tool_name: str, tool_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Pre-tool use hook that sends events to A1."""
    
    # Build event for A1
    event = {
        "type": "pre_tool_use",
        "tool": tool_name,
        "data": tool_data,
        "timestamp": datetime.now().isoformat(),
        "session_id": kwargs.get("session_id", "unknown"),
        "context": {
            "recent_files": kwargs.get("recent_files", []),
            "active_rules": kwargs.get("active_rules", [])
        }
    }
    
    # Send to A1 for processing
    send_to_a1(event)
    
    # A1 might return rule adaptations (in real implementation)
    # For now, always allow
    return {"allow": True}


def post_tool_use_hook(tool_name: str, tool_data: Dict[str, Any], result: Any, **kwargs) -> None:
    """Post-tool use hook that sends completion events to A1."""
    
    # Build completion event
    event = {
        "type": "post_tool_use", 
        "tool": tool_name,
        "data": tool_data,
        "result": {
            "success": result.get("success", True) if isinstance(result, dict) else True,
            "duration": result.get("duration", 0) if isinstance(result, dict) else 0
        },
        "timestamp": datetime.now().isoformat(),
        "session_id": kwargs.get("session_id", "unknown")
    }
    
    # Special handling for different tools
    if tool_name == "Edit":
        event["data"]["changes"] = len(result.get("diff", "").split("\n")) if isinstance(result, dict) else 0
    elif tool_name == "Read":
        event["data"]["lines"] = len(result.get("content", "").split("\n")) if isinstance(result, dict) else 0
    
    send_to_a1(event)


def stop_hook(**kwargs) -> None:
    """Stop hook when Claude finishes - good time for A1 to update patterns."""
    
    event = {
        "type": "stop",
        "timestamp": datetime.now().isoformat(),
        "session_id": kwargs.get("session_id", "unknown"),
        "summary": {
            "total_events": kwargs.get("total_events", 0),
            "duration": kwargs.get("duration", 0)
        }
    }
    
    send_to_a1(event)


# Hook registration for Quaestor
HOOKS = {
    "pre_tool_use": pre_tool_use_hook,
    "post_tool_use": post_tool_use_hook,
    "stop": stop_hook
}