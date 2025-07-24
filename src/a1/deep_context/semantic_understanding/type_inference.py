"""Type inference engine for Python code analysis.

This module provides static type inference capabilities without requiring
explicit type annotations, using AST analysis and pattern recognition.
"""

import ast
from dataclasses import dataclass, field
from typing import Any

from a1.core.event_bus import EventBus

from ..ast_parser import FunctionInfo, ModuleInfo, PythonASTParser
from ..events import SystemEvent
from ..symbol_table import Symbol, SymbolTable


@dataclass
class TypeInfo:
    """Information about an inferred type."""

    type_name: str
    module: str | None = None
    is_generic: bool = False
    type_params: list[str] = field(default_factory=list)
    confidence: float = 1.0  # 0.0 to 1.0
    source: str = "inference"  # "annotation", "inference", "docstring"


@dataclass
class TypeContext:
    """Context for type inference within a scope."""

    variables: dict[str, TypeInfo] = field(default_factory=dict)
    imports: dict[str, str] = field(default_factory=dict)  # alias -> module
    return_type: TypeInfo | None = None
    in_function: str | None = None
    in_class: str | None = None


class TypeInferenceEngine:
    """Engine for inferring types in Python code."""

    def __init__(self, symbol_table: SymbolTable | None = None, event_bus: EventBus | None = None):
        """Initialize the type inference engine.

        Args:
            symbol_table: Optional symbol table for cross-module inference
            event_bus: Optional event bus for inference events
        """
        self.symbol_table = symbol_table
        self.event_bus = event_bus
        self.parser = PythonASTParser(event_bus)
        self._type_cache: dict[str, TypeInfo] = {}

        # Built-in type mappings
        self._builtin_types = {
            "int": TypeInfo("int", "builtins"),
            "float": TypeInfo("float", "builtins"),
            "str": TypeInfo("str", "builtins"),
            "bool": TypeInfo("bool", "builtins"),
            "list": TypeInfo("list", "builtins", is_generic=True),
            "dict": TypeInfo("dict", "builtins", is_generic=True),
            "set": TypeInfo("set", "builtins", is_generic=True),
            "tuple": TypeInfo("tuple", "builtins", is_generic=True),
            "None": TypeInfo("NoneType", "builtins"),
        }

    def infer_module_types(self, module_info: ModuleInfo) -> dict[str, TypeInfo]:
        """Infer types for all symbols in a module.

        Args:
            module_info: Parsed module information

        Returns:
            Dictionary mapping symbol names to inferred types
        """
        if not module_info.ast_tree:
            return {}

        # Create module context
        context = TypeContext()

        # Process imports first
        for import_info in module_info.imports:
            if import_info.alias:
                context.imports[import_info.alias] = import_info.module
            else:
                context.imports[import_info.module] = import_info.module

        # Visit the AST
        visitor = TypeInferenceVisitor(self, context)
        visitor.visit(module_info.ast_tree)

        # Combine results
        types = {}

        # Add function types
        for func in module_info.functions:
            func_type = self._infer_function_type(func, context)
            types[func.name] = func_type

        # Add class types
        for cls in module_info.classes:
            types[cls.name] = TypeInfo(cls.name, module_info.path.stem)

        # Add inferred variable types
        types.update(context.variables)

        # Emit event
        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="types_inferred",
                    data={
                        "module": str(module_info.path),
                        "types_count": len(types),
                    },
                )
            )

        return types

    def infer_expression_type(self, expr: ast.expr, context: TypeContext) -> TypeInfo | None:
        """Infer the type of an expression.

        Args:
            expr: AST expression node
            context: Current type context

        Returns:
            Inferred type information or None
        """
        if isinstance(expr, ast.Constant):
            return self._infer_constant_type(expr.value)

        elif isinstance(expr, ast.Name):
            # Look up in context
            if expr.id in context.variables:
                return context.variables[expr.id]
            elif expr.id in self._builtin_types:
                return self._builtin_types[expr.id]

        elif isinstance(expr, ast.List):
            # Infer list element type
            element_types = []
            for elt in expr.elts:
                elt_type = self.infer_expression_type(elt, context)
                if elt_type:
                    element_types.append(elt_type)

            list_type = TypeInfo("list", "builtins", is_generic=True)
            if element_types:
                # Use the most common element type
                list_type.type_params = [self._unify_types(element_types).type_name]
            return list_type

        elif isinstance(expr, ast.Dict):
            # Infer dict key and value types
            key_types = []
            value_types = []

            for key, value in zip(expr.keys, expr.values, strict=False):
                if key:
                    key_type = self.infer_expression_type(key, context)
                    if key_type:
                        key_types.append(key_type)

                value_type = self.infer_expression_type(value, context)
                if value_type:
                    value_types.append(value_type)

            dict_type = TypeInfo("dict", "builtins", is_generic=True)
            if key_types and value_types:
                dict_type.type_params = [
                    self._unify_types(key_types).type_name,
                    self._unify_types(value_types).type_name,
                ]
            return dict_type

        elif isinstance(expr, ast.Set):
            # Infer set element type
            element_types = []
            for elt in expr.elts:
                elt_type = self.infer_expression_type(elt, context)
                if elt_type:
                    element_types.append(elt_type)

            set_type = TypeInfo("set", "builtins", is_generic=True)
            if element_types:
                set_type.type_params = [self._unify_types(element_types).type_name]
            return set_type

        elif isinstance(expr, ast.Call):
            return self._infer_call_type(expr, context)

        elif isinstance(expr, ast.BinOp):
            return self._infer_binop_type(expr, context)

        elif isinstance(expr, ast.Compare):
            return TypeInfo("bool", "builtins")

        elif isinstance(expr, ast.IfExp):
            # Type is union of body and orelse types
            body_type = self.infer_expression_type(expr.body, context)
            else_type = self.infer_expression_type(expr.orelse, context)
            if body_type and else_type:
                return self._unify_types([body_type, else_type])
            return body_type or else_type

        return None

    def _infer_function_type(self, func: FunctionInfo, context: TypeContext) -> TypeInfo:
        """Infer the type of a function."""
        func_type = TypeInfo(type_name="Callable", module="typing", is_generic=True)

        # Infer parameter types
        param_types = []
        for _arg in func.arguments:
            # Could enhance this with docstring parsing
            param_types.append("Any")

        # Infer return type
        return_type = "Any"
        if func.return_annotation:
            return_type = func.return_annotation
        elif context.return_type:
            return_type = context.return_type.type_name

        func_type.type_params = [f"[{', '.join(param_types)}]", return_type]
        return func_type

    def _infer_constant_type(self, value: Any) -> TypeInfo:
        """Infer type from a constant value."""
        # Check bool before int since bool is a subclass of int
        if isinstance(value, bool):
            return TypeInfo("bool", "builtins")
        elif isinstance(value, int):
            return TypeInfo("int", "builtins")
        elif isinstance(value, float):
            return TypeInfo("float", "builtins")
        elif isinstance(value, str):
            return TypeInfo("str", "builtins")
        elif value is None:
            return TypeInfo("NoneType", "builtins")
        else:
            return TypeInfo(type(value).__name__, confidence=0.8)

    def _infer_call_type(self, call: ast.Call, context: TypeContext) -> TypeInfo | None:
        """Infer the return type of a function call."""
        if isinstance(call.func, ast.Name):
            func_name = call.func.id

            # Check built-in constructors
            if func_name in self._builtin_types:
                return self._builtin_types[func_name]

            # Check known patterns
            if func_name == "len":
                return TypeInfo("int", "builtins")
            elif func_name == "range":
                return TypeInfo("range", "builtins")
            elif func_name == "open":
                return TypeInfo("TextIOWrapper", "io")

            # Look up in symbol table if available
            if self.symbol_table:
                symbols = self.symbol_table.find_symbols_by_name(func_name)
                if symbols:
                    # Could analyze the function to infer return type
                    pass

        return None

    def _infer_binop_type(self, binop: ast.BinOp, context: TypeContext) -> TypeInfo | None:
        """Infer the type of a binary operation."""
        left_type = self.infer_expression_type(binop.left, context)
        right_type = self.infer_expression_type(binop.right, context)

        if not left_type or not right_type:
            return None

        # Numeric operations
        if isinstance(binop.op, ast.Add | ast.Sub | ast.Mult | ast.Pow):
            if left_type.type_name in ("int", "float") and right_type.type_name in ("int", "float"):
                if "float" in (left_type.type_name, right_type.type_name):
                    return TypeInfo("float", "builtins")
                return TypeInfo("int", "builtins")
            elif left_type.type_name == "str" and isinstance(binop.op, ast.Add):
                return TypeInfo("str", "builtins")

        # Division always returns float
        elif isinstance(binop.op, ast.Div):
            return TypeInfo("float", "builtins")

        # Floor division
        elif isinstance(binop.op, ast.FloorDiv):
            if left_type.type_name in ("int", "float"):
                return TypeInfo("int", "builtins")

        return None

    def _unify_types(self, types: list[TypeInfo]) -> TypeInfo:
        """Unify multiple types into a single type."""
        if not types:
            return TypeInfo("Any", "typing", confidence=0.5)

        if len(types) == 1:
            return types[0]

        # Check if all types are the same
        type_names = {t.type_name for t in types}
        if len(type_names) == 1:
            return types[0]

        # Check for numeric types
        if type_names.issubset({"int", "float"}):
            return TypeInfo("float", "builtins", confidence=0.9)

        # Otherwise, use Union type
        return TypeInfo("Union", "typing", is_generic=True, type_params=list(type_names), confidence=0.7)

    def get_symbol_type(self, symbol: Symbol) -> TypeInfo | None:
        """Get the inferred type for a symbol.

        Args:
            symbol: The symbol to get type for

        Returns:
            Type information or None
        """
        cache_key = symbol.qualified_name
        if cache_key in self._type_cache:
            return self._type_cache[cache_key]

        # Infer based on symbol type
        if symbol.signature:
            # Parse signature for type info
            pass

        return None


