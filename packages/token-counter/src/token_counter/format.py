"""Rendering sorted FileTokenCount results as table, csv, or json text."""

import csv
import io
import json
from enum import StrEnum
from typing import assert_never

from token_counter.counts import SortedFileTokenCounts
from token_counter.errors import TokenCounterError

__all__ = ["OutputFormat", "parse_output_format", "format_counts"]


class OutputFormat(StrEnum):
    """The supported output formats. Single source of truth for CLI choices."""

    TABLE = "table"
    CSV = "csv"
    JSON = "json"


class InvalidOutputFormatError(TokenCounterError, ValueError):
    """`raw` is not one of the supported output formats."""


def parse_output_format(raw: str) -> OutputFormat:
    """Narrow a raw CLI string into an OutputFormat.

    Raises:
        InvalidOutputFormatError: `raw` is not "table", "csv", or "json".
    """
    try:
        return OutputFormat(raw)
    except ValueError as exc:
        raise InvalidOutputFormatError(raw) from exc


def format_counts(counts: SortedFileTokenCounts, fmt: OutputFormat) -> str:
    """Render sorted file token counts in the requested format.

    `table` includes a total-tokens summary row; `csv` and `json` stay flat
    per-file records with no injected total.
    """
    match fmt:
        case OutputFormat.TABLE:
            return _format_table(counts)
        case OutputFormat.CSV:
            return _format_csv(counts)
        case OutputFormat.JSON:
            return _format_json(counts)
        case _:
            assert_never(fmt)


def _format_table(counts: SortedFileTokenCounts) -> str:
    total = sum(c.tokens for c in counts)
    token_col_width = max((len(str(c.tokens)) for c in counts), default=0)
    token_col_width = max(token_col_width, len(str(total)))
    rows = [f"{c.tokens:>{token_col_width}}  {c.path}" for c in counts]
    total_row = f"{total:>{token_col_width}}  TOTAL"
    return "\n".join([*rows, total_row])


def _format_csv(counts: SortedFileTokenCounts) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["tokens", "path"])
    for c in counts:
        writer.writerow([c.tokens, str(c.path)])
    return buffer.getvalue().rstrip("\n")


def _format_json(counts: SortedFileTokenCounts) -> str:
    records = [{"tokens": c.tokens, "path": str(c.path)} for c in counts]
    return json.dumps(records, indent=2)
