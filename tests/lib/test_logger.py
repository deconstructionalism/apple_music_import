from io import StringIO
from typing import Callable, Tuple, TypeAlias

import pytest

from src.lib.logger import COLORS, RESET, IndentColoredLogger

LoggerWithStream: TypeAlias = Tuple[IndentColoredLogger, StringIO]
StripColor: TypeAlias = Callable[[str, str], str]


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
def test_log_levels(
    logger_with_stream: LoggerWithStream, level: str, message: str
) -> None:
    logger, stream = logger_with_stream
    log_method = getattr(logger, level)
    print(level, log_method)
    log_method(message)

    output = stream.getvalue()
    assert message in output
    assert output.startswith(COLORS[level])
    assert output.strip().endswith(RESET)


def test_indent_and_dedent(
    logger_with_stream: LoggerWithStream, strip_color: StripColor
) -> None:
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

    output = [strip_color(line, "debug") for line in stream.getvalue().splitlines()]
    assert "  Indented once" == output[0]
    assert "      Indented three times" == output[1]
    assert "    Indented two times" == output[2]
    assert "Dedented fully" == output[3]
    assert "Dedented fully" == output[4]


def test_prompt_log_level(
    logger_with_stream: LoggerWithStream, strip_color: StripColor
):
    logger, stream = logger_with_stream

    logger.prompt("This is a prompt message")
    output = strip_color(stream.getvalue().splitlines()[0], "prompt")

    assert "This is a prompt message" == output


def test_log_section(logger_with_stream: LoggerWithStream, strip_color: StripColor):
    logger, stream = logger_with_stream

    # test a section is indented and dedented
    logger.info("outside of section")
    end_section = logger.log_section("test section")
    logger.info("inside of section")
    end_section()
    logger.info("outside of section")

    output = [strip_color(line, "info") for line in stream.getvalue().splitlines()]
    assert "outside of section" == output[0]
    assert "[test section]" == output[1]
    assert "  inside of section" == output[2]
    assert "[/test section]" == output[3]
    assert "outside of section" == output[4]


def test_custom_log_section_start_and_end_formats(
    logger_with_stream: LoggerWithStream, strip_color: StripColor
):
    logger, stream = logger_with_stream

    # test that a custom start format is applied
    logger.info("outside of section")
    end_section = logger.log_section(
        "test section", "|{section_name}|", "||{section_name}||"
    )
    logger.info("inside of section")
    end_section()
    logger.info("outside of section")

    output = [strip_color(line, "info") for line in stream.getvalue().splitlines()]
    assert "outside of section" == output[0]
    assert "|test section|" == output[1]
    assert "  inside of section" == output[2]
    assert "||test section||" == output[3]
    assert "outside of section" == output[4]

    # clear the stream
    stream.seek(0)
    stream.truncate()

    # test that a custom end format on calling end section callback is applied
    logger.info("outside of section")
    end_section = logger.log_section("test section")
    logger.info("inside of section")
    end_section("|{section_name}|")
    logger.info("outside of section")

    output = [strip_color(line, "info") for line in stream.getvalue().splitlines()]
    assert "outside of section" == output[0]
    assert "[test section]" == output[1]
    assert "  inside of section" == output[2]
    assert "|test section|" == output[3]
    assert "outside of section" == output[4]
