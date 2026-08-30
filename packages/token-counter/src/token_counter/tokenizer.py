"""Token counting via tiktoken, split into an effectful loader and a pure counter."""

import tiktoken

__all__ = ["load_encoding", "count_tokens"]

_DEFAULT_ENCODING_NAME = "o200k_base"


def load_encoding(name: str = _DEFAULT_ENCODING_NAME) -> tiktoken.Encoding:
    """Load a tiktoken encoding by name.

    Effects:
        Downloads the encoding's BPE data on first use per machine; tiktoken
        caches it locally afterward. Requires network access on a cold cache.
    """
    return tiktoken.get_encoding(name)


def count_tokens(text: str, encoding: tiktoken.Encoding) -> int:
    """Count the number of tokens `text` encodes to under `encoding`.

    Special-token substrings (e.g. "<|endoftext|>") in `text` are treated as
    ordinary text rather than rejected, since `text` is arbitrary file
    content, not a trusted prompt.
    """
    return len(encoding.encode(text, disallowed_special=()))
