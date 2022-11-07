from pathlib import Path

import pytest

from fehmtk.config import BoundaryConfig, FlowConfig, ModelConfig
from fehmtk.preprocessors.flow_boundaries import _validate_flow_config, warn_if_file_not_referenced


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


@pytest.fixture
def valid_model_config():
    return ModelConfig(
        kind='open_flow',
        params={'input_fluid_temp_degC': 2, 'aiped_to_volume_ratio': 1.0e-08},
    )


@pytest.fixture
def bad_model_config():
    return ModelConfig(
        kind='nonsense',
        params={'input_fluid_temp_degC': 2, 'aiped_to_volume_ratio': 1.0e-08},
    )


def test_warn_if_file_not_referenced(fake_input_file: Path):
    with pytest.warns(UserWarning):
        warn_if_file_not_referenced(input_file=fake_input_file, referenced_file=Path('cond.flow'))


def test_warn_if_file_not_referenced_ok(fake_input_file: Path, recwarn):
    warn_if_file_not_referenced(input_file=fake_input_file, referenced_file=Path('p12.flow'))
    assert len(recwarn) == 0  # no warnings


def test_validate_no_config():
    with pytest.raises(ValueError):
        _validate_flow_config(None)


def test_validate_no_zones(valid_model_config):
    config = FlowConfig(boundary_configs=[
        BoundaryConfig(
            boundary_model=valid_model_config,
            outside_zones=[],
            material_zones=[],
        )
    ])
    with pytest.raises(ValueError):
        _validate_flow_config(config)
