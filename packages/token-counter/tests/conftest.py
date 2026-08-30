"""Shared pytest fixtures for token_counter's test suite."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Directory of committed synthetic files with known token counts."""
    return Path(__file__).parent / "fixtures"
