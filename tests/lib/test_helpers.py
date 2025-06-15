import json
import mimetypes
import os
from pathlib import Path
from typing import List

import pytest

from src.lib.helpers import (
    ClassKeyJSONEncoder,
    delete_child_and_parent_dir_if_empty,
    find_files_by_ext,
    find_files_by_mime_type,
    is_dir_empty,
)


@pytest.fixture(autouse=True)
def ensure_default_mimetypes():
    # Make sure common types are registered
    mimetypes.init()
    yield


def test_find_files_by_ext(tmp_path: Path):
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


def test_find_files_by_mime_type(tmp_path: Path):
    json_file = tmp_path / "data.json"
    txt_file = tmp_path / "notes.txt"
    json_file.write_text('{"ok": true}')
    txt_file.write_text("notes")

    # one MIME type
    found = find_files_by_mime_type(str(tmp_path), ["application/json"])
    assert str(json_file) in found
    assert str(txt_file) not in found

    # multiple MIME types
    found = find_files_by_mime_type(str(tmp_path), ["application/json", "text/plain"])
    assert set(found) == {str(json_file), str(txt_file)}

    # no matching MIME type
    found = find_files_by_mime_type(str(tmp_path), ["image/jpeg"])
    assert len(found) == 0


ignored_file_names: List[str] = [".ignore", ".also-ignore"]
ignored_dir_names: List[str] = ["ignore-dir", "ignore-dir-2"]


