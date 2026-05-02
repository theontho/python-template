import logging
from typing import Optional

from rich.logging import RichHandler


class EmojiFormatter(logging.Formatter):
    """Custom formatter to add emojis to log levels."""

    level_emojis = {
        logging.DEBUG: "🐞",
        logging.INFO: "ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Replace the levelname with just the emoji
        record.levelname = self.level_emojis.get(record.levelno, record.levelname)
        return super().format(record)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging with format: [timestamp file:line] emoji message
    """
    handlers: list[logging.Handler] = []

    # Rich handler for console output
    rich_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_path=False,
        show_time=False,  # We'll include time in our own format string
        show_level=False,
        omit_repeated_times=False,
    )

    # Format: [%(asctime)s %(filename)s:%(lineno)d] %(levelname)s %(message)s
    # Note: RichHandler will still handle the rich output, but with our custom structure
    rich_handler.setFormatter(
        EmojiFormatter("[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s %(message)s", datefmt="%X")
    )
    handlers.append(rich_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        handlers=handlers,
    )

    logging.getLogger("pydantic").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
