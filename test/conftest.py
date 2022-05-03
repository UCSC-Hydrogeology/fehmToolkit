import pytest

from pathlib import Path


@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / 'fixtures'
