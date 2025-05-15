import os
from abc import ABC, abstractmethod
from typing import List, Optional

from .apple_music import import_file_to_apple_music
from .constants import APPLE_MUSIC_COMPATIBLE_MIME_TYPES, IMAGE_EXTENSIONS
from .cover_image import CoverImage
from .file_convertor import FileConvertor
from .helpers import find_files_by_ext, find_files_by_mime_type
from .logger import logger


class AbstractAlbumFolder(ABC):
    """
    Abstract class for processing images from a folder that contains
    music files to import.

    Args:
        path (str): path to the folder
        folder_type (str): friendly unique name to call the folder type
        cover_image_file_name (Optional[str]): name of image file within the folder
    """

    def __init__(
        self, path: str, folder_type: str, cover_image_file_name: Optional[str] = None
    ) -> None:
        self.path = path
        self.folder_type = folder_type
        self.compatible_file_paths: List[str] = []
        self.file_convertor: Optional[FileConvertor] = None
        self.cover_image = (
            CoverImage(os.path.join(path, cover_image_file_name))
            if cover_image_file_name
            else None
        )
        self.has_errors = False

    def __find_files(self) -> None:
        """Find all music files in folder path"""

        # find all compatible music files
        compatible_files = find_files_by_mime_type(
            self.path, APPLE_MUSIC_COMPATIBLE_MIME_TYPES
        )

        self.compatible_file_paths = [
            os.path.join(self.path, file_name) for file_name in compatible_files
        ]

    def __choose_cover_image(self) -> None:
        image_paths_in_folder = find_files_by_ext(self.path, IMAGE_EXTENSIONS)

        # HELPER METHODS

        def load_image_from_url() -> None:
            """
            Load a cover image from a url.
            """
            while True:
                logger.prompt("please enter the URL of a cover image")
                image_url = input()
                try:
                    self.cover_image = CoverImage.load_image_from_url(image_url)

                    break
                except Exception as e:
                    logger.indent()
                    logger.error(f"error loading image (Error: {e})")
                    logger.dedent()

        # if no images are found in folder, ask for a URL
        if len(image_paths_in_folder) == 0:
            logger.warning(f"no compatible images found in folder '{self.path}'.")
            load_image_from_url()

        # if there are images to pick from, display and ask user to pick one
        else:
            # display images with numbers
            images_in_folder = [CoverImage(path) for path in image_paths_in_folder]
            logger.info(f"{len(images_in_folder)} images found in folder.")
            logger.prompt(
                "please pick one by entering the number you would like to use or enter "
                + "'url' if you would like to load a cover image from a URL"
            )
            for index, image in enumerate(images_in_folder):
                logger.info(index + 1)
                image.display()

            # prompt user to pick an image or load from a url
            while True:
                which_image = input()
                if which_image == "url":
                    load_image_from_url()
                    break
                if which_image not in [i + i for i, _ in enumerate(images_in_folder)]:
                    logger.indent()
                    logger.warning(
                        f"please pick a number from 1 to {len(images_in_folder) + 1}"
                    )
                    logger.dedent()

                self.cover_image = images_in_folder[int(which_image) - 1]
                break

        assert isinstance(self.cover_image, CoverImage)
        logger.info("cover image set to:")
        self.cover_image.display()
        logger.dedent()

    def __convert_files(self) -> None:
        """Convert any files not compatible with Apple Music to .aac."""

        # convert all incompatible audio files in folder
        self.file_convertor = FileConvertor(self.path)
        for file in self.file_convertor.convert_all():
            old_path = os.path.join(file["path"], file["old_name"])
            new_path = os.path.join(file["path"], file["new_name"])
            if file["state"]["status"] == "success":
                logger.indent()
                logger.info("conversion succeeded:")
                logger.indent()
                logger.info(f"{old_path} -->")
                logger.info(f"{new_path}")
                logger.dedent(2)
            if file["state"]["status"] == "error":
                self.has_errors = True
                logger.indent()
                logger.error(f"conversion failed for {old_path}:")
                logger.indent()
                logger.error(f"error: {file['state']['errorMessage']}")
                logger.dedent(2)

    def __tag_files_with_image(self) -> None:
        """Tag compatible audio files with cover image."""

        # if no cover image file name was set, choose a cover image
        if not self.cover_image:
            self.__choose_cover_image()

        # tag each music file in folder with cover image
        assert isinstance(self.cover_image, CoverImage)
        for path in self.compatible_file_paths:
            self.cover_image.tag_music_file(path)

    def __import_all_files(self) -> None:
        """Try to import all compatible audio files into Apple Music."""
        try:
            for file_path in self.compatible_file_paths:
                import_file_to_apple_music(file_path)
                logger.indent()
                logger.info("imported file into Apple Music:")
                logger.indent()
                logger.info(file_path)
                logger.dedent(2)
        except Exception as e:
            self.has_errors = True
            logger.indent()
            logger.error("import into Apple Music failed:")
            logger.indent()
            logger.error(file_path)
            logger.error(f"error: {str(e)}")
            logger.dedent(2)

    @abstractmethod
    def delete_folder(self) -> None:
        """Delete the folder at this path."""
        pass

    def process_files(self, delete_folder_after: bool = False) -> None:
        logger.info(f"processing {self.folder_type} folder at '{self.path}'...")
        logger.indent()
        logger.info("starting file conversion...")
        self.__convert_files()
        logger.info("...completed file conversions")
        self.__find_files()
        logger.info(
            f"found {len(self.compatible_file_paths)} compatible files to import"
        )
        logger.info("tagging files with cover image...")
        self.__tag_files_with_image()
        logger.info("...completed tagging files")
        logger.info("importing files to Apple Music...")
        self.__import_all_files()
        logger.info("completed imports")
        if delete_folder_after:
            if self.has_errors:
                logger.warn("errors during processing. will not delete folder")
            else:
                logger.info("deleting folder after import...")
                self.delete_folder()
                logger.info("...folder deleted")
        logger.dedent()
        logger.info("...completed processing folder")
