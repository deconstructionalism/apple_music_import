# Apple Music Import

[![CI](https://github.com/deconstructionalism/apple_music_import/actions/workflows/ci.yaml/badge.svg)](https://github.com/deconstructionalism/apple_music_import/actions/workflows/ci.yaml)
![PyPI - Version](https://img.shields.io/pypi/v/apple-music-import)

Script to import any type of music file along with metadata and album art
into Apple Music.

> Please consider purchasing music you download if you want to support small,
> weird and independent artists!

## Requirements

> This has only been tested on MacOS 15.4.1 on Apple M1 Max

- [viu](https://github.com/atanunq/viu?tab=readme-ov-file) and compatible terminal
- [FFmpeg](https://ffmpeg.org/)
- python 3.10^
- [uv](https://docs.astral.sh/uv/getting-started/installation)

## Setup

1. clone this repository locally
2. run `uv pip install -r pyproject.toml` to install all packages
3. run `uv run -m src.main` to run the script

## Configuration

### Delete Folder After Import

`src/config::DELETE_FOLDER_AFTER_IMPORT` - set boolean to determine delete behavior
after folder contents are imported.

### Music Folders Search Space

`src/config::FOLDER_TYPE_GLOB_MAPPINGS` - for a given concrete class of
`AbstractAlbumFolder`, set a list of unix-style glob strings that will locate folders
that should be processes by said concrete class.

### Music Folder Types

You can create new concrete class instances of `AbstractAlbumFolder` abstract class
and place them in `src/folder_classes`. Each of these classes represent a type of
folder containing an album of music files, with or without a cover image. The concrete
class can optionally set the name of cover images in the folder (if they exist and
have consistent naming), and must specify a method for deleting the folder when the
import is done.

## Development

### Linting

Run `uv run ruff check`. You can run `uv run ruff check --fix` to automatically fix
linting issues that are fixable.

Run `uv run pydoclint .` to lint docstrings.

### Formatting

Run `uv run ruff format`.

### Commits

This repo contains pre-commit hooks to make sure code passes above lint and format
checks, as well as making sure that commit message is formatted as a
[conventional commit](https://www.conventionalcommits.org/en/v1.0.0/).

### Testing

...TBA
