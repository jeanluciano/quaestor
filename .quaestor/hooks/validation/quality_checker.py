#!/usr/bin/env python3
"""Run quality checks based on project type."""

import sys
from pathlib import Path

# Import shared utilities
try:
    from ..shared_utils import get_project_root, run_quality_checks
except ImportError:
    # Fallback for when run as standalone script
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from shared_utils import get_project_root, run_quality_checks


if __name__ == "__main__":
    # Check if we should block on failure
    block_on_fail = "--block-on-fail" in sys.argv

    # Run quality checks using shared utility
    project_root = get_project_root()
    success = run_quality_checks(project_root, block_on_fail)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
