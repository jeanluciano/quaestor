"""AST Parser for Python code analysis.

This module provides comprehensive AST parsing capabilities for Python files,
extracting code structure, imports, functions, classes, and their relationships.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from a1.core.event_bus import EventBus

from .events import SystemEvent


@dataclass
class ImportInfo:
    """Information about an import statement."""

    module: str
    names: list[str]
    alias: str | None = None
    level: int = 0  # For relative imports
    line_number: int = 0
    is_from_import: bool = False


@dataclass
class FunctionInfo:
    """Information about a function definition."""

    name: str
    line_start: int
    line_end: int
    arguments: list[str]
    decorators: list[str]
    docstring: str | None = None
    return_annotation: str | None = None
    is_async: bool = False
    is_method: bool = False
    complexity: int = 1  # Cyclomatic complexity


@dataclass
class ClassInfo:
    """Information about a class definition."""

    name: str
    line_start: int
    line_end: int
    bases: list[str]
    decorators: list[str]
    methods: list[FunctionInfo]
    attributes: list[str]
    docstring: str | None = None
    is_abstract: bool = False


@dataclass
class ModuleInfo:
    """Complete information about a Python module."""

    path: Path
    imports: list[ImportInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    constants: dict[str, Any] = field(default_factory=dict)
    module_docstring: str | None = None
    ast_tree: ast.AST | None = None


class PythonASTParser:
    """Parser for Python AST analysis."""

    def __init__(self, event_bus: EventBus | None = None):
        """Initialize the parser.

        Args:
            event_bus: Optional event bus for emitting parse events
        """
        self.event_bus = event_bus
        self._current_class: str | None = None

    def parse_file(self, file_path: Path) -> ModuleInfo:
        """Parse a Python file and extract structural information.

        Args:
            file_path: Path to the Python file

        Returns:
            ModuleInfo containing all extracted information

        Raises:
            SyntaxError: If the file contains invalid Python syntax
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        return self.parse_source(source, file_path)

    def parse_source(self, source: str, path: Path | None = None) -> ModuleInfo:
        """Parse Python source code.

        Args:
            source: Python source code
            path: Optional path for the source

        Returns:
            ModuleInfo containing all extracted information
        """
        tree = ast.parse(source)

        module_info = ModuleInfo(path=path or Path("<string>"), ast_tree=tree)

        # Extract module docstring
        module_info.module_docstring = ast.get_docstring(tree)

        # Visit all nodes - use visitor pattern to track context correctly
        visitor = _ModuleVisitor(self)
        visitor.visit(tree)

        module_info.imports = visitor.imports
        module_info.functions = visitor.functions
        module_info.classes = visitor.classes
        module_info.constants = visitor.constants

        # Emit event if we have an event bus
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="ast_parsed",
                    data={
                        "path": str(path),
                        "imports": len(module_info.imports),
                        "functions": len(module_info.functions),
                        "classes": len(module_info.classes),
                    },
                )
            )

        return module_info

    def _parse_import(self, node: ast.Import) -> list[ImportInfo]:
        """Parse an import statement."""
        imports = []
        for alias in node.names:
            imports.append(
                ImportInfo(
                    module=alias.name, names=[], alias=alias.asname, line_number=node.lineno, is_from_import=False
                )
            )
        return imports

    def _parse_import_from(self, node: ast.ImportFrom) -> list[ImportInfo]:
        """Parse a from...import statement."""
        imports = []
        module = node.module or ""
        level = node.level

        names = []
        for alias in node.names:
            if alias.name == "*":
                names.append("*")
            else:
                names.append(f"{alias.name}" + (f" as {alias.asname}" if alias.asname else ""))

        imports.append(
            ImportInfo(module=module, names=names, level=level, line_number=node.lineno, is_from_import=True)
        )

        return imports

    def _parse_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        """Parse a function definition."""
        # Extract arguments
        args = []
        for arg in node.args.args:
            args.append(arg.arg)

        # Extract decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))

        # Extract return annotation
        return_annotation = None
        if node.returns:
            return_annotation = ast.unparse(node.returns)

        # Calculate cyclomatic complexity (simplified)
        complexity = self._calculate_complexity(node)

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            arguments=args,
            decorators=decorators,
            docstring=ast.get_docstring(node),
            return_annotation=return_annotation,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=self._current_class is not None,
            complexity=complexity,
        )

    def _parse_class(self, node: ast.ClassDef) -> ClassInfo:
        """Parse a class definition."""
        # Save current class context
        old_class = self._current_class
        self._current_class = node.name

        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            else:
                bases.append(ast.unparse(base))

        # Extract decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))

        # Extract methods and attributes
        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                methods.append(self._parse_function(item))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        # Check if abstract
        is_abstract = any(dec in ["abstractmethod", "ABC"] for dec in decorators)

        # Restore class context
        self._current_class = old_class

        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            bases=bases,
            decorators=decorators,
            methods=methods,
            attributes=attributes,
            docstring=ast.get_docstring(node),
            is_abstract=is_abstract,
        )

    def _parse_assignment(self, node: ast.Assign, constants: dict[str, Any]) -> None:
        """Parse module-level assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Track uppercase names and special names like __all__
                if target.id.isupper() or target.id == "__all__":
                    try:
                        constants[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        # If we can't evaluate it as a literal, store the unparsed version
                        constants[target.id] = ast.unparse(node.value)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.While | ast.For | ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each and/or adds a branch
                complexity += len(child.values) - 1

        return complexity

    def extract_dependencies(self, module_info: ModuleInfo) -> set[str]:
        """Extract all external dependencies from a module.

        Args:
            module_info: The parsed module information

        Returns:
            Set of module names that are imported
        """
        dependencies = set()

        for import_info in module_info.imports:
            if import_info.module:
                # Extract top-level module name
                top_level = import_info.module.split(".")[0]
                dependencies.add(top_level)

        return dependencies

    def find_symbol_usage(self, tree: ast.AST, symbol_name: str) -> list[tuple[int, int]]:
        """Find all usages of a symbol in the AST.

        Args:
            tree: The AST to search
            symbol_name: Name of the symbol to find

        Returns:
            List of (line, column) tuples where the symbol is used
        """
        usages = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == symbol_name:
                usages.append((node.lineno, node.col_offset))

        return usages


class _ModuleVisitor(ast.NodeVisitor):
    """AST visitor to properly track context when extracting module elements."""

    def __init__(self, parser: PythonASTParser):
        self.parser = parser
        self.imports: list[ImportInfo] = []
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self.constants: dict[str, Any] = {}
        self._class_stack: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.extend(self.parser._parse_import(node))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.extend(self.parser._parse_import_from(node))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not self._class_stack:  # Module-level function
            self.functions.append(self.parser._parse_function(node))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if not self._class_stack:  # Module-level function
            func_info = self.parser._parse_function(node)
            func_info.is_async = True
            self.functions.append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.parser._current_class = node.name
        class_info = self.parser._parse_class(node)
        self.classes.append(class_info)
        self.parser._current_class = None
        self._class_stack.pop()
        # Don't call generic_visit - we already parsed the class body

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self._class_stack:  # Module-level assignment
            self.parser._parse_assignment(node, self.constants)
        self.generic_visit(node)
