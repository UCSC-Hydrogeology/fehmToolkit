from decimal import Decimal

from fehmtk.config import (
    ModelConfig,
    PropertyConfig,
)
from fehmtk.file_interface.legacy_config import (
    read_legacy_hfi_config,
    read_legacy_ipi_config,
    read_legacy_rpi_config,
)


def test_read_legacy_hfi_config_jdf(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_jdf.hfi')
    assert len(config.boundary_configs) == 1
    boundary_config = config.boundary_configs[0]
    assert boundary_config.boundary_model.params == {
        'crustal_age_sign': Decimal('1'),
        'crustal_age_dimension': 'x',
        'spread_rate_mm_per_year': Decimal('28.57'),
        'coefficient_MW': Decimal('0.367E-6'),
        'boundary_distance_to_ridge_m': Decimal('60000'),
    }


def test_read_legacy_hfi_config_np(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_np.hfi')
    assert len(config.boundary_configs) == 1
    boundary_config = config.boundary_configs[0]
    assert boundary_config.boundary_model.params == {
        'crustal_age_sign': Decimal('-1'),
        'crustal_age_dimension': 'x',
        'spread_rate_mm_per_year': Decimal('17'),
        'coefficient_MW': Decimal('0.5E-6'),
        'boundary_distance_to_ridge_m': Decimal('144000'),
    }


def test_read_legacy_ipi_config_jdf(fixture_dir):
    config = read_legacy_ipi_config(fixture_dir / 'legacy_jdf.ipi')
    assert config.pressure_model == ModelConfig(
        kind='depth',
        params={
            'z_interval_m': Decimal('5'),
            'reference_z': Decimal('4450'),
            'reference_pressure_MPa': Decimal('25'),
            'reference_temperature_degC': Decimal('2'),
        }
    )
    assert config.interpolation_model is None
    assert config.sampling_model is None


def test_read_legacy_ipi_config_np(fixture_dir):
    config = read_legacy_ipi_config(fixture_dir / 'legacy_np.ipi')
    assert config.pressure_model == ModelConfig(
        kind='depth',
        params={
            'z_interval_m': Decimal('5'),
            'reference_z': Decimal('4174.31'),
            'reference_pressure_MPa': Decimal('45.289'),
            'reference_temperature_degC': Decimal('2'),
        }
    )
    assert config.interpolation_model is None
    assert config.sampling_model is None


def test_read_legacy_rpi_config_jdf(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_jdf.rpi')
    assert config.zone_assignment_order == [1, 2, 3, 4, 5]
    for property_config in (
        config.compressibility_configs + config.conductivity_configs + config.permeability_configs
        + config.grain_density_configs + config.specific_heat_configs + config.porosity_configs
    ):
        assert isinstance(property_config, PropertyConfig)
        for zone in property_config.zones:
            assert zone in config.zone_assignment_order

    assert config.permeability_configs == [
        PropertyConfig(
            property_model=ModelConfig(
                kind='void_ratio_exponential',
                params={'A': Decimal('3.66E-18'), 'B': Decimal('1.68')},
            ),
            zones=[1],
        ),
        PropertyConfig(
            property_model=ModelConfig(kind='constant', params={'constant': Decimal('1E-12')}),
            zones=[2, 3, 4],
        ),
        PropertyConfig(
            property_model=ModelConfig(kind='constant', params={'constant': Decimal('1E-18')}),
            zones=[5],
        ),
    ]


def test_read_legacy_rpi_config_np(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_np.rpi')
    assert config.zone_assignment_order == [1, 2, 3, 4, 5, 6]
    for property_config in (
        config.compressibility_configs + config.conductivity_configs + config.permeability_configs
        + config.grain_density_configs + config.specific_heat_configs + config.porosity_configs
    ):
        assert isinstance(property_config, PropertyConfig)
        for zone in property_config.zones:
            assert zone in config.zone_assignment_order

    assert config.conductivity_configs == [
        PropertyConfig(
            property_model=ModelConfig(
                kind='porosity_weighted',
                params={'water_conductivity': Decimal('0.62'), 'rock_conductivity': Decimal('2.60')},
            ),
            zones=[1],
        ),
        PropertyConfig(
            property_model=ModelConfig(
                kind='porosity_weighted',
                params={'water_conductivity': Decimal('0.62'), 'rock_conductivity': Decimal('2.05')},
            ),
            zones=[2, 3, 4, 5, 6],
        ),
    ]
