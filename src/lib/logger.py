import logging
from typing import Any, Callable, Dict

# CONSTANTS

COLORS: Dict[str, str] = {
    "debug": "\033[37m",  # White
    "info": "\033[36m",  # Cyan
    "warning": "\033[33m",  # Yellow
    "error": "\033[31m",  # Red
    "critical": "\033[41m",  # Red background
    "prompt": "\033[32m",  # Green
}
RESET = "\033[0m"

# # add 'prompt' level to logger that will show at any log level setting
# # (critical is level 50)
PROMPT_LEVEL = 51
logging.addLevelName(PROMPT_LEVEL, "PROMPT")


class IndentColoredLogger(logging.Logger):
    """
    Custom python logger that allows consistent indentation and color coding
    of log levels.
    """

    def __init__(self, name: str = __name__, level: int = logging.DEBUG):
        super().__init__(name, level)
        self.indent_level = 0
        self.indent_str = "  "

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        self.addHandler(handler)
        self.setLevel(level)

    def indent(self, count: int = 1):
        """
        Indent logs by a given number of indents.

        Args:
            count (int, optional): number of indents to apply. Defaults to 1.
        """
        self.indent_level += count

    def dedent(self, count: int = 1):
        """
        Dedent logs by a given number of dedents.

        Args:
            count (int, optional): number of dedents to apply. Defaults to 1.
        """
        self.indent_level = max(0, self.indent_level - count)

    def log_section(
        self,
        section_name: str,
        start_format: str = "[{section_name}]",
        end_format: str = "[/{section_name}]",
    ) -> Callable[..., None]:
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

    def _log(self, level: int, msg: str, *args: Any, **kwargs: Any):
        """
        Internal logging function that applies color and indentation given the log level
        and indent state of the logger, respectively.
        """
        indent = self.indent_str * self.indent_level
        level_name = logging.getLevelName(level)
        colored_indented_message = f"{COLORS[level_name.lower()]}{indent}{msg}{RESET}"
        super()._log(level, colored_indented_message, *args, **kwargs)

    def prompt(self, msg: str, *args: Any, **kwargs: Any):
        """
        Custom class method for prompt log level.
        """
        if self.isEnabledFor(PROMPT_LEVEL):
            self._log(PROMPT_LEVEL, msg, args, **kwargs)


logger = IndentColoredLogger()
