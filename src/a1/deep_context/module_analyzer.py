"""Module analyzer for extracting structure and signatures.

This module builds on the AST parser to provide higher-level analysis
of Python modules, including dependency graphs and API extraction.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from a1.core.event_bus import EventBus

from .ast_parser import FunctionInfo, ModuleInfo, PythonASTParser
from .events import SystemEvent


@dataclass
class ModuleSignature:
    """Public API signature of a module."""

    module_path: str
    exports: list[str]  # __all__ if defined, otherwise all public names
    functions: dict[str, str]  # name -> signature
    classes: dict[str, list[str]]  # class name -> public methods
    constants: list[str]
    version: str | None = None


@dataclass
class DependencyEdge:
    """Edge in the dependency graph."""

    source: str
    target: str
    import_type: str  # 'import' or 'from'
    names: list[str]  # What was imported
    line_number: int


class ModuleAnalyzer:
    """Analyzes Python modules to extract structure and relationships."""

    def __init__(self, event_bus: EventBus | None = None):
        """Initialize the analyzer.

        Args:
            event_bus: Optional event bus for analysis events
        """
        self.parser = PythonASTParser(event_bus)
        self.event_bus = event_bus
        self._module_cache: dict[Path, ModuleInfo] = {}
        self._signature_cache: dict[Path, ModuleSignature] = {}

    def analyze_module(self, file_path: Path, use_cache: bool = True) -> ModuleInfo:
        """Analyze a Python module.

        Args:
            file_path: Path to the module
            use_cache: Whether to use cached results

        Returns:
            ModuleInfo with parsed data
        """
        if use_cache and file_path in self._module_cache:
            return self._module_cache[file_path]

        module_info = self.parser.parse_file(file_path)
        self._module_cache[file_path] = module_info

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="module_analyzed",
                    data={
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "functions": len(module_info.functions),
                        "classes": len(module_info.classes),
                    },
                )
            )

        return module_info

    def extract_module_signature(self, module_info: ModuleInfo) -> ModuleSignature:
        """Extract the public API signature of a module.

        Args:
            module_info: Parsed module information

        Returns:
            ModuleSignature with public API details
        """
        if module_info.path in self._signature_cache:
            return self._signature_cache[module_info.path]

        # Determine exports
        exports = self._determine_exports(module_info)

        # Extract function signatures - only those in exports
        function_sigs = {}
        for func in module_info.functions:
            if func.name in exports:
                function_sigs[func.name] = self._format_function_signature(func)

        # Extract class information - only those in exports
        class_info = {}
        for cls in module_info.classes:
            if cls.name in exports:
                public_methods = [
                    method.name
                    for method in cls.methods
                    if not method.name.startswith("_") or method.name in ["__init__", "__str__", "__repr__"]
                ]
                class_info[cls.name] = public_methods

        # Extract constants - only those in exports
        constants = [name for name in module_info.constants if name in exports]

        signature = ModuleSignature(
            module_path=str(module_info.path),
            exports=exports,
            functions=function_sigs,
            classes=class_info,
            constants=constants,
        )

        self._signature_cache[module_info.path] = signature
        return signature

    def build_import_graph(self, root_path: Path) -> dict[str, list[DependencyEdge]]:
        """Build an import dependency graph starting from a root path.

        Args:
            root_path: Root directory to analyze

        Returns:
            Dictionary mapping module paths to their dependencies
        """
        import_graph = {}

        # Find all Python files
        python_files = list(root_path.rglob("*.py"))

        for file_path in python_files:
            if file_path.name == "__pycache__":
                continue

            try:
                module_info = self.analyze_module(file_path)
                module_path = self._path_to_module_name(file_path, root_path)

                edges = []
                for import_info in module_info.imports:
                    edge = DependencyEdge(
                        source=module_path,
                        target=import_info.module,
                        import_type="from" if import_info.is_from_import else "import",
                        names=import_info.names,
                        line_number=import_info.line_number,
                    )
                    edges.append(edge)

                import_graph[module_path] = edges

            except SyntaxError as e:
                # Log syntax errors but continue
                if self.event_bus:
                    self.event_bus.emit(
                        SystemEvent(type="analysis_error", data={"path": str(file_path), "error": str(e)})
                    )

        return import_graph

    def find_circular_dependencies(self, import_graph: dict[str, list[DependencyEdge]]) -> list[list[str]]:
        """Find circular dependencies in the import graph.

        Args:
            import_graph: The import dependency graph

        Returns:
            List of circular dependency chains
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def _dfs(module: str, path: list[str]) -> None:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            if module in import_graph:
                for edge in import_graph[module]:
                    target = edge.target

                    # Skip external dependencies
                    if target not in import_graph:
                        continue

                    if target not in visited:
                        _dfs(target, path.copy())
                    elif target in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(target)
                        cycle = path[cycle_start:] + [target]
                        cycles.append(cycle)

            rec_stack.remove(module)

        # Check each module
        for module in import_graph:
            if module not in visited:
                _dfs(module, [])

        return cycles

    def calculate_module_metrics(self, module_info: ModuleInfo) -> dict[str, any]:
        """Calculate various metrics for a module.

        Args:
            module_info: Parsed module information

        Returns:
            Dictionary of metrics
        """
        metrics = {
            "loc": self._count_lines_of_code(module_info),
            "num_functions": len(module_info.functions),
            "num_classes": len(module_info.classes),
            "num_methods": sum(len(cls.methods) for cls in module_info.classes),
            "avg_function_complexity": self._average_complexity(module_info.functions),
            "max_function_complexity": self._max_complexity(module_info.functions),
            "num_imports": len(module_info.imports),
            "has_docstring": bool(module_info.module_docstring),
            "docstring_coverage": self._calculate_docstring_coverage(module_info),
        }

        return metrics

    def export_analysis(self, output_path: Path, include_ast: bool = False) -> None:
        """Export the analysis results to a JSON file.

        Args:
            output_path: Path for the output file
            include_ast: Whether to include raw AST data
        """
        analysis_data = {"modules": {}, "signatures": {}, "metrics": {}}

        for path, module_info in self._module_cache.items():
            module_data = asdict(module_info)

            # Remove AST unless requested
            if not include_ast:
                module_data.pop("ast_tree", None)

            analysis_data["modules"][str(path)] = module_data

            # Add signature
            signature = self.extract_module_signature(module_info)
            analysis_data["signatures"][str(path)] = asdict(signature)

            # Add metrics
            metrics = self.calculate_module_metrics(module_info)
            analysis_data["metrics"][str(path)] = metrics

        with open(output_path, "w") as f:
            json.dump(analysis_data, f, indent=2)

    def _determine_exports(self, module_info: ModuleInfo) -> list[str]:
        """Determine what a module exports."""
        # Check for __all__
        if "__all__" in module_info.constants:
            all_value = module_info.constants["__all__"]
            if isinstance(all_value, list):
                return all_value
            elif isinstance(all_value, str):
                # Sometimes __all__ is stored as string representation
                try:
                    import ast

                    parsed = ast.literal_eval(all_value)
                    if isinstance(parsed, list):
                        return parsed
                except:
                    pass

        # Otherwise, all public names
        exports = []

        for func in module_info.functions:
            if not func.name.startswith("_"):
                exports.append(func.name)

        for cls in module_info.classes:
            if not cls.name.startswith("_"):
                exports.append(cls.name)

        for const in module_info.constants:
            if not const.startswith("_") and const != "__all__":
                exports.append(const)

        return exports

    def _format_function_signature(self, func: FunctionInfo) -> str:
        """Format a function signature as a string."""
        args = ", ".join(func.arguments)
        sig = f"{func.name}({args})"

        if func.return_annotation:
            sig += f" -> {func.return_annotation}"

        return sig

    def _path_to_module_name(self, file_path: Path, root: Path) -> str:
        """Convert file path to module name."""
        relative = file_path.relative_to(root)
        parts = list(relative.parts[:-1]) + [relative.stem]

        # Remove __init__ from module name
        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    def _count_lines_of_code(self, module_info: ModuleInfo) -> int:
        """Count lines of code (excluding blanks and comments)."""
        if not module_info.path.exists():
            return 0

        with open(module_info.path) as f:
            lines = f.readlines()

        loc = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                loc += 1

        return loc

    def _average_complexity(self, functions: list[FunctionInfo]) -> float:
        """Calculate average cyclomatic complexity."""
        if not functions:
            return 0.0

        total = sum(func.complexity for func in functions)
        return total / len(functions)

    def _max_complexity(self, functions: list[FunctionInfo]) -> int:
        """Find maximum cyclomatic complexity."""
        if not functions:
            return 0

        return max(func.complexity for func in functions)

    def _calculate_docstring_coverage(self, module_info: ModuleInfo) -> float:
        """Calculate percentage of functions/classes with docstrings."""
        total = len(module_info.functions) + len(module_info.classes)

        if total == 0:
            return 100.0

        documented = 0

        for func in module_info.functions:
            if func.docstring:
                documented += 1

        for cls in module_info.classes:
            if cls.docstring:
                documented += 1

        return (documented / total) * 100
