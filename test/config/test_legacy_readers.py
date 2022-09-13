from fehm_toolkit.config import (
    ModelConfig,
    PropertyConfig,
)
from fehm_toolkit.file_interface.legacy_config import (
    read_legacy_hfi_config,
    read_legacy_ipi_config,
    read_legacy_rpi_config,
)


def test_read_legacy_hfi_config_jdf(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_jdf.hfi')
    model_config = config.heat_flux_model
    assert model_config.params == {
        'crustal_age_sign': 1,
        'spread_rate_mm_per_year': 28.57,
        'coefficient_MW': 0.367E-6,
        'boundary_distance_to_ridge_m': 60000,
    }


def test_read_legacy_hfi_config_np(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_np.hfi')
    model_config = config.heat_flux_model
    assert model_config.params == {
        'crustal_age_sign': -1,
        'spread_rate_mm_per_year': 17,
        'coefficient_MW': 0.5E-6,
        'boundary_distance_to_ridge_m': 144000,
    }


def test_read_legacy_ipi_config_jdf(fixture_dir):
    config = read_legacy_ipi_config(fixture_dir / 'legacy_jdf.ipi')
    assert config.pressure_model == ModelConfig(
        kind='depth',
        params={
            'z_interval_m': 5,
            'reference_z': 4450,
            'reference_pressure_MPa': 25,
            'reference_temperature_degC': 2,
        }
    )
    assert config.interpolation_model is None
    assert config.sampling_model is None


def test_read_legacy_ipi_config_np(fixture_dir):
    config = read_legacy_ipi_config(fixture_dir / 'legacy_np.ipi')
    assert config.pressure_model == ModelConfig(
        kind='depth',
        params={
            'z_interval_m': 5,
            'reference_z': 4174.31,
            'reference_pressure_MPa': 45.289,
            'reference_temperature_degC': 2,
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
                params={'A': 3.66E-18, 'B': 1.68},
            ),
            zones=[1],
        ),
        PropertyConfig(
            property_model=ModelConfig(kind='constant', params={'constant': 1E-12}),
            zones=[2, 3, 4],
        ),
        PropertyConfig(
            property_model=ModelConfig(kind='constant', params={'constant': 1E-18}),
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
                params={'water_conductivity': 0.62, 'rock_conductivity': 2.60},
            ),
            zones=[1],
        ),
        PropertyConfig(
            property_model=ModelConfig(
                kind='porosity_weighted',
                params={'water_conductivity': 0.62, 'rock_conductivity': 2.05},
            ),
            zones=[2, 3, 4, 5, 6],
        ),
    ]
