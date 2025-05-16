# Apple Music Import

[![CI](https://github.com/deconstructionalism/apple_music_import/actions/workflows/ci.yaml/badge.svg)](https://github.com/deconstructionalism/apple_music_import/actions/workflows/ci.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/apple-music-import)](https://pypi.org/project/apple-music-import/)

App to bulk import music from multiple folders into Apple Music.

> Please consider purchasing music you download if you want to support small,
> weird and independent artists!

## Requirements

> This has only been tested on MacOS 15.4.1 on Apple M1 Max

- [`viu`](https://github.com/atanunq/viu?tab=readme-ov-file) and compatible terminal
- [`FFmpeg`](https://ffmpeg.org/)
- python 3.10^
- [`uv`](https://docs.astral.sh/uv/getting-started/installation)

## Setup

1. Clone this repository locally
1. Run `uv venv` to set up and activate virtual env
1. Run `uv pip install -r pyproject.toml` to install all packages

## Run App

Run `poe run` to run the app and import all files found give the configuration
(see [Configuration](#configuration) section).

During the run, the app will search for folders containing music based on the
configuration, then it will attempt the following steps for each folder:

1. Convert music files in the folder to Apple Lossless mp4 if they aren't already,
   using the Apple Lossless Audio Codec, carrying over all of the ID3 metadata
1. Find all Apple Lossless mp4s in the folder
1. Check and see if a cover image has been provided for the album
   - if there is a cover image named as specified in the config, the app will tag
     the music files with this image
   - if there are multiple images in the folder, it will display them and ask
     you to choose one, or provide a URL to an image
   - if there are no image files in the folder, it will ask you to provide a URL
     to an image
1. Import all files in the folder into Apple Music
1. If the app is configured to delete the folder after successfully importing all
   files, it will do so. Some of the existing folder types in this repo (bandcamp,
   Soulseek) available in this app will also delete the parent folder if there are
   no other files in it beside the album that was uploaded

## Configuration

### Delete Folder After Import

`src/config.py:DELETE_FOLDER_AFTER_IMPORT` - set boolean to determine delete behavior
after folder contents are imported.

### Music Folders Search Space

`src/config.py:FOLDER_TYPE_GLOB_MAPPINGS` - for a given concrete class of
`AbstractAlbumFolder`, set a list of unix-style glob strings that will locate folders
that should be processes by said concrete class.

### Music Folder Types

You can create new concrete class instances of `AbstractAlbumFolder` abstract class
and place them in `src/folder_classes/`. Each of these classes represent a type of
folder containing an album of music files, with or without a cover image. The concrete
class can optionally set the name of cover images in the folder (if they exist and
have consistent naming), and must specify a method for deleting the folder when the
import is done.

## Development

[`poethepoet`](https://github.com/nat-n/poethepoet) is used as a task runner to
simplify common operations.

### Linting

- `poe lint` to lint code
  - `poe lint:fix` if you want automatic fixing of linting issues
- `poe doclint` to lint docstrings

### Formatting

- `poe format` to format code

### Testing

Testing is done with [`pytest`](https://pytest.org)

- `poe test` to run all tests

### Versioning

- `poe bump_version [major, minor, patch]` bump version, updating `pyproject.toml`
  and adding a git tag for the version

### Building

- `poe build` to build the app into `dist/`

### Publishing

- `poe publish` to publish to PyPi. You must have an API token for PyPi to do this

## Contributing

Please read and follow these guidelines to help keep the project consistent and
maintainable

### General Rules

- **Do NOT open pull requests directly against `main`.**
  - Fork a copy of the repo and open your PR against `dev` on the main repo
- All pull requests should be focused, small, and ideally scoped to a single
  change or fix
- Ensure your branch is up to date with the base branch before opening a PR
- Please do not publish or increment the version unless you are forking off a
  separately maintained version of this repo

### Test Coverage

- If you’re adding a new feature, include full test coverage
- Run `poe test` to ensure all tests pass

### Code Style

This repo contains pre-commit hooks to make sure code passes above lint and
format checks as well as making sure that commit message is formatted as a
[conventional commit](https://www.conventionalcommits.org/en/v1.0.0/)

- Run `poe lint:fix` to auto-fix linting issues and `poe format` to
  auto-format code
- Use conventional commit messages

### Docs

- Update documentation for any new feature or behavior change
- Ensure docstrings are present and lint them using `poe doclint`

### Communication

- For significant changes, please open an issue first to discuss your ideas.
- PRs may be reviewed and require changes before being merged.
