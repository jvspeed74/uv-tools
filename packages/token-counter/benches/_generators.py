"""Synthetic text generators shared across benchmark scripts."""

__all__ = ["normal_text", "repeated_char_text", "repeated_digit_text"]

_WORDS = "the quick brown fox jumps over the lazy dog and runs through the forest at dawn "


def normal_text(size_bytes: int) -> str:
    """English-ish prose, repeated and trimmed to exactly `size_bytes` characters."""
    reps = size_bytes // len(_WORDS) + 1
    return (_WORDS * reps)[:size_bytes]


def repeated_char_text(size_bytes: int, char: str = "a") -> str:
    """A single character repeated with no whitespace -- one unbroken "word"."""
    return char * size_bytes


def repeated_digit_text(size_bytes: int) -> str:
    """A long unbroken run of the digit "1" -- no whitespace, no letters.

    tiktoken's regex has special numeral-grouping handling that has
    historically been vulnerable to catastrophic backtracking on inputs
    like this -- see pathological_bench.py.
    """
    return "1" * size_bytes
