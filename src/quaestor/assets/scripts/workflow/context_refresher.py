#!/usr/bin/env python3
"""Refresh context for long conversations."""

import sys
from pathlib import Path


def refresh_context():
    """Remind about important files when conversation gets long."""
    important_files = [".quaestor/CRITICAL_RULES.md", ".quaestor/MEMORY.md", ".quaestor/ARCHITECTURE.md"]

    print("\n📚 CONTEXT REFRESH - Re-read these important files:")

    for file_path in important_files:
        if Path(file_path).exists():
            print(f"  • {file_path}")

    print("\n💡 Remember: Research → Plan → Implement workflow")
    return True


if __name__ == "__main__":
    success = refresh_context()
    sys.exit(0 if success else 1)
