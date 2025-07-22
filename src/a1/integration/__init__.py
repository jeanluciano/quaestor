"""Integration layer between A1 and Quaestor."""

from .quaestor_bridge import QuaestorRuleBridge, wrap_quaestor_hook

__all__ = [
    "QuaestorRuleBridge",
    "wrap_quaestor_hook",
]
