"""Token counting via tiktoken, split into an effectful loader and a pure counter."""

from collections.abc import Sequence
from typing import Protocol

import tiktoken

__all__ = ["load_encoding", "count_tokens"]

_DEFAULT_ENCODING_NAME = "o200k_base"


class SupportsEncode(Protocol):
    """Structural contract for count_tokens: anything with a compatible .encode().

    tiktoken.Encoding satisfies this structurally. Depending on the Protocol
    instead of the concrete class lets tests supply a stub encoding without
    constructing a real one (§5, python-coder-v2).
    """

    def encode(self, text: str, *, disallowed_special: object = ...) -> Sequence[int]: ...


def load_encoding(name: str = _DEFAULT_ENCODING_NAME) -> tiktoken.Encoding:
    """Load a tiktoken encoding by name.

    Effects:
        Downloads the encoding's BPE data on first use per machine; tiktoken
        caches it locally afterward. Requires network access on a cold cache.
    """
    return tiktoken.get_encoding(name)


def count_tokens(text: str, encoding: SupportsEncode) -> int:
    """Count the number of tokens `text` encodes to under `encoding`.

    Special-token substrings (e.g. "<|endoftext|>") in `text` are treated as
    ordinary text rather than rejected, since `text` is arbitrary file
    content, not a trusted prompt.
    """
    return len(encoding.encode(text, disallowed_special=()))
