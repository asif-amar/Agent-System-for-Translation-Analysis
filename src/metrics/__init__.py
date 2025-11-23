"""
Metrics module for calculating vector distances and similarities.

This module provides embedding generation and distance calculation capabilities.
"""

from .embeddings import Embedder, EmbeddingError
from .distance import VectorMetrics

__all__ = [
    "Embedder",
    "EmbeddingError",
    "VectorMetrics",
]
