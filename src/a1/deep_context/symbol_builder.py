"""Symbol table builder that processes AST to populate symbol table.

This module bridges the AST parser and symbol table, converting parsed
module information into symbol table entries with proper relationships.
"""

import ast
from pathlib import Path

from a1.core.event_bus import EventBus

from .ast_parser import ClassInfo, FunctionInfo, ImportInfo, PythonASTParser
from .events import SystemEvent
from .symbol_table import Symbol, SymbolLocation, SymbolRelation, SymbolTable, SymbolType


class SymbolBuilder:
    """Builds symbol table from parsed AST information."""

    def __init__(self, symbol_table: SymbolTable, event_bus: EventBus | None = None):
        """Initialize the builder.

        Args:
            symbol_table: The symbol table to populate
            event_bus: Optional event bus for build events
        """
        self.symbol_table = symbol_table
        self.parser = PythonASTParser(event_bus)
        self.event_bus = event_bus
        self._current_module: str | None = None
        self._import_map: dict[str, str] = {}  # alias -> full module name

    def process_file(self, file_path: Path, module_name: str | None = None) -> None:
        """Process a Python file and add its symbols to the table.

        Args:
            file_path: Path to the Python file
            module_name: Optional module name (will be inferred if not provided)
        """
        # Parse the file
        module_info = self.parser.parse_file(file_path)

        # Determine module name
        if module_name is None:
            module_name = self._infer_module_name(file_path)

        self._current_module = module_name
        self._import_map.clear()

        # Add module symbol
        module_symbol = Symbol(
            name=module_name.split(".")[-1],
            qualified_name=module_name,
            symbol_type=SymbolType.MODULE,
            location=SymbolLocation(file_path=file_path, line_start=1, line_end=self._count_lines(file_path)),
            docstring=module_info.module_docstring,
        )
        self.symbol_table.add_symbol(module_symbol)

        # Process imports first to build import map
        self._process_imports(module_info.imports, file_path)

        # Process module-level symbols
        self._process_constants(module_info.constants, file_path, module_name)
        self._process_functions(module_info.functions, file_path, module_name)
        self._process_classes(module_info.classes, file_path, module_name)

        # Extract relationships from AST
        if module_info.ast_tree:
            self._extract_relationships(module_info.ast_tree, file_path, module_name)

        # Emit completion event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="file_processed",
                    data={
                        "file": str(file_path),
                        "module": module_name,
                        "symbols": len(self.symbol_table.get_symbols_in_file(file_path)),
                    },
                )
            )

    def process_directory(self, directory: Path, base_module: str = "") -> None:
        """Process all Python files in a directory recursively.

        Args:
            directory: Root directory to process
            base_module: Base module name for the directory
        """
        python_files = list(directory.rglob("*.py"))

        for file_path in python_files:
            # Skip __pycache__ directories
            if "__pycache__" in str(file_path):
                continue

            # Calculate module name
            relative_path = file_path.relative_to(directory)
            module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]

            # Remove __init__ from module name
            if module_parts[-1] == "__init__":
                module_parts = module_parts[:-1]

            # Combine with base module
            if base_module:
                module_name = f"{base_module}.{'.'.join(module_parts)}" if module_parts else base_module
            else:
                module_name = ".".join(module_parts) if module_parts else "root"

            try:
                self.process_file(file_path, module_name)
            except Exception as e:
                # Log error but continue processing
                if self.event_bus:
                    self.event_bus.emit(
                        SystemEvent(type="process_error", data={"file": str(file_path), "error": str(e)})
                    )

    def _process_imports(self, imports: list[ImportInfo], file_path: Path) -> None:
        """Process import statements and build import map."""
        for import_info in imports:
            # Add import symbol
            import_symbol = Symbol(
                name=import_info.module,
                qualified_name=f"{self._current_module}:import:{import_info.module}",
                symbol_type=SymbolType.IMPORT,
                location=SymbolLocation(
                    file_path=file_path, line_start=import_info.line_number, line_end=import_info.line_number
                ),
            )
            self.symbol_table.add_symbol(import_symbol)

            # Build import map for aliases
            if import_info.alias:
                self._import_map[import_info.alias] = import_info.module
            else:
                # For from imports, map individual names
                if import_info.is_from_import:
                    for name in import_info.names:
                        if " as " in name:
                            real_name, alias = name.split(" as ")
                            self._import_map[alias.strip()] = f"{import_info.module}.{real_name.strip()}"
                        else:
                            self._import_map[name] = f"{import_info.module}.{name}"
                else:
                    self._import_map[import_info.module] = import_info.module

    def _process_constants(self, constants: dict[str, any], file_path: Path, parent: str) -> None:
        """Process module-level constants."""
        for name, value in constants.items():
            const_symbol = Symbol(
                name=name,
                qualified_name=f"{parent}.{name}",
                symbol_type=SymbolType.CONSTANT,
                location=SymbolLocation(
                    file_path=file_path,
                    line_start=1,  # Would need AST node for exact location
                    line_end=1,
                ),
                parent=parent,
                value=str(value),
            )
            self.symbol_table.add_symbol(const_symbol)

    def _process_functions(self, functions: list[FunctionInfo], file_path: Path, parent: str) -> None:
        """Process function definitions."""
        for func in functions:
            func_symbol = Symbol(
                name=func.name,
                qualified_name=f"{parent}.{func.name}",
                symbol_type=SymbolType.FUNCTION,
                location=SymbolLocation(file_path=file_path, line_start=func.line_start, line_end=func.line_end),
                parent=parent,
                docstring=func.docstring,
                signature=self._build_function_signature(func),
                metadata={"is_async": func.is_async, "complexity": func.complexity, "decorators": func.decorators},
            )
            self.symbol_table.add_symbol(func_symbol)

            # Add parameters as symbols
            for param in func.arguments:
                param_symbol = Symbol(
                    name=param,
                    qualified_name=f"{parent}.{func.name}:{param}",
                    symbol_type=SymbolType.PARAMETER,
                    location=SymbolLocation(file_path=file_path, line_start=func.line_start, line_end=func.line_start),
                    parent=f"{parent}.{func.name}",
                )
                self.symbol_table.add_symbol(param_symbol)

    def _process_classes(self, classes: list[ClassInfo], file_path: Path, parent: str) -> None:
        """Process class definitions."""
        for cls in classes:
            class_symbol = Symbol(
                name=cls.name,
                qualified_name=f"{parent}.{cls.name}",
                symbol_type=SymbolType.CLASS,
                location=SymbolLocation(file_path=file_path, line_start=cls.line_start, line_end=cls.line_end),
                parent=parent,
                docstring=cls.docstring,
                metadata={"bases": cls.bases, "decorators": cls.decorators, "is_abstract": cls.is_abstract},
            )
            self.symbol_table.add_symbol(class_symbol)

            # Add inheritance relations
            for base in cls.bases:
                # Try to resolve base class
                resolved_base = self._resolve_name(base)
                if resolved_base:
                    relation = SymbolRelation(
                        source=f"{parent}.{cls.name}",
                        target=resolved_base,
                        relation_type="inherits",
                        location=SymbolLocation(
                            file_path=file_path, line_start=cls.line_start, line_end=cls.line_start
                        ),
                    )
                    self.symbol_table.add_relation(relation)

            # Process methods
            for method in cls.methods:
                method_symbol = Symbol(
                    name=method.name,
                    qualified_name=f"{parent}.{cls.name}.{method.name}",
                    symbol_type=SymbolType.METHOD,
                    location=SymbolLocation(
                        file_path=file_path, line_start=method.line_start, line_end=method.line_end
                    ),
                    parent=f"{parent}.{cls.name}",
                    docstring=method.docstring,
                    signature=self._build_function_signature(method),
                    metadata={
                        "is_async": method.is_async,
                        "complexity": method.complexity,
                        "decorators": method.decorators,
                    },
                )
                self.symbol_table.add_symbol(method_symbol)

            # Process attributes
            for attr in cls.attributes:
                attr_symbol = Symbol(
                    name=attr,
                    qualified_name=f"{parent}.{cls.name}.{attr}",
                    symbol_type=SymbolType.VARIABLE,
                    location=SymbolLocation(file_path=file_path, line_start=cls.line_start, line_end=cls.line_start),
                    parent=f"{parent}.{cls.name}",
                )
                self.symbol_table.add_symbol(attr_symbol)

    def _extract_relationships(self, tree: ast.AST, file_path: Path, module: str) -> None:
        """Extract call and usage relationships from AST."""

        class RelationshipExtractor(ast.NodeVisitor):
            def __init__(self, builder: "SymbolBuilder", file_path: Path, module: str):
                self.builder = builder
                self.file_path = file_path
                self.module = module
                self.current_context: list[str] = [module]

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                self.current_context.append(node.name)
                self.generic_visit(node)
                self.current_context.pop()

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self.visit_FunctionDef(node)

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                self.current_context.append(node.name)
                self.generic_visit(node)
                self.current_context.pop()

            def visit_Call(self, node: ast.Call) -> None:
                # Try to resolve the call target
                target = None

                if isinstance(node.func, ast.Name):
                    target = self.builder._resolve_name(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle attribute calls like obj.method()
                    if isinstance(node.func.value, ast.Name):
                        base = node.func.value.id
                        resolved_base = self.builder._resolve_name(base)
                        if resolved_base:
                            target = f"{resolved_base}.{node.func.attr}"

                if target:
                    source = ".".join(self.current_context)
                    relation = SymbolRelation(
                        source=source,
                        target=target,
                        relation_type="calls",
                        location=SymbolLocation(
                            file_path=self.file_path,
                            line_start=node.lineno,
                            line_end=node.lineno,
                            column_start=node.col_offset,
                        ),
                    )
                    self.builder.symbol_table.add_relation(relation)

                self.generic_visit(node)

        extractor = RelationshipExtractor(self, file_path, module)
        extractor.visit(tree)

    def _resolve_name(self, name: str) -> str | None:
        """Resolve a name to its fully qualified form."""
        # Check import map first
        if name in self._import_map:
            return self._import_map[name]

        # Check if it's a local reference
        local_ref = f"{self._current_module}.{name}"
        if self.symbol_table.get_symbol(local_ref):
            return local_ref

        # Could be a builtin or unresolved
        return None

    def _build_function_signature(self, func: FunctionInfo) -> str:
        """Build a function signature string."""
        args = ", ".join(func.arguments)
        sig = f"{func.name}({args})"

        if func.return_annotation:
            sig += f" -> {func.return_annotation}"

        return sig

    def _infer_module_name(self, file_path: Path) -> str:
        """Infer module name from file path."""
        # This is a simple implementation - in practice would need
        # to consider the Python path and package structure
        parts = file_path.stem.split("/")
        return ".".join(parts)

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        with open(file_path) as f:
            return sum(1 for _ in f)
