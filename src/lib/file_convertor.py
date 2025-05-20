import mimetypes
import os
from typing import Dict, Generator, List, Literal, Optional, TypedDict

from pydub import AudioSegment
from pydub.utils import mediainfo

from .constants import APPLE_MUSIC_COMPATIBLE_MIME_TYPES


class FileConversionStatus(TypedDict):
    status: Literal["pre-conversion", "success", "error"]
    errorMessage: Optional[str]


class FileConversion(TypedDict):
    """File conversion data."""

    """MIME type of file that was converted from"""
    old_mime_type: Optional[str]

    """MIME type of converted file"""
    new_mime_type: str

    """Name file that was converted from"""
    old_name: str

    """Name of converted file"""
    new_name: str

    """Path of to folder with file"""
    path: str

    """Conversion state"""
    state: FileConversionStatus


class FileConvertor(object):
    """
    Convert all music files in a directory that are not compatible with
    Apple Music imports to .m4a files.


    Args:
        path (str): path to folder containing music files.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.incompatible_files: List[FileConversion] = []

    def __find_incompatible_audio_files(self) -> None:
        """
        Find all audio files in folder that are not compatible with Apple
        Music.
        """

        # get a list of all files in folder
        file_names = [
            file
            for file in os.listdir(self.path)
            if os.path.isfile(os.path.join(self.path, file))
        ]

        # find all audio files in files that need conversion
        incompatible_files: List[FileConversion] = []

        for name in file_names:
            mime_type = mimetypes.guess_type(name)[0]
            is_audio = isinstance(mime_type, str) and mime_type.startswith("audio/")

            # only collect audio files that are not compatible
            if is_audio and mime_type not in APPLE_MUSIC_COMPATIBLE_MIME_TYPES:
                # determine new file name with .m4a extension
                base_name = name.rsplit(
                    ".",
                )[0]
                new_name = f"{base_name}.m4a"

                # set up a file conversion dict
                audio_file: FileConversion = {
                    "old_mime_type": mime_type,
                    "new_mime_type": "audio/ipod",
                    "old_name": name,
                    "new_name": new_name,
                    "path": self.path,
                    "state": {"status": "pre-conversion", "errorMessage": None},
                }
                incompatible_files.append(audio_file)

        self.incompatible_files = incompatible_files

    def __convert_file(self, file: FileConversion) -> None:
        """Attempt to convert a single audio file to lossless .m4a.

        Args:
            file (FileConversion): info about file to convert
        """
        try:
            file_path = os.path.join(file["path"], file["old_name"])
            song = AudioSegment.from_file(file_path)

            # check that tags are present and a dict
            raw_tags = mediainfo(file_path).get("TAG", {})
            tags: Optional[Dict[str, str]] = (
                raw_tags if isinstance(raw_tags, dict) else None
            )
            song.export(
                os.path.join(file["path"], file["new_name"]),
                format="mp4",
                codec="alac",
                tags=tags,
            )
            file["state"]["status"] = "success"
        except Exception as e:
            file["state"]["status"] = "error"
            file["state"]["errorMessage"] = str(e)

    def convert_all(self) -> Generator[FileConversion, None, None]:
        """Convert all Apple Music incompatible audio files in folder to .m4a."""

        self.__find_incompatible_audio_files()

        for file in self.incompatible_files:
            self.__convert_file(file)
            yield file
