class TokenCounterError(Exception):
    """Root exception for every error raised by token_counter."""


class PathNotFoundError(TokenCounterError, FileNotFoundError):
    """A top-level path argument does not exist."""
