from pathlib import Path

import pytest


@pytest.fixture
def end_to_end_fixture_dir() -> Path:
    return Path(__file__).parent / 'fixtures'
