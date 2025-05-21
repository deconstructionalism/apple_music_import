from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.lib.apple_music import AppleMusicImportError, import_file_to_apple_music


def test_AppleMusicImportClass() -> None:
    error_message = "test message"
    with pytest.raises(AppleMusicImportError) as e:
        raise AppleMusicImportError(error_message)

    assert str(e.value) == error_message


# NOTE: there is really no great way to test AppleScript called
# from within a python script without actually running it. This
# test just asserts some basic statements are present, but cannot
# test whether the Apple Script actually works


def test_import_file_to_apple_music(tmp_path: Path) -> None:
    # create a dummy file
    dummy_file = tmp_path / "test_song.m4a"
    dummy_file.write_text("fake audio content")

    # create a mock subprocess result without an error
    mock_result = MagicMock()
    mock_result.stderr = b""

    with patch(
        "src.lib.apple_music.subprocess.run", return_value=mock_result
    ) as mock_run:
        import_file_to_apple_music(str(dummy_file))

        assert mock_run.called
        called_args = mock_run.call_args[0][0]
        print(called_args)
        assert "osascript" == called_args[0]
        assert "-e" == called_args[1]
        assert f'set thePath to POSIX path of "{dummy_file}"' in called_args[2]
        assert "add thePath" in called_args[2]


def test_failed_import_file_to_apple_music(tmp_path: Path) -> None:
    # create a dummy file
    dummy_file = tmp_path / "bad_song.m4a"
    dummy_file.write_text("fake audio content")

    # create a mock subprocess result with an error
    mock_result = MagicMock()
    error_message = "Applescript error: could not add file"
    mock_result.stderr = error_message.encode("utf-8")

    with patch("src.lib.apple_music.subprocess.run", return_value=mock_result):
        with pytest.raises(AppleMusicImportError) as e:
            import_file_to_apple_music(str(dummy_file))

        assert str(e.value) == error_message
