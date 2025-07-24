"""Semantic code understanding for deep context analysis.

This module provides advanced code understanding capabilities including:
- Type inference without explicit annotations
- Function signature extraction and matching
- Code similarity detection using local embeddings
- Semantic search across codebases
- Context-aware code suggestions
"""

from .code_embedding import CodeEmbedding, CodeVector
from .signature_extractor import FunctionSignature, ParameterInfo, SignatureExtractor
from .signature_index import SignatureIndex
from .similarity_engine import CloneDetectionResult, SimilarityEngine, SimilarityMatch
from .type_database import TypeDatabase
from .type_inference import TypeContext, TypeInferenceEngine, TypeInfo

__all__ = [
    "TypeInferenceEngine",
    "TypeInfo",
    "TypeContext",
    "TypeDatabase",
    "CodeEmbedding",
    "CodeVector",
    "SimilarityEngine",
    "SimilarityMatch",
    "CloneDetectionResult",
    "SignatureExtractor",
    "FunctionSignature",
    "ParameterInfo",
    "SignatureIndex",
]
