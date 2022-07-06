from fehm_toolkit.config import (
    ModelConfig,
    PropertyConfig,
    read_legacy_rpi_config,
)
from fehm_toolkit.file_interface.legacy_config import (
    read_legacy_hfi_config,
    read_legacy_ipi_config,
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
    assert config.interpolation_model == ModelConfig(kind='none', params={})
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
    assert config.interpolation_model == ModelConfig(kind='none', params={})
    assert config.sampling_model is None


def test_read_legacy_rpi_config_jdf(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_jdf.rpi')
    assert config == {
        "rock_properties":
        {
            "zone_assignment_order": [1, 2, 3, 4, 5],
            "zone_configs_by_zone": {
                1: {
                    "porosity":
                    {
                        "model_kind": "depth_exponential_with_maximum",
                        "model_params":
                        {
                            "porosity_a": 0.84,
                            "porosity_b": -0.125
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "ctr2tcon",
                        "model_params":
                        {
                            "node_depth_columns":
                            [
                                [
                                    0,
                                    100,
                                    200,
                                    300,
                                    425,
                                    450
                                ],
                                [
                                    0,
                                    200,
                                    425,
                                    450
                                ],
                                [
                                    0,
                                    425,
                                    450
                                ]
                            ],
                            "ctr_model":
                            {
                                "model_kind": "polynomial",
                                "model_params":
                                {
                                    "x^0": 0,
                                    "x^1": 0.603,
                                    "x^2": 0.000531,
                                    "x^3": -6.84E-7
                                }
                            }
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "void_ratio_power_law",
                        "model_params":
                        {
                            "A": 3.66E-18,
                            "B": 1.68
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "overburden",
                        "model_params":
                        {
                            "a": 0.09,
                            "grav": 9.81,
                            "rhow": 1000.0,
                            "min_overburden": 25.0
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2650.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                2: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.1
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-12
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                3: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.1
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-12
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                4: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.1
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-12
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                5: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.05
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-18
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                }
            }
        }
    }


def test_read_legacy_rpi_config_np(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_np.rpi')
    assert config == {
        "rock_properties":
        {
            "zone_assignment_order": [1, 2, 3, 4, 5, 6],
            "zone_configs_by_zone": {
                1: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.62
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.6
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "void_ratio_power_law",
                        "model_params":
                        {
                            "A": 1.1E-17,
                            "B": 2.2
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "overburden",
                        "model_params":
                        {
                            "a": 0.09,
                            "grav": 9.81,
                            "rhow": 1000.0,
                            "min_overburden": 25.0
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2650.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                2: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.1
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-15
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                3: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.08
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-15
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                4: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.05
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-15
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                5: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.02
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-17
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                },
                6: {
                    "porosity":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 0.01
                        }
                    },
                    "conductivity":
                    {
                        "model_kind": "porosity_weighted",
                        "model_params":
                        {
                            "water_conductivity": 0.62,
                            "rock_conductivity": 2.05
                        }
                    },
                    "permeability":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 1E-17
                        }
                    },
                    "compressibility":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 6E-10
                        }
                    },
                    "grain_density":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 2700.0
                        }
                    },
                    "specific_heat":
                    {
                        "model_kind": "constant",
                        "model_params":
                        {
                            "constant": 800.0
                        }
                    }
                }
            }
        }
    }
