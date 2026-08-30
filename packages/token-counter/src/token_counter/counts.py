"""Typed record for a file's token count, and the sorted collection type."""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

from token_counter.errors import UnsortedCountsError

__all__ = ["FileTokenCount", "SortedFileTokenCounts", "sort_file_token_counts_desc"]


@dataclass(frozen=True, slots=True, kw_only=True)
class FileTokenCount:
    """A single file's path and its token count."""

    path: Path
    tokens: int


def _sort_key(count: FileTokenCount) -> tuple[int, Path]:
    return (-count.tokens, count.path)


@dataclass(frozen=True, slots=True, kw_only=True)
class SortedFileTokenCounts:
    """A collection of FileTokenCount records, sorted descending by token count."""

    counts: tuple[FileTokenCount, ...]

    def __post_init__(self) -> None:
        if self.counts != tuple(sorted(self.counts, key=_sort_key)):
            raise UnsortedCountsError(self.counts)

    def __iter__(self) -> Iterator[FileTokenCount]:
        return iter(self.counts)

    def __len__(self) -> int:
        return len(self.counts)


def sort_file_token_counts_desc(counts: Sequence[FileTokenCount]) -> SortedFileTokenCounts:
    """Sort file token counts descending by token count.

    Ties are broken by ascending path, so output is stable and reproducible
    regardless of filesystem enumeration order.
    """
    ordered = tuple(sorted(counts, key=_sort_key))
    return SortedFileTokenCounts(counts=ordered)
