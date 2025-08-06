"""Specification schema validation and enforcement."""

from typing import Any


class SpecificationSchema:
    """Schema definition and validation for specifications."""

    # Define the expected schema structure
    SPEC_SCHEMA = {
        "type": "object",
        "required": ["id", "title", "type", "status", "priority", "description", "rationale"],
        "properties": {
            "id": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9-_]*$",
                "maxLength": 100,
                "description": "Unique specification identifier",
            },
            "title": {"type": "string", "minLength": 3, "maxLength": 200, "description": "Human-readable title"},
            "type": {
                "type": "string",
                "enum": ["feature", "bugfix", "refactor", "documentation", "performance", "security", "testing"],
                "description": "Specification type",
            },
            "status": {
                "type": "string",
                "enum": ["draft", "staged", "active", "completed"],
                "description": "Current status",
            },
            "priority": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low"],
                "description": "Priority level",
            },
            "description": {"type": "string", "minLength": 10, "description": "Detailed description"},
            "rationale": {"type": "string", "minLength": 10, "description": "Why this spec is needed"},
            "use_cases": {"type": "array", "items": {"type": "string"}, "description": "List of use cases"},
            "contract": {
                "type": "object",
                "properties": {
                    "inputs": {"type": "object"},
                    "outputs": {"type": "object"},
                    "behavior": {"type": "array", "items": {"type": "string"}},
                    "constraints": {"type": "array", "items": {"type": "string"}},
                    "error_handling": {"type": "object"},
                },
            },
            "acceptance_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of acceptance criteria",
            },
            "test_scenarios": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "given", "when", "then"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "given": {"type": "string"},
                        "when": {"type": "string"},
                        "then": {"type": "string"},
                        "examples": {"type": "array"},
                    },
                },
            },
            "dependencies": {
                "type": "object",
                "properties": {
                    "requires": {"type": "array", "items": {"type": "string"}},
                    "blocks": {"type": "array", "items": {"type": "string"}},
                    "related": {"type": "array", "items": {"type": "string"}},
                },
            },
            "branch": {"type": ["string", "null"], "description": "Associated git branch"},
            "created_at": {"type": "string", "description": "ISO datetime when created"},
            "updated_at": {"type": "string", "description": "ISO datetime when last updated"},
            "metadata": {"type": "object", "description": "Additional metadata"},
        },
    }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate specification data against schema.

        Args:
            data: Specification data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required = cls.SPEC_SCHEMA.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate field types and constraints
        properties = cls.SPEC_SCHEMA.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_errors = cls._validate_field(field, value, properties[field])
                errors.extend(field_errors)

        return len(errors) == 0, errors

    @classmethod
    def _validate_field(cls, field_name: str, value: Any, schema: dict[str, Any]) -> list[str]:
        """Validate a single field against its schema.

        Args:
            field_name: Name of the field
            value: Field value
            schema: Field schema definition

        Returns:
            List of validation errors
        """
        errors = []

        # Type validation
        expected_type = schema.get("type")
        if expected_type:
            if not cls._check_type(value, expected_type):
                errors.append(f"Field '{field_name}' should be {expected_type}, got {type(value).__name__}")
                return errors  # No point checking further constraints

        # String constraints
        if expected_type == "string" and isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                errors.append(f"Field '{field_name}' too short (min {schema['minLength']} characters)")
            if "maxLength" in schema and len(value) > schema["maxLength"]:
                errors.append(f"Field '{field_name}' too long (max {schema['maxLength']} characters)")
            if "pattern" in schema:
                import re

                if not re.match(schema["pattern"], value):
                    errors.append(f"Field '{field_name}' doesn't match required pattern")

        # Enum validation
        if "enum" in schema:
            if value not in schema["enum"]:
                errors.append(f"Field '{field_name}' must be one of: {', '.join(schema['enum'])}")

        # Array validation
        if expected_type == "array" and isinstance(value, list):
            item_schema = schema.get("items", {})
            for i, item in enumerate(value):
                if "type" in item_schema:
                    if not cls._check_type(item, item_schema["type"]):
                        errors.append(f"Field '{field_name}[{i}]' has invalid type")

        return errors

    @classmethod
    def _check_type(cls, value: Any, expected_type: str | list) -> bool:
        """Check if value matches expected type(s).

        Args:
            value: Value to check
            expected_type: Expected type or list of types

        Returns:
            True if type matches
        """
        if isinstance(expected_type, list):
            return any(cls._check_type(value, t) for t in expected_type)

        type_map = {
            "string": str,
            "object": dict,
            "array": list,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None),
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)

        return False

    @classmethod
    def sanitize(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize specification data.

        Args:
            data: Raw specification data

        Returns:
            Sanitized data
        """
        sanitized = data.copy()

        # Sanitize string fields
        string_fields = ["id", "title", "description", "rationale"]
        for field in string_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                # Remove dangerous characters
                sanitized[field] = cls._sanitize_string(sanitized[field])

        # Sanitize arrays of strings
        array_fields = ["use_cases", "acceptance_criteria"]
        for field in array_fields:
            if field in sanitized and isinstance(sanitized[field], list):
                sanitized[field] = [
                    cls._sanitize_string(item) if isinstance(item, str) else item for item in sanitized[field]
                ]

        return sanitized

    @classmethod
    def _sanitize_string(cls, value: str) -> str:
        """Sanitize a string value.

        Args:
            value: String to sanitize

        Returns:
            Sanitized string
        """
        # Remove control characters
        import re

        value = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", value)

        # Remove potential script injection
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"\$\(",
            r"`.*`",
        ]

        for pattern in dangerous_patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)

        return value.strip()

    @classmethod
    def provide_template(cls) -> dict[str, Any]:
        """Provide a template for creating new specifications.

        Returns:
            Template specification data
        """
        from datetime import datetime

        return {
            "id": "spec-type-001",
            "title": "Brief descriptive title",
            "type": "feature",  # One of: feature, bugfix, refactor, etc.
            "status": "draft",
            "priority": "medium",
            "description": "Detailed description of what needs to be built",
            "rationale": "Why this specification is needed",
            "use_cases": [],
            "contract": {"inputs": {}, "outputs": {}, "behavior": [], "constraints": [], "error_handling": {}},
            "acceptance_criteria": [],
            "test_scenarios": [],
            "dependencies": {"requires": [], "blocks": [], "related": []},
            "branch": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {},
        }
