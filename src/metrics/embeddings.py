"""
Embedding generation module for semantic vector representations.

This module provides functionality to generate semantic embeddings of text
using sentence-transformers or OpenAI models.
"""

import logging
from typing import List, Optional, Union
import numpy as np


class Embedder:
    """
    Generate semantic embeddings for text.

    This class handles loading embedding models and generating vector
    representations of text for semantic similarity calculations.

    Attributes:
        model_name: Name of the embedding model to use
        model: Loaded embedding model
        logger: Logger instance
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_openai: bool = False,
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize the embedder.

        Args:
            model_name: Name of the embedding model
                       For sentence-transformers: 'all-MiniLM-L6-v2', 'all-mpnet-base-v2'
                       For OpenAI: 'text-embedding-3-small', 'text-embedding-3-large'
            use_openai: Whether to use OpenAI embeddings (requires API key)
            openai_api_key: OpenAI API key (required if use_openai=True)

        Raises:
            ValueError: If use_openai=True but no API key provided
            ImportError: If required library is not installed
        """
        self.model_name = model_name
        self.use_openai = use_openai
        self.logger = logging.getLogger(self.__class__.__name__)

        if use_openai:
            if not openai_api_key:
                raise ValueError("OpenAI API key required when use_openai=True")

            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_api_key)
                self.model = None
                self.logger.info(f"Initialized OpenAI embeddings with model: {model_name}")
            except ImportError:
                raise ImportError(
                    "OpenAI library not installed. Install with: pip install openai"
                )
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
                self.client = None
                self.logger.info(
                    f"Loaded sentence-transformer model: {model_name} "
                    f"(dimension: {self.model.get_sentence_embedding_dimension()})"
                )
            except ImportError:
                raise ImportError(
                    "sentence-transformers library not installed. "
                    "Install with: pip install sentence-transformers"
                )

    def encode(
        self,
        text: Union[str, List[str]],
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for text.

        Args:
            text: Single text string or list of texts
            normalize: Whether to normalize embeddings to unit length

        Returns:
            Numpy array of embeddings
            - For single text: shape (embedding_dim,)
            - For list of texts: shape (num_texts, embedding_dim)

        Raises:
            ValueError: If text is empty
        """
        if isinstance(text, str):
            if not text.strip():
                raise ValueError("Input text cannot be empty")
            texts = [text]
            single_input = True
        else:
            if not text or any(not t.strip() for t in text):
                raise ValueError("Input texts cannot be empty")
            texts = text
            single_input = False

        if self.use_openai:
            embeddings = self._encode_openai(texts)
        else:
            embeddings = self._encode_sentence_transformer(texts, normalize)

        if single_input:
            return embeddings[0]

        return embeddings

    def _encode_sentence_transformer(
        self,
        texts: List[str],
        normalize: bool
    ) -> np.ndarray:
        """
        Generate embeddings using sentence-transformers.

        Args:
            texts: List of texts to encode
            normalize: Whether to normalize embeddings

        Returns:
            Numpy array of embeddings
        """
        self.logger.debug(f"Encoding {len(texts)} texts with sentence-transformers")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        )

        return np.array(embeddings)

    def _encode_openai(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings using OpenAI API.

        Args:
            texts: List of texts to encode

        Returns:
            Numpy array of embeddings
        """
        self.logger.debug(f"Encoding {len(texts)} texts with OpenAI")

        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text,
            )
            embeddings.append(response.data[0].embedding)

        return np.array(embeddings)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of embeddings.

        Returns:
            Embedding dimension size
        """
        if self.use_openai:
            # OpenAI embedding dimensions
            if "small" in self.model_name:
                return 1536
            elif "large" in self.model_name:
                return 3072
            else:
                return 1536  # Default
        else:
            return self.model.get_sentence_embedding_dimension()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Embedder("
            f"model={self.model_name}, "
            f"use_openai={self.use_openai}, "
            f"dim={self.get_embedding_dimension()})"
        )


class EmbeddingError(Exception):
    """Exception raised when embedding generation fails."""

    pass
