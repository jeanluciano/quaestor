"""Tests for A1 Deep Context analysis functionality."""

from pathlib import Path

from a1.deep_context import ModuleAnalyzer, PythonASTParser, SymbolTable
from a1.deep_context.symbol_builder import SymbolBuilder
from a1.deep_context.symbol_table import SymbolType


class TestPythonASTParser:
    """Test AST parsing functionality."""

    def test_parse_simple_module(self):
        """Test parsing a simple Python module."""
        source = '''
"""Module docstring."""

import os
from pathlib import Path

CONSTANT = 42

def simple_function(x, y):
    """Add two numbers."""
    return x + y

class SimpleClass:
    """A simple class."""

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value
'''

        parser = PythonASTParser()
        module_info = parser.parse_source(source)

        # Check module docstring
        assert module_info.module_docstring == "Module docstring."

        # Check imports
        assert len(module_info.imports) == 2
        assert module_info.imports[0].module == "os"
        assert module_info.imports[1].module == "pathlib"
        assert module_info.imports[1].names == ["Path"]

        # Check constants
        assert "CONSTANT" in module_info.constants
        assert module_info.constants["CONSTANT"] == 42

        # Check functions
        assert len(module_info.functions) == 1
        func = module_info.functions[0]
        assert func.name == "simple_function"
        assert func.arguments == ["x", "y"]
        assert func.docstring == "Add two numbers."

        # Check classes
        assert len(module_info.classes) == 1
        cls = module_info.classes[0]
        assert cls.name == "SimpleClass"
        assert cls.docstring == "A simple class."
        assert len(cls.methods) == 2
        assert cls.methods[0].name == "__init__"
        assert cls.methods[1].name == "get_value"

    def test_parse_complex_imports(self):
        """Test parsing complex import statements."""
        source = """
import os.path
from typing import List, Dict, Optional
from ..parent import ParentClass
from . import sibling
import numpy as np
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(source)

        assert len(module_info.imports) == 5

        # Check specific imports
        numpy_import = next(i for i in module_info.imports if i.alias == "np")
        assert numpy_import.module == "numpy"

        typing_import = next(i for i in module_info.imports if i.module == "typing")
        assert set(typing_import.names) == {"List", "Dict", "Optional"}

        relative_import = next(i for i in module_info.imports if i.level == 2)
        assert relative_import.module == "parent"

    def test_parse_async_functions(self):
        """Test parsing async functions."""
        source = '''
async def async_function():
    """An async function."""
    await some_operation()

def sync_function():
    """A sync function."""
    pass
'''

        parser = PythonASTParser()
        module_info = parser.parse_source(source)

        assert len(module_info.functions) == 2

        async_func = module_info.functions[0]
        assert async_func.name == "async_function"
        assert async_func.is_async is True

        sync_func = module_info.functions[1]
        assert sync_func.name == "sync_function"
        assert sync_func.is_async is False

    def test_cyclomatic_complexity(self):
        """Test cyclomatic complexity calculation."""
        source = """
def simple_function():
    return 1

def complex_function(x):
    if x > 0:
        if x > 10:
            return "big"
        else:
            return "small"
    elif x < 0:
        return "negative"
    else:
        return "zero"

def loop_function(items):
    for item in items:
        if item:
            process(item)
    while condition:
        do_something()
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(source)

        assert module_info.functions[0].complexity == 1  # simple_function
        assert module_info.functions[1].complexity >= 4  # complex_function
        assert module_info.functions[2].complexity >= 3  # loop_function


class TestModuleAnalyzer:
    """Test module analysis functionality."""

    def test_analyze_module(self, tmp_path):
        """Test analyzing a module file."""
        # Create a test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text('''
"""Test module."""

def public_function():
    pass

def _private_function():
    pass

class PublicClass:
    pass

class _PrivateClass:
    pass
''')

        analyzer = ModuleAnalyzer()
        module_info = analyzer.analyze_module(test_file)

        assert module_info.path == test_file
        assert len(module_info.functions) == 2
        assert len(module_info.classes) == 2

    def test_extract_module_signature(self):
        """Test extracting module signatures."""
        source = '''
"""Module with explicit exports."""

__all__ = ["public_func", "PublicClass"]

def public_func():
    """A public function."""
    pass

def other_func():
    """Not in __all__."""
    pass

class PublicClass:
    """A public class."""

    def method(self):
        pass

    def _private_method(self):
        pass
