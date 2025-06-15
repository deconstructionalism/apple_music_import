import hashlib
import io
import mimetypes
import subprocess
import tempfile
from typing import List, Set

import requests
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image

from src.lib.constants import APPLE_MUSIC_COMPATIBLE_MIME_TYPES
from src.lib.helpers import find_files_by_mime_type


class CoverImage(object):
    """Object for displaying and retrieving image for album cover.

    Args:
        path (str): path to file.
    """

    def __init__(self, path: str):
        self.path = path
        self.mime_type = mimetypes.guess_type(path)[0]

    def display(self) -> None:
        subprocess.run(f'viu "{self.path}"', shell=True)

    @staticmethod
    def load_image_from_url(url: str):
        """
        Saves an image file from a url and return a new `CoverImage`.

        Args:
            url (str): url of image to load

        Returns:
            (CoverImage): new instance of `CoverImage`
        """

        # request image file and make sure it exists
        response = requests.get(url)
        response.raise_for_status()

        if not response.headers.get("content-type", "").startswith("image"):
            raise TypeError("URL does not point to an image")

        # save the image
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file.flush()

        return CoverImage(tmp_file.name)

    def tag_music_file(self, file_path: str) -> None:
        """Add cover image to music file.

        Args:
            file_path (str): file to tag with cover image
        """
        audio = MP4(file_path)
        if not audio.tags:
            audio.add_tags()

        # read the image
        with open(self.path, "rb") as img:
            img_data = img.read()

        # handle PNG images
        if self.mime_type == "image/png":
            cover = MP4Cover(img_data, imageformat=MP4Cover.FORMAT_PNG)
        else:
            cover = MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)

        # assign the image
        audio["covr"] = [cover]
        getattr(audio, "save")()
        audio.save()


class CoverImagesInAlbumFiles(object):
    """
    Object for discovering all unique cover images already tagged to
    music files in an album folder. This class assumed that the files
    are already `m4a` format.

    Args:
        dir_path (str): Album folder path.
    """

    def __init__(self, dir_path: str) -> None:
        self.dir_path = dir_path
        self.music_files: List[MP4] = []
        self._cover_image_hashes: Set[bytes] = set()
        self._unique_cover_image_data: List[MP4Cover] = []
        self.cover_image_paths: List[str] = []

    def __find_files(self) -> None:
        """
        Find all `.m4a` files in the album folder.
        """
        music_file_paths = find_files_by_mime_type(
            self.dir_path, APPLE_MUSIC_COMPATIBLE_MIME_TYPES
        )
        self.music_files = [MP4(path) for path in music_file_paths]

    def __find_unique_cover_images(self) -> None:
        """
        Find all cover images tagged to files in the album folder and
        only save the ones that are unique at the byte hash level.
        """
        for music_file in self.music_files:
            # find all valid cover images in file
            cover_images = [
                data
                for data in getattr(music_file, "covr", [])
                if isinstance(data, MP4Cover)
            ]

            # for each cover image, determine if it's unique given
            # other cover images that have already been processed
            for image in cover_images:
                # create hash digest of image
                cover_bytes = bytes(image)
                hash_digest = hashlib.sha256(cover_bytes).digest()

                # if the hash is unique, save the image
                if hash_digest not in self._cover_image_hashes:
                    self._cover_image_hashes.add(hash_digest)
                    self._unique_cover_image_data.append(image)

    def __save_cover_images(self) -> None:
        """
        Turn all the unique cover images into temporary files.
        """
        for image_data in self._unique_cover_image_data:
            if getattr(image_data, "imageformat") == MP4Cover.FORMAT_PNG:
                format = "PNG"
                suffix = ".png"
            else:
                format = "JPEG"
                suffix = ".jpg"

            image = Image.open(io.BytesIO(image_data))
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                image.save(tmp_file, format=format)
                self.cover_image_paths.append(tmp_file.name)

    def process(self) -> List[str]:
        """
        Process the files in an album folder.

        Returns:
            List[str]: Temporary paths to unique cover image files
        """
        self.__find_files()
        self.__find_unique_cover_images()
        self.__save_cover_images()

        return self.cover_image_paths
