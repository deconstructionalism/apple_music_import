import os
from pathlib import Path
from typing import TypedDict
from unittest.mock import MagicMock, patch

import pytest
from pydub import AudioSegment

from src.lib.file_convertor import FileConversion, FileConvertor


class FileConvertorItems(TypedDict):
    file_convertor: FileConvertor
    album_dir: Path
    music_file_1: Path
    music_file_2: Path
    music_file_4: Path


def generate_file_conversion(album_path: Path) -> FileConversion:
    return {
        "old_mime_type": "audio/mpeg",
        "new_mime_type": "audio/ipod",
        "old_name": "file1.mp3",
        "new_name": "file1.m4a",
        "path": str(album_path),
        "state": {
            "error_message": None,
            "status": "pre-conversion",
        },
    }


@pytest.fixture()
def setup_file_convertor(tmp_path: Path) -> FileConvertorItems:
    # test that only incompatible audio files are found
    album_dir = tmp_path / "album"
    album_dir.mkdir()
    music_file_1 = album_dir / "file_1.mp3"
    music_file_2 = album_dir / "file_2.wav"
    music_file_3 = album_dir / "file_3.m4a"
    music_file_4 = album_dir / "file_4.wma"
    image_file = album_dir / "image.jpg"
    text_file = album_dir / "info.txt"

    for f in (
        music_file_1,
        music_file_2,
        music_file_3,
        music_file_4,
        image_file,
        text_file,
    ):
        f.write_text("hello")

    file_convertor = FileConvertor(str(album_dir))

    result: FileConvertorItems = {
        "file_convertor": file_convertor,
        "album_dir": album_dir,
        "music_file_1": music_file_1,
        "music_file_2": music_file_2,
        "music_file_4": music_file_4,
    }

    return result


def test_file_convertor():
    # test that dir must exist
    file_convertor = FileConvertor("path/that/does/not/exist")

    with pytest.raises(TypeError) as error:
        file_convertor._find_incompatible_audio_files()  # type: ignore[reportPrivateUsage]
        assert str(error) == "`path` must be a directory"


def test_file_convertor_find_incompatible_files(
    setup_file_convertor: FileConvertorItems,
):
    album_dir = setup_file_convertor["album_dir"]
    music_file_1 = setup_file_convertor["music_file_1"]
    music_file_2 = setup_file_convertor["music_file_2"]
    music_file_4 = setup_file_convertor["music_file_4"]
    file_convertor = setup_file_convertor["file_convertor"]

    file_convertor._find_incompatible_audio_files()  # type: ignore[reportPrivateUsage]
    incompatible_file_paths = [
        os.path.join(file["path"], file["old_name"])
        for file in file_convertor.incompatible_files
    ]

    # only music files are found, and only incompatible ones
    assert set(incompatible_file_paths) == set(
        [str(music_file_1), str(music_file_2), str(music_file_4)]
    )

    # structure of found file `FileConversion` instances matches what is expected
    for file_conversion in file_convertor.incompatible_files:
        assert file_conversion["new_mime_type"] == "audio/ipod"
        assert file_conversion["old_name"] in [
            music_file_1.name,
            music_file_2.name,
            music_file_4.name,
        ]
        assert file_conversion["path"] == str(album_dir)
        if file_conversion["old_name"] == music_file_1.name:
            assert file_conversion["old_mime_type"] == "audio/mpeg"
        if file_conversion["old_name"] == music_file_2.name:
            assert file_conversion["old_mime_type"] == "audio/x-wav"
        if file_conversion["old_name"] == music_file_4.name:
            assert file_conversion["old_mime_type"] == "audio/x-ms-wma"
        assert (
            file_conversion["new_name"]
            == file_conversion["old_name"].split(".")[0] + ".m4a"
        )
        assert file_conversion["state"] == {
            "error_message": None,
            "status": "pre-conversion",
        }


