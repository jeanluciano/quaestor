"""Concrete rule implementations for the enforcement system."""

from .enforcement_history import EnforcementHistory
from .enforcement_levels import EnforcementLevel
from .rule_enforcer import EnforcementContext, RuleEnforcer


class ResearchBeforeImplementationRule(RuleEnforcer):
    """Enforce research phase before implementation."""

    def __init__(self, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="research_before_impl",
            rule_name="Research Before Implementation",
            base_level=EnforcementLevel.JUSTIFY,
            history=history,
        )

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check if research was done before implementation."""
        if context.workflow_phase != "implementing":
            return True, "Not in implementation phase"

        # Check if research was done (simplified check)
        files_examined = context.metadata.get("files_examined", 0)
        if files_examined < 3:
            return False, f"Only {files_examined} files examined. Need at least 3 files."

        return True, "Sufficient research completed"

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get suggestions for completing research."""
        return [
            "Use Grep to search for relevant patterns",
            "Read key implementation files with Read tool",
            "Check existing tests for usage examples",
            "Review related documentation",
        ]


class ComplexityLimitRule(RuleEnforcer):
    """Enforce complexity limits on code."""

    def __init__(self, max_lines: int = 50, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="complexity_limit",
            rule_name="Code Complexity Limit",
            base_level=EnforcementLevel.WARN,
            history=history,
        )
        self.max_lines = max_lines

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check if code complexity is within limits."""
        if context.tool_name not in ["Write", "Edit", "MultiEdit"]:
            return True, "Not a code modification"

        # Check code content
        content = context.metadata.get("content", "")
        lines = content.split("\n")

        # Check for large functions
        in_function = False
        function_lines = 0
        function_name = ""

        for line in lines:
            if line.strip().startswith("def ") or line.strip().startswith("async def "):
                if in_function and function_lines > self.max_lines:
                    return False, f"Function '{function_name}' has {function_lines} lines (max: {self.max_lines})"
                in_function = True
                function_lines = 0
                function_name = line.strip().split("(")[0].replace("def ", "").replace("async ", "")
            elif in_function:
                function_lines += 1

        # Check last function
        if in_function and function_lines > self.max_lines:
            return False, f"Function '{function_name}' has {function_lines} lines (max: {self.max_lines})"

        return True, "Code complexity within limits"

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get suggestions for reducing complexity."""
        return [
            "Break large functions into smaller, focused functions",
            "Extract complex logic into separate helper functions",
            "Consider using composition over deep nesting",
            "Apply SOLID principles to reduce complexity",
        ]


class TestCoverageRule(RuleEnforcer):
    """Enforce test coverage for new code."""

    def __init__(self, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="test_coverage",
            rule_name="Test Coverage Required",
            base_level=EnforcementLevel.WARN,
            history=history,
        )

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check if tests are being written for new code."""
        if context.tool_name not in ["Write", "Edit", "MultiEdit"]:
            return True, "Not a code modification"

        # Check if this is a test file
        file_path = context.file_path or ""
        if "test" in file_path.lower():
            return True, "This is a test file"

        # Check if tests were mentioned in intent
        if "test" in context.user_intent.lower():
            return True, "User intent includes testing"

        # Check if this is a significant code addition
        content = context.metadata.get("content", "")
        if content.count("\n") > 20:  # More than 20 lines
            # Check if there's a plan to write tests
            has_test_plan = context.metadata.get("test_plan", False)
            if not has_test_plan:
                return False, "Significant code addition without test plan"

        return True, "Test coverage check passed"

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get suggestions for test coverage."""
        return [
            "Write unit tests for new functions",
            "Add integration tests for new features",
            "Update existing tests affected by changes",
            "Consider test-driven development (TDD) approach",
        ]


class DocumentationRule(RuleEnforcer):
    """Enforce documentation standards."""

    def __init__(self, history: EnforcementHistory | None = None):
        super().__init__(
            rule_id="documentation",
            rule_name="Documentation Standards",
            base_level=EnforcementLevel.INFORM,
            history=history,
        )

    def check_rule(self, context: EnforcementContext) -> tuple[bool, str]:
        """Check if documentation standards are met."""
        if context.tool_name not in ["Write", "Edit", "MultiEdit"]:
            return True, "Not a code modification"

        content = context.metadata.get("content", "")

        # Check for docstrings in Python code
        if context.file_path and context.file_path.endswith(".py"):
            # Simple check for function docstrings
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("def ") or line.strip().startswith("async def "):
                    # Check if next non-empty line is a docstring
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line:
                            if not (next_line.startswith('"""') or next_line.startswith("'''")):
                                func_name = line.strip().split("(")[0].replace("def ", "").replace("async ", "")
                                return False, f"Function '{func_name}' missing docstring"
                            break

        return True, "Documentation standards met"

    def get_suggestions(self, context: EnforcementContext) -> list[str]:
        """Get suggestions for documentation."""
        return [
            "Add docstrings to all public functions",
            "Include parameter descriptions in docstrings",
            "Document return values and exceptions",
            "Update README if adding new features",
        ]
