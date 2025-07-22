#!/usr/bin/env python3
"""Run quality checks based on project type."""

import sys
from pathlib import Path

# Add parent directory to path for imports
hook_parent = Path(__file__).parent.parent
if str(hook_parent) not in sys.path:
    sys.path.insert(0, str(hook_parent))

# Import shared utilities
from shared_utils import get_project_root, run_quality_checks  # noqa: E402

if __name__ == "__main__":
    # Check if we should block on failure
    block_on_fail = "--block-on-fail" in sys.argv

    # Run quality checks using shared utility
    project_root = get_project_root()
    success = run_quality_checks(project_root, block_on_fail)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
