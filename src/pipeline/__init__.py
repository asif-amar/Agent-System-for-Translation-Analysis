"""
Pipeline module for orchestrating translation experiments.

This module provides the pipeline executor for managing the complete
translation chain workflow.
"""

from .executor import TranslationPipeline

__all__ = [
    "TranslationPipeline",
]
