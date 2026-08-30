"""End-to-end tests for token_counter.cli: main() through the actual entry point."""

import json
from pathlib import Path

import pytest
from token_counter.cli import main

# Precomputed real o200k_base token counts for tests/fixtures content.
_SHORT_TOKENS = 4
_MEDIUM_TOKENS = 59
_DEEPER_TOKENS = 7
_FIXTURES_TOTAL = _SHORT_TOKENS + _MEDIUM_TOKENS + _DEEPER_TOKENS


@pytest.mark.e2e
def test_main_table_output_is_sorted_desc_with_correct_counts_and_total(
    fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(fixtures_dir), "--format", "table"])

    out = capsys.readouterr().out
    lines = out.strip().splitlines()

    assert lines[0].split()[0] == str(_MEDIUM_TOKENS)
    assert lines[0].endswith("medium.txt")
    assert lines[-1].endswith("TOTAL")
    assert str(_FIXTURES_TOTAL) in lines[-1]


@pytest.mark.e2e
def test_main_csv_output_has_exact_counts_and_no_total(
    fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(fixtures_dir), "--format", "csv"])

    out = capsys.readouterr().out
    lines = out.strip().splitlines()

    assert lines[0] == "tokens,path"
    rows = {tuple(line.split(",", 1)) for line in lines[1:]}
    assert (str(_MEDIUM_TOKENS), str(fixtures_dir / "medium.txt")) in rows
    assert (str(_SHORT_TOKENS), str(fixtures_dir / "short.txt")) in rows
    assert not any("TOTAL" in line for line in lines)


@pytest.mark.e2e
def test_main_json_output_has_exact_counts_and_no_total(
    fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(fixtures_dir), "--format", "json"])

    out = capsys.readouterr().out
    records = json.loads(out)

    assert {"tokens": _MEDIUM_TOKENS, "path": str(fixtures_dir / "medium.txt")} in records
    assert not any("total" in record for record in records)
    assert isinstance(records, list)


@pytest.mark.e2e
def test_main_defaults_to_table_format(
    fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(fixtures_dir)])

    out = capsys.readouterr().out
    assert out.strip().splitlines()[-1].endswith("TOTAL")


@pytest.mark.e2e
def test_main_exits_1_with_stderr_when_no_files_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        main([str(empty_dir)])

    assert exc_info.value.code == 1
    assert "no readable files" in capsys.readouterr().err


@pytest.mark.e2e
def test_main_exits_1_with_stderr_naming_missing_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist"

    with pytest.raises(SystemExit) as exc_info:
        main([str(missing)])

    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert str(missing) in err


@pytest.mark.e2e
def test_main_skips_binary_fixture_with_stderr_warning(
    fixtures_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(fixtures_dir), "--format", "json"])

    captured = capsys.readouterr()
    records = json.loads(captured.out)
    paths = {record["path"] for record in records}

    assert str(fixtures_dir / "binary.bin") not in paths
    assert "binary.bin" in captured.err
