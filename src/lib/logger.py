import logging
from typing import Callable

# CONSTANTS

COLORS = {
    "debug": "\033[37m",  # White
    "info": "\033[36m",  # Cyan
    "warning": "\033[33m",  # Yellow
    "error": "\033[31m",  # Red
    "critical": "\033[41m",  # Red background
    "prompt": "\033[32m",  # Green
}
RESET = "\033[0m"

# add 'prompt' level to logger that will show at any log level setting
# (critical is level 50)
PROMPT_LEVEL = 51
logging.addLevelName(PROMPT_LEVEL, "PROMPT")


def prompt(self, message: str, *args, **kwargs):
    """
    Custom log level function to be added to global logger.

    Args:
        message (str): message to log
    """
    if self.isEnabledFor(PROMPT_LEVEL):
        self._log(PROMPT_LEVEL, message, args, **kwargs)


# add custom logger to global logger
logging.Logger.prompt = prompt


class IndentColoredLogger(object):
    """
    Custom python logger that allows consistent indentation and color coding
    of log levels.
    """

    def __init__(self, name: str = __name__, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.indent_level = 0
        self.indent_str = "  "

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def indent(self, count=1):
        """
        Indent logs by a given number of indents.

        Args:
            count (int, optional): number of indents to apply. Defaults to 1.
        """
        self.indent_level += count

    def dedent(self, count=1):
        """
        Dedent logs by a given number of dedents.

        Args:
            count (int, optional): number of dedents to apply. Defaults to 1.
        """
        self.indent_level = max(0, self.indent_level - count)

    def log_section(
        self,
        section_name: str,
        start_format="[{section_name}]",
        end_format="[/{section_name}]",
    ) -> Callable[[], None]:
        """
        Log an indented section of logic with names section start and stop
        and indented internal logging. Return a function to end a section.

        Args:
            section_name (str): the name of the section
            start_format (str): start section template string that include
                                `section_name`. Defaults to "[{section_name}]"
            end_format (str): end section template string that include
                              `section_name`. Defaults to "[/{section_name}]"
        Returns:
            Callable: callback to end a section

        """

        self.info(start_format.format(section_name=section_name))
        self.indent()

        def end_section(end_format: str = end_format):
            """
            Callback to end a section by logging and de-denting.

            Args:
                end_format (str, optional): use this to add custom data to the end
                                            section format that was acquired during
                                            the section logic. Defaults to end_format.
            """
            self.dedent()
            self.info(end_format.format(section_name=section_name))

        return end_section

    def _log(self, level: str, message: str):
        """
        Internal logging function that applies color and indentation given the log level
        and indent state of the logger, respectively.

        Args:
            level (str): log level
            message (str): message to log
        """
        indent = self.indent_str * self.indent_level
        colored_indented_message = f"{COLORS[level]}{indent}{message}{RESET}"
        getattr(self.logger, level)(colored_indented_message)

    def debug(self, message: str):
        """
        Base class override for debug log level.

        Args:
            message (str): message to log
        """
        self._log("debug", message)

    def info(self, message: str):
        """
        Base class override for info log level.

        Args:
            message (str): message to log
        """
        self._log("info", message)

    def warning(self, message: str):
        """
        Base class override for warning log level.

        Args:
            message (str): message to log
        """
        self._log("warning", message)

    def error(self, message: str):
        """
        Base class override for error log level.

        Args:
            message (str): message to log
        """
        self._log("error", message)

    def critical(self, message: str):
        """
        Base class override for critical log level.

        Args:
            message (str): message to log
        """
        self._log("critical", message)

    def prompt(self, message: str):
        """
        Custom class method for prompt log level.

        Args:
            message (str): message to log
        """
        self._log("prompt", message)


logger = IndentColoredLogger()
