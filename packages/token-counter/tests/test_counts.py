"""Unit tests for token_counter.counts."""

from pathlib import Path

import pytest
from token_counter.counts import FileTokenCount, SortedFileTokenCounts, sort_file_token_counts_desc
from token_counter.errors import UnsortedCountsError


@pytest.mark.unit
def test_sort_file_token_counts_desc_orders_by_tokens_descending() -> None:
    counts = [
        FileTokenCount(path=Path("a.txt"), tokens=5),
        FileTokenCount(path=Path("b.txt"), tokens=20),
        FileTokenCount(path=Path("c.txt"), tokens=1),
    ]

    sorted_counts = sort_file_token_counts_desc(counts)

    assert [c.tokens for c in sorted_counts] == [20, 5, 1]


@pytest.mark.unit
def test_sort_file_token_counts_desc_breaks_ties_by_ascending_path() -> None:
    counts = [
        FileTokenCount(path=Path("z.txt"), tokens=10),
        FileTokenCount(path=Path("a.txt"), tokens=10),
        FileTokenCount(path=Path("m.txt"), tokens=10),
    ]

    sorted_counts = sort_file_token_counts_desc(counts)

    assert [c.path for c in sorted_counts] == [Path("a.txt"), Path("m.txt"), Path("z.txt")]


@pytest.mark.unit
def test_sort_file_token_counts_desc_empty_input_returns_empty() -> None:
    assert len(sort_file_token_counts_desc([])) == 0


@pytest.mark.unit
def test_sorted_file_token_counts_rejects_unsorted_input_on_direct_construction() -> None:
    # The invariant must be enforced at construction, not just documented --
    # a caller bypassing sort_file_token_counts_desc should still be caught.
    unsorted = (
        FileTokenCount(path=Path("a.txt"), tokens=1),
        FileTokenCount(path=Path("b.txt"), tokens=20),
    )

    with pytest.raises(UnsortedCountsError):
        SortedFileTokenCounts(counts=unsorted)


@pytest.mark.unit
def test_sorted_file_token_counts_accepts_correctly_sorted_input() -> None:
    ordered = (
        FileTokenCount(path=Path("b.txt"), tokens=20),
        FileTokenCount(path=Path("a.txt"), tokens=1),
    )

    SortedFileTokenCounts(counts=ordered)  # must not raise
