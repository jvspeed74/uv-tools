"""Unit tests for token_counter.tokenizer, using a stubbed encoding.

count_tokens depends on SupportsEncode (a Protocol), not the concrete
tiktoken.Encoding class, so these tests never call load_encoding() and
never touch the network -- the unit tier stays hermetic.
"""

from collections.abc import Sequence

import pytest
from token_counter.tokenizer import SupportsEncode, count_tokens


class _StubEncoding:
    """A fake encoding whose .encode() returns a fixed token sequence."""

    def __init__(self, tokens: Sequence[int]) -> None:
        self._tokens = tokens

    def encode(self, text: str, *, disallowed_special: object = ...) -> Sequence[int]:
        del text, disallowed_special
        return self._tokens


_stub_conforms: SupportsEncode = _StubEncoding(tokens=())


@pytest.mark.unit
def test_count_tokens_returns_length_of_encoded_sequence() -> None:
    stub = _StubEncoding(tokens=[1, 2, 3, 4, 5])

    assert count_tokens("irrelevant text", stub) == 5


@pytest.mark.unit
def test_count_tokens_empty_encoding_is_zero() -> None:
    stub = _StubEncoding(tokens=[])

    assert count_tokens("", stub) == 0
