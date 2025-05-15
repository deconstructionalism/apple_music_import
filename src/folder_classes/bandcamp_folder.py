from src.lib.abstract_album_folder import AbstractAlbumFolder


class BandCampAlbumFolder(AbstractAlbumFolder):
    def __init__(self, path: str):
        self._path = path
        super().__init__(path, "bandcamp", "cover.jpg")