class TypeInferenceVisitor(ast.NodeVisitor):
    """AST visitor for type inference."""

    def __init__(self, engine: TypeInferenceEngine, context: TypeContext):
        self.engine = engine
        self.context = context
        self.current_class: str | None = None

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment to infer variable types."""
        # Infer the type of the right-hand side
        value_type = self.engine.infer_expression_type(node.value, self.context)

        if value_type:
            # Assign type to all targets
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.context.variables[target.id] = value_type

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignment."""
        if isinstance(node.target, ast.Name) and node.annotation:
            # Parse the annotation
            type_name = ast.unparse(node.annotation)
            type_info = TypeInfo(type_name, source="annotation")
            self.context.variables[node.target.id] = type_info

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        old_context = self.context
        self.context = TypeContext(
            imports=self.context.imports.copy(), in_function=node.name, in_class=self.current_class
        )

        # Process parameters
        for arg in node.args.args:
            if arg.annotation:
                type_name = ast.unparse(arg.annotation)
                self.context.variables[arg.arg] = TypeInfo(type_name, source="annotation")

        # Visit function body
        self.generic_visit(node)

        # Restore context
        self.context = old_context

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        old_class = self.current_class
        self.current_class = node.name

        self.generic_visit(node)

        self.current_class = old_class

    def visit_Return(self, node: ast.Return) -> None:
        """Visit return statement to infer return type."""
        if node.value and self.context.in_function:
            return_type = self.engine.infer_expression_type(node.value, self.context)
            if return_type:
                self.context.return_type = return_type

        self.generic_visit(node)
