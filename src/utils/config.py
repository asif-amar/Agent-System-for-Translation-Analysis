"""
Configuration management module.

This module handles loading and validating configuration from environment variables.
"""

import os
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """
    Configuration manager for the translation analysis pipeline.

    Loads configuration from environment variables and provides validation.

    Attributes:
        anthropic_api_key: Anthropic API key for Claude
        openai_api_key: OpenAI API key (optional)
        translation_model: Model to use for translation
        embedding_model: Model to use for embeddings
        use_openai_embeddings: Whether to use OpenAI for embeddings
        default_error_rates: Default error rates to test
        random_seed: Random seed for reproducibility
        max_retries: Maximum retry attempts for API calls
        timeout_seconds: Timeout for API calls
        cache_enabled: Whether to enable API response caching
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration from environment variables.

        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        # Load environment variables from .env file
        if env_file is None:
            env_file = Path(__file__).parent.parent.parent / ".env"

        if Path(env_file).exists():
            load_dotenv(env_file)

        # API Keys
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Model Configuration
        self.translation_model = os.getenv(
            "TRANSLATION_MODEL",
            "claude-3-5-sonnet-20250929"
        )
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "all-MiniLM-L6-v2"
        )
        self.use_openai_embeddings = os.getenv(
            "USE_OPENAI_EMBEDDINGS",
            "false"
        ).lower() == "true"

        # Experiment Settings
        error_rates_str = os.getenv("DEFAULT_ERROR_RATES", "0,10,25,35,50")
        self.default_error_rates = [
            float(x) / 100 for x in error_rates_str.split(",")
        ]

        self.random_seed = int(os.getenv("RANDOM_SEED", "42"))

        # Performance Tuning
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "30"))
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"

        # Validate configuration
        self.validate()

    def validate(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )

        if self.use_openai_embeddings and not self.openai_api_key:
            raise ValueError(
                "USE_OPENAI_EMBEDDINGS is true but OPENAI_API_KEY is not set. "
                "Please provide an OpenAI API key or use local embeddings."
            )

        if not all(0.0 <= rate <= 1.0 for rate in self.default_error_rates):
            raise ValueError(
                f"Error rates must be between 0 and 1. Got: {self.default_error_rates}"
            )

        if self.max_retries < 1:
            raise ValueError(f"MAX_RETRIES must be at least 1. Got: {self.max_retries}")

        if self.timeout_seconds < 1:
            raise ValueError(
                f"TIMEOUT_SECONDS must be at least 1. Got: {self.timeout_seconds}"
            )

    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary (excluding sensitive data).

        Returns:
            Dictionary of configuration values
        """
        return {
            "translation_model": self.translation_model,
            "embedding_model": self.embedding_model,
            "use_openai_embeddings": self.use_openai_embeddings,
            "default_error_rates": self.default_error_rates,
            "random_seed": self.random_seed,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "cache_enabled": self.cache_enabled,
        }

    def __repr__(self) -> str:
        """String representation (safe, no secrets)."""
        return f"Config({self.to_dict()})"


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment.

    Args:
        env_file: Optional path to .env file

    Returns:
        Config instance

    Example:
        >>> config = load_config()
        >>> print(config.translation_model)
        claude-3-5-sonnet-20250929
    """
    return Config(env_file=env_file)
