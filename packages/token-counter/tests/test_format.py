"""Unit tests for token_counter.format."""

import json
from pathlib import Path

import pytest
from token_counter.counts import FileTokenCount, SortedFileTokenCounts
from token_counter.format import (
    InvalidOutputFormatError,
    OutputFormat,
    format_counts,
    parse_output_format,
)


def _sorted(*items: FileTokenCount) -> SortedFileTokenCounts:
    return SortedFileTokenCounts(counts=items)


@pytest.mark.unit
@pytest.mark.parametrize("raw", ["table", "csv", "json"])
def test_parse_output_format_accepts_valid_values(raw: str) -> None:
    assert parse_output_format(raw) == raw


@pytest.mark.unit
def test_parse_output_format_rejects_invalid_value() -> None:
    with pytest.raises(InvalidOutputFormatError):
        parse_output_format("xml")


@pytest.mark.unit
def test_format_table_includes_total_row() -> None:
    counts = _sorted(
        FileTokenCount(path=Path("a.txt"), tokens=10),
        FileTokenCount(path=Path("b.txt"), tokens=5),
    )

    lines = format_counts(counts, OutputFormat.TABLE).splitlines()

    assert lines[0].endswith("a.txt")
    assert lines[1].endswith("b.txt")
    assert lines[2].endswith("TOTAL")
    assert "15" in lines[2]


@pytest.mark.unit
def test_format_csv_has_header_and_no_total_row() -> None:
    counts = _sorted(
        FileTokenCount(path=Path("a.txt"), tokens=10),
        FileTokenCount(path=Path("b.txt"), tokens=5),
    )

    lines = format_counts(counts, OutputFormat.CSV).splitlines()

    assert lines[0] == "tokens,path"
    assert lines[1:] == ["10,a.txt", "5,b.txt"]
    assert not any("TOTAL" in line for line in lines)


@pytest.mark.unit
def test_format_json_is_a_flat_array_with_no_total_field() -> None:
    counts = _sorted(FileTokenCount(path=Path("a.txt"), tokens=10))

    parsed = json.loads(format_counts(counts, OutputFormat.JSON))

    assert parsed == [{"tokens": 10, "path": "a.txt"}]
