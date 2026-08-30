"""Measures count_tokens's peak process memory relative to input size.

Peak memory (OS-tracked: peak working set on Windows, peak RSS on POSIX) only
ever grows over a process's lifetime, so each size is measured in its own
subprocess to keep the readings independent of each other.

Run: uv run --group bench python benches/memory_bench.py
"""

import subprocess
import sys
from pathlib import Path

from _generators import normal_text

_SIZES_MB = [1, 10, 100, 500, 1000]


def _peak_memory_mb() -> float:
    """This process's peak memory usage so far, per the OS's own tracking."""
    if sys.platform == "win32":
        import psutil

        return psutil.Process().memory_info().peak_wset / 1e6

    import resource

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # ru_maxrss is bytes on macOS/BSD, kilobytes on Linux.
    return peak / 1e6 if sys.platform == "darwin" else peak / 1e3


def _run_single(size_bytes: int) -> None:
    from token_counter.tokenizer import count_tokens, load_encoding

    encoding = load_encoding()
    text = normal_text(size_bytes)
    count_tokens(text, encoding)
    print(_peak_memory_mb())


def main() -> None:
    print(f"{'input':>10}  {'peak mem':>12}  {'multiple':>10}")
    for mb in _SIZES_MB:
        size_bytes = mb * 1_000_000
        result = subprocess.run(
            [sys.executable, str(Path(__file__)), "--single", str(size_bytes)],
            capture_output=True,
            text=True,
            check=True,
        )
        peak_mb = float(result.stdout.strip())
        print(f"{mb:>8}MB  {peak_mb:>10.1f}MB  {peak_mb / mb:>8.2f}x")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--single":
        _run_single(int(sys.argv[2]))
    else:
        main()
