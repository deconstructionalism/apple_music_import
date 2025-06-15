import glob
import json
import mimetypes
import os
from itertools import chain
from typing import Any, Dict, Hashable, List, Tuple, cast

from send2trash import send2trash


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
            [glob.glob(os.path.join(path, f"*{ext}")) for ext in extensions]
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
        os.path.join(path, item)
        for item in os.listdir(path)
        if os.path.isfile(os.path.join(path, item))
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

    if not os.path.isdir(dir_path):
        raise TypeError("`dir_path` must be a directory")

    for _, dirs, files in os.walk(dir_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        files[:] = [f for f in files if f not in ignore_files]
        if files:
            return False

    return True


def delete_child_and_parent_dir_if_empty(child_path: str) -> Tuple[bool, str]:
    """
    Delete a child dir and if it's parent dir is empty besides the child dir,
    then the parent dir is also deleted.


    Args:
        child_path (str): path to child dir

    Returns:
        Tuple[bool, str]: (whether the parent dir was also deleted, parent dir)
    """

    if not os.path.isdir(child_path):
        raise TypeError("`child_path` must be a directory")

    # delete parent directory if it is empty
    parent_dir = os.path.dirname(child_path)
    if is_dir_empty(parent_dir, ignore_dirs=[os.path.basename(child_path)]):
        send2trash(parent_dir)
        return True, parent_dir
    else:
        send2trash(child_path)
        return False, parent_dir


class ClassKeyJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle classes as dict keys in config object
    to serialize to JSON string.
    """

    def encode(self, o: Any) -> str:
        """Convert dicts with class keys to string keys.

        Args:
            o (Any): object to encode

        Returns:
            str: object representation serialized to a string
        """
        if isinstance(o, dict):
            o_dict = cast(Dict[Hashable, Any], o)
            o = {self.__encode_key(k): v for k, v in o_dict.items()}
        return super().encode(o)

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
            return f"{key.__name__}"
        return str(key)
