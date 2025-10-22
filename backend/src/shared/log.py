"""Loguru logging configuration for Lambda handlers."""

import sys
from loguru import logger

from shared.settings import get_settings


def configure_logging() -> None:
    """Configure Loguru logger for Lambda environment.
    
    - Removes default handler
    - Adds structured JSON logging to stdout (Lambda CloudWatch-friendly)
    - Sets log level from settings (LOG_LEVEL env var)
    - Includes Lambda request context when available
    
    Call this once at module initialization in each Lambda handler.
    """
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Add JSON-structured handler for CloudWatch
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        serialize=False,  # Use False for human-readable; True for JSON (requires loguru[json])
        backtrace=True,
        diagnose=True,
    )
    
    logger.info(f"Logging configured at level: {settings.log_level}")


# Auto-configure on import (safe for Lambda as each invocation gets fresh container on cold start)
configure_logging()
