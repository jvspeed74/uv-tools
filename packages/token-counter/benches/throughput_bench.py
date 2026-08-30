"""Measures count_tokens's throughput (MB/s) across input sizes.

Run: uv run --group bench python benches/throughput_bench.py
"""

import time

from _generators import normal_text
from token_counter.tokenizer import count_tokens, load_encoding

_SIZES_MB = [1, 10, 100, 500, 1000]


def main() -> None:
    encoding = load_encoding()
    print(f"{'input':>10}  {'tokens':>12}  {'time':>10}  {'rate':>12}")
    for mb in _SIZES_MB:
        size_bytes = mb * 1_000_000
        text = normal_text(size_bytes)
        start = time.perf_counter()
        tokens = count_tokens(text, encoding)
        elapsed = time.perf_counter() - start
        rate = size_bytes / 1e6 / elapsed
        print(f"{mb:>8}MB  {tokens:>12}  {elapsed:>9.3f}s  {rate:>10.1f}MB/s")


if __name__ == "__main__":
    main()
