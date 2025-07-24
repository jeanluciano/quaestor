"""Tests for A1 semantic code understanding."""

import tempfile
from pathlib import Path

from src.a1.deep_context.ast_parser import FunctionInfo, PythonASTParser
from src.a1.deep_context.semantic_understanding import (
    CodeEmbedding,
    SimilarityEngine,
    TypeDatabase,
    TypeInferenceEngine,
    TypeInfo,
)


class TestTypeInference:
    """Test type inference engine."""

    def test_infer_constant_types(self):
        """Test inference of constant types."""
        engine = TypeInferenceEngine()

        code = """
x = 42
y = 3.14
z = "hello"
flag = True
nothing = None
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code)
        types = engine.infer_module_types(module_info)

        assert types["x"].type_name == "int"
        assert types["y"].type_name == "float"
        assert types["z"].type_name == "str"
        assert types["flag"].type_name == "bool"
        assert types["nothing"].type_name == "NoneType"

    def test_infer_collection_types(self):
        """Test inference of collection types."""
        engine = TypeInferenceEngine()

        code = """
numbers = [1, 2, 3]
mixed = [1, "two", 3.0]
mapping = {"key": "value", "count": 42}
items = {1, 2, 3}
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code)
        types = engine.infer_module_types(module_info)

        assert types["numbers"].type_name == "list"
        assert types["numbers"].is_generic
        assert "int" in types["numbers"].type_params

        assert types["mapping"].type_name == "dict"
        assert types["items"].type_name == "set"

    def test_infer_function_types(self):
        """Test inference of function types."""
        engine = TypeInferenceEngine()

        code = """
def add(x, y):
    return x + y

def greet(name: str) -> str:
    return f"Hello, {name}"

async def fetch_data():
    return {"data": "value"}
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code)
        types = engine.infer_module_types(module_info)

        assert types["add"].type_name == "Callable"
        assert types["greet"].type_name == "Callable"
        assert types["fetch_data"].type_name == "Callable"

    def test_infer_class_types(self):
        """Test inference of class types."""
        engine = TypeInferenceEngine()

        code = """
class Person:
    def __init__(self, name: str):
        self.name = name

