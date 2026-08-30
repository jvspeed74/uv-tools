"""Filesystem discovery: recursing into directories and reading file text."""

import os
from collections.abc import Iterable
from pathlib import Path

from token_counter.errors import PathNotFoundError

__all__ = ["discover_files", "read_text_file"]


def discover_files(
    paths: Iterable[Path],
    *,
    ignore_names: frozenset[str] = frozenset(),
) -> tuple[Path, ...]:
    """Resolve `paths` (files and/or directories) into a flat tuple of files.

    Each top-level entry in `paths` is always included, or recursed into,
    regardless of `ignore_names` — ignore filtering only applies to entries
    encountered while descending into a directory. Directory recursion does
    not follow symlinks, so a symlink cycle cannot cause infinite recursion.

    Raises:
        PathNotFoundError: a top-level path in `paths` does not exist.
    """
    files: list[Path] = []
    for top in paths:
        if not top.exists():
            raise PathNotFoundError(top)
        if top.is_file():
            files.append(top)
            continue
        files.extend(_walk_directory(top, ignore_names))
    return tuple(files)


def _walk_directory(root: Path, ignore_names: frozenset[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in ignore_names]
        for filename in filenames:
            if filename in ignore_names:
                continue
            yield Path(dirpath) / filename


def read_text_file(path: Path) -> str | None:
    """Read `path` as UTF-8 text.

    Returns:
        The decoded text, or None if `path` is not valid UTF-8 — the caller
        is expected to skip and warn rather than treat this as fatal.
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
