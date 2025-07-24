"""Code embedding generation for similarity detection.

This module generates numerical representations of code using AST analysis
and identifier tokenization, without requiring external models or APIs.
"""

import ast
import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import log, sqrt

from a1.core.event_bus import EventBus

from ..ast_parser import FunctionInfo, ModuleInfo


@dataclass
class CodeVector:
    """Vector representation of code."""

    symbol_id: str
    vector: list[float]
    metadata: dict[str, any] = field(default_factory=dict)
    feature_names: list[str] = field(default_factory=list)


class CodeEmbedding:
    """Generate embeddings for code using local analysis."""

    def __init__(self, vector_size: int = 128, event_bus: EventBus | None = None):
        """Initialize the code embedding generator.

        Args:
            vector_size: Size of the embedding vectors
            event_bus: Optional event bus for embedding events
        """
        self.vector_size = vector_size
        self.event_bus = event_bus

        # Vocabulary for TF-IDF
        self.vocabulary: dict[str, int] = {}
        self.idf_scores: dict[str, float] = {}
        self.doc_count = 0

        # AST node type weights
        self.node_weights = {
            ast.FunctionDef: 2.0,
            ast.ClassDef: 2.0,
            ast.Call: 1.5,
            ast.For: 1.2,
            ast.While: 1.2,
            ast.If: 1.1,
            ast.Try: 1.3,
            ast.With: 1.2,
            ast.Import: 1.0,
            ast.Return: 1.0,
        }

    def build_vocabulary(self, modules: list[ModuleInfo]) -> None:
        """Build vocabulary from a collection of modules.

        Args:
            modules: List of parsed modules
        """
        term_doc_counts = defaultdict(int)
        self.doc_count = 0

        for module in modules:
            self.doc_count += 1
            terms_in_doc = set()

            # Extract identifiers from the module
            for func in module.functions:
                terms = self._tokenize_identifier(func.name)
                terms_in_doc.update(terms)

                # Also tokenize parameters
                for param in func.arguments:
                    terms_in_doc.update(self._tokenize_identifier(param))

            for cls in module.classes:
                terms_in_doc.update(self._tokenize_identifier(cls.name))

                for method in cls.methods:
                    terms_in_doc.update(self._tokenize_identifier(method.name))

            # Update document frequencies
            for term in terms_in_doc:
                term_doc_counts[term] += 1

        # Calculate IDF scores
        for term, doc_freq in term_doc_counts.items():
            self.idf_scores[term] = log(self.doc_count / doc_freq)

        # Build vocabulary (most common terms)
        sorted_terms = sorted(term_doc_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (term, _) in enumerate(sorted_terms[: self.vector_size // 2]):
            self.vocabulary[term] = i

    def generate_function_embedding(self, func: FunctionInfo, module_ast: ast.AST | None = None) -> CodeVector:
        """Generate embedding for a function.

        Args:
            func: Function information
            module_ast: Optional module AST for deeper analysis

        Returns:
            Code vector representation
        """
        # Initialize features
        features = [0.0] * self.vector_size

        # 1. Structural features (first quarter of vector)
        struct_features = self._extract_structural_features(func, module_ast)
        struct_end = self.vector_size // 4
        features[:struct_end] = self._normalize_features(struct_features, struct_end)

        # 2. Identifier features (second quarter)
        id_features = self._extract_identifier_features(func)
        id_start = struct_end
        id_end = self.vector_size // 2
        features[id_start:id_end] = self._normalize_features(id_features, id_end - id_start)

        # 3. Pattern features (third quarter)
        pattern_features = self._extract_pattern_features(func, module_ast)
        pattern_start = id_end
        pattern_end = 3 * self.vector_size // 4
        features[pattern_start:pattern_end] = self._normalize_features(pattern_features, pattern_end - pattern_start)

        # 4. Complexity features (last quarter)
        complex_features = self._extract_complexity_features(func)
        complex_start = pattern_end
        features[complex_start:] = self._normalize_features(complex_features, self.vector_size - complex_start)

        # Normalize entire vector
        norm = sqrt(sum(x * x for x in features))
        if norm > 0:
            features = [x / norm for x in features]

        return CodeVector(
            symbol_id=func.name,
            vector=features,
            metadata={
                "type": "function",
                "lines": func.line_end - func.line_start + 1,
                "complexity": func.complexity,
            },
        )

    def generate_module_embedding(self, module: ModuleInfo) -> CodeVector:
        """Generate embedding for an entire module.

        Args:
            module: Module information

        Returns:
            Code vector representation
        """
        # Aggregate function embeddings
        if not module.functions and not module.classes:
            # Empty module
            return CodeVector(
                symbol_id=str(module.path), vector=[0.0] * self.vector_size, metadata={"type": "module", "empty": True}
            )

        # Generate embeddings for all functions
        func_embeddings = []
        for func in module.functions:
            embedding = self.generate_function_embedding(func, module.ast_tree)
            func_embeddings.append(embedding.vector)

        # Generate embeddings for all methods
        for cls in module.classes:
            for method in cls.methods:
                embedding = self.generate_function_embedding(method, module.ast_tree)
                func_embeddings.append(embedding.vector)

        # Average the embeddings
        if func_embeddings:
            avg_vector = [0.0] * self.vector_size
            for vec in func_embeddings:
                for i in range(self.vector_size):
                    avg_vector[i] += vec[i]

            avg_vector = [x / len(func_embeddings) for x in avg_vector]
        else:
            avg_vector = [0.0] * self.vector_size

        return CodeVector(
            symbol_id=str(module.path),
            vector=avg_vector,
            metadata={
                "type": "module",
                "functions": len(module.functions),
                "classes": len(module.classes),
            },
        )

    def _extract_structural_features(self, func: FunctionInfo, module_ast: ast.AST | None) -> list[float]:
        """Extract structural features from a function."""
        features = []

        # Basic metrics
        features.append(float(len(func.arguments)))  # Parameter count
        features.append(float(func.line_end - func.line_start + 1))  # Lines of code
        features.append(float(func.complexity))  # Cyclomatic complexity
        features.append(float(func.is_async))  # Async function
        features.append(float(len(func.decorators)))  # Decorator count

        # AST node frequencies
        if module_ast:
            node_counts = self._count_ast_nodes(func, module_ast)
            for node_type, weight in self.node_weights.items():
                count = node_counts.get(node_type.__name__, 0)
                features.append(count * weight)

        return features

    def _extract_identifier_features(self, func: FunctionInfo) -> list[float]:
        """Extract identifier-based features using TF-IDF."""
        features = [0.0] * (self.vector_size // 4)

        # Tokenize function name and parameters
        terms = []
        terms.extend(self._tokenize_identifier(func.name))
        for param in func.arguments:
            terms.extend(self._tokenize_identifier(param))

        # Calculate term frequencies
        term_freq = Counter(terms)

        # Convert to TF-IDF vector
        for term, freq in term_freq.items():
            if term in self.vocabulary:
                idx = self.vocabulary[term]
                if idx < len(features):
                    tf = freq / len(terms) if terms else 0
                    idf = self.idf_scores.get(term, 1.0)
                    features[idx] = tf * idf

        return features

    def _extract_pattern_features(self, func: FunctionInfo, module_ast: ast.AST | None) -> list[float]:
        """Extract code pattern features."""
        features = []

        # Pattern indicators
        patterns = {
            "getter": func.name.startswith("get_"),
            "setter": func.name.startswith("set_"),
            "test": func.name.startswith("test_"),
            "private": func.name.startswith("_"),
            "dunder": func.name.startswith("__") and func.name.endswith("__"),
            "async": func.is_async,
            "generator": False,  # Would need AST analysis
            "recursive": False,  # Would need AST analysis
        }

        for _pattern, present in patterns.items():
            features.append(float(present))

        # Decorator patterns
        decorator_patterns = {
            "property": "property" in func.decorators,
            "staticmethod": "staticmethod" in func.decorators,
            "classmethod": "classmethod" in func.decorators,
            "cached": any("cache" in dec for dec in func.decorators),
        }

        for _pattern, present in decorator_patterns.items():
            features.append(float(present))

        return features

    def _extract_complexity_features(self, func: FunctionInfo) -> list[float]:
        """Extract complexity-related features."""
        features = []

        # Normalized complexity metrics
        lines = func.line_end - func.line_start + 1

        features.append(func.complexity / max(lines, 1))  # Complexity per line
        features.append(len(func.arguments) / max(lines, 1))  # Params per line
        features.append(float(bool(func.return_annotation)))  # Has return type
        features.append(float(bool(func.docstring)))  # Has docstring

        # Docstring length (normalized)
        if func.docstring:
            features.append(min(len(func.docstring) / 100.0, 1.0))
        else:
            features.append(0.0)

        return features

    def _tokenize_identifier(self, identifier: str) -> list[str]:
        """Tokenize an identifier into meaningful parts."""
        # Handle snake_case
        parts = identifier.split("_")

        # Handle camelCase within each part
        tokens = []
        for part in parts:
            # Split on uppercase letters
            camel_parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", part)
            tokens.extend(p.lower() for p in camel_parts if p)

            # If no camelCase found, use the whole part
            if not camel_parts and part:
                tokens.append(part.lower())

        return tokens

    def _count_ast_nodes(self, func: FunctionInfo, module_ast: ast.AST) -> dict[str, int]:
        """Count AST node types within a function."""
        counts = defaultdict(int)

        # Find the function node in the AST
        for node in ast.walk(module_ast):
            if isinstance(node, ast.FunctionDef) and node.name == func.name:
                if node.lineno == func.line_start:
                    # Count nodes within this function
                    for child in ast.walk(node):
                        counts[type(child).__name__] += 1
                    break

        return counts

    def _normalize_features(self, features: list[float], target_size: int) -> list[float]:
        """Normalize features to target size using hashing trick."""
        if len(features) == target_size:
            return features

        normalized = [0.0] * target_size

        if len(features) < target_size:
            # Pad with zeros
            normalized[: len(features)] = features
        else:
            # Hash to compress
            for i, value in enumerate(features):
                # Use hash to distribute values
                hash_idx = int(hashlib.md5(str(i).encode()).hexdigest(), 16) % target_size
                normalized[hash_idx] += value

        return normalized

    def calculate_similarity(self, vec1: CodeVector, vec2: CodeVector) -> float:
        """Calculate cosine similarity between two code vectors.

        Args:
            vec1: First code vector
            vec2: Second code vector

        Returns:
            Similarity score between 0 and 1
        """
        if len(vec1.vector) != len(vec2.vector):
            raise ValueError("Vectors must have the same dimension")

        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1.vector, vec2.vector, strict=False))

        # Vectors should already be normalized, but ensure
        norm1 = sqrt(sum(x * x for x in vec1.vector))
        norm2 = sqrt(sum(x * x for x in vec2.vector))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # Clamp to [0, 1] to handle floating point errors
        return max(0.0, min(1.0, similarity))
