import os
from .config import FOLDER_TYPE_GLOB_MAPPINGS, DELETE_FOLDER_AFTER_IMPORT
import glob
from itertools import chain
import json
from typing import List
from .lib.abstract_album_folder import AbstractAlbumFolder
from .lib.logger import logger


class ClassKeyJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        # Convert dicts with class keys to str keys
        if isinstance(obj, dict):
            obj = {
                self._encode_key(k): v for k, v in obj.items()
            }
        return super().encode(obj)

    def _encode_key(self, key):
        if isinstance(key, type):  # a class
            return f"{key.__qualname__}"
        return str(key)  # fallback

    def default(self, obj):
        # Extend if you want to handle non-serializable values too
        return super().default(obj)


def main():

    logger.info("Apple Music Import")
    logger.info("-" * 30)
    logger.info("run settings:")
    logger.indent()
    logger.info(f"FOLDER_TYPE_GLOB_MAPPINGS = ")
    logger.indent()
    logger.info(
        f"{json.dumps(FOLDER_TYPE_GLOB_MAPPINGS, cls=ClassKeyJSONEncoder)}"
    )
    logger.dedent()
    logger.info(f"DELETE_FOLDER_AFTER_IMPORT = {DELETE_FOLDER_AFTER_IMPORT}")
    logger.dedent()
    logger.info("-" * 30)

    all_folders: List[AbstractAlbumFolder] = []

    for folder_class, globs in FOLDER_TYPE_GLOB_MAPPINGS.items():
        all_path_matches = chain.from_iterable(
            glob.glob(os.path.expanduser(folder_glob)) for folder_glob in globs
        )
        folder_path_matches = list(
            set([item for item in all_path_matches if os.path.isdir(item)])
        )

        folders = [folder_class(folder) for folder in folder_path_matches]
        all_folders.extend(folders)

    logger.info("discovered folders:")
    logger.indent()
    for folder in all_folders:
        logger.info(f"type: {folder.folder_type}, path: {folder.path}")
    logger.dedent()
    logger.info("-" * 30)

    for folder in all_folders:
        folder.process_files(DELETE_FOLDER_AFTER_IMPORT)


if __name__ == "__main__":
    main()