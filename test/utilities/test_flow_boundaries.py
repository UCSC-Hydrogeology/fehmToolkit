from pathlib import Path

import pytest

from fehmtk.preprocessors.flow_boundaries import warn_if_file_not_referenced


@pytest.fixture
def fake_input_file(tmp_path: Path) -> Path:
    input_file = tmp_path / 'p12.dat'
    input_file.write_text(""""Fake FEHM input file"
sol
1    -1
perm
file
p12.perm
flow
file
p12.flow
stop
""")
    return input_file


def test_warn_if_file_not_referenced(fake_input_file: Path):
    with pytest.warns(UserWarning):
        warn_if_file_not_referenced(input_file=fake_input_file, referenced_file=Path('cond.flow'))


def test_warn_if_file_not_referenced_ok(fake_input_file: Path, recwarn):
    warn_if_file_not_referenced(input_file=fake_input_file, referenced_file=Path('p12.flow'))
    assert len(recwarn) == 0  # no warnings
