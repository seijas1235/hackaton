"""Tests for shared.log module."""

from loguru import logger
from shared.log import configure_logging


def test_configure_logging():
    """Test that configure_logging runs without errors."""
    # Re-run configuration to ensure it's idempotent
    configure_logging()
    
    # Verify logger works after configuration
    logger.info("Test log message")
    logger.debug("Test debug message")
    logger.warning("Test warning message")
    
    # If we got here without exceptions, configuration succeeded
    assert True


def test_logger_levels():
    """Test that logger accepts different log levels."""
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # All should execute without raising exceptions
    assert True
