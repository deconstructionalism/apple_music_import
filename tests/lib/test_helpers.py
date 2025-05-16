import mimetypes

import pytest

from src.lib.helpers import find_files_by_ext, find_files_by_mime_type


@pytest.fixture(autouse=True)
def ensure_default_mimetypes():
    # Make sure common types are registered
    mimetypes.init()
    yield


def test_find_files_by_ext(tmp_path):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta").mkdir()
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.log"
    file_c = tmp_path / "c.txt"
    file_d = tmp_path / "d.md"
    for f in (file_a, file_b, file_c, file_d):
        f.write_text("hello")

    # one extension
    found = find_files_by_ext(str(tmp_path), [".txt"])
    assert all(p.endswith(".txt") for p in found)
    assert str(file_a) in found
    assert str(file_c) in found
    assert all(not p.endswith((".log", ".md")) for p in found)

    # multiple extensions
    found = find_files_by_ext(str(tmp_path), [".txt", ".log"])
    assert all(p.endswith((".txt", ".log")) for p in found)
    assert str(file_a) in found
    assert str(file_b) in found
    assert str(file_c) in found
    assert all(not p.endswith(".md") for p in found)

    # no matching extensions
    found = find_files_by_ext(str(tmp_path), [".mov"])
    assert len(found) == 0


def test_find_files_by_mime_type(tmp_path):
    json_file = tmp_path / "data.json"
    txt_file = tmp_path / "notes.txt"
    json_file.write_text('{"ok": true}')
    txt_file.write_text("notes")

    # one MIME type
    found = find_files_by_mime_type(str(tmp_path), ["application/json"])
    assert "data.json" in found
    assert "notes.txt" not in found

    # multiple MIME types
    found = find_files_by_mime_type(str(tmp_path), ["application/json", "text/plain"])
    assert set(found) == {"data.json", "notes.txt"}

    # no matching MIME type
    found = find_files_by_mime_type(str(tmp_path), ["image/jpeg"])
    assert len(found) == 0
