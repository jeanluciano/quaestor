"""Function signature extraction and analysis.

This module extracts comprehensive function signatures including parameters,
return types, and call patterns for better code understanding.
"""

import ast
import re
from dataclasses import dataclass, field

from a1.core.event_bus import EventBus

from ..ast_parser import FunctionInfo, ModuleInfo
from ..events import SystemEvent


@dataclass
class ParameterInfo:
    """Information about a function parameter."""

    name: str
    type_annotation: str | None = None
    default_value: str | None = None
    is_variadic: bool = False  # *args
    is_keyword_variadic: bool = False  # **kwargs
    position: int = 0


@dataclass
class FunctionSignature:
    """Comprehensive function signature information."""

    qualified_name: str
    name: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_type: str | None = None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    is_property: bool = False
    docstring: str | None = None
    raises: list[str] = field(default_factory=list)  # Exceptions it might raise
    calls: list[str] = field(default_factory=list)  # Functions it calls


class SignatureExtractor:
    """Extracts function signatures from Python code."""

    def __init__(self, event_bus: EventBus | None = None):
        """Initialize the signature extractor.

        Args:
            event_bus: Optional event bus for extraction events
        """
        self.event_bus = event_bus
        self._current_module: str | None = None
        self._current_class: str | None = None

    def extract_module_signatures(self, module_info: ModuleInfo) -> dict[str, FunctionSignature]:
        """Extract all function signatures from a module.

        Args:
            module_info: Parsed module information

        Returns:
            Dictionary mapping qualified names to signatures
        """
        signatures = {}
        self._current_module = str(module_info.path)

        # Extract function signatures
        for func in module_info.functions:
            sig = self._extract_function_signature(func, module_info.ast_tree)
            signatures[sig.qualified_name] = sig

        # Extract method signatures
        for cls in module_info.classes:
            self._current_class = cls.name
            for method in cls.methods:
                sig = self._extract_function_signature(method, module_info.ast_tree, is_method=True)
                signatures[sig.qualified_name] = sig
            self._current_class = None

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="signatures_extracted",
                    data={
                        "module": self._current_module,
                        "count": len(signatures),
                    },
                )
            )

        return signatures

    def _extract_function_signature(
        self, func_info: FunctionInfo, ast_tree: ast.AST | None, is_method: bool = False
    ) -> FunctionSignature:
        """Extract signature from function info."""
        # Build qualified name
        parts = []
        if self._current_module:
            parts.append(self._current_module)
        if self._current_class:
            parts.append(self._current_class)
        parts.append(func_info.name)
        qualified_name = "::".join(parts)

        # Extract parameters
        parameters = self._extract_parameters(func_info, ast_tree)

        # Analyze decorators
        is_classmethod = "classmethod" in func_info.decorators
        is_staticmethod = "staticmethod" in func_info.decorators
        is_property = "property" in func_info.decorators

        # Extract additional info from AST if available
        raises = []
        calls = []
        if ast_tree:
            func_node = self._find_function_node(ast_tree, func_info)
            if func_node:
                raises = self._extract_raises(func_node)
                calls = self._extract_calls(func_node)

        # Parse docstring for additional type hints
        if func_info.docstring:
            doc_params, doc_return, doc_raises = self._parse_docstring(func_info.docstring)
            # Merge docstring info with annotations
            for param in parameters:
                if param.name in doc_params and not param.type_annotation:
                    param.type_annotation = doc_params[param.name]
            if doc_raises:
                raises.extend(doc_raises)

        return FunctionSignature(
            qualified_name=qualified_name,
            name=func_info.name,
            parameters=parameters,
            return_type=func_info.return_annotation,
            decorators=func_info.decorators,
            is_async=func_info.is_async,
            is_method=is_method,
            is_classmethod=is_classmethod,
            is_staticmethod=is_staticmethod,
            is_property=is_property,
            docstring=func_info.docstring,
            raises=raises,
            calls=calls,
        )

    def _extract_parameters(self, func_info: FunctionInfo, ast_tree: ast.AST | None) -> list[ParameterInfo]:
        """Extract parameter information."""
        if not ast_tree:
            # Basic extraction from argument names only
            return [ParameterInfo(name=arg, position=i) for i, arg in enumerate(func_info.arguments)]

        # Find the function node for detailed analysis
        func_node = self._find_function_node(ast_tree, func_info)
        if not func_node:
            return [ParameterInfo(name=arg, position=i) for i, arg in enumerate(func_info.arguments)]

        parameters = []
        args = func_node.args

        # Regular arguments
        for i, arg in enumerate(args.args):
            param = ParameterInfo(
                name=arg.arg,
                position=i,
                type_annotation=ast.unparse(arg.annotation) if arg.annotation else None,
            )

            # Check for default values
            default_offset = len(args.args) - len(args.defaults)
            if i >= default_offset:
                default_idx = i - default_offset
                if default_idx < len(args.defaults):
                    param.default_value = ast.unparse(args.defaults[default_idx])

            parameters.append(param)

        # *args
        if args.vararg:
            parameters.append(
                ParameterInfo(
                    name=args.vararg.arg,
                    type_annotation=ast.unparse(args.vararg.annotation) if args.vararg.annotation else None,
                    is_variadic=True,
                    position=len(parameters),
                )
            )

        # **kwargs
        if args.kwarg:
            parameters.append(
                ParameterInfo(
                    name=args.kwarg.arg,
                    type_annotation=ast.unparse(args.kwarg.annotation) if args.kwarg.annotation else None,
                    is_keyword_variadic=True,
                    position=len(parameters),
                )
            )

        return parameters

    def _find_function_node(self, ast_tree: ast.AST, func_info: FunctionInfo) -> ast.FunctionDef | None:
        """Find the AST node for a function."""
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name == func_info.name and node.lineno == func_info.line_start:
                    return node
        return None

    def _extract_raises(self, func_node: ast.FunctionDef) -> list[str]:
        """Extract exceptions that might be raised."""
        raises = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    raises.append(node.exc.func.id)
                elif isinstance(node.exc, ast.Name):
                    raises.append(node.exc.id)

        return list(set(raises))  # Unique exceptions

    def _extract_calls(self, func_node: ast.FunctionDef) -> list[str]:
        """Extract function calls made within the function."""
        calls = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    calls.append(f".{node.func.attr}")

        return list(set(calls))  # Unique calls

    def _parse_docstring(self, docstring: str) -> tuple[dict[str, str], str | None, list[str]]:
        """Parse docstring for type information.

        Returns:
            Tuple of (param_types, return_type, raises)
        """
        param_types = {}
        return_type = None
        raises = []

        # Common docstring patterns
        # Google style
        param_pattern = r":param\s+(\w+):\s*(.+?)(?=:param|:type|:return|:raises|$)"
        type_pattern = r":type\s+(\w+):\s*(.+?)(?=:param|:type|:return|:raises|$)"
        # return_pattern = r':return:\s*(.+?)(?=:rtype|:raises|$)'  # Not used currently
        rtype_pattern = r":rtype:\s*(.+?)(?=:raises|$)"
        raises_pattern = r":raises\s+(\w+):"

        # Extract parameter descriptions and types
        for match in re.finditer(param_pattern, docstring, re.MULTILINE | re.DOTALL):
            param_name = match.group(1)
            # Try to extract type from description
            desc = match.group(2).strip()
            type_match = re.match(r"^\(([^)]+)\)", desc)
            if type_match:
                param_types[param_name] = type_match.group(1)

        # Extract explicit types
        for match in re.finditer(type_pattern, docstring, re.MULTILINE | re.DOTALL):
            param_types[match.group(1)] = match.group(2).strip()

        # Extract return type
        rtype_match = re.search(rtype_pattern, docstring, re.MULTILINE | re.DOTALL)
        if rtype_match:
            return_type = rtype_match.group(1).strip()

        # Extract raises
        for match in re.finditer(raises_pattern, docstring):
            raises.append(match.group(1))

        return param_types, return_type, raises

    def normalize_signature(self, signature: FunctionSignature) -> str:
        """Normalize a signature to a canonical string form.

        Args:
            signature: Function signature

        Returns:
            Normalized signature string
        """
        parts = []

        # Add decorators
        for decorator in sorted(signature.decorators):
            parts.append(f"@{decorator}")

        # Add async
        if signature.is_async:
            parts.append("async")

        # Add def and name
        parts.append(f"def {signature.name}(")

        # Add parameters
        param_strs = []
        for param in signature.parameters:
            param_str = param.name
            if param.type_annotation:
                param_str += f": {param.type_annotation}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            if param.is_variadic:
                param_str = f"*{param_str}"
            elif param.is_keyword_variadic:
                param_str = f"**{param_str}"
            param_strs.append(param_str)

        parts.append(", ".join(param_strs))
        parts.append(")")

        # Add return type
        if signature.return_type:
            parts.append(f" -> {signature.return_type}")

        return "".join(parts)

    def signature_compatibility(self, sig1: FunctionSignature, sig2: FunctionSignature) -> float:
        """Calculate compatibility score between two signatures.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            Compatibility score (0.0 to 1.0)
        """
        score = 0.0
        max_score = 0.0

        # Name similarity (partial credit for similar names)
        max_score += 1.0
        if sig1.name == sig2.name:
            score += 1.0
        elif sig1.name.lower() == sig2.name.lower():
            score += 0.7
        elif self._name_similarity(sig1.name, sig2.name) > 0.5:
            score += 0.3

        # Parameter count
        max_score += 1.0
        param_diff = abs(len(sig1.parameters) - len(sig2.parameters))
        score += max(0, 1.0 - param_diff * 0.2)

        # Parameter types (for matching positions)
        max_score += min(len(sig1.parameters), len(sig2.parameters))
        for i in range(min(len(sig1.parameters), len(sig2.parameters))):
            p1 = sig1.parameters[i]
            p2 = sig2.parameters[i]

            if p1.type_annotation == p2.type_annotation:
                score += 1.0
            elif p1.type_annotation and p2.type_annotation:
                # Partial credit for related types
                if self._types_related(p1.type_annotation, p2.type_annotation):
                    score += 0.5

        # Return type
        max_score += 1.0
        if sig1.return_type == sig2.return_type:
            score += 1.0
        elif sig1.return_type and sig2.return_type:
            if self._types_related(sig1.return_type, sig2.return_type):
                score += 0.5

        # Async compatibility
        max_score += 0.5
        if sig1.is_async == sig2.is_async:
            score += 0.5

        return score / max_score if max_score > 0 else 0.0

    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using simple heuristics."""
        # Split on underscores and camelCase
        parts1 = self._split_identifier(name1)
        parts2 = self._split_identifier(name2)

        # Calculate Jaccard similarity
        set1 = set(parts1)
        set2 = set(parts2)

        if not set1 or not set2:
            return 0.0

        intersection = set1 & set2
        union = set1 | set2

        return len(intersection) / len(union)

    def _split_identifier(self, name: str) -> list[str]:
        """Split identifier into parts."""
        # Handle snake_case
        parts = name.split("_")

        # Handle camelCase
        result = []
        for part in parts:
            camel_parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", part)
            if camel_parts:
                result.extend(p.lower() for p in camel_parts)
            elif part:
                result.append(part.lower())

        return result

    def _types_related(self, type1: str, type2: str) -> bool:
        """Check if two types are related."""
        # Simple heuristics for type relationships
        type_groups = [
            {"int", "float", "number", "num"},
            {"str", "string", "text"},
            {"list", "List", "Sequence", "Iterable"},
            {"dict", "Dict", "Mapping"},
            {"bool", "Boolean"},
        ]

        type1_lower = type1.lower()
        type2_lower = type2.lower()

        for group in type_groups:
            if type1_lower in group and type2_lower in group:
                return True

        return False
