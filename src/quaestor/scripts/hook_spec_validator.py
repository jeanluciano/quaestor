#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Specification Validation Hook for Quaestor.

Validates specification markdown files for basic format compliance.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Import from quaestor package for spec validation
from quaestor.specifications import SpecificationManager

# Configure logging
LOG_DIR = Path.home() / ".quaestor" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"hooks_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("quaestor.hooks.spec_validator")


def get_project_root() -> Path:
    """Find the project root directory (where .quaestor exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def validate_spec_file(file_path: str) -> dict:
    """Validate a specification markdown file.

    Args:
        file_path: Path to the specification markdown file

    Returns:
        Dict with validation results
    """
    try:
        spec_path = Path(file_path).resolve()
        spec_id = spec_path.stem

        # Check file exists
        if not spec_path.exists():
            return {
                "valid": False,
                "spec_id": spec_id,
                "error": f"File does not exist: {file_path}",
                "issues": [{"level": "error", "message": "File not found"}],
            }

        # Check file is readable
        try:
            _ = spec_path.read_text()
        except Exception as e:
            return {
                "valid": False,
                "spec_id": spec_id,
                "error": f"Cannot read file: {e}",
                "issues": [{"level": "error", "message": f"File not readable: {e}"}],
            }

        # Get project root and spec manager
        project_root = get_project_root()
        spec_manager = SpecificationManager(project_root)

        # Try to load the spec (SpecificationManager validates on load)
        try:
            spec = spec_manager.get_specification(spec_id)
            if spec is None:
                return {
                    "valid": False,
                    "spec_id": spec_id,
                    "error": "Specification not found in manager",
                    "issues": [{"level": "error", "message": "Spec not loadable"}],
                }

            # Basic validation passed
            issues = []

            # Check for empty title
            if not spec.title or not spec.title.strip():
                issues.append({"level": "warning", "message": "Specification has empty title"})

            # Check for acceptance criteria
            if not spec.acceptance_criteria:
                issues.append({"level": "warning", "message": "No acceptance criteria defined"})

            return {"valid": True, "spec_id": spec_id, "issues": issues}

        except Exception as e:
            logger.error(f"Failed to load spec {spec_id}: {e}")
            return {
                "valid": False,
                "spec_id": spec_id,
                "error": f"Validation failed: {e}",
                "issues": [{"level": "error", "message": str(e)}],
            }

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {
            "valid": False,
            "spec_id": "unknown",
            "error": str(e),
            "issues": [{"level": "error", "message": str(e)}],
        }


def main():
    """Main entry point for hook execution."""
    if len(sys.argv) < 2:
        output = {"error": "Usage: hook_spec_validator.py <spec_file>", "blocking": True}
        print(json.dumps(output))
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result = validate_spec_file(file_path)

        if result["valid"]:
            # Success
            message = f"✅ Specification '{result['spec_id']}' is valid"
            if result.get("issues"):
                warnings = [i for i in result["issues"] if i["level"] == "warning"]
                if warnings:
                    message += f" ({len(warnings)} warnings)"

            output = {"message": message, "blocking": False}
            print(json.dumps(output))
            sys.exit(0)
        else:
            # Validation failed
            errors = [i for i in result.get("issues", []) if i["level"] == "error"]
            warnings = [i for i in result.get("issues", []) if i["level"] == "warning"]

            error_msg = f"❌ Specification '{result['spec_id']}' validation failed"
            if result.get("error"):
                error_msg += f": {result['error']}"
            error_msg += "\n"

            for error in errors[:5]:
                error_msg += f"  • {error['message']}\n"

            if warnings:
                error_msg += "\nWarnings:\n"
                for warning in warnings[:3]:
                    error_msg += f"  ⚠️  {warning['message']}\n"

            output = {"error": error_msg, "blocking": True, "validation_errors": errors, "warnings": warnings}
            print(json.dumps(output))
            sys.exit(1)

    except Exception as e:
        logger.error(f"Hook execution failed: {e}", exc_info=True)
        output = {"error": f"Failed to validate spec: {str(e)}", "blocking": True}
        print(json.dumps(output))
        sys.exit(1)


if __name__ == "__main__":
    main()
