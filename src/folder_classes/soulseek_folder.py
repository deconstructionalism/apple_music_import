import os

from send2trash import send2trash

from src.lib.abstract_album_folder import AbstractAlbumFolder

from ..lib.helpers import is_dir_empty
from ..lib.logger import logger


class SoulseekAlbumFolder(AbstractAlbumFolder):
    """
    Concrete album folder class for processing completed Soulseek downloads.
    """

    def __init__(self, path: str):
        self._path = path
        super().__init__(path)

    @property
    def folder_type(self) -> str:
        return "Soulseek"

    def delete_folder(self):
        """
        Extend abstract class method to delete the parent directory if it is empty
        since Soulseek album downloads have the following structure:
           [Soulseek user folder] > [album folder] > [...files]
        """

        # delete parent directory if it is empty
        parent_dir = os.path.dirname(self.path)
        if is_dir_empty(parent_dir, ignore_dirs=[os.path.basename(self.path)]):
            logger.indent()
            logger.info(
                f"no other files in parent dir ({parent_dir}). parent dir "
                + "will be deleted"
            )
            logger.dedent()
            send2trash(parent_dir)
        # otherwise just delete just the album
        else:
            send2trash(self.path)
