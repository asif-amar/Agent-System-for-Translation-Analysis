"""
Logging configuration for the translation analysis pipeline.

This module sets up structured logging with appropriate formatters and handlers.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    experiment_id: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the application.

    Sets up logging with both console and file handlers. File logs are saved
    with timestamps for each experiment run.

    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional custom log file path. If None, creates timestamped file
        experiment_id: Optional experiment ID to include in log filename

    Returns:
        Configured root logger

    Example:
        >>> logger = setup_logging(log_level="DEBUG", experiment_id="exp_001")
        >>> logger.info("Starting experiment")
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Generate log filename if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_suffix = f"_{experiment_id}" if experiment_id else ""
        log_file = log_dir / f"experiment_{timestamp}{exp_suffix}.log"

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set root logger level
    root_logger.setLevel(numeric_level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(
        fmt="[%(levelname)s] %(message)s"
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File handler (all levels based on log_level)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Log initialization
    root_logger.info(f"Logging initialized - Level: {log_level} - File: {log_file}")

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class ExperimentLogger:
    """
    Context manager for experiment-specific logging.

    This class provides a context manager that sets up logging for an experiment
    and ensures proper cleanup.

    Example:
        >>> with ExperimentLogger(experiment_id="exp_001", log_level="DEBUG") as logger:
        ...     logger.info("Running experiment")
        ...     # Experiment code here
    """

    def __init__(
        self,
        experiment_id: str,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        """
        Initialize the experiment logger.

        Args:
            experiment_id: Unique identifier for the experiment
            log_level: Logging level
            log_file: Optional custom log file path
        """
        self.experiment_id = experiment_id
        self.log_level = log_level
        self.log_file = log_file
        self.logger = None

    def __enter__(self) -> logging.Logger:
        """Set up logging when entering context."""
        self.logger = setup_logging(
            log_level=self.log_level,
            log_file=self.log_file,
            experiment_id=self.experiment_id,
        )

        self.logger.info("=" * 70)
        self.logger.info(f"Experiment started: {self.experiment_id}")
        self.logger.info("=" * 70)

        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up logging when exiting context."""
        if self.logger:
            if exc_type is None:
                self.logger.info("=" * 70)
                self.logger.info(f"Experiment completed successfully: {self.experiment_id}")
                self.logger.info("=" * 70)
            else:
                self.logger.error("=" * 70)
                self.logger.error(f"Experiment failed: {self.experiment_id}")
                self.logger.error(f"Error: {exc_type.__name__}: {exc_val}")
                self.logger.error("=" * 70)

        return False  # Don't suppress exceptions


def log_experiment_config(logger: logging.Logger, config: dict) -> None:
    """
    Log experiment configuration in a structured format.

    Args:
        logger: Logger instance
        config: Configuration dictionary to log
    """
    logger.info("Experiment Configuration:")
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
