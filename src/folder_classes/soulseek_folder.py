from src.lib.abstract_album_folder import AbstractAlbumFolder
from src.lib.helpers import delete_child_and_parent_dir_if_empty
from src.lib.logger import logger


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

        parent_deleted, parent_dir = delete_child_and_parent_dir_if_empty(self.path)

        if parent_deleted:
            logger.indent()
            logger.info(
                f"no other files in parent dir ({parent_dir}). parent dir was "
                + "deleted"
            )
            logger.dedent()
