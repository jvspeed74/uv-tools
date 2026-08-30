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
| `pathological_bench.py` | The scaling exponent of time vs. size for known-adversarial patterns (long unbroken runs, long digit sequences), against a normal-prose baseline. Flags a regression only if the exponent crosses a threshold well above the known-accepted worst case -- see below for why a single-size ratio check doesn't work here. |

Run any of them directly:

```bash
uv run --group bench python benches/throughput_bench.py
uv run --group bench python benches/memory_bench.py
uv run --group bench python benches/pathological_bench.py
```

## What we found running these

Measured against the pinned `tiktoken` version and `o200k_base`.

### Throughput

| Input size | Time | Rate |
|---:|---:|---:|
| 1 MB | 0.016 s | 63.8 MB/s |
| 10 MB | 0.155 s | 64.6 MB/s |
| 100 MB | 1.541 s | 64.9 MB/s |
| 500 MB | 7.857 s | 63.6 MB/s |
| 1000 MB | 15.215 s | 65.7 MB/s |

Flat rate across three orders of magnitude -- linear, no algorithmic cliff.

### Peak memory

| Input size | Peak memory | Multiple of input |
|---:|---:|---:|
| 1 MB | 96.0 MB | 96.0x |
| 10 MB | 184.4 MB | 18.4x |
| 100 MB | 1,068.4 MB | 10.7x |
| 500 MB | 4,998.4 MB | 10.0x |
| 1000 MB | 9,911.1 MB | 9.9x |

The multiple falls as size grows because a fixed cost (interpreter startup +
loading `o200k_base`'s encoding table) dominates at small sizes but is negligible
at large ones.

#### Variables

- $S$ -- input file size, in megabytes.
- $M(S)$ -- peak process memory as a function of $S$, in megabytes. Fitted by
  least squares against the table above.
- $k$ -- the per-megabyte memory cost. Dominated by the returned token list
  (one Python `int` object per token), not the input string itself.
- $C$ -- the fixed memory cost independent of input size (interpreter startup
  + loading `o200k_base`'s encoding table).
- $M_{\text{free}}$ -- free memory on the machine running `token-counter`, in
  megabytes, at the time it runs.
- $S_{\max}$ -- the largest input size that fits within $M_{\text{free}}$.

Fitting $M(S)$ as linear in $S$:

$$
M(S) \approx k \cdot S + C, \qquad k \approx 9.8, \qquad C \approx 85\text{ MB}
$$

**Upper bound.** Solving for $S_{\max}$:

$$
S_{\max} \approx \frac{M_{\text{free}} - C}{k}
$$

This is a property of the machine running `token-counter` at the time, not a
constant in the code -- `token_counter` reads each file fully into memory with no
size guard, so nothing stops an attempt at a file larger than $S_{\max}$. Past
that point it degrades into OS-level paging well before a clean error, rather
than failing fast.

### Adversarial patterns

| Pattern | Scaling exponent | Rate @ 16 MB |
|---|---:|---:|
| Normal prose | 1.02 | 66.8 MB/s |
| Repeated digit run | 1.01 | 29.5 MB/s |
| Repeated char, no whitespace | 1.19 | 3.2 MB/s |

Exponent $\approx 1.0$ is linear (time doubles when size doubles); tiktoken has a
documented history of some inputs pushing this toward quadratic-or-worse
(historically exponential) via catastrophic regex backtracking. Neither pattern
tested does that here -- the repeated-char case is a real, legitimate ~20x
slowdown per byte (it forms one unbreakable "word" needing many BPE merge
passes), but its *growth rate* stays mildly super-linear (1.19), not
catastrophic. `pathological_bench.py`'s regression threshold (1.6) has headroom
above this measured baseline specifically so a real regression toward
quadratic-or-worse behavior gets flagged without false-triggering on this
already-known, bounded characteristic.
