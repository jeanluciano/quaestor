"""Test code analyzer for extracting test structure and dependencies.

This module analyzes test files to understand what they test and how.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path

from a1.core.event_bus import EventBus

from ..ast_parser import PythonASTParser
from ..events import SystemEvent
from ..symbol_table import SymbolTable


@dataclass
class TestInfo:
    """Information about a test function or method."""

    name: str
    qualified_name: str
    line_start: int
    line_end: int
    test_class: str | None = None
    docstring: str | None = None
    fixtures: list[str] = field(default_factory=list)  # pytest fixtures
    marks: list[str] = field(default_factory=list)  # pytest marks
    calls: list[str] = field(default_factory=list)  # Functions it calls
    imports: list[str] = field(default_factory=list)  # What it imports
    assertions: int = 0  # Number of assertions


@dataclass
class TestClass:
    """Information about a test class."""

    name: str
    line_start: int
    line_end: int
    base_classes: list[str]
    test_methods: list[TestInfo]
    setup_methods: list[str] = field(default_factory=list)
    teardown_methods: list[str] = field(default_factory=list)
    docstring: str | None = None


@dataclass
class TestModule:
    """Complete analysis of a test module."""

    path: Path
    module_name: str
    imports: list[str]
    test_functions: list[TestInfo]
    test_classes: list[TestClass]
    fixtures: list[str] = field(default_factory=list)  # Module-level fixtures
    setup_functions: list[str] = field(default_factory=list)
    teardown_functions: list[str] = field(default_factory=list)


class TestAnalyzer:
    """Analyzes test code to extract structure and dependencies."""

    def __init__(self, symbol_table: SymbolTable | None = None, event_bus: EventBus | None = None):
        """Initialize the test analyzer.

        Args:
            symbol_table: Optional symbol table for resolving references
            event_bus: Optional event bus for analysis events
        """
        self.parser = PythonASTParser(event_bus)
        self.symbol_table = symbol_table
        self.event_bus = event_bus

    def analyze_test_file(self, file_path: Path) -> TestModule:
        """Analyze a test file to extract test information.

        Args:
            file_path: Path to the test file

        Returns:
            TestModule with analysis results
        """
        # Parse the file
        module_info = self.parser.parse_file(file_path)

        # Create test module
        test_module = TestModule(
            path=file_path,
            module_name=self._path_to_module(file_path),
            imports=self._extract_imports(module_info.imports),
            test_functions=[],
            test_classes=[],
        )

        # Analyze module-level functions
        for func in module_info.functions:
            if self._is_test_function(func.name):
                test_info = self._analyze_test_function(func, module_info)
                test_module.test_functions.append(test_info)
            elif self._is_fixture_function(func.name, func.decorators):
                test_module.fixtures.append(func.name)
            elif self._is_setup_function(func.name):
                test_module.setup_functions.append(func.name)
            elif self._is_teardown_function(func.name):
                test_module.teardown_functions.append(func.name)

        # Analyze test classes
        for cls in module_info.classes:
            if self._is_test_class(cls.name):
                test_class = self._analyze_test_class(cls, module_info)
                test_module.test_classes.append(test_class)

        # Emit analysis event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="test_file_analyzed",
                    data={
                        "path": str(file_path),
                        "test_functions": len(test_module.test_functions),
                        "test_classes": len(test_module.test_classes),
                        "total_tests": self._count_total_tests(test_module),
                    },
                )
            )

        return test_module

    def extract_test_targets(self, test_module: TestModule) -> set[str]:
        """Extract what source code a test module targets.

        Args:
            test_module: Analyzed test module

        Returns:
            Set of target module/function names
        """
        targets = set()

        # Add imported modules (excluding test helpers)
        for import_name in test_module.imports:
            if not self._is_test_import(import_name):
                targets.add(import_name)

        # Add called functions from all tests
        for test in test_module.test_functions:
            for call in test.calls:
                if not self._is_test_helper(call):
                    targets.add(call)

        for test_class in test_module.test_classes:
            for test_method in test_class.test_methods:
                for call in test_method.calls:
                    if not self._is_test_helper(call):
                        targets.add(call)

        return targets

    def _analyze_test_function(self, func_info, module_info) -> TestInfo:
        """Analyze a test function."""
        test_info = TestInfo(
            name=func_info.name,
            qualified_name=f"{module_info.path.stem}.{func_info.name}",
            line_start=func_info.line_start,
            line_end=func_info.line_end,
            docstring=func_info.docstring,
        )

        # Extract fixtures from arguments
        test_info.fixtures = [arg for arg in func_info.arguments if arg not in ["self", "cls"]]

        # Extract marks from decorators
        test_info.marks = self._extract_pytest_marks(func_info.decorators)

        # Analyze function body if AST is available
        if module_info.ast_tree:
            self._analyze_function_body(func_info.name, module_info.ast_tree, test_info)

        return test_info

    def _analyze_test_class(self, class_info, module_info) -> TestClass:
        """Analyze a test class."""
        test_class = TestClass(
            name=class_info.name,
            line_start=class_info.line_start,
            line_end=class_info.line_end,
            base_classes=class_info.bases,
            test_methods=[],
            docstring=class_info.docstring,
        )

        # Analyze methods
        for method in class_info.methods:
            if self._is_test_method(method.name):
                test_info = self._analyze_test_function(method, module_info)
                test_info.test_class = class_info.name
                test_info.qualified_name = f"{module_info.path.stem}.{class_info.name}.{method.name}"
                test_class.test_methods.append(test_info)
            elif self._is_setup_method(method.name):
                test_class.setup_methods.append(method.name)
            elif self._is_teardown_method(method.name):
                test_class.teardown_methods.append(method.name)

        return test_class

    def _analyze_function_body(self, func_name: str, tree: ast.AST, test_info: TestInfo) -> None:
        """Analyze the body of a test function."""

        class TestBodyAnalyzer(ast.NodeVisitor):
            def __init__(self, test_info: TestInfo):
                self.test_info = test_info
                self.in_target_function = False

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                if node.name == func_name:
                    self.in_target_function = True
                    self.generic_visit(node)
                    self.in_target_function = False
                elif not self.in_target_function:
                    self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self.visit_FunctionDef(node)

            def visit_Call(self, node: ast.Call) -> None:
                if not self.in_target_function:
                    self.generic_visit(node)
                    return

                # Track function calls
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                    if call_name.startswith("assert"):
                        self.test_info.assertions += 1
                    else:
                        self.test_info.calls.append(call_name)
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    if isinstance(node.func.value, ast.Name):
                        call_name = f"{node.func.value.id}.{node.func.attr}"
                        self.test_info.calls.append(call_name)

                self.generic_visit(node)

            def visit_Assert(self, node: ast.Assert) -> None:
                if self.in_target_function:
                    self.test_info.assertions += 1
                self.generic_visit(node)

        analyzer = TestBodyAnalyzer(test_info)
        analyzer.visit(tree)

    def _is_test_function(self, name: str) -> bool:
        """Check if a function name indicates a test."""
        return name.startswith("test_") or name.startswith("test")

    def _is_test_method(self, name: str) -> bool:
        """Check if a method name indicates a test."""
        return self._is_test_function(name)

    def _is_test_class(self, name: str) -> bool:
        """Check if a class name indicates a test class."""
        return name.startswith("Test") or name.endswith("Test") or name.endswith("Tests")

    def _is_fixture_function(self, name: str, decorators: list[str]) -> bool:
        """Check if a function is a pytest fixture."""
        return any("fixture" in dec for dec in decorators)

    def _is_setup_function(self, name: str) -> bool:
        """Check if a function is a setup function."""
        return name in ["setup", "setUp", "setup_module", "setup_class", "setup_method", "setup_function"]

    def _is_teardown_function(self, name: str) -> bool:
        """Check if a function is a teardown function."""
        return name in [
            "teardown",
            "tearDown",
            "teardown_module",
            "teardown_class",
            "teardown_method",
            "teardown_function",
        ]

    def _is_setup_method(self, name: str) -> bool:
        """Check if a method is a setup method."""
        return name in ["setup", "setUp", "setup_method", "setup_class"]

    def _is_teardown_method(self, name: str) -> bool:
        """Check if a method is a teardown method."""
        return name in ["teardown", "tearDown", "teardown_method", "teardown_class"]

    def _extract_imports(self, imports) -> list[str]:
        """Extract import names from import info."""
        import_names = []
        for imp in imports:
            if imp.module:
                import_names.append(imp.module)
            for name in imp.names:
                if " as " in name:
                    name = name.split(" as ")[0].strip()
                if name != "*":
                    import_names.append(name)
        return import_names

    def _extract_pytest_marks(self, decorators: list[str]) -> list[str]:
        """Extract pytest marks from decorators."""
        marks = []
        for dec in decorators:
            if dec.startswith("pytest.mark."):
                marks.append(dec[12:])  # Remove pytest.mark. prefix
            elif dec.startswith("mark."):
                marks.append(dec[5:])  # Remove mark. prefix
        return marks

    def _is_test_import(self, import_name: str) -> bool:
        """Check if an import is a test-related import."""
        test_imports = ["pytest", "unittest", "nose", "mock", "hypothesis", "faker", "factory", "fixtures"]
        return any(test_imp in import_name.lower() for test_imp in test_imports)

    def _is_test_helper(self, call_name: str) -> bool:
        """Check if a call is to a test helper function."""
        test_helpers = ["assert", "mock", "patch", "fixture", "parametrize", "skip", "xfail"]
        return any(helper in call_name.lower() for helper in test_helpers)

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name."""
        parts = file_path.stem.split("/")
        return ".".join(parts)

    def _count_total_tests(self, test_module: TestModule) -> int:
        """Count total number of tests in a module."""
        count = len(test_module.test_functions)
        for test_class in test_module.test_classes:
            count += len(test_class.test_methods)
        return count
