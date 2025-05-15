import logging

# add 'prompt' level to logger

PROMPT_LEVEL = 51
logging.addLevelName(PROMPT_LEVEL, "PROMPT")

def prompt(self, message, *args, **kwargs):
    if self.isEnabledFor(PROMPT_LEVEL):
        self._log(PROMPT_LEVEL, message, args, **kwargs)

logging.Logger.prompt = prompt

COLORS = {
        "debug": "\033[37m",  # White
        "info": "\033[36m",  # Cyan
        "warning": "\033[33m",  # Yellow
        "error": "\033[31m",  # Red
        "critical": "\033[41m",  # Red background
        "prompt": "\033[32m",  # Green
    }
RESET = "\033[0m"

class IndentColoredLogger(object):
    def __init__(self, name: str = __name__, level = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.indent_level = 0
        self.indent_str = "  "

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)-8s %(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def indent(self, count = 1):
        self.indent_level += count

    def dedent(self, count = 1):
        self.indent_level = max(0, self.indent_level - count)

    def _log(self, level: str, message: str):
        indent = self.indent_str * self.indent_level
        colored_indented_message = f"{COLORS[level]}{indent}{message}{RESET}"
        getattr(self.logger, level)(colored_indented_message)

    def debug(self, message: str): self._log('debug', message)
    def info(self, message: str): self._log('info', message)
    def warning(self, message: str): self._log('warning', message)
    def error(self, message: str): self._log('error', message)
    def critical(self, message: str): self._log('critical', message)
    def prompt(self, message: str): self._log('prompt', message)


logger = IndentColoredLogger()