from fehm_toolkit.config import read_legacy_hfi_config, read_legacy_rpi_config


def test_read_legacy_hfi_config_jdf(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_jdf.hfi')
    params = config['heatflux']['model_params']
    assert params == {
        'crustal_age_sign': 1,
        'spread_rate_mm_per_year': 28.57,
        'coefficient_MW': 0.367E-6,
        'boundary_distance_to_ridge_m': 60000,
    }


def test_read_legacy_hfi_config_np(fixture_dir):
    config = read_legacy_hfi_config(fixture_dir / 'legacy_np.hfi')
    params = config['heatflux']['model_params']
    assert params == {
        'crustal_age_sign': -1,
        'spread_rate_mm_per_year': 17,
        'coefficient_MW': 0.5E-6,
        'boundary_distance_to_ridge_m': 144000,
    }


def test_read_legacy_rpi_config_jdf(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_jdf.rpi')
    assert config == {
        'rock_properties': {
            'compressibility': [
                {
                    'model_kind': 'overburden_compressibility',
                    'model_params': {
                        'a': 0.09,
                        'grav': 9.81,
                        'min_overburden': 25.0,
                        'rhog': 2650.0,
                        'rhow': 1000.0,
                        'specheat': 800.0,
                    },
                    'zones': [1]
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 6e-10},
                    'zones': [2, 3, 4, 5],
                },
            ],
            'conductivity': [
                {
                    'model_kind': 'ctr2tcon',
                    'model_params': {
                        'ctr_model': {
                            'model_kind': 'polynomial',
                            'model_params': {
                                'x^0': 0,
                                'x^1': 0.603,
                                'x^2': 0.000531,
                                'x^3': 6.84e-07,
                            }
                        },
                        'node_depth_columns': [
                            [0, 100, 200, 300, 425, 450],
                            [0, 200, 425, 450],
                            [0, 425, 450]],
                    },
                    'zones': [1],
                },
                {
                    'model_kind': 'porosity_weighted_conductivity',
                    'model_params': {'rock_conductivity': 2.05, 'water_conductivity': 0.62},
                    'zones': [2, 3, 4, 5],
                },
            ],
            'permeability': [
                {
                    'model_kind': 'void_ratio_power_law',
                    'model_params': {'A': 3.66e-18, 'B': 1.68},
                    'zones': [1],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-12},
                    'zones': [2],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-12},
                    'zones': [3],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-12},
                    'zones': [4],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-18},
                    'zones': [5],
                },
            ],
            'porosity': [
                {
                    'model_kind': 'sediment_porosity',
                    'model_params': {'porosity_a': 0.84, 'porosity_b': -0.125},
                    'zones': [1],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.1},
                    'zones': [2, 3, 4],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.05},
                    'zones': [5],
                },
            ],
        },
    }


def test_read_legacy_rpi_config_np(fixture_dir):
    config = read_legacy_rpi_config(fixture_dir / 'legacy_np.rpi')
    assert config == {
        'rock_properties': {
            'compressibility': [
                {
                    'model_kind': 'overburden_compressibility',
                    'model_params': {
                        'a': 0.09,
                        'grav': 9.81,
                        'min_overburden': 25.0,
                        'rhog': 2650.0,
                        'rhow': 1000.0,
                        'specheat': 800.0,
                    },
                    'zones': [1],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 6e-10},
                    'zones': [2, 3, 4, 5, 6],
                },
            ],
            'conductivity': [
                {
                    'model_kind': 'porosity_weighted_conductivity',
                    'model_params': {'rock_conductivity': 2.6, 'water_conductivity': 0.62},
                    'zones': [1],
                },
                {
                    'model_kind': 'porosity_weighted_conductivity',
                    'model_params': {'rock_conductivity': 2.05, 'water_conductivity': 0.62},
                    'zones': [2, 3, 4, 5, 6],
                },
            ],
            'permeability': [
                {
                    'model_kind': 'void_ratio_power_law',
                    'model_params': {'A': 1.1e-17, 'B': 2.2},
                    'zones': [1],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-15},
                    'zones': [2, 3, 4],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 1e-17},
                    'zones': [5, 6],
                },
            ],
            'porosity': [
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.62},
                    'zones': [1],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.1},
                    'zones': [2],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.08},
                    'zones': [3],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.05},
                    'zones': [4],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.02},
                    'zones': [5],
                },
                {
                    'model_kind': 'constant',
                    'model_params': {'constant': 0.01},
                    'zones': [6],
                },
            ],
        },
    }
