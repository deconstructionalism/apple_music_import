import logging
from io import StringIO

import pytest

from src.lib.logger import COLORS, RESET, IndentColoredLogger


@pytest.fixture()
def log_stream():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    return stream, handler


@pytest.fixture()
def logger_with_stream(log_stream):
    stream, handler = log_stream
    logger = IndentColoredLogger(name="test_logger")
    logger.logger.handlers = []  # Clear default handlers
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.DEBUG)
    return logger, stream


@pytest.fixture()
def strip_color():
    def _strip_color(message: str, log_level):
        start = COLORS.get(log_level, "")
        return message.removeprefix(start).removesuffix(RESET)

    return _strip_color