'''

        parser = PythonASTParser()
        module_info = parser.parse_source(source, Path("test.py"))

        analyzer = ModuleAnalyzer()
        signature = analyzer.extract_module_signature(module_info)

        assert set(signature.exports) == {"public_func", "PublicClass"}
        assert "public_func" in signature.functions
        assert "PublicClass" in signature.classes
        assert "method" in signature.classes["PublicClass"]
        assert "_private_method" not in signature.classes["PublicClass"]

    def test_build_import_graph(self, tmp_path):
        """Test building import dependency graph."""
        # Create test modules
        (tmp_path / "module_a.py").write_text("import module_b")
        (tmp_path / "module_b.py").write_text("import module_c")
        (tmp_path / "module_c.py").write_text("import module_a")  # Circular

        analyzer = ModuleAnalyzer()
        import_graph = analyzer.build_import_graph(tmp_path)

        assert len(import_graph) == 3
        assert any("module_b" in edge.target for edge in import_graph["module_a"])

    def test_find_circular_dependencies(self):
        """Test detecting circular dependencies."""
        from a1.deep_context.module_analyzer import DependencyEdge

        # Create a simple circular dependency graph
        import_graph = {
            "a": [DependencyEdge("a", "b", "import", [], 1)],
            "b": [DependencyEdge("b", "c", "import", [], 1)],
            "c": [DependencyEdge("c", "a", "import", [], 1)],
        }

        analyzer = ModuleAnalyzer()
        cycles = analyzer.find_circular_dependencies(import_graph)

        assert len(cycles) > 0
        # Should find the a->b->c->a cycle
        cycle = cycles[0]
        assert len(cycle) == 4  # includes return to start
        assert set(cycle[:3]) == {"a", "b", "c"}


class TestSymbolTable:
    """Test symbol table functionality."""

    def test_add_and_retrieve_symbols(self):
        """Test adding and retrieving symbols."""
        from a1.deep_context.symbol_table import Symbol, SymbolLocation

        table = SymbolTable()

        # Add a function symbol
        func_symbol = Symbol(
            name="test_func",
            qualified_name="module.test_func",
            symbol_type=SymbolType.FUNCTION,
            location=SymbolLocation(file_path=Path("test.py"), line_start=10, line_end=15),
            docstring="Test function",
        )

        table.add_symbol(func_symbol)

        # Retrieve by qualified name
        retrieved = table.get_symbol("module.test_func")
        assert retrieved is not None
        assert retrieved.name == "test_func"
        assert retrieved.docstring == "Test function"

        # Find by simple name
        found = table.find_symbols_by_name("test_func")
        assert len(found) == 1
        assert found[0].qualified_name == "module.test_func"

    def test_symbol_relationships(self):
        """Test adding and querying symbol relationships."""
        from a1.deep_context.symbol_table import Symbol, SymbolLocation, SymbolRelation

        table = SymbolTable()

        # Add two symbols
        caller = Symbol(
            name="caller",
            qualified_name="module.caller",
            symbol_type=SymbolType.FUNCTION,
            location=SymbolLocation(Path("test.py"), 1, 5),
        )
        callee = Symbol(
            name="callee",
            qualified_name="module.callee",
            symbol_type=SymbolType.FUNCTION,
            location=SymbolLocation(Path("test.py"), 10, 15),
        )

        table.add_symbol(caller)
        table.add_symbol(callee)

        # Add a call relationship
        relation = SymbolRelation(
            source="module.caller",
            target="module.callee",
            relation_type="calls",
            location=SymbolLocation(Path("test.py"), 3, 3),
        )

        table.add_relation(relation)

        # Query relations
        relations = table.get_relations("module.caller")
        assert len(relations) == 1
        assert relations[0].target == "module.callee"
        assert relations[0].relation_type == "calls"

    def test_call_graph_generation(self):
        """Test generating call graphs."""
        from a1.deep_context.symbol_table import Symbol, SymbolLocation, SymbolRelation

        table = SymbolTable()

        # Create a simple call hierarchy
        symbols = ["main", "func_a", "func_b", "func_c"]
        for sym in symbols:
            table.add_symbol(
                Symbol(
                    name=sym,
                    qualified_name=f"module.{sym}",
                    symbol_type=SymbolType.FUNCTION,
                    location=SymbolLocation(Path("test.py"), 1, 1),
                )
            )

        # Add call relationships
        table.add_relation(
            SymbolRelation("module.main", "module.func_a", "calls", SymbolLocation(Path("test.py"), 1, 1))
        )
        table.add_relation(
            SymbolRelation("module.func_a", "module.func_b", "calls", SymbolLocation(Path("test.py"), 1, 1))
        )
        table.add_relation(
            SymbolRelation("module.func_a", "module.func_c", "calls", SymbolLocation(Path("test.py"), 1, 1))
        )

        # Generate call graph
        call_graph = table.get_call_graph("module.main", max_depth=2)

        assert "module.main" in call_graph
        assert "module.func_a" in call_graph["module.main"]
        assert "module.func_b" in call_graph["module.func_a"]
        assert "module.func_c" in call_graph["module.func_a"]


class TestSymbolBuilder:
    """Test symbol table builder."""

    def test_process_file(self, tmp_path):
        """Test processing a file into symbol table."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text('''
"""Test module."""

class TestClass:
    """Test class."""

    def method(self, x):
        """Test method."""
        return x * 2

def test_function():
    """Test function."""
    obj = TestClass()
    return obj.method(5)
''')

        table = SymbolTable()
        builder = SymbolBuilder(table)

        builder.process_file(test_file, "test_module")

        # Check symbols were added
        assert table.get_symbol("test_module") is not None
        assert table.get_symbol("test_module.TestClass") is not None
        assert table.get_symbol("test_module.TestClass.method") is not None
        assert table.get_symbol("test_module.test_function") is not None

        # Check relationships
        relations = table.get_relations("test_module.test_function", "calls")
        # Should have detected the method call
        assert len(relations) > 0

    def test_process_directory(self, tmp_path):
        """Test processing a directory of Python files."""
        # Create package structure
        pkg_dir = tmp_path / "package"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module1.py").write_text("def func1(): pass")
        (pkg_dir / "module2.py").write_text("def func2(): pass")

        sub_pkg = pkg_dir / "subpackage"
        sub_pkg.mkdir()
        (sub_pkg / "__init__.py").write_text("")
        (sub_pkg / "submodule.py").write_text("def subfunc(): pass")

        table = SymbolTable()
        builder = SymbolBuilder(table)

        builder.process_directory(pkg_dir, "package")

        # Check all modules were processed
        assert table.get_symbol("package") is not None
        assert table.get_symbol("package.module1") is not None
        assert table.get_symbol("package.module2") is not None
        assert table.get_symbol("package.subpackage") is not None
        assert table.get_symbol("package.subpackage.submodule") is not None

        # Check functions
        assert table.get_symbol("package.module1.func1") is not None
        assert table.get_symbol("package.module2.func2") is not None
        assert table.get_symbol("package.subpackage.submodule.subfunc") is not None
