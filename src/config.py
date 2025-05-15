from typing import Dict, List, Type

from .folder_classes.bandcamp_folder import BandCampAlbumFolder
from .folder_classes.soulseek_folder import SoulseekAlbumFolder
from .lib.abstract_album_folder import AbstractAlbumFolder

# Map album folder classes to lists of globs for where those folder
# can be located
FOLDER_TYPE_GLOB_MAPPINGS: Dict[Type[AbstractAlbumFolder], List[str]] = {
    BandCampAlbumFolder: ["~/Music/bandcamp/**/*"],
    SoulseekAlbumFolder: ["~/Music/soulseek/complete/**/*"],
}

# If true, will delete found folders after successful import
DELETE_FOLDER_AFTER_IMPORT: bool = True
