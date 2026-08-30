# token-counter

Count tokens per file across one or more files and directories, sorted from
most to least. Useful for sizing what you're about to paste into an LLM
context window.

Tokens are counted with [tiktoken](https://github.com/openai/tiktoken)'s
`o200k_base` encoding (the one used by GPT-4o and o-series models).

## Install

From a clone of this repo:

```bash
uv tool install --editable packages/token-counter
```

This registers a global `token-counter` command, backed by an isolated `uv`-managed
environment. `--editable` means local changes to the source take effect immediately,
without reinstalling.

## Usage

```bash
token-counter <path> [<path> ...] [-f {table,csv,json}] [-i NAME ...]
```

`<path>` can be any mix of files and directories; directories are scanned recursively.

```
$ token-counter src
 681  src\token_counter\cli.py
 573  src\token_counter\format.py
 504  src\token_counter\scan.py
 338  src\token_counter\counts.py
 218  src\token_counter\tokenizer.py
  71  src\token_counter\errors.py
   0  src\token_counter\__init__.py
   0  src\token_counter\py.typed
2385  TOTAL
```

### Options

| Flag | Description |
|---|---|
| `-f, --format {table,csv,json}` | Output format. Default: `table`. |
| `-i, --ignore NAME` | A file or directory name to ignore during recursion. Repeatable: `-i node_modules -i .venv`. Never applies to a path you named directly on the command line, even if its own name matches. |
| `-h, --help` | Show usage and exit. |

### Output formats

**`table`** (default) — aligned columns, sorted descending, with a total row (shown
above).

**`csv`** — one row per file, no total row:

```
tokens,path
681,src\token_counter\cli.py
573,src\token_counter\format.py
504,src\token_counter\scan.py
...
```

**`json`** — a flat array of records, no total field:

```json
[
  {
    "tokens": 71,
    "path": "src\\token_counter\\errors.py"
  }
]
```

### What gets skipped

- **Non-UTF-8 files** (images, binaries, compiled artifacts) are skipped with a
  warning on stderr — the run continues.
- **Names passed via `-i`/`--ignore`** are skipped during recursion. There is no
  default ignore-set — nothing is skipped unless you say so.
- A path you name **directly** on the command line is always scanned, even if its
  name matches an `--ignore` name — ignoring only applies to what recursion
  *finds*, not to what you explicitly asked for.

### Exit codes

`0` on success. `1` if a given path doesn't exist, or if no readable files were
found (e.g. an empty or entirely-ignored directory) — either way, a message is
printed to stderr explaining why.

## Notes

The `o200k_base` encoding's data is downloaded and cached locally by `tiktoken` on
first use per machine; this requires network access the first time you run the tool.
