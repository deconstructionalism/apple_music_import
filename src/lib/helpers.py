import glob
from typing import List
import os
from itertools import chain
import mimetypes


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
