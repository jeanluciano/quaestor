"""Code similarity detection engine.

This module provides functionality to find similar code patterns,
detect code clones, and recommend similar functions.
"""

import ast
import heapq
from dataclasses import dataclass
from pathlib import Path

from a1.core.event_bus import EventBus

from ..ast_parser import FunctionInfo, PythonASTParser
from ..events import SystemEvent
from .code_embedding import CodeEmbedding, CodeVector


@dataclass
class SimilarityMatch:
    """A similarity match between code elements."""

    source_id: str
    target_id: str
    similarity_score: float
    match_type: str  # "exact", "similar", "structural"
    metadata: dict[str, any] = None


@dataclass
class CloneDetectionResult:
    """Result of clone detection analysis."""

    clone_type: int  # Type 1-4
    clones: list[tuple[str, str]]  # Pairs of similar code
    description: str


class SimilarityEngine:
    """Engine for detecting code similarity and clones."""

    def __init__(self, embedding_size: int = 128, similarity_threshold: float = 0.7, event_bus: EventBus | None = None):
        """Initialize the similarity engine.

        Args:
            embedding_size: Size of embedding vectors
            similarity_threshold: Minimum similarity for matches
            event_bus: Optional event bus for similarity events
        """
        self.embedding_generator = CodeEmbedding(embedding_size, event_bus)
        self.similarity_threshold = similarity_threshold
        self.event_bus = event_bus
        self.parser = PythonASTParser(event_bus)

        # Storage for embeddings
        self._function_embeddings: dict[str, CodeVector] = {}
        self._module_embeddings: dict[str, CodeVector] = {}

        # Clone detection thresholds
        self.clone_thresholds = {
            1: 0.95,  # Type 1: Exact clones
            2: 0.85,  # Type 2: Renamed clones
            3: 0.70,  # Type 3: Modified clones
            4: 0.60,  # Type 4: Semantic clones
        }

    def index_codebase(self, root_path: Path) -> None:
        """Index an entire codebase for similarity search.

        Args:
            root_path: Root directory of the codebase
        """
        # Find all Python files
        python_files = list(root_path.rglob("*.py"))

        # Parse all modules
        modules = []
        for file_path in python_files:
            if "__pycache__" in str(file_path):
                continue

            try:
                module_info = self.parser.parse_file(file_path)
                modules.append(module_info)
            except Exception:
                # Skip files with syntax errors
                continue

        # Build vocabulary for TF-IDF
        self.embedding_generator.build_vocabulary(modules)

        # Generate embeddings
        for module in modules:
            # Module embedding
            module_embedding = self.embedding_generator.generate_module_embedding(module)
            self._module_embeddings[str(module.path)] = module_embedding

            # Function embeddings
            for func in module.functions:
                func_id = f"{module.path}::{func.name}"
                func_embedding = self.embedding_generator.generate_function_embedding(func, module.ast_tree)
                self._function_embeddings[func_id] = func_embedding

            # Method embeddings
            for cls in module.classes:
                for method in cls.methods:
                    method_id = f"{module.path}::{cls.name}.{method.name}"
                    method_embedding = self.embedding_generator.generate_function_embedding(method, module.ast_tree)
                    self._function_embeddings[method_id] = method_embedding

        if self.event_bus:
            self.event_bus.emit(
                SystemEvent(
                    type="codebase_indexed",
                    data={
                        "modules": len(self._module_embeddings),
                        "functions": len(self._function_embeddings),
                    },
                )
            )

    def find_similar_functions(
        self, function_id: str, top_k: int = 5, min_similarity: float | None = None
    ) -> list[SimilarityMatch]:
        """Find functions similar to a given function.

        Args:
            function_id: ID of the function to match
            top_k: Number of top matches to return
            min_similarity: Minimum similarity score

        Returns:
            List of similarity matches
        """
        if function_id not in self._function_embeddings:
            return []

        source_embedding = self._function_embeddings[function_id]
        min_sim = min_similarity or self.similarity_threshold

        # Calculate similarities to all other functions
        candidates = []

        for target_id, target_embedding in self._function_embeddings.items():
            if target_id == function_id:
                continue

            similarity = self.embedding_generator.calculate_similarity(source_embedding, target_embedding)

            if similarity >= min_sim:
                match_type = self._classify_match_type(similarity)
                candidates.append((similarity, target_id, match_type))

        # Get top-k matches
        top_matches = heapq.nlargest(top_k, candidates, key=lambda x: x[0])

        results = []
        for similarity, target_id, match_type in top_matches:
            results.append(
                SimilarityMatch(
                    source_id=function_id,
                    target_id=target_id,
                    similarity_score=similarity,
                    match_type=match_type,
                    metadata={
                        "source_complexity": source_embedding.metadata.get("complexity", 0),
                        "target_complexity": self._function_embeddings[target_id].metadata.get("complexity", 0),
                    },
                )
            )

        return results

    def detect_clones(self, min_clone_type: int = 3) -> list[CloneDetectionResult]:
        """Detect code clones in the indexed codebase.

        Args:
            min_clone_type: Minimum clone type to detect (1-4)

        Returns:
            List of clone detection results
        """
        results = []

        # Check all pairs of functions
        function_ids = list(self._function_embeddings.keys())
        processed_pairs = set()

        for clone_type in range(1, min_clone_type + 1):
            threshold = self.clone_thresholds[clone_type]
            clones = []

            for i, func1_id in enumerate(function_ids):
                for func2_id in function_ids[i + 1 :]:
                    pair = tuple(sorted([func1_id, func2_id]))
                    if pair in processed_pairs:
                        continue

                    similarity = self.embedding_generator.calculate_similarity(
                        self._function_embeddings[func1_id], self._function_embeddings[func2_id]
                    )

                    if similarity >= threshold:
                        clones.append(pair)
                        processed_pairs.add(pair)

            if clones:
                results.append(
                    CloneDetectionResult(
                        clone_type=clone_type, clones=clones, description=self._get_clone_type_description(clone_type)
                    )
                )

        return results

    def find_similar_to_snippet(self, code_snippet: str, top_k: int = 5) -> list[SimilarityMatch]:
        """Find functions similar to a code snippet.

        Args:
            code_snippet: Python code snippet
            top_k: Number of top matches to return

        Returns:
            List of similarity matches
        """
        # Ensure we have embeddings
        if not self._function_embeddings:
            return []

        # Parse the snippet
        try:
            tree = ast.parse(code_snippet)
        except SyntaxError:
            return []

        # Extract function from snippet if present
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        if not functions:
            # Try to wrap in a function
            wrapped = "def _snippet():\n" + "\n".join(f"    {line}" for line in code_snippet.splitlines())
            try:
                tree = ast.parse(wrapped)
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            except SyntaxError:
                return []

        if not functions:
            return []

        # Create FunctionInfo from AST node
        func_node = functions[0]
        func_info = FunctionInfo(
            name="_snippet",
            line_start=func_node.lineno,
            line_end=func_node.end_lineno or func_node.lineno,
            arguments=[arg.arg for arg in func_node.args.args],
            decorators=[],
            docstring=ast.get_docstring(func_node),
            complexity=self._calculate_complexity(func_node),
        )

        # Generate embedding (ensure vocabulary is available)
        if not self.embedding_generator.vocabulary:
            # Build a minimal vocabulary from existing embeddings
            self.embedding_generator.vocabulary = {"snippet": 0}
            self.embedding_generator.idf_scores = {"snippet": 1.0}

        snippet_embedding = self.embedding_generator.generate_function_embedding(func_info)

        # Find similar functions
        candidates = []

        for func_id, func_embedding in self._function_embeddings.items():
            similarity = self.embedding_generator.calculate_similarity(snippet_embedding, func_embedding)

            if similarity >= self.similarity_threshold:
                match_type = self._classify_match_type(similarity)
                candidates.append((similarity, func_id, match_type))

        # Get top-k matches
        top_matches = heapq.nlargest(top_k, candidates, key=lambda x: x[0])

        results = []
        for similarity, target_id, match_type in top_matches:
            results.append(
                SimilarityMatch(
                    source_id="_snippet",
                    target_id=target_id,
                    similarity_score=similarity,
                    match_type=match_type,
                )
            )

        return results

    def get_embedding(self, function_id: str) -> CodeVector | None:
        """Get the embedding for a function.

        Args:
            function_id: Function identifier

        Returns:
            Code vector or None if not found
        """
        return self._function_embeddings.get(function_id)

    def _classify_match_type(self, similarity: float) -> str:
        """Classify the type of match based on similarity score."""
        if similarity >= 0.95:
            return "exact"
        elif similarity >= 0.8:
            return "similar"
        else:
            return "structural"

    def _get_clone_type_description(self, clone_type: int) -> str:
        """Get description for clone type."""
        descriptions = {
            1: "Type 1: Exact clones (identical except whitespace and comments)",
            2: "Type 2: Renamed clones (identical except identifiers)",
            3: "Type 3: Modified clones (similar with modifications)",
            4: "Type 4: Semantic clones (similar behavior, different implementation)",
        }
        return descriptions.get(clone_type, f"Type {clone_type}")

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.While | ast.For | ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def clear_index(self) -> None:
        """Clear all indexed embeddings."""
        self._function_embeddings.clear()
        self._module_embeddings.clear()