class Employee(Person):
    pass
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code)
        types = engine.infer_module_types(module_info)

        assert "Person" in types
        assert types["Person"].type_name == "Person"
        assert "Employee" in types
        assert types["Employee"].type_name == "Employee"

    def test_type_inference_with_operations(self):
        """Test type inference with operations."""
        engine = TypeInferenceEngine()

        code = """
x = 10
y = 20
sum_xy = x + y
product = x * y
division = x / y
comparison = x > y
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code)
        types = engine.infer_module_types(module_info)

        assert types["sum_xy"].type_name == "int"
        assert types["product"].type_name == "int"
        assert types["division"].type_name == "float"
        assert types["comparison"].type_name == "bool"


class TestTypeDatabase:
    """Test type database storage."""

    def test_store_and_retrieve_types(self):
        """Test storing and retrieving type information."""
        db = TypeDatabase()

        # Store some types
        type_info1 = TypeInfo("str", "builtins", confidence=0.9)
        db.store_type("module.func1", "module", "func1", type_info1)

        type_info2 = TypeInfo("list", "builtins", is_generic=True, type_params=["int"])
        db.store_type("module.func2", "module", "func2", type_info2)

        # Retrieve types
        retrieved1 = db.get_type("module.func1")
        assert retrieved1.type_name == "str"
        assert retrieved1.confidence == 0.9

        retrieved2 = db.get_type("module.func2")
        assert retrieved2.type_name == "list"
        assert retrieved2.is_generic
        assert retrieved2.type_params == ["int"]

    def test_find_symbols_by_type(self):
        """Test finding symbols by type."""
        db = TypeDatabase()

        # Store various types
        db.store_type("mod1.func1", "mod1", "func1", TypeInfo("str"))
        db.store_type("mod1.func2", "mod1", "func2", TypeInfo("int"))
        db.store_type("mod2.func3", "mod2", "func3", TypeInfo("str"))

        # Find all str functions
        str_symbols = db.find_symbols_by_type("str")
        assert len(str_symbols) == 2

        # Find str functions in specific module
        mod1_str = db.find_symbols_by_type("str", "mod1")
        assert len(mod1_str) == 1
        assert mod1_str[0][2] == "func1"

    def test_get_module_types(self):
        """Test getting all types for a module."""
        db = TypeDatabase()

        # Store types for a module
        db.store_type("mymod.func1", "mymod", "func1", TypeInfo("int"))
        db.store_type("mymod.func2", "mymod", "func2", TypeInfo("str"))
        db.store_type("mymod.MyClass", "mymod", "MyClass", TypeInfo("MyClass", "mymod"))

        # Get all module types
        module_types = db.get_module_types("mymod")
        assert len(module_types) == 3
        assert module_types["func1"].type_name == "int"
        assert module_types["func2"].type_name == "str"
        assert module_types["MyClass"].type_name == "MyClass"

    def test_type_statistics(self):
        """Test database statistics."""
        db = TypeDatabase()

        # Store various types
        db.store_type("m.f1", "m", "f1", TypeInfo("int", source="annotation"))
        db.store_type("m.f2", "m", "f2", TypeInfo("str", source="inference", confidence=0.8))
        db.store_type("m.f3", "m", "f3", TypeInfo("list", is_generic=True))

        stats = db.get_statistics()
        assert stats["total_types"] == 3
        assert stats["by_source"]["annotation"] == 1
        assert stats["by_source"]["inference"] == 2
        assert stats["generic_types"] == 1


class TestCodeEmbedding:
    """Test code embedding generation."""

    def test_tokenize_identifier(self):
        """Test identifier tokenization."""
        embedder = CodeEmbedding()

        # Test snake_case
        tokens = embedder._tokenize_identifier("get_user_name")
        assert tokens == ["get", "user", "name"]

        # Test camelCase
        tokens = embedder._tokenize_identifier("getUserName")
        assert tokens == ["get", "user", "name"]

        # Test mixed
        tokens = embedder._tokenize_identifier("get_userName")
        assert tokens == ["get", "user", "name"]

    def test_generate_function_embedding(self):
        """Test function embedding generation."""
        embedder = CodeEmbedding(vector_size=64)

        func_info = FunctionInfo(
            name="calculate_total",
            line_start=1,
            line_end=5,
            arguments=["items", "tax_rate"],
            decorators=[],
            complexity=3,
        )

        embedding = embedder.generate_function_embedding(func_info)

        assert len(embedding.vector) == 64
        assert all(isinstance(x, float) for x in embedding.vector)
        assert embedding.symbol_id == "calculate_total"
        assert embedding.metadata["type"] == "function"
        assert embedding.metadata["complexity"] == 3

    def test_calculate_similarity(self):
        """Test similarity calculation."""
        embedder = CodeEmbedding(vector_size=32)

        # Create two similar functions
        func1 = FunctionInfo(
            name="add_numbers", line_start=1, line_end=3, arguments=["a", "b"], decorators=[], complexity=1
        )

        func2 = FunctionInfo(
            name="sum_values", line_start=1, line_end=3, arguments=["x", "y"], decorators=[], complexity=1
        )

        # Create a different function
        func3 = FunctionInfo(
            name="parse_xml_document",
            line_start=1,
            line_end=50,
            arguments=["xml_string", "schema", "validate"],
            decorators=["lru_cache"],
            complexity=10,
        )

        emb1 = embedder.generate_function_embedding(func1)
        emb2 = embedder.generate_function_embedding(func2)
        emb3 = embedder.generate_function_embedding(func3)

        # Similar functions should have higher similarity
        sim_12 = embedder.calculate_similarity(emb1, emb2)
        sim_13 = embedder.calculate_similarity(emb1, emb3)

        assert 0 <= sim_12 <= 1
        assert 0 <= sim_13 <= 1
        assert sim_12 > sim_13  # func1 and func2 are more similar


class TestSimilarityEngine:
    """Test code similarity detection."""

    def test_find_similar_functions(self):
        """Test finding similar functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test files
            (root / "math_utils.py").write_text("""
def add(a, b):
    return a + b

def subtract(x, y):
    return x - y

def multiply(a, b):
    result = a * b
    return result
""")

            (root / "string_utils.py").write_text("""
def concat(str1, str2):
    return str1 + str2

def add_numbers(num1, num2):
    return num1 + num2
""")

            # Index codebase
            engine = SimilarityEngine(similarity_threshold=0.5)
            engine.index_codebase(root)

            # Find similar to 'add'
            matches = engine.find_similar_functions(f"{root}/math_utils.py::add", top_k=3)

            assert len(matches) > 0
            # Should find add_numbers as similar
            assert any("add_numbers" in match.target_id for match in matches)

    def test_detect_clones(self):
        """Test clone detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files with clones
            (root / "module1.py").write_text("""
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

def filter_positive(values):
    output = []
    for val in values:
        if val > 0:
            output.append(val)
    return output
""")

            (root / "module2.py").write_text("""
def process_items(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
""")

            # Index and detect clones
            engine = SimilarityEngine()
            engine.index_codebase(root)

            clone_results = engine.detect_clones(min_clone_type=3)

            assert len(clone_results) > 0
            # Should detect process_data and process_items as clones

    def test_find_similar_to_snippet(self):
        """Test finding functions similar to a code snippet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test file
            (root / "utils.py").write_text("""
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def compute_mean(values):
    if len(values) == 0:
        return 0.0
    total = sum(values)
    return total / len(values)
""")

            # Index codebase with lower threshold
            engine = SimilarityEngine(similarity_threshold=0.3)
            engine.index_codebase(root)

            # Search with snippet
            snippet = """
def avg(nums):
    return sum(nums) / len(nums) if nums else 0
"""

            matches = engine.find_similar_to_snippet(snippet, top_k=10)

            assert len(matches) > 0
            # Should find both calculate_average and compute_mean

    def test_embedding_retrieval(self):
        """Test retrieving embeddings."""
        engine = SimilarityEngine(embedding_size=32)

        # Create a simple module
        code = """
def test_function():
    return 42
"""

        parser = PythonASTParser()
        module_info = parser.parse_source(code, Path("test.py"))

        # Build vocabulary and generate embedding
        engine.embedding_generator.build_vocabulary([module_info])

        for func in module_info.functions:
            func_id = f"test.py::{func.name}"
            embedding = engine.embedding_generator.generate_function_embedding(func)
            engine._function_embeddings[func_id] = embedding

        # Retrieve embedding
        retrieved = engine.get_embedding("test.py::test_function")
        assert retrieved is not None
        assert len(retrieved.vector) == 32
