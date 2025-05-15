import os
import subprocess


class AppleMusicImportError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        pass


def import_file_to_apple_music(file_path: str) -> None:
    """Import an audio file into Apple Music.

    Args:
        file_path (str): path to audio file to import
    """

    # Make sure the file path is absolute and escaped
    file_path = os.path.abspath(file_path)
    apple_script = f'''
    set thePath to POSIX path of "{file_path}"
    tell application "Music"
        activate
        add thePath
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script], capture_output=True)
    if result.stderr:
        raise AppleMusicImportError(result.stderr.decode("utf-8"))
