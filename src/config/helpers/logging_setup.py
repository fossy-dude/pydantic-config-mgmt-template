"""Logging configuration setup utility."""

import logging

import pythonjsonlogger.json

from config.models.logging import LoggingConfig


def _create_formatter(config: LoggingConfig) -> logging.Formatter:
    """
    Create a JSON logging formatter based on configuration.

    Parameters
    ----------
    config : LoggingConfig
        Logging configuration settings.

    Returns
    -------
    logging.Formatter
        Configured formatter instance (JSON).
    """
    return pythonjsonlogger.json.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s", datefmt=config.LOG_DATE_FORMAT
    )

    # Default formatter (switch if required)
    # return logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)


def _create_console_handler(config: LoggingConfig, formatter: logging.Formatter) -> logging.StreamHandler:
    """
    Create console logging handler if enabled.

    Parameters
    ----------
    config : LoggingConfig
        Logging configuration settings.
    formatter : logging.Formatter
        Formatter to apply to the handler.

    Returns
    -------
    Optional[logging.StreamHandler]
        Console handler if enabled, None otherwise.
    """
    handler = logging.StreamHandler()
    handler.setLevel(config.LOG_LEVEL.value)
    handler.setFormatter(formatter)
    return handler


def setup_logging(config: LoggingConfig, *, force_reconfigure: bool = False) -> dict[str, logging.Logger]:
    """
    Set up console-only application logging based on configuration.

    Parameters
    ----------
    config : LoggingConfig
        Logging configuration settings.
    force_reconfigure : bool, optional
        If True, clears existing handlers before reconfiguring.
        If False, skips setup if root logger already has handlers.
        Default is False for performance.

    Returns
    -------
    dict[str, logging.Logger]
        Dictionary of configured loggers by name, including 'root'.

    Raises
    ------
    ValueError
        If configuration contains invalid logging levels or formats.

    Notes
    -----
    This function configures the root logger and any specific loggers
    defined in the configuration for console-only logging with optional
    JSON formatting. For performance, it avoids reconfiguration if the
    root logger already has handlers unless force_reconfigure=True.

    The function is designed to be called multiple times safely - subsequent
    calls will not duplicate handlers unless explicitly forced.
    """
    root_logger = logging.getLogger()

    # Skip reconfiguration if already set up (unless forced)
    if root_logger.handlers and not force_reconfigure:
        loggers = {"root": root_logger}
        return loggers

    # Clear existing handlers if reconfiguring
    if force_reconfigure:
        root_logger.handlers.clear()

    # Set root logging level
    root_logger.setLevel(config.LOG_LEVEL.value)

    # Create shared formatter
    formatter = _create_formatter(config)

    # Add console handler if enabled
    console_handler = _create_console_handler(config, formatter)
    if console_handler:
        root_logger.addHandler(console_handler)

    # Configure specific loggers and collect all loggers
    loggers = {"root": root_logger}

    return loggers


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.

    Parameters
    ----------
    name : str
        Name of the logger (typically __name__ from the calling module).

    Returns
    -------
    logging.Logger
        Logger instance.

    Notes
    -----
    This is a convenience wrapper around logging.getLogger() that maintains
    consistency with the module's logging approach.
    """
    return logging.getLogger(name)


def reset_logging() -> None:
    """
    Reset all logging configuration to default state.

    Notes
    -----
    This function clears all handlers from the root logger and resets
    the logging level to WARNING. Useful for testing or when needing
    to completely reconfigure logging.
    """
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.WARNING)
