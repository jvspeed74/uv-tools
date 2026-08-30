"""Typed record for a file's token count, and the sorted collection type."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NewType

__all__ = ["FileTokenCount", "SortedCounts", "sort_file_token_counts_desc"]


@dataclass(frozen=True, slots=True, kw_only=True)
class FileTokenCount:
    """A single file's path and its token count."""

    path: Path
    tokens: int


SortedCounts = NewType("SortedCounts", tuple[FileTokenCount, ...])
# Only sort_file_token_counts_desc may produce one. Formatters should require
# this type instead of a bare tuple[FileTokenCount, ...], so passing unsorted
# data to them is a type error rather than a latent output bug.


def sort_file_token_counts_desc(counts: Sequence[FileTokenCount]) -> SortedCounts:
    """Sort file token counts descending by token count.

    Ties are broken by ascending path, so output is stable and reproducible
    regardless of filesystem enumeration order.
    """
    ordered = sorted(counts, key=lambda c: (-c.tokens, c.path))
    return SortedCounts(tuple(ordered))
