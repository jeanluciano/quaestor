#!/usr/bin/env python3
"""Specification validation hook for Quaestor.

This hook validates specification files to ensure they conform to the required
schema and contain valid values.
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class SpecType(str, Enum):
    """Valid specification types."""

    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"


class SpecStatus(str, Enum):
    """Valid specification statuses."""

    DRAFT = "draft"
    STAGED = "staged"
    ACTIVE = "active"
    COMPLETED = "completed"


class SpecPriority(str, Enum):
    """Valid specification priorities."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    """Result of specification validation."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    spec_id: str | None = None


class SpecificationValidator:
    """Validates Quaestor specification files."""

    REQUIRED_FIELDS = [
        "id",
        "title",
        "type",
        "status",
        "priority",
        "description",
        "rationale",
        "created_at",
        "updated_at",
    ]

    OPTIONAL_FIELDS = [
        "dependencies",
        "risks",
        "success_metrics",
        "contract",
        "acceptance_criteria",
        "test_scenarios",
        "metadata",
    ]

    def __init__(self):
        """Initialize the validator."""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_spec_file(self, file_path: Path) -> ValidationResult:
        """Validate a specification file.

        Args:
            file_path: Path to the specification YAML file

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        self.errors = []
        self.warnings = []

        # Check file exists
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return ValidationResult(False, self.errors, self.warnings)

        # Load and parse YAML
        try:
            with open(file_path) as f:
                spec_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return ValidationResult(False, self.errors, self.warnings)
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return ValidationResult(False, self.errors, self.warnings)

        if not isinstance(spec_data, dict):
            self.errors.append("Specification must be a YAML dictionary")
            return ValidationResult(False, self.errors, self.warnings)

        spec_id = spec_data.get("id", "unknown")

        # Validate required fields
        self._validate_required_fields(spec_data)

        # Validate field types and values
        self._validate_field_types(spec_data)

        # Validate enum values
        self._validate_enums(spec_data)

        # Validate timestamps
        self._validate_timestamps(spec_data)

        # Validate dependencies structure
        self._validate_dependencies(spec_data)

        # Validate contract structure
        self._validate_contract(spec_data)

        # Validate test scenarios
        self._validate_test_scenarios(spec_data)

        # Check for placeholder values
        self._check_placeholders(spec_data)

        # Validate spec ID format
        self._validate_spec_id(spec_data)

        return ValidationResult(
            valid=len(self.errors) == 0, errors=self.errors, warnings=self.warnings, spec_id=spec_id
        )

    def _validate_required_fields(self, spec: dict[str, Any]) -> None:
        """Check that all required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in spec:
                self.errors.append(f"Required field missing: {field}")
            elif spec[field] is None:
                self.errors.append(f"Required field is null: {field}")
            elif isinstance(spec[field], str) and not spec[field].strip():
                self.errors.append(f"Required field is empty: {field}")

    def _validate_field_types(self, spec: dict[str, Any]) -> None:
        """Validate that fields have the correct types."""
        type_expectations = {
            "id": str,
            "title": str,
            "type": str,
            "status": str,
            "priority": str,
            "description": str,
            "rationale": str,
            "created_at": str,
            "updated_at": str,
            "dependencies": dict,
            "risks": list,
            "success_metrics": list,
            "acceptance_criteria": list,
            "test_scenarios": list,
            "metadata": dict,
        }

        for field, expected_type in type_expectations.items():
            if field in spec and spec[field] is not None:
                if not isinstance(spec[field], expected_type):
                    self.errors.append(
                        f"Field '{field}' must be {expected_type.__name__}, got {type(spec[field]).__name__}"
                    )

    def _validate_enums(self, spec: dict[str, Any]) -> None:
        """Validate enum fields have valid values."""
        # Validate type
        if "type" in spec:
            try:
                SpecType(spec["type"])
            except ValueError:
                self.errors.append(
                    f"Invalid type: '{spec['type']}'. Must be one of: {', '.join([t.value for t in SpecType])}"
                )

        # Validate status
        if "status" in spec:
            try:
                SpecStatus(spec["status"])
            except ValueError:
                self.errors.append(
                    f"Invalid status: '{spec['status']}'. Must be one of: {', '.join([s.value for s in SpecStatus])}"
                )

        # Validate priority
        if "priority" in spec:
            try:
                SpecPriority(spec["priority"])
            except ValueError:
                self.errors.append(
                    f"Invalid priority: '{spec['priority']}'. "
                    f"Must be one of: {', '.join([p.value for p in SpecPriority])}"
                )

    def _validate_timestamps(self, spec: dict[str, Any]) -> None:
        """Validate timestamp fields are valid ISO format strings."""
        timestamp_fields = ["created_at", "updated_at"]

        for field in timestamp_fields:
            if field in spec and spec[field]:
                try:
                    # Try to parse as ISO format
                    datetime.fromisoformat(spec[field].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    self.errors.append(
                        f"Invalid timestamp format for '{field}': {spec[field]}. "
                        f"Must be ISO format (e.g., '2024-01-10T10:30:00')"
                    )

    def _validate_spec_id(self, spec: dict[str, Any]) -> None:
        """Validate spec ID format."""
        if "id" in spec and spec["id"]:
            spec_id = spec["id"]
            # Check format: should be like spec-type-NNN
            if not isinstance(spec_id, str):
                self.errors.append(f"Spec ID must be a string, got {type(spec_id).__name__}")
                return

            # Check for invalid characters
            if not all(c.isalnum() or c == "-" for c in spec_id):
                self.errors.append(f"Spec ID contains invalid characters: {spec_id}")

            # Check format pattern
            parts = spec_id.split("-")
            if len(parts) < 3:
                self.warnings.append(f"Spec ID '{spec_id}' doesn't follow recommended format 'spec-type-NNN'")
            elif parts[0] != "spec":
                self.warnings.append(f"Spec ID '{spec_id}' should start with 'spec-'")

    def _check_placeholders(self, spec: dict[str, Any]) -> None:
        """Check for placeholder values that shouldn't be in final specs."""

        def check_value(value: Any, path: str = "") -> None:
            if isinstance(value, str):
                # Skip type hints with square brackets (like Optional[Any], List[str])
                import re

                type_hint_pattern = r"^(Optional|List|Dict|Set|Tuple|Union|Callable)\[.*\]$"
                if re.match(type_hint_pattern, value):
                    return  # This is a valid type hint, not a placeholder

                # Check for placeholder patterns (but not type hints)
                # Look for template-style placeholders like [placeholder] or [TODO]
                placeholder_pattern = r"\[((?!Optional|List|Dict|Set|Tuple|Union|Callable)[^\]]+)\]"
                if re.search(placeholder_pattern, value):
                    # Check if it's a template placeholder
                    if any(word in value for word in ["type", "NNN", "TODO", "FIXME", "placeholder"]):
                        self.errors.append(f"Placeholder found in {path}: '{value}'")

                # Check for template variables
                if any(pattern in value for pattern in ["{{", "}}", "${", "TODO", "FIXME"]):
                    self.errors.append(f"Template variable found in {path}: '{value}'")

                # Check for function calls
                if any(pattern in value for pattern in ["datetime.now()", "Date()", "new Date"]):
                    self.errors.append(f"Function call found in {path}: '{value}'. Use actual values.")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    check_value(item, f"{path}[{i}]" if path else f"[{i}]")

        check_value(spec)

    def _validate_dependencies(self, spec: dict[str, Any]) -> None:
        """Validate dependencies structure."""
        if "dependencies" not in spec:
            return

        deps = spec["dependencies"]
        if not isinstance(deps, dict):
            return  # Type error already caught

        valid_keys = ["requires", "blocks", "related"]
        for key in deps:
            if key not in valid_keys:
                self.warnings.append(f"Unknown dependency type '{key}'. Expected one of: {', '.join(valid_keys)}")

            if key in deps and deps[key] is not None:
                if not isinstance(deps[key], list):
                    self.errors.append(f"Dependencies.{key} must be a list, got {type(deps[key]).__name__}")
                else:
                    # Check each dependency is a string
                    for i, dep in enumerate(deps[key]):
                        if not isinstance(dep, str):
                            self.errors.append(f"Dependencies.{key}[{i}] must be a string, got {type(dep).__name__}")

    def _validate_contract(self, spec: dict[str, Any]) -> None:
        """Validate contract structure."""
        if "contract" not in spec:
            return

        contract = spec["contract"]
        if not isinstance(contract, dict):
            return  # Type error already caught

        # Check contract sections
        valid_sections = ["inputs", "outputs", "behavior", "behaviors", "constraints", "error_handling", "errors"]

        for key in contract:
            if key not in valid_sections:
                self.warnings.append(f"Unknown contract section '{key}'. Expected one of: {', '.join(valid_sections)}")

        # Validate inputs/outputs structure
        for field in ["inputs", "outputs"]:
            if field in contract and contract[field]:
                if isinstance(contract[field], list):
                    for i, item in enumerate(contract[field]):
                        if not isinstance(item, dict):
                            self.errors.append(f"Contract.{field}[{i}] must be a dictionary")
                        elif "name" not in item:
                            self.errors.append(f"Contract.{field}[{i}] missing 'name' field")
                elif isinstance(contract[field], dict):
                    # Alternative format: dict of field definitions
                    pass
                else:
                    self.errors.append(f"Contract.{field} must be a list or dictionary")

    def _validate_test_scenarios(self, spec: dict[str, Any]) -> None:
        """Validate test scenarios structure."""
        if "test_scenarios" not in spec:
            return

        scenarios = spec["test_scenarios"]
        if not isinstance(scenarios, list):
            return  # Type error already caught

        for i, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                self.errors.append(f"Test scenario {i} must be a dictionary")
                continue

            # Check required fields
            required = ["name", "given", "when", "then"]
            for field in required:
                if field not in scenario:
                    self.errors.append(f"Test scenario {i} missing required field '{field}'")


def validate_specification(file_path: str) -> tuple[bool, str]:
    """Validate a specification file and return results.

    Args:
        file_path: Path to the specification file

    Returns:
        Tuple of (is_valid, message)
    """
    validator = SpecificationValidator()
    result = validator.validate_spec_file(Path(file_path))

    if result.valid:
        message = f"✅ Specification '{result.spec_id}' is valid!"
    else:
        message = "❌ Specification validation failed:\n"
        for error in result.errors:
            message += f"  ERROR: {error}\n"

    if result.warnings:
        message += "\n⚠️  Warnings:\n"
        for warning in result.warnings:
            message += f"  WARNING: {warning}\n"

    return result.valid, message


def main():
    """Main entry point for the validation hook."""
    if len(sys.argv) < 2:
        print("Usage: python spec_validator.py <spec_file.yaml>")
        sys.exit(1)

    file_path = sys.argv[1]
    is_valid, message = validate_specification(file_path)

    print(message)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
