"""Override system for justified rule bypasses."""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class Override:
    """Record of a rule override."""

    id: str
    rule_id: str
    timestamp: float
    justification: str
    context: dict[str, Any]
    expires_at: float | None = None
    approved_by: str | None = None

    @property
    def is_expired(self) -> bool:
        """Check if this override has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def is_active(self) -> bool:
        """Check if this override is currently active."""
        return not self.is_expired


class OverrideSystem:
    """Manage rule override requests and approvals."""

    def __init__(self, storage_path: Path | None = None):
        self.storage_path = storage_path or Path(".quaestor/.override_history.json")
        self.overrides: dict[str, Override] = {}
        self._load_overrides()

    def _load_overrides(self) -> None:
        """Load overrides from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    data = json.load(f)
                    for override_data in data:
                        override = Override(**override_data)
                        self.overrides[override.id] = override
            except Exception:
                self.overrides = {}

    def _save_overrides(self) -> None:
        """Save overrides to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to serializable format
            data = []
            for override in self.overrides.values():
                override_dict = {
                    "id": override.id,
                    "rule_id": override.rule_id,
                    "timestamp": override.timestamp,
                    "justification": override.justification,
                    "context": override.context,
                    "expires_at": override.expires_at,
                    "approved_by": override.approved_by,
                }
                data.append(override_dict)

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Fail silently for now

    def request_override(
        self, rule_id: str, justification: str, context: dict[str, Any], duration_hours: float | None = None
    ) -> Override:
        """Request an override for a rule."""
        override_id = str(uuid4())
        expires_at = None

        if duration_hours:
            expires_at = time.time() + (duration_hours * 3600)

        override = Override(
            id=override_id,
            rule_id=rule_id,
            timestamp=time.time(),
            justification=justification,
            context=context,
            expires_at=expires_at,
        )

        self.overrides[override_id] = override
        self._save_overrides()

        return override

    def approve_override(self, override_id: str, approver: str = "system") -> bool:
        """Approve an override request."""
        if override_id in self.overrides:
            self.overrides[override_id].approved_by = approver
            self._save_overrides()
            return True
        return False

    def check_override(self, rule_id: str, context: dict[str, Any]) -> Override | None:
        """Check if there's an active override for a rule in the given context."""
        # Clean up expired overrides
        self._cleanup_expired()

        # Look for matching overrides
        for override in self.overrides.values():
            if override.rule_id == rule_id and override.is_active:
                # Check if context matches (simple implementation)
                if self._context_matches(override.context, context):
                    return override

        return None

    def _context_matches(self, override_context: dict[str, Any], current_context: dict[str, Any]) -> bool:
        """Check if contexts match for override applicability."""
        # Simple implementation - check key fields
        key_fields = ["user_intent", "workflow_phase", "file_path"]

        for field in key_fields:
            if field in override_context and field in current_context:
                if override_context[field] != current_context[field]:
                    return False

        return True

    def _cleanup_expired(self) -> None:
        """Remove expired overrides."""
        expired_ids = [override_id for override_id, override in self.overrides.items() if override.is_expired]

        for override_id in expired_ids:
            del self.overrides[override_id]

        if expired_ids:
            self._save_overrides()

    def get_override_stats(self) -> dict[str, Any]:
        """Get statistics about overrides."""
        self._cleanup_expired()

        stats = {
            "total_overrides": len(self.overrides),
            "active_overrides": sum(1 for o in self.overrides.values() if o.is_active),
            "by_rule": {},
            "recent_overrides": [],
        }

        # Count by rule
        for override in self.overrides.values():
            rule_id = override.rule_id
            if rule_id not in stats["by_rule"]:
                stats["by_rule"][rule_id] = 0
            stats["by_rule"][rule_id] += 1

        # Get recent overrides (last 24 hours)
        cutoff_time = time.time() - 86400
        recent = [
            {"rule_id": o.rule_id, "justification": o.justification, "timestamp": o.timestamp}
            for o in self.overrides.values()
            if o.timestamp > cutoff_time
        ]
        stats["recent_overrides"] = sorted(recent, key=lambda x: x["timestamp"], reverse=True)[:10]

        return stats
