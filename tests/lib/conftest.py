import logging
from io import StringIO
from typing import Callable, Tuple

import pytest

from src.lib.logger import COLORS, RESET, IndentColoredLogger


@pytest.fixture()
def logger_with_stream() -> Tuple[IndentColoredLogger, StringIO]:
    """Create a debug level logger with captured log stream.

    Returns:
        Tuple[IndentColoredLogger, StringIO]: logger instance and log stream
    """
    # set up an IO stream
    stream = StringIO()

    # set up logging settings
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    # instantiate logger and attach handlers and config
    logger = IndentColoredLogger(name="test_logger")

    # clear default handlers
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger, stream


@pytest.fixture()
def strip_color() -> Callable[[str, str], str]:
    """Return a function to strip color prefixes and suffixes from logged text.

    Returns:
        Callable[[str, str], str]: returned function
    """

    def _strip_color(message: str, log_level: str) -> str:
        """Strip color info from a logged message from `IndentColoredLogger`

        Args:
            message (str): logged message
            log_level (str): log level

        Returns:
            str: message stripped of color prefix nad suffic
        """
        start = COLORS.get(log_level, "")
        return message.removeprefix(start).removesuffix(RESET)

    return _strip_color
