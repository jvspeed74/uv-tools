"""Unit tests for token_counter.counts."""

from pathlib import Path

import pytest

from token_counter.counts import FileTokenCount, sort_file_token_counts_desc


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
    assert sort_file_token_counts_desc([]) == ()
