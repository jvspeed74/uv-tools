"""CLI entry point: argument parsing, pipeline wiring, and exit codes."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from token_counter.counts import FileTokenCount, sort_file_token_counts_desc
from token_counter.errors import PathNotFoundError
from token_counter.format import format_counts, parse_output_format
from token_counter.scan import DEFAULT_IGNORE_NAMES, discover_files, read_text_file
from token_counter.tokenizer import count_tokens, load_encoding

__all__ = ["main"]


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token-counter",
        description="Count tokens per file across files and directories, sorted most to least.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="One or more files and/or directories to scan.",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="table",
        choices=["table", "csv", "json"],
        help="Output format (default: table).",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",
        default=(),
        metavar="NAME",
        help=(
            "One or more file/directory names to ignore during recursion. "
            "Never applies to a top-level path argument, even if its own name matches."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Disable the default ignore-set (.git, .venv, node_modules, etc). --ignore names still apply.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the `token-counter` command.

    Effects:
        Reads argv and the filesystem, writes stdout/stderr, and calls
        sys.exit on both the success and failure paths.
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    fmt = parse_output_format(args.format)
    ignore_names = frozenset(args.ignore) | (frozenset() if args.all else DEFAULT_IGNORE_NAMES)

    try:
        discovered = discover_files(args.paths, ignore_names=ignore_names)
    except PathNotFoundError as exc:
        print(f"token-counter: path does not exist: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    encoding = load_encoding()
    file_counts: list[FileTokenCount] = []
    for path in discovered:
        text = read_text_file(path)
        if text is None:
            print(f"token-counter: skipping non-UTF-8 file: {path}", file=sys.stderr)
            continue
        file_counts.append(FileTokenCount(path=path, tokens=count_tokens(text, encoding)))

    if not file_counts:
        print("token-counter: no readable files found", file=sys.stderr)
        raise SystemExit(1)

    sorted_counts = sort_file_token_counts_desc(file_counts)
    print(format_counts(sorted_counts, fmt))


if __name__ == "__main__":
    main()
