import mimetypes
import subprocess
import tempfile
import requests
from mutagen.mp4 import MP4, MP4Cover


class CoverImage(object):
    def __init__(self, path: str):
        """Object for displaying and retrieving image for album cover.

        Args:
            path (str): path to file.
        """
        self.path = path
        self.mime_type = mimetypes.guess_type(path)[0]

    def display(self) -> None:
        subprocess.run(f"viu {self.path}", shell=True)

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

        if not response.headers.get("content-type").startswith('image'):
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

        # Read the image
        with open(self.path, "rb") as img:
            img_data = img.read()

        ## handle PNG images
        if self.mime_type == "image/png":
            cover = MP4Cover(img_data, imageformat=MP4Cover.FORMAT_PNG)
        else:
            cover = MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)

        ## assign the image
        audio["covr"] = [cover]
        audio.save()
