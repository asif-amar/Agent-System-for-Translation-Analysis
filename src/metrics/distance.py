"""
Vector distance calculation module.

This module provides functions for calculating various distance metrics
between text embeddings to measure semantic similarity.
"""

import logging
from typing import Union, Tuple
import numpy as np
from scipy.spatial.distance import cosine, euclidean
from .embeddings import Embedder


logger = logging.getLogger(__name__)


class VectorMetrics:
    """
    Calculate vector distance metrics between texts.

    This class uses embeddings to calculate semantic similarity/distance
    between texts using various metrics.

    Attributes:
        embedder: Embedder instance for generating embeddings
    """

    def __init__(self, embedder: Embedder):
        """
        Initialize the vector metrics calculator.

        Args:
            embedder: Embedder instance to use for generating embeddings
        """
        self.embedder = embedder
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_distance(
        self,
        text1: str,
        text2: str,
        metric: str = "cosine",
    ) -> float:
        """
        Calculate distance between two texts.

        Args:
            text1: First text
            text2: Second text
            metric: Distance metric to use ('cosine', 'euclidean', 'manhattan')

        Returns:
            Distance value (float)
            - Cosine distance: 0 (identical) to 2 (opposite)
            - Euclidean distance: 0 (identical) to infinity
            - Manhattan distance: 0 (identical) to infinity

        Raises:
            ValueError: If metric is not supported or texts are invalid
        """
        supported_metrics = ['cosine', 'euclidean', 'manhattan']
        if metric not in supported_metrics:
            raise ValueError(
                f"Metric '{metric}' not supported. Use one of: {supported_metrics}"
            )

        # Generate embeddings
        emb1 = self.embedder.encode(text1, normalize=False)
        emb2 = self.embedder.encode(text2, normalize=False)

        # Calculate distance based on metric
        if metric == "cosine":
            distance = self.cosine_distance(emb1, emb2)
        elif metric == "euclidean":
            distance = self.euclidean_distance(emb1, emb2)
        elif metric == "manhattan":
            distance = self.manhattan_distance(emb1, emb2)

        self.logger.debug(
            f"Calculated {metric} distance: {distance:.4f} "
            f"(text1: {len(text1)} chars, text2: {len(text2)} chars)"
        )

        return float(distance)

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
        metric: str = "cosine",
    ) -> float:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            metric: Similarity metric to use ('cosine', 'euclidean')

        Returns:
            Similarity value (float)
            - Cosine similarity: -1 (opposite) to 1 (identical)

        Raises:
            ValueError: If metric is not supported or texts are invalid
        """
        if metric == "cosine":
            emb1 = self.embedder.encode(text1, normalize=True)
            emb2 = self.embedder.encode(text2, normalize=True)
            return self.cosine_similarity(emb1, emb2)
        elif metric == "euclidean":
            # Convert euclidean distance to similarity (inverse)
            dist = self.calculate_distance(text1, text2, metric="euclidean")
            return 1.0 / (1.0 + dist)
        else:
            raise ValueError(f"Similarity metric '{metric}' not supported")

    @staticmethod
    def cosine_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine distance between two vectors.

        Cosine distance = 1 - cosine similarity
        Range: [0, 2] where 0 means identical direction

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine distance (0 to 2)
        """
        return float(cosine(vec1, vec2))

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Cosine similarity = (vec1 · vec2) / (||vec1|| ||vec2||)
        Range: [-1, 1] where 1 means identical direction

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (-1 to 1)
        """
        return float(1.0 - cosine(vec1, vec2))

    @staticmethod
    def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Euclidean distance = sqrt(sum((vec1[i] - vec2[i])^2))
        Range: [0, infinity] where 0 means identical

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Euclidean distance (0 to infinity)
        """
        return float(euclidean(vec1, vec2))

    @staticmethod
    def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate Manhattan (L1) distance between two vectors.

        Manhattan distance = sum(|vec1[i] - vec2[i]|)
        Range: [0, infinity] where 0 means identical

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Manhattan distance (0 to infinity)
        """
        return float(np.sum(np.abs(vec1 - vec2)))

    def calculate_all_metrics(
        self,
        text1: str,
        text2: str,
    ) -> dict:
        """
        Calculate all available distance and similarity metrics.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Dictionary with all metrics:
            {
                'cosine_distance': float,
                'cosine_similarity': float,
                'euclidean_distance': float,
                'manhattan_distance': float,
            }
        """
        # Generate embeddings once
        emb1 = self.embedder.encode(text1, normalize=False)
        emb2 = self.embedder.encode(text2, normalize=False)

        # Calculate all metrics
        metrics = {
            'cosine_distance': self.cosine_distance(emb1, emb2),
            'cosine_similarity': self.cosine_similarity(emb1, emb2),
            'euclidean_distance': self.euclidean_distance(emb1, emb2),
            'manhattan_distance': self.manhattan_distance(emb1, emb2),
        }

        self.logger.debug(f"Calculated all metrics: {metrics}")

        return metrics

    def get_embeddings(
        self,
        text1: str,
        text2: str,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get embeddings for both texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Tuple of (embedding1, embedding2)
        """
        emb1 = self.embedder.encode(text1, normalize=False)
        emb2 = self.embedder.encode(text2, normalize=False)
        return emb1, emb2
