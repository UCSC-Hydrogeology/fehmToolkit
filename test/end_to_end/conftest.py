from pathlib import Path

import pytest


@pytest.fixture
def matlab_fixture_dir() -> Path:
    return Path(__file__).parent.parent.parent / 'matlab_archive' / 'test' / 'fixtures'
