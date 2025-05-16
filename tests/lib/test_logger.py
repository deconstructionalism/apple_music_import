import logging
from io import StringIO

import pytest

from src.lib.logger import COLORS, PROMPT_LEVEL, RESET, IndentColoredLogger


@pytest.fixture
def log_stream():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    return stream, handler


@pytest.fixture
def logger_with_stream(log_stream):
    stream, handler = log_stream
    logger = IndentColoredLogger(name="test_logger")
    logger.logger.handlers = []  # Clear default handlers
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.DEBUG)
    return logger, stream


@pytest.mark.parametrize(
    "level,message",
    [
        ("debug", "Debug message"),
        ("info", "Info message"),
        ("warning", "Warning message"),
        ("error", "Error message"),
        ("critical", "Critical message"),
        ("prompt", "Prompt message"),
    ],
)
def test_log_levels(logger_with_stream, level, message):
    logger, stream = logger_with_stream
    log_method = getattr(logger, level)
    log_method(message)

    output = stream.getvalue()
    assert message in output
    assert output.startswith(COLORS[level])
    assert output.strip().endswith(RESET)


def test_indent_and_dedent(logger_with_stream):
    logger, stream = logger_with_stream

    logger.indent()
    logger.debug("Indented once")

    logger.indent(2)
    logger.debug("Indented three times")

    logger.dedent()
    logger.debug("Indented two times")

    logger.dedent(5)
    logger.debug("Dedented fully")

    logger.dedent()
    logger.debug("Dedented fully")

    output = stream.getvalue().splitlines()
    assert "  Indented once" in output[0]
    assert "      Indented three times" in output[1]
    assert "    Indented two times" in output[2]
    assert "Dedented fully" in output[3]
    assert "Dedented fully" in output[4]


def test_prompt_log_level_functionality(caplog):
    logger = logging.getLogger("test_prompt_log")
    logger.setLevel(logging.DEBUG)

    with caplog.at_level(PROMPT_LEVEL):
        logger.prompt("This is a prompt message")

    assert "This is a prompt message" in caplog.text
