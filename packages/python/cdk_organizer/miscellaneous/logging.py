"""Logging Module."""

import logging
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_logging(module: str, loglevel='INFO') -> logging.Logger:
    """
    Set up logging.

    By default, the python logging module is configured to push logs to stdout as long as \
        their level is at least INFO. The log format is set to `[%(asctime)s] - %(name)s - %(message)s` and \
            the date format is set to `%Y-%m-%d %H:%M:%S`.

    To use the logger configuration add this code block in the CDK main Python script:

    ```python
    from cdk_organizer.logging import setup_logging

    logger = setup_logging(module_name, app.node.try_get_context("loglevel") or "INFO")
    ```

    To use in the modules or stacks

    ```python
    import logging

    logger = logging.getLogger(__name__)
    ```

    Args:
        module (str): python module name `string`
        loglevel (str): log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

    Returns:
        A logger instance.
    """
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(_get_formatter())
    logger = logging.getLogger(module)
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(log_handler)
    logger.setLevel(loglevel)
    return logger


def _get_formatter() -> logging.Formatter:
    """
    Get Logger Formatter `[%(asctime)s] - %(message)s`.

    Returns:
        logger formatter
    """
    fmt = "[%(asctime)s] - %(message)s"
    return logging.Formatter(
        fmt=fmt,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
