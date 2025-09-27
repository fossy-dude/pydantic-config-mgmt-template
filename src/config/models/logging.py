"""Logging configuration model."""

import logging
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class LogLevel(str, Enum):
    """Valid Python logging levels."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingConfig(BaseModel):
    """Configuration for application logging."""

    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        min_length=1,
        description="Python logging format string",
    )
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_format_string(cls, v: str) -> str:
        """
        Validate that the log format string is safe and well-formed.

        Parameters
        ----------
        v : str
            The log format string to validate.

        Returns
        -------
        str
            The validated format string.

        Raises
        ------
        ValueError
            If the format string contains potentially unsafe patterns.
        """
        # Check for potentially dangerous format specifiers
        if any(dangerous in v for dangerous in ["%{", "%(", ")", "{"]):
            try:
                # Test the format string with dummy data
                test_record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg="test",
                    args=(),
                    exc_info=None,
                )
                _ = v % test_record.__dict__
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Invalid log format string: {e}") from e
        return v
