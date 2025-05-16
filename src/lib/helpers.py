import glob
import json
import mimetypes
import os
from itertools import chain
from typing import Any, Callable, List

from .logger import logger


def find_files_by_ext(path: str, extensions: List[str]) -> List[str]:
    """Find all file in path folder that have certain extensions.

    Args:
        path (str): path of folder containing files
        extensions (List[str]): list of valid extensions

    Returns:
        List[str]: full paths to each file with a valid extension
    """

    matched_items = list(
        chain.from_iterable(
            [glob.glob(os.path.join(path, "*", ext)) for ext in extensions]
        )
    )
    matched_files = [
        item for item in matched_items if os.path.isfile(os.path.join(path, item))
    ]

    return matched_files


def find_files_by_mime_type(path: str, mime_types: List[str]) -> List[str]:
    """Find all file in path folder that have a certain MIME types.

    Args:
        path (str): path of folder containing files
        mime_types (List[str]): MIME types to filter by

    Returns:
        List[str]: full paths to each file with matching MIME types
    """

    all_files = [
        item for item in os.listdir(path) if os.path.isfile(os.path.join(path, item))
    ]
    matched_files = [
        file for file in all_files if mimetypes.guess_type(file)[0] in mime_types
    ]

    return matched_files


# system files to not consider
IGNORE_FILES = [".DS_Store"]


def is_dir_empty(
    dir_path: str, ignore_files: List[str] = IGNORE_FILES, ignore_dirs: List[str] = []
) -> bool:
    """
    Check if directory is empty of files, and only contains empty folder or
    system files to ignore.

    Args:
        dir_path (str): path of directory to check
        ignore_files (List[str]): list of file names to ignore
        ignore_dirs (List[str]): list of dir names to ignore

    Returns:
        bool: whether or not the directory is empty
    """

    for _, dirs, files in os.walk(dir_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        files[:] = [f for f in files if f not in ignore_files]
        if files:
            return False

    return True


class ClassKeyJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle classes as dict keys in config object
    to serialize to JSON string.
    """

    def encode(self, obj: Any) -> str:
        """Convert dicts with class keys to string keys.

        Args:
            obj (Any): object to encode

        Returns:
            str: object representation serialized to a string
        """
        if isinstance(obj, dict):
            obj = {self.__encode_key(k): v for k, v in obj.items()}
        return super().encode(obj)

    def __encode_key(self, key: Any) -> str:
        """
        Encode a class key into a representative string, otherwise
        perform default encoding for JSON keys.

        Args:
            key (Any): key to encode

        Returns:
            str: encoded key
        """
        if isinstance(key, type):
            return f"{key.__qualname__}"
        return str(key)


def log_section(
    section_name: str, start_format="[{section_name}]", end_format="[/{section_name}]"
) -> Callable[[], None]:
    """
    Log an indented section of logic with names section start and stop
    and indented internal logging. Return a function to end a section.

    Args:
        section_name (str): the name of the section
        start_format (str): start section template string that include `section_name`.
                            Defaults to "[{section_name}]"
        end_format (str): end section template string that include `section_name`.
                          Defaults to "[/{section_name}]"
    Returns:
        Callable: callback to end a section

    """

    logger.info(start_format.format(section_name=section_name))
    logger.indent()

    def end_section(end_format: str = end_format):
        """
        Callback to end a section by logging and de-denting.

        Args:
            end_format (str, optional): use this to add custom data to the end section
                                        format that was acquired during the section
                                        logic. Defaults to end_format.
        """
        logger.dedent()
        logger.info(end_format.format(section_name=section_name))

    return end_section
