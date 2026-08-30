"""Regression check: adversarial input patterns must not blow up algorithmically.

tiktoken has a documented history of catastrophic regex backtracking on long
unbroken text runs (no whitespace, long digit sequences). Each pattern is
measured across several sizes, and its scaling exponent -- the least-squares
slope of log(time) vs log(size) -- is compared against a threshold set with
headroom above the known, accepted worst case (see benches/README.md for the
calibration data). Linear is ~1.0; a real regression toward
quadratic-or-worse behavior pushes this well past the threshold, which a
single-size ratio against a baseline would miss or false-trigger on.

Run: uv run --group bench python benches/pathological_bench.py
"""

import math
import time
from collections.abc import Callable

import tiktoken
from _generators import normal_text, repeated_char_text, repeated_digit_text
from token_counter.tokenizer import count_tokens, load_encoding

_SIZES_MB = [1, 2, 4, 8, 16]
_MAX_ACCEPTABLE_EXPONENT = 1.6  # linear is 1.0; known worst case (repeated-char) is ~1.2


def _time_seconds(text: str, encoding: tiktoken.Encoding) -> float:
    start = time.perf_counter()
    count_tokens(text, encoding)
    return time.perf_counter() - start


def _scaling_exponent(sizes_bytes: list[int], times: list[float]) -> float:
    """Least-squares slope of log(time) vs log(size) -- the empirical growth rate.

    ~1.0 means linear (time doubles when size doubles). Higher means
    super-linear; this is what flags a return to quadratic-or-worse
    tokenizer behavior on adversarial input.
    """
    xs = [math.log(s) for s in sizes_bytes]
    ys = [math.log(t) for t in times]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    return numerator / denominator


def main() -> None:
    encoding = load_encoding()
    sizes_bytes = [mb * 1_000_000 for mb in _SIZES_MB]

    generators: dict[str, Callable[[int], str]] = {
        "normal prose": normal_text,
        "repeated char (no whitespace)": repeated_char_text,
        "repeated digit run": repeated_digit_text,
    }

    print(f"{'pattern':<32}{'exponent':>10}  {'rate @ max size':>18}")
    for name, generate in generators.items():
        times = [_time_seconds(generate(size), encoding) for size in sizes_bytes]
        exponent = _scaling_exponent(sizes_bytes, times)
        rate = (sizes_bytes[-1] / 1e6) / times[-1]
        flag = "" if exponent <= _MAX_ACCEPTABLE_EXPONENT else "  <-- REGRESSION"
        print(f"{name:<32}{exponent:>10.2f}  {rate:>15.1f}MB/s{flag}")


if __name__ == "__main__":
    main()
