"""Regression check: adversarial text patterns must not blow up throughput.

tiktoken has a documented history of catastrophic regex behavior on long
unbroken runs of text (no whitespace, long digit sequences). This compares
throughput on those patterns against normal prose -- a large gap would flag
a regression, e.g. from a tiktoken upgrade reintroducing the old behavior.

Run: uv run --group bench python benches/pathological_bench.py
"""

import time

import tiktoken
from _generators import normal_text, repeated_char_text, repeated_digit_text
from token_counter.tokenizer import count_tokens, load_encoding

_SIZE_MB = 5
_MIN_ACCEPTABLE_RATE_FRACTION = 0.1  # adversarial rate must stay within 10x of baseline


def _rate_mb_s(text: str, encoding: tiktoken.Encoding) -> float:
    size_mb = len(text) / 1e6
    start = time.perf_counter()
    count_tokens(text, encoding)
    elapsed = time.perf_counter() - start
    return size_mb / elapsed


def main() -> None:
    encoding = load_encoding()
    size_bytes = _SIZE_MB * 1_000_000

    patterns = {
        "normal prose": normal_text(size_bytes),
        "repeated char (no whitespace)": repeated_char_text(size_bytes),
        "repeated digit run": repeated_digit_text(size_bytes),
    }

    rates = {name: _rate_mb_s(text, encoding) for name, text in patterns.items()}
    baseline = rates["normal prose"]

    print(f"{'pattern':<32}{'rate':>10}  {'vs baseline':>12}")
    for name, rate in rates.items():
        ratio = rate / baseline
        flag = "" if ratio >= _MIN_ACCEPTABLE_RATE_FRACTION else "  <-- REGRESSION"
        print(f"{name:<32}{rate:>8.1f}MB/s  {ratio:>10.2f}x{flag}")


if __name__ == "__main__":
    main()
