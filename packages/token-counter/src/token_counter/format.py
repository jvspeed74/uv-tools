"""Rendering sorted FileTokenCount results as table, csv, or json text."""

import csv
import io
import json
from typing import Literal, assert_never, cast, get_args

from token_counter.counts import SortedCounts
from token_counter.errors import TokenCounterError

__all__ = ["OutputFormat", "parse_output_format", "format_counts"]

OutputFormat = Literal["table", "csv", "json"]

_VALID_FORMATS: frozenset[str] = frozenset(get_args(OutputFormat))


class InvalidOutputFormatError(TokenCounterError, ValueError):
    """`raw` is not one of the supported output formats."""


def parse_output_format(raw: str) -> OutputFormat:
    """Narrow a raw CLI string into an OutputFormat.

    Raises:
        InvalidOutputFormatError: `raw` is not "table", "csv", or "json".
    """
    if raw not in _VALID_FORMATS:
        raise InvalidOutputFormatError(raw)
    return cast(OutputFormat, raw)


def format_counts(counts: SortedCounts, fmt: OutputFormat) -> str:
    """Render sorted file token counts in the requested format.

    `table` includes a total-tokens summary row; `csv` and `json` stay flat
    per-file records with no injected total.
    """
    match fmt:
        case "table":
            return _format_table(counts)
        case "csv":
            return _format_csv(counts)
        case "json":
            return _format_json(counts)
        case _:
            assert_never(fmt)


def _format_table(counts: SortedCounts) -> str:
    total = sum(c.tokens for c in counts)
    token_col_width = max((len(str(c.tokens)) for c in counts), default=0)
    token_col_width = max(token_col_width, len(str(total)))
    rows = [f"{c.tokens:>{token_col_width}}  {c.path}" for c in counts]
    total_row = f"{total:>{token_col_width}}  TOTAL"
    return "\n".join([*rows, total_row])


def _format_csv(counts: SortedCounts) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["tokens", "path"])
    for c in counts:
        writer.writerow([c.tokens, str(c.path)])
    return buffer.getvalue().rstrip("\n")


def _format_json(counts: SortedCounts) -> str:
    records = [{"tokens": c.tokens, "path": str(c.path)} for c in counts]
    return json.dumps(records, indent=2)