def test_is_dir_empty(tmp_path: Path):
    # test for `TypeError` if non-dir is passed as arg
    random_file = (tmp_path / "random_file").write_text("hello")
    with pytest.raises(TypeError) as e:
        is_dir_empty(str(random_file))
    assert str(e.value) == "`dir_path` must be a directory"

    # test an empty dir with no files
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    assert is_dir_empty(str(empty_dir)) is True
    assert is_dir_empty(str(empty_dir), ignore_files=ignored_file_names) is True
    assert is_dir_empty(str(empty_dir), ignore_dirs=ignored_dir_names) is True
    assert (
        is_dir_empty(
            str(empty_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is True
    )

    # test a dir with ignored files only
    ignored_flat_dir = tmp_path / "ignored_flat"
    ignored_flat_dir.mkdir()
    for file_name in ignored_file_names:
        (ignored_flat_dir / file_name).write_text("hello")

    assert is_dir_empty(str(ignored_flat_dir), ignore_files=ignored_file_names) is True
    assert (
        is_dir_empty(
            str(ignored_flat_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is True
    )

    # test a dir with a mix of ignored and not ignored files
    mixed_flat_dir = tmp_path / "mixed_flat"
    mixed_flat_dir.mkdir()
    for file_name in [*ignored_file_names, "file1", "file2"]:
        (mixed_flat_dir / file_name).write_text("hello")

    assert is_dir_empty(str(mixed_flat_dir), ignore_files=ignored_file_names) is False
    assert (
        is_dir_empty(
            str(mixed_flat_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is False
    )

    # test a dir within a dir containing, both dirs containing ignored and not ignored
    # files
    deep_mixed_dir = tmp_path / "deep_mixed"
    deep_mixed_dir.mkdir()
    deeper_mixed_dir = deep_mixed_dir / "deeper_mixed"
    deeper_mixed_dir.mkdir()

    for file_name in [*ignored_file_names, "file1", "file2"]:
        (deep_mixed_dir / file_name).write_text("hello")
        (deeper_mixed_dir / file_name).write_text("hello")

    assert is_dir_empty(str(deep_mixed_dir), ignore_files=ignored_file_names) is False
    assert (
        is_dir_empty(
            str(deep_mixed_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is False
    )

    # test a dir within a dir containing, both only containing ignored files
    deep_ignored_dir = tmp_path / "deep_ignored"
    deep_ignored_dir.mkdir()
    deeper_ignored_dir = deep_ignored_dir / "deeper_mixed"
    deeper_ignored_dir.mkdir()

    for file_name in ignored_file_names:
        (deep_ignored_dir / file_name).write_text("hello")
        (deeper_ignored_dir / file_name).write_text("hello")

    assert is_dir_empty(str(deep_ignored_dir), ignore_files=ignored_file_names) is True
    assert (
        is_dir_empty(
            str(deep_ignored_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is True
    )

    # test a dir to be excluded within a dir ignored files
    deep_excluded_dir = tmp_path / "deep_excluded"
    deep_excluded_dir.mkdir()
    deeper_excluded_dirs = [
        deep_excluded_dir / dir_name for dir_name in ignored_dir_names
    ]
    for dir in deeper_excluded_dirs:
        dir.mkdir()

    for file_name in ignored_file_names:
        (deep_excluded_dir / file_name).write_text("hello")

    for dir in deeper_excluded_dirs:
        for file_name in [*ignored_file_names, "file1", "file2"]:
            (dir / file_name).write_text("hello")

    assert (
        is_dir_empty(
            str(deep_excluded_dir),
            ignore_files=ignored_file_names,
            ignore_dirs=ignored_dir_names,
        )
        is True
    )


def test_delete_child_and_parent_dir_if_empty(tmp_path: Path) -> None:
    # test for `TypeError` if non-dir is passed as arg
    random_file = (tmp_path / "random_file").write_text("hello")
    with pytest.raises(TypeError) as e:
        delete_child_and_parent_dir_if_empty(str(random_file))
    assert str(e.value) == "`child_path` must be a directory"

    # test if parent dir is not empty
    non_empty_parent_dir = tmp_path / "non_empty_parent_dir"
    non_empty_parent_dir.mkdir()
    random_file = non_empty_parent_dir / "random_file"
    random_file.write_text("hello")
    child_dir_1 = non_empty_parent_dir / "child_dir_1"
    child_dir_1.mkdir()
    (child_dir_1 / "file.mp4").write_text("hello")

    parent_empty, parent_dir = delete_child_and_parent_dir_if_empty(str(child_dir_1))

    assert parent_empty is False
    assert parent_dir == str(non_empty_parent_dir)
    assert os.path.exists(str(parent_dir))
    assert not os.path.exists(str(child_dir_1))

    # test if parent dir is empty
    empty_parent_dir = tmp_path / "empty_parent_dir"
    empty_parent_dir.mkdir()
    child_dir_2 = empty_parent_dir / "child_dir_2"
    child_dir_2.mkdir()
    (child_dir_2 / "file.mp4").write_text("hello")

    parent_empty, parent_dir = delete_child_and_parent_dir_if_empty(str(child_dir_2))

    assert parent_empty is True
    assert parent_dir == str(empty_parent_dir)
    assert not os.path.exists(str(parent_dir))
    assert not os.path.exists(str(child_dir_2))


def test_ClassKeyJSONEncoder():
    # test that JSON without class keys produces identical JSON strings
    # for standard JSON string generation and JSON string generation
    # using `ClassKeyJSONEncoder`
    pojo_json = {
        "first_name": "Sally",
        "last_name": "Ride",
        "age": 61,
        "hours_in_space": 343.766,
        "alive": False,
        "missions": ["STS-7", "STS-41-G"],
        "location": {"state": "CA", "city": "Los Angeles", "street": None},
    }

    standard_json = json.dumps(pojo_json)
    custom_encoded_json = json.dumps(pojo_json, cls=ClassKeyJSONEncoder)

    assert standard_json == custom_encoded_json

    class CustomA:
        pass

    class CustomB:
        pass

    class_json = {**pojo_json, CustomA: True, CustomB: "ok"}

    # test that JSON with class keys fails standard JSON string generation
    with pytest.raises(TypeError):
        json.dumps(class_json)

    # test that JSON with class keys using `ClassKeyJSONEncoder` succeeds
    expected_json = json.dumps({**pojo_json, "CustomA": True, "CustomB": "ok"})
    result_json = json.dumps(class_json, cls=ClassKeyJSONEncoder)

    assert expected_json == result_json
