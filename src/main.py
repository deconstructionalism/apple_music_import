import glob
import json
import os
import subprocess
from itertools import chain
from typing import List

from src.config import DELETE_FOLDER_AFTER_IMPORT, FOLDER_TYPE_GLOB_MAPPINGS
from src.lib.abstract_album_folder import AbstractAlbumFolder
from src.lib.helpers import ClassKeyJSONEncoder
from src.lib.logger import logger


def main():
    # get app version info
    result = subprocess.run(["uv", "version"], capture_output=True)

    logger.info(result.stdout.decode("utf-8").strip())
    logger.info("-" * 30)
    logger.info("run settings:")
    logger.indent()
    logger.info("FOLDER_TYPE_GLOB_MAPPINGS = ")
    logger.indent()
    logger.info(f"{json.dumps(FOLDER_TYPE_GLOB_MAPPINGS, cls=ClassKeyJSONEncoder)}")
    logger.dedent()
    logger.info(f"DELETE_FOLDER_AFTER_IMPORT = {DELETE_FOLDER_AFTER_IMPORT}")
    logger.dedent()
    logger.info("-" * 30)

    # get a list of all folders discovered using `FOLDER_TYPE_GLOB_MAPPINGS`
    all_folders: List[AbstractAlbumFolder] = []

    for folder_class, globs in FOLDER_TYPE_GLOB_MAPPINGS.items():
        # find all files that match globs
        all_path_matches = chain.from_iterable(
            glob.glob(os.path.expanduser(folder_glob)) for folder_glob in globs
        )

        # filter out only the folder matches
        folder_path_matches = list(
            set([item for item in all_path_matches if os.path.isdir(item)])
        )

        # instantiate folder processing classes for each discovered folder
        folders = [folder_class(folder_path) for folder_path in folder_path_matches]
        all_folders.extend(folders)
    if len(all_folders) == 0:
        logger.info("no folders discovered")
        logger.info("-" * 30)
        return
    logger.info("discovered folders:")
    logger.indent()
    for folder in all_folders:
        logger.info(f"type: {folder.folder_type}, path: {folder.path}")
    logger.dedent()
    logger.info("-" * 30)

    # process each folder
    for folder in all_folders:
        folder.process_files(DELETE_FOLDER_AFTER_IMPORT)


if __name__ == "__main__":
    main()
