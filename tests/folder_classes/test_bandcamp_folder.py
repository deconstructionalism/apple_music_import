from unittest.mock import MagicMock, patch

import pytest

from src.folder_classes.bandcamp_folder import BandCampAlbumFolder


@pytest.fixture
def album_path() -> str:
    return "/music/test_band/album"


def test_folder_type_property(album_path: str) -> None:
    folder = BandCampAlbumFolder(str(album_path))
    assert folder.folder_type == "bandcamp"


@patch("src.folder_classes.bandcamp_folder.logger")
@patch("src.folder_classes.bandcamp_folder.delete_child_and_parent_dir_if_empty")
def test_delete_folder_deletes_parent(
    mock_delete_fn: MagicMock, mock_logger: MagicMock, album_path: str
):
    # simulate that the parent was deleted
    mock_delete_fn.return_value = (True, "/music/test_band")

    folder = BandCampAlbumFolder(album_path)
    folder.delete_folder()

    mock_delete_fn.assert_called_once_with(album_path)
    mock_logger.indent.assert_called_once()
    mock_logger.info.assert_called_once_with(
        "no other files in parent dir (/music/test_band). parent dir was deleted"
    )
    mock_logger.dedent.assert_called_once()


@patch("src.folder_classes.bandcamp_folder.logger")
@patch("src.folder_classes.bandcamp_folder.delete_child_and_parent_dir_if_empty")
def test_delete_folder_only_deletes_child(
    mock_delete_fn: MagicMock, mock_logger: MagicMock, album_path: str
):
    # simulate that the parent was NOT deleted
    mock_delete_fn.return_value = (False, "/music/test_band")

    folder = BandCampAlbumFolder(album_path)
    folder.delete_folder()

    mock_delete_fn.assert_called_once_with(album_path)
    mock_logger.indent.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.dedent.assert_not_called()
