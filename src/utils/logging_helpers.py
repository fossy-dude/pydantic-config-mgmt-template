import logging
from enum import StrEnum


def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)


class ProgressStage(StrEnum):
    """Enumeration of progress stages for logging."""

    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"


def log_progress(
    logger: logging.Logger,
    module: str,
    stage: ProgressStage = ProgressStage.STARTED,
    level: int = logging.DEBUG,
    **kwargs,
) -> None:
    """Log the current stage of processing."""
    logger.log(level, "Processing - %s: %s", module, stage, **kwargs)
