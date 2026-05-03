import logging

from python_template.log import get_logger, setup_logging


def test_get_logger() -> None:
    """Test that get_logger returns a logger with the correct name."""
    logger = get_logger("test-logger")
    assert logger.name == "test-logger"
    assert isinstance(logger, logging.Logger)


def test_setup_logging() -> None:
    """Test that setup_logging configures the root logger."""
    setup_logging(level="DEBUG")
    # We can't easily check the rich handler without more complex mocking,
    # but we can check if the level was set.
    assert logging.getLogger().level == logging.DEBUG
