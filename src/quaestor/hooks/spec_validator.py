"""Specification Validation Hook for Quaestor."""

import json
import sys
from pathlib import Path

from quaestor.cli.spec import get_spec_manager, validate_single_spec


def validate_spec_hook(file_path: str) -> dict:
    """
    Validate a specification file.

    Args:
        file_path (str): Path to the specification markdown file

    Returns:
        Dict with validation results
    """
    # Extract spec ID from filename
    spec_id = Path(file_path).stem

    # Get spec manager
    spec_mgr = get_spec_manager()
    if not spec_mgr:
        return {"valid": False, "error": "Could not initialize specification manager"}

    # Validate specification
    result = validate_single_spec(spec_mgr, spec_id)

    return {"valid": result.valid, "spec_id": spec_id, "issues": result.issues}


def main():
    """Main entry point for hook execution."""
    if len(sys.argv) < 2:
        output = {"error": "Usage: python -m quaestor.hooks.spec_validator <spec_file>", "blocking": True}
        print(json.dumps(output))
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result = validate_spec_hook(file_path)

        if result["valid"]:
            # Success
            output = {"message": f"✅ Specification '{result['spec_id']}' is valid", "blocking": False}
            print(json.dumps(output))
            sys.exit(0)
        else:
            # Validation failed
            errors = [i for i in result["issues"] if i["level"] == "error"]
            warnings = [i for i in result["issues"] if i["level"] == "warning"]

            error_msg = f"❌ Specification '{result['spec_id']}' validation failed:\n"
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
        output = {"error": f"Failed to validate spec: {str(e)}", "blocking": True}
        print(json.dumps(output))
        sys.exit(1)


if __name__ == "__main__":
    main()
