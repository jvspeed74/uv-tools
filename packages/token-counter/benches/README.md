# benches

Standalone diagnostic scripts, not part of the test suite or the shipped package.
They characterize `count_tokens`'s performance and memory behavior on large/adversarial
input, to answer "when does this break, and how" with real measurements instead of
guesses.

## Setup

```bash
uv sync --group bench
```

(`psutil` is only needed for `memory_bench.py` on Windows, and only for benching --
it's not a dependency of the package itself.)

## Scripts

| Script | What it measures |
|---|---|
| `throughput_bench.py` | `count_tokens` MB/s across input sizes (1MB-1GB of normal prose). |
| `memory_bench.py` | Peak process memory relative to input size, at the same sizes. Each size runs in its own subprocess, since peak-memory counters only ever grow over a process's lifetime. |
| `pathological_bench.py` | Throughput on known-adversarial patterns (long unbroken runs, long digit sequences) against a normal-prose baseline -- flags a regression if the ratio drops below 10%. |

Run any of them directly:

```bash
uv run --group bench python benches/throughput_bench.py
uv run --group bench python benches/memory_bench.py
uv run --group bench python benches/pathological_bench.py
```

## What we found running these

On the pinned `tiktoken` version and `o200k_base`:

- Throughput is linear, ~70MB/s, from 1MB through 1GB -- no algorithmic cliff.
- Peak memory is ~9.5x the input file's byte size (dominated by the returned
  token list: one Python `int` object per token, not the input string).
- Neither adversarial pattern tested (long no-whitespace runs, long digit runs --
  both historically known to cause catastrophic regex backtracking in some
  tokenizer implementations) triggers a throughput cliff on this version.

So in practice, the tool's upper bound on file size is set by available RAM
(`~9.5 x file size` must fit), not by pathological input content. There's no
guard against this in `token_counter` itself (see `R17` in the project's design
notes) -- a file too large for available memory degrades into OS-level paging
long before a clean error, rather than failing fast.
