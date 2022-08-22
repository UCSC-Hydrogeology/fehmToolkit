from dataclasses import asdict
import os
from pathlib import Path

import pytest
import yaml

from fehm_toolkit.config import (
    FilesConfig,
    HeatFluxConfig,
    ModelConfig,
    PressureConfig,
    PropertyConfig,
    RockPropertiesConfig,
    RunConfig,
)


@pytest.fixture
def config_dict(fixture_dir):
    with open(fixture_dir / 'flat_box_config.yaml') as f:
        return yaml.load(f, Loader=yaml.Loader)


@pytest.fixture
def files_config_dict():
    return {
      'run_root': 'run_root',
      'material_zone': 'run_root.zone',
      'outside_zone': 'run_root.zone',
      'area': 'run_root.area',
      'initial_conditions': 'run_root.ini',
      'final_conditions': 'run_root.fin',
      'rock_properties': 'run_root.rock',
      'conductivity': 'run_root.cond',
      'pore_pressure': 'run_root.ppor',
      'permeability': 'run_root.perm',
      'heat_flux': 'run_root.hflx',
      'flow': 'run_root.flow',
      'files': 'run_root.files',
      'grid': 'run_root.fehm',
      'input': 'run_root.dat',
      'output': 'run_root.out',
      'store': 'run_root.stor',
      'history': 'run_root.hist',
      'water_properties': '../../end_to_end/fixtures/nist120-1800.out',
      'check': 'run_root.chk',
      'error': 'run_root.err',
    }


@pytest.fixture
def pressure_config_dict():
    return {
        'pressure_model': {
            'kind': 'depth',
            'params': {
                  'z_interval_m': 10,
                  'reference_z': 5000,
                  'reference_pressure_MPa': 25,
                  'reference_temperature_degC': 2,
            },
        },
        'interpolation_model': {
            'kind': 'regular_grid',
            'params': {'x_samples': 10, 'y_samples': 30, 'z_samples': 50},
        },
        'sampling_model': {
            'kind': 'explicit_lists',
            'params': {'explicit_nodes': [1, 2, 3, 4, 5]},
        },
    }


@pytest.fixture
def rock_properties_config_dict():
    return {
        'zone_assignment_order': [1, 2],
        'compressibility_configs': [
            {
                'property_model': {
                    'kind': 'overburden',
                    'params': {
                        'a': 0.09,
                        'grav': 9.81,
                        'min_overburden': 25.0,
                        'rhow': 1000.0,
                    },
                },
                'zones': [1, 2],
            },
        ],
        'conductivity_configs': [
            {
                'property_model': {
                    'kind': 'porosity_weighted',
                    'params': {'rock_conductivity': 2.05, 'water_conductivity': 0.62},
                },
                'zones': [1, 2],
            },
        ],
        'permeability_configs': [
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 1e-16}},
                'zones': [1],
            },
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 1e-10}},
                'zones': [2],
            },
        ],
        'grain_density_configs': [
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 2400}},
                'zones': [1],
            },
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 2650}},
                'zones': [2],
            },
        ],
        'specific_heat_configs': [
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 800}},
                'zones': [1, 2],
            },
        ],
        'porosity_configs': [
            {
                'property_model': {
                    'kind': 'depth_power_law',
                    'params': {'porosity_a': 0.84, 'porosity_b': -0.125},
                },
                'zones': [1],
            },
            {
                'property_model': {'kind': 'constant', 'params': {'constant': 0.1}},
                'zones': [2],
            },
        ],
    }


def test_read_config(config_dict):
    config = RunConfig.from_dict(config_dict)
    assert isinstance(config.files_config, FilesConfig)
    assert isinstance(config.heat_flux_config, HeatFluxConfig)
    assert isinstance(config.pressure_config, PressureConfig)
    assert isinstance(config.rock_properties_config, RockPropertiesConfig)


def test_run_config_writes_relative_files(tmp_path, config_dict):
    # Get config file in temp directory as-is
    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config_dict, f, Dumper=yaml.Dumper)

    # Writeback config using RunConfig object
    test_config_file = tmp_path / 'test_config.yaml'
    config = RunConfig.from_yaml(config_file)
    config.to_yaml(test_config_file)
    with open(test_config_file) as f:
        raw_config = yaml.load(f, Loader=yaml.Loader)

    assert raw_config['files_config']['run_root'] == 'cond'
    assert raw_config['files_config']['files'] == 'fehmn.files'
    assert raw_config['files_config']['area'] == 'cond.area'
    assert raw_config['files_config']['water_properties'] == os.path.join(
        '..', '..', 'end_to_end', 'fixtures', 'nist120-1800.out'
    )


def test_files_config(files_config_dict):
    config = FilesConfig.from_dict(files_config_dict)
    assert config.run_root == 'run_root'
    assert config.material_zone == Path.cwd() / 'run_root.zone'
    assert config.area == Path.cwd() / 'run_root.area'
    assert config.water_properties == Path.cwd() / '../../end_to_end/fixtures/nist120-1800.out'
    for k, v in asdict(config).items():
        if k == 'run_root':
            assert isinstance(v, str)
            continue
        assert isinstance(v, Path)


def test_model_config():
    assert ModelConfig.from_dict(
        {'kind': 'constant', 'params': {'constant': 9000}}
    ) == ModelConfig(kind='constant', params={'constant': 9000})


def test_heat_flux_config():
    assert HeatFluxConfig.from_dict(
        {'heat_flux_model': {'kind': 'constant', 'params': {'constant': 9000}}}
    ) == HeatFluxConfig(heat_flux_model=ModelConfig(kind='constant', params={'constant': 9000}))


def test_pressure_config(pressure_config_dict):
    config = PressureConfig.from_dict(pressure_config_dict)
    assert isinstance(config.pressure_model, ModelConfig)
    assert isinstance(config.interpolation_model, ModelConfig)
    assert isinstance(config.sampling_model, ModelConfig)


def test_pressure_config_no_sampling(pressure_config_dict):
    del pressure_config_dict['sampling_model']
    config = PressureConfig.from_dict(pressure_config_dict)
    assert isinstance(config.pressure_model, ModelConfig)
    assert isinstance(config.interpolation_model, ModelConfig)
    assert config.sampling_model is None


def test_rock_properties_config(rock_properties_config_dict):
    config = RockPropertiesConfig.from_dict(rock_properties_config_dict)
    assert config.zone_assignment_order == [1, 2]
    assert config.permeability_configs == [
        PropertyConfig(property_model=ModelConfig(kind='constant', params={'constant': 1e-16}), zones=[1]),
        PropertyConfig(property_model=ModelConfig(kind='constant', params={'constant': 1e-10}), zones=[2]),
    ]
    assert config.conductivity_configs == [
        PropertyConfig(
            property_model=ModelConfig(
                kind='porosity_weighted',
                params={'rock_conductivity': 2.05, 'water_conductivity': 0.62},
            ),
            zones=[1, 2],
        ),
    ]
    for property_config in (
        config.compressibility_configs + config.conductivity_configs + config.permeability_configs
        + config.grain_density_configs + config.specific_heat_configs + config.porosity_configs
    ):
        assert isinstance(property_config, PropertyConfig)
