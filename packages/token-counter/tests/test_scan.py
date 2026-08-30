"""Integration tests for token_counter.scan against the real filesystem."""

from pathlib import Path

import pytest
from token_counter.errors import PathNotFoundError
from token_counter.scan import discover_files, read_text_file


@pytest.mark.integration
def test_discover_files_finds_all_fixture_files(fixtures_dir: Path) -> None:
    discovered = discover_files([fixtures_dir])

    names = {p.name for p in discovered}
    assert names == {"short.txt", "medium.txt", "binary.bin", "deeper.txt"}


@pytest.mark.integration
def test_read_text_file_decodes_known_fixture(fixtures_dir: Path) -> None:
    text = read_text_file(fixtures_dir / "short.txt")

    assert text == "Hello, world!\n"


@pytest.mark.integration
def test_read_text_file_returns_none_for_binary_fixture(fixtures_dir: Path) -> None:
    assert read_text_file(fixtures_dir / "binary.bin") is None


@pytest.mark.integration
def test_discover_files_raises_for_missing_top_level_path(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"

    with pytest.raises(PathNotFoundError):
        discover_files([missing])


@pytest.mark.integration
def test_discover_files_prunes_directory_named_git(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git config", encoding="utf-8")
    (tmp_path / "readme.txt").write_text("hello", encoding="utf-8")

    discovered = discover_files([tmp_path], ignore_names=frozenset({".git"}))

    names = {p.name for p in discovered}
    assert names == {"readme.txt"}


@pytest.mark.integration
def test_discover_files_ignores_specific_file_by_name(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("kept", encoding="utf-8")
    (tmp_path / "secrets.env").write_text("secret", encoding="utf-8")

    discovered = discover_files([tmp_path], ignore_names=frozenset({"secrets.env"}))

    names = {p.name for p in discovered}
    assert names == {"keep.txt"}


@pytest.mark.integration
def test_discover_files_ignore_name_matching_top_level_dir_only_prunes_subdirectories(
    tmp_path: Path,
) -> None:
    # target/keep.txt
    # target/target/nested.txt  <- subdirectory sharing the top-level dir's name
    target = tmp_path / "target"
    (target / "target").mkdir(parents=True)
    (target / "keep.txt").write_text("kept", encoding="utf-8")
    (target / "target" / "nested.txt").write_text("nested", encoding="utf-8")

    discovered = discover_files([target], ignore_names=frozenset({"target"}))

    names = {p.name for p in discovered}
    assert names == {"keep.txt"}  # the top-level "target" dir itself is never filtered (R11)


@pytest.mark.integration
def test_discover_files_does_not_follow_symlink_loop(tmp_path: Path) -> None:
    loop_dir = tmp_path / "loop"
    loop_dir.mkdir()
    (loop_dir / "real.txt").write_text("real", encoding="utf-8")
    try:
        (loop_dir / "self").symlink_to(loop_dir, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation requires elevated privilege on this machine")

    discovered = discover_files([loop_dir])  # must terminate, not recurse forever

    names = {p.name for p in discovered}
    assert "real.txt" in names