def test_file_convertor_convert_files(
    setup_file_convertor: FileConvertorItems,
):
    file_convertor = setup_file_convertor["file_convertor"]
    album_dir = setup_file_convertor["album_dir"]

    file_conversion_1 = generate_file_conversion(album_dir)
    old_file_path_1 = os.path.join(
        file_conversion_1["path"], file_conversion_1["old_name"]
    )
    new_file_path_1 = os.path.join(
        file_conversion_1["path"], file_conversion_1["new_name"]
    )

    mock_song_1 = MagicMock(spec=AudioSegment)

    # test if there are already tags on the files
    with (
        patch(
            "src.lib.file_convertor.AudioSegment.from_file", return_value=mock_song_1
        ) as mock_audiosegment_from_file,
        patch(
            "src.lib.file_convertor.mediainfo",
            return_value={"TAG": {"covr": ["fake_image_data"]}},
        ) as mock_mediainfo,
    ):
        # check pre-conversion status
        assert file_conversion_1["state"]["status"] == "pre-conversion"
        assert file_conversion_1["state"]["error_message"] is None

        # convert the file
        file_convertor._convert_file(file_conversion_1)  # type: ignore[reportPrivateUsage]

        # check that conversion was successful
        mock_audiosegment_from_file.assert_called_once_with(old_file_path_1)
        mock_song_1.export.assert_called_once_with(
            new_file_path_1,
            format="mp4",
            codec="alac",
            tags=mock_mediainfo.return_value["TAG"],
        )
        assert file_conversion_1["state"]["status"] == "success"
        assert file_conversion_1["state"]["error_message"] is None

    # test if there are no tags on the files

    file_conversion_2 = generate_file_conversion(album_dir)
    old_file_path_2 = os.path.join(
        file_conversion_2["path"], file_conversion_2["old_name"]
    )
    new_file_path_2 = os.path.join(
        file_conversion_2["path"], file_conversion_2["new_name"]
    )

    mock_song_2 = MagicMock(spec=AudioSegment)

    with (
        patch(
            "src.lib.file_convertor.AudioSegment.from_file", return_value=mock_song_2
        ) as mock_audiosegment_from_file,
        patch("src.lib.file_convertor.mediainfo", return_value={}),
    ):
        # check pre-conversion status
        assert file_conversion_2["state"]["status"] == "pre-conversion"
        assert file_conversion_2["state"]["error_message"] is None

        # convert the file
        file_convertor._convert_file(file_conversion_2)  # type: ignore[reportPrivateUsage]

        # check that conversion was successful
        mock_audiosegment_from_file.assert_called_once_with(old_file_path_2)
        mock_song_2.export.assert_called_once_with(
            new_file_path_2,
            format="mp4",
            codec="alac",
            tags={},
        )

        assert file_conversion_2["state"]["status"] == "success"
        assert file_conversion_2["state"]["error_message"] is None

    # test if file conversion throws an error

    file_conversion_3 = generate_file_conversion(album_dir)
    error_during_conversion = ValueError("Random error")

    with patch(
        "src.lib.file_convertor.AudioSegment.from_file",
        side_effect=error_during_conversion,
    ):
        # check pre-conversion status
        assert file_conversion_3["state"]["status"] == "pre-conversion"
        assert file_conversion_3["state"]["error_message"] is None

        # convert the file
        file_convertor._convert_file(file_conversion_3)  # type: ignore[reportPrivateUsage]

        # check that conversion failed
        assert file_conversion_3["state"]["status"] == "error"
        assert file_conversion_3["state"]["error_message"] == str(
            error_during_conversion
        )


def test_file_convertor_convert_all(
    setup_file_convertor: FileConvertorItems,
):
    file_convertor = setup_file_convertor["file_convertor"]

    with (
        patch.object(
            FileConvertor,
            "_find_incompatible_audio_files",
            wraps=file_convertor._find_incompatible_audio_files,  # type: ignore[reportPrivateUsage]
        ) as spy_find_incompatible,
        patch.object(
            FileConvertor,
            "_convert_file",
            wraps=file_convertor._convert_file,  # type: ignore[reportPrivateUsage]
        ) as spy_convert_file,
    ):
        # convert the files
        files = [file for file in file_convertor.convert_all()]

        assert len(files) == 3
        spy_find_incompatible.assert_called_once()
        assert len(file_convertor.incompatible_files) == 3
        assert spy_convert_file.call_count == 3
